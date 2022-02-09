import pygame as pg
import pytmx
from settings import *
from os import path
import pyscroll
import copy
import logging
from pytmx.util_pygame import handle_transformation
from pytmx import TileFlags
logger = logging.getLogger('orthographic')
logger.setLevel(logging.ERROR)

class StoredMapData: #Used to keep track of what NPCs, animals and objects move to what maps, and are still alive.
    def __init__(self, map_width, map_hight):
        self.npcs = []
        self.animals = []
        self.moved_npcs = []
        self.moved_animals = []
        self.moved_vehicles = []
        self.items = []
        self.vehicles = []
        self.breakable = []
        self.visited = False

        self.chests =[[0 for j in range(map_hight)] for i in range(map_width)] # Makes an empty 2D array for storing chest locations. Chests will be stored in the array as dictionaries.
        self.doors = self.chests.copy()
        self.tile_changes = {}
        self.gid_changes = set()

class TiledMap:
    def __init__(self, game, map_name):
        self.game = game
        self.filename = path.join(map_folder, map_name)
        self.map_name = map_name
        self.name, _ = map_name.split(".")
        tm = pytmx.load_pygame(self.filename)
        self.width = tm.width * tm.tilewidth
        self.tiles_wide = tm.width
        self.tile_size = tm.tilewidth
        self.height = tm.height * tm.tileheight
        self.tiles_high = tm.height
        self.tmxdata = tm
        map_data = pyscroll.data.TiledMapData(self.tmxdata)
        self.stored_map_data = StoredMapData(self.tiles_wide, self.tiles_high)
        self.map_layer = pyscroll.BufferedRenderer(map_data, (self.game.screen_width, self.game.screen_height), clamp_camera=True)
        for i, layer in enumerate(self.tmxdata.visible_layers):
            if layer.name == 'Base Layer':
                self.base_layer = i
            elif layer.name == 'Rounded Corners':
                self.ocean_plants_layer = i
            elif layer.name == 'Water':
                self.water_layer = i
            elif layer.name == 'Plants Waves Rivers':
                self.river_layer = i
            elif layer.name == 'Trees':
                self.trees_layer = i
        self.items_layer = self.ocean_plants_layer
        self.mob_layer = self.river_layer
        self.player_layer = self.river_layer
        self.vehicle_layer = self.river_layer + 1
        self.bullet_layer = self.river_layer + 2
        self.effects_layer = self.river_layer + 5
        self.sky_layer = self.river_layer + 6
        self.walls = []
        self.tile_props = []
        self.set_map_tiles_props()
        #self.export_tmx_data()
        #self.overlay = self.generate_over_layer()
        #self.minimap = MiniMap(tm)

    def store_map_changes(self, layer, x, y, gid):
        self.stored_map_data.tile_changes[(layer, (x, y))] = gid
        self.tmxdata.layers[layer].data[y][x] = gid
        self.update_tile_props(x, y)

    def get_and_store_new_rotated_gid(self, gid, hor=False, vert=False, diag=False):
        if hor in [True, False]:
            tileflags = TileFlags(hor, vert, diag)
        else:
            tileflags = hor # allows for passing tile fags as one parameter.
        self.stored_map_data.gid_changes.add((gid, tileflags))
        return self.get_new_rotated_gid(gid, tileflags)

    def load_stored_data(self):
        for value in self.stored_map_data.gid_changes:
            gid = value[0]
            tileflags = value[1]
            temp_gid = self.get_new_rotated_gid(gid, tileflags)
        for key, value in self.stored_map_data.tile_changes.items():
            layer = key[0]
            x = key[1][0]
            y = key[1][1]
            self.tmxdata.layers[layer].data[y][x] = value
            self.update_tile_props(x, y)
        self.redraw()

    def get_new_rotated_gid(self, gid, hor = False, vert = False, diag = False):
        if hor in [True, False]:
            tileflags = TileFlags(hor, vert, diag)
        else:
            tileflags = hor # allows for passing tile fags as one parameter.
        tiled_gid = self.tmxdata.tiledgidmap[gid]
        new_gid = self.tmxdata.register_gid(tiled_gid, tileflags)
        gid_info = self.tmxdata.map_gid(tiled_gid)
        unrotated_gid = None
        orig_flags = None
        for tile in gid_info:
            if tile[1] == (False, False, False): # Gets unrotated tile gid
                unrotated_gid = tile[0]
        if unrotated_gid:
            gid = unrotated_gid
        else:
            gid = gid_info[0][0]
            orig_flags = gid_info[0][1] # gets the rotational flags

        original_image = self.tmxdata.get_tile_image_by_gid(gid)
        if orig_flags:
            if orig_flags.flipped_diagonally:
                orig_flags = TileFlags(orig_flags.flipped_horizontally, orig_flags.flipped_vertically, orig_flags.flipped_diagonally)
            unrotated_image = handle_transformation(original_image, orig_flags)
        else:
            unrotated_image = original_image
        new_image = handle_transformation(unrotated_image, tileflags)
        if new_gid > len(self.tmxdata.images) - 1:
            self.tmxdata.images.append(new_image)
        else:
            self.tmxdata.images[new_gid] = new_image

        props = self.tmxdata.get_tile_properties_by_gid(gid)
        self.tmxdata.set_tile_properties(new_gid, props)
        return new_gid

    def gid_to_nearest_angle(self, gid, angle):
        nearest = 90 * round(angle / 90)
        if nearest == 90:
            return gid
        elif nearest == 180:
            return self.get_and_store_new_rotated_gid(gid, True, False, True)
        elif nearest == 270:
            return self.get_and_store_new_rotated_gid(gid, True, True, False)
        elif nearest in [0, 360]:
            return self.get_and_store_new_rotated_gid(gid, False, True, True)

    def is_next_to(self, x, y, tile_prop): # Checks to see if a location is by a specific kind of tile
        surrounding_tilesxy_list = [(x, y), ((x - 1), (y - 1)), (x, (y - 1)), ((x + 1), (y - 1)), ((x - 1), y), ((x + 1), y),
                                    ((x - 1), (y + 1)), (x, (y + 1)), ((x + 1), (y + 1))]
        for tile_pos in surrounding_tilesxy_list:
            if tile_prop in self.tile_props[tile_pos[1]][tile_pos[0]]['material']:
                return True
            elif tile_prop in self.tile_props[tile_pos[1]][tile_pos[0]]['roof']:
                return True
        return False

    def gid_with_property(self, key, value):
        for gid, props in self.tmxdata.tile_properties.items():
            if props.get(key) == value:
                return gid

    def get_gid_by_prop_name(self, property_name):
        gid = self.gid_with_property('roof', property_name)
        if gid == None:
            gid = self.gid_with_property('material', property_name)
        gid = self.get_and_store_new_rotated_gid(gid)
        return gid

    def get_tile_flags(self, gid): # gets the rotational flags from the tiled map data that are associated with a gid
        flags = TileFlags(False, False, False)
        tiled_gid = self.tmxdata.tiledgidmap[gid]
        gid_info = self.tmxdata.map_gid(tiled_gid)
        for tile in gid_info:
            if tile[0] == gid:
                flags = tile[1]
                return flags
        return flags

    def set_map_tiles_props(self):
        self.walls = []
        self.tile_props = []
        for y in range(0, self.tiles_high):
            wall_row = []
            props_row = []
            for x in range(0, self.tiles_wide):
                tile_rect, tile_props = self.get_tile_props(x, y)
                wall_row.append(tile_rect)
                props_row.append(tile_props)
            self.tile_props.append(props_row)
            self.walls.append(wall_row)

    def update_tile_props(self, x, y):
        tile_rect, tile_props = self.get_tile_props(x, y)
        self.tile_props[y][x] = tile_props
        self.walls[y][x] = tile_rect

    def get_tile_props(self, x, y):
        tile_props = {}
        tile_props['material'] = ''
        tile_props['wall'] = ''
        tile_props['plant'] = ''
        tile_props['plant layer'] = self.river_layer
        tile_props['harvest'] = ''
        tile_props['tree'] = ''
        tile_props['roof'] = ''
        tile_rect = False

        layers = [self.trees_layer, self.river_layer, self.ocean_plants_layer, self.water_layer, self.base_layer]
        for layer in layers:
            props = self.tmxdata.get_tile_properties(x, y, layer)
            if props != None:
                if 'wall' in props:
                    tile_props['wall'] = props['wall']
                    tile_rect = pg.Rect(x * self.tile_size, y * self.tile_size, self.tile_size, self.tile_size)
                if (not tile_props['material']) and ('material' in props): # the not clause makes it so it doesn't assign tiles that have already been assigned, as they must be assigned in order of the layers list.
                    tile_props['material'] = props['material']
                    chest_found = False
                    if 'chest' in props['material']:
                        for chest in CHESTS.keys():
                            if (chest == (x, y)) and (CHESTS[chest]['map'] == self.name):
                                if not self.stored_map_data.chests[y][x]: # Assigns the chest dictionary to the chest array if it hasn't been assigned yet.
                                    self.stored_map_data.chests[y][x] = fix_inventory(CHESTS[chest], 'chest')
                                chest_found = True
                        if not chest_found: # If not chest is found in the chests.py CHESTS then an empty chest is created and the map name assigned.
                            self.stored_map_data.chests[y][x] = fix_inventory(EMPTY_CHEST.copy(), 'chest')
                            self.stored_map_data.chests[y][x]['map'] = self.map_name

                    door_found = False
                    if 'door' in props['material']:
                        for door in DOORS.keys():
                            if (door == (x, y)) and (DOORS[door]['map'] == self.name):
                                if not self.stored_map_data.doors[y][x]: # Assigns the door dictionary to the door array if it hasn't been assigned yet.
                                    self.stored_map_data.doors[y][x] = DOORS[door].copy()
                                door_found = True
                        if not door_found: # If not chest is found in the chests.py CHESTS then an empty chest is created and the map name assigned.
                            self.stored_map_data.doors[y][x] = STANDARD_DOOR.copy()
                            self.stored_map_data.doors[y][x]['map'] = self.map_name

                if 'plant' in props:
                    tile_props['plant'] = props['plant']
                    tile_props['plant layer'] = layer
                    if 'harvest' in props:
                        tile_props['harvest'] = props['harvest']
                if 'tree' in props:
                    tile_props['tree'] = props['tree']
                if 'roof' in props:
                    tile_props['roof'] = props['roof']
        return tile_rect, tile_props

    def toggle_visible_layers(self):
        if self.game.player_inside:
            for layer in self.tmxdata.visible_layers:
                if ('roof' in layer.name or 'Trees' in layer.name):
                    if isinstance(layer, pytmx.TiledTileLayer):
                        layer.visible = False
        else:
            for layer in self.tmxdata:
                if layer.name != None:
                    if ('roof' in layer.name or 'Trees' in layer.name):
                        if isinstance(layer, pytmx.TiledTileLayer):
                            layer.visible = True
        self.map_layer.redraw_tiles(self.map_layer._buffer)

    def redraw(self): # Redraws the map for tile updates
        self.map_layer.redraw_tiles(self.map_layer._buffer)

    def export_tmx_data(self):
        tiled_layers = {}
        for i, layer in enumerate(self.tmxdata.layers):
            if isinstance(layer, pytmx.TiledTileLayer):  # Excludes object layers
                tiled_layer = []
                for row in self.tmxdata.layers[i].data:
                    new_row = []
                    for item in row:
                        new_row.append(self.convert_to_tiled_gid(item))
                    tiled_layer.append(row)
                tiled_layers[layer.name] = tiled_layer

        self.write_tmx_file(tiled_layers)

    def convert_to_tiled_gid(self, gid):
        if gid == 0:
            return 0
        tiled_gid = self.tmxdata.tiledgidmap[gid] # Does not truely map pytmx gids to tiled gids
        return tiled_gid

    def write_tmx_file(self, tiled_layers):
        MAP_SIZE = 1000
        filename = path.join(map_folder, "newmap.tmx")
        outfile = open(filename, "w")
        for layer_name, layer_data in tiled_layers.items():
            next_layer_txt = """<layer id="5" name="{lname}" width="{mapw}" height="{mapw}">
              <data encoding="csv">""".format(lname=layer_name, mapw=str(MAP_SIZE))
            outfile.write(next_layer_txt)
            outfile.write("\n")
            for i, y in enumerate(layer_data):
                new_row_str = str(y)
                new_row_str = new_row_str.replace(', ', ',')
                new_row_str = new_row_str.replace('[', '')
                new_row_str = new_row_str.replace(']', '')
                if i != MAP_SIZE - 1:
                    new_row_str = new_row_str + ","
                outfile.write(new_row_str)
                outfile.write("\n")
            footer = """</data>
             </layer>"""
            outfile.write(footer)
        outfile.close()

    #def generate_under_layer(self):
    #    for layer in self.tmxdata.visible_layers:
    #        if isinstance(layer, pytmx.TiledTileLayer):
    #            if ('roof' in layer.name or 'tree' in layer.name or 'high shadow' in layer.name):
    #                layer.visible = False
    #            else:
    #                layer.visible = True
    #    map_data = pyscroll.data.TiledMapData(self.tmxdata)
    #    return pyscroll.BufferedRenderer(map_data, (self.game.screen_width, self.game.screen_height), clamp_camera=True, tall_sprites=1)

    #def generate_over_layer(self):
    #    for layer in self.overlay_data.visible_layers:
    #        if isinstance(layer, pytmx.TiledTileLayer):
    #            if ('roof' in layer.name or 'tree' in layer.name or 'high shadow' in layer.name):
    #                layer.visible = True
    #            else:
    #                layer.visible = False
    #    map_data = pyscroll.data.TiledMapData(self.overlay_data)
    #    return pyscroll.BufferedRenderer(map_data, (self.game.screen_width, self.game.screen_height), clamp_camera=True, alpha=True, tall_sprites=1)

    #def render(self, surface):
    #    ti = self.tmxdata.get_tile_image_by_gid
    #    for layer in self.tmxdata.visible_layers:
    #        if not ('roof' in layer.name or 'tree' in layer.name or 'high shadow' in layer.name):
    #            if isinstance(layer, pytmx.TiledTileLayer):
    #                for x, y, gid, in layer:
    #                    tile = ti(gid)
    #                    if tile:
    #                        surface.blit(tile, (x * self.tmxdata.tilewidth,
    #                                            y * self.tmxdata.tileheight))

    #def test_render(self, surface):
    #    ti = self.tmxdata.get_tile_image_by_gid
    #    blank_surface = pg.Surface((self.tile_size, self.tile_size)).convert()
    #    playerx = int(self.game.player.pos.x / self.tile_size)
    #    playery = int(self.game.player.pos.y / self.tile_size)
    #    for layernum, layer in enumerate(self.tmxdata.visible_layers):
    #        if isinstance(layer, pytmx.TiledTileLayer):
    #            for j, y in enumerate(range(playery - 5, playery + 5)):
    #                for i, x in enumerate(range(playerx - 8, playerx + 8)):
    #                    try:
    #                        tile_img = self.tmxdata.get_tile_image(x, y, layernum)
    #                        if tile_img != None:
    #                            surface.blit(tile_img, (i * self.tmxdata.tilewidth, j * self.tmxdata.tileheight))
    #                    except:
    #                        surface.blit(blank_surface, (i * self.tmxdata.tilewidth, j * self.tmxdata.tileheight))

    #def update(self):
    #    self.image = self.make_map()
    #    self.rect = self.image.get_rect()
    #    self.rect.center = self.game.player.rect.center

    #def make_map(self):
    #    #temp_surface = pg.Surface((self.width, self.height)).convert()
    #    temp_surface = pg.Surface((self.tile_size * 16, self.tile_size * 10)).convert()
    #    self.render(temp_surface)
    #    return temp_surface

    # This section creates the map image that is drawn over the player: for roofs and trees.

"""
class MapOverlay:
    def __init__(self, tm):
        self.width = tm.width * tm.tilewidth
        self.height = tm.height * tm.tileheight
        self.tmxdata = tm
        self.image = self.make_map()
        self.rect = self.image.get_rect()
    def render(self, surface):
        ti = self.tmxdata.get_tile_image_by_gid
        for layer in self.tmxdata.visible_layers:
            if 'roof' in layer.name or 'tree' in layer.name  or 'high shadow' in layer.name:
                if isinstance(layer, pytmx.TiledTileLayer):
                    for x, y, gid, in layer:
                        tile = ti(gid)
                        if tile:
                            surface.blit(tile, (x * self.tmxdata.tilewidth,
                                                y * self.tmxdata.tileheight))

    def make_map(self):
        temp_surface = pg.Surface((self.width, self.height), pg.SRCALPHA).convert_alpha()  # SRCALPHA does per pixel transparency and allows the transparency of this layer to show through on the bellow layers.
        self.render(temp_surface)
        return temp_surface
"""

"""
class MiniMap:
    def __init__(self, tm):
        self.mapwidth = tm.width * tm.tilewidth
        self.mapheight = tm.height * tm.tileheight
        self.tmxdata = tm
        self.size = 256
        self.ratio = self.size / self.mapwidth
        self.tile_size = int(self.size / tm.width)
        self.height = self.mapheight * self.ratio
        self.image = self.make_map()
        self.rect = self.image.get_rect()

    def render(self, surface):
        ti = self.tmxdata.get_tile_image_by_gid
        for layer in self.tmxdata.visible_layers:
            if isinstance(layer, pytmx.TiledTileLayer):
                for x, y, gid, in layer:
                    tile = ti(gid)
                    if tile:
                        small_tile = pg.transform.scale(tile, (self.tile_size, self.tile_size))
                        surface.blit(small_tile, (x * self.tile_size,
                                            y * self.tile_size))
        mini_surface = surface
        return mini_surface

    def make_map(self):
        temp_surface = pg.Surface((self.size, self.height)).convert()
        temp_surface = self.render(temp_surface)
        return temp_surface

    def resize(self, enlarge = True):
        if enlarge:
            self.size += 128
            if self.size > HEIGHT:
                self.size = 128
        else:
            self.size -= 128
            if self.size < 128:
                self.size = 128
        self.ratio = self.size / self.mapwidth
        self.height = self.mapheight * self.ratio
        self.tile_size = int(self.size / 64)
        self.image = self.make_map()
        self.rect = self.image.get_rect()"""


class Camera():
    def __init__(self, game, width, height):
        self.camera = self.rect = pg.Rect(0, 0, width, height)
        self.width = width
        self.height = height
        self.x = 0
        self.y = 0
        self.game = game

    def apply(self, entity):
        return entity.rect.move(self.camera.topleft)

    def apply_rect(self, rect):
        return rect.move(self.camera.topleft)

    def update(self, target): #Centers camera on player. target = player
        self.x = -target.rect.centerx + int(self.game.screen_width / 2)
        self.y = -target.rect.centery + int(self.game.screen_height / 2)

        # limit scrolling to map size
        self.x = min(0, self.x)  # left
        self.y = min(0, self.y)  # top
        self.x = max(-(self.width - self.game.screen_width), self.x)  # right
        self.y = max(-(self.height - self.game.screen_height), self.y)  # bottom

        self.camera = pg.Rect(self.x, self.y, self.width, self.height)