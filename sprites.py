import pygame as pg
from random import uniform, choice, randint, random, randrange
from settings import *
from npcs import *
from os import path
import copy
from collections import Counter
from menu import *
from vehicles import *
from math import ceil
from time import perf_counter, sleep

vec = pg.math.Vector2

def play_relative_volume(source, sound, effect = True):  # This def plays sounds where the volume is adjusted according to the distance the source is from the player (the listener).
    volume = 1
    if source != source.game.player:
        player_dist = source.game.player.pos - source.pos
        player_dist = source.game.player.pos - source.pos
        player_dist = player_dist.length()
        if player_dist < SOUND_SOURCE_DISTANCE:
            if player_dist > 0:
                volume = 128 / player_dist
            else:
                volume = 1
            if volume > 1:
                volume = 1
        else:
            volume = 0
    if volume > 0:
        if effect:
            snd = source.game.effects_sounds[sound]
        else:
            snd = sound
        for channel in source.game.channel_list:
            if not channel.get_busy():
                channel.set_volume(volume)
                channel.play(snd, loops=0)
                break

def gender_tag(sprite):
    if sprite.equipped['gender'] == 'male':
        return "_M"
    else:
        return "_F"

def correct_filename(item):
    filename = item['name']
    for material in MATERIALS:
        if material in item['name']:
            filename = item['name'].replace(material + ' ', '')
            return filename
            break
    for color in ALL_ITEM_COLORS:
        if color in item['name']:
            filename = item['name'].replace(color + ' ', '')
            return filename
            break

    if 'potion' in item['name']:
        filename = 'potion'
    elif ('type' in item.keys()) and (item['type'] == 'book'):
        filename = 'generic book'
    elif 'key' in item['name']:
        filename = 'key'
    return filename

def round_to_base(x, base=90):
    return base * round(x / base)

def get_tile_pos(sprite):
    return int(sprite.pos.x / sprite.game.map.tile_size), int(sprite.pos.y / sprite.game.map.tile_size)

def get_next_tile_pos(sprite):
    pdir = vec(1, 0).rotate(-sprite.rot)
    next_x = int(sprite.pos.x / sprite.game.map.tile_size + pdir.x)
    next_y = int(sprite.pos.y / sprite.game.map.tile_size + pdir.y)
    if next_x >= sprite.game.map.tiles_wide: next_x = sprite.game.map.tiles_wide - 1
    if next_y >= sprite.game.map.tiles_high: next_y = sprite.game.map.tiles_high - 1
    return next_x, next_y

#def get_tile_props(sprite, layer, x = None, y = None):  # Gets the properties of the tile the sprite is on.
#    if x == None:
#        pos = get_tile_pos(sprite)
#        x = pos[0]
#        y = pos[1]
#    if x < 0: x = 0
#    if y < 0: y = 0
#    if x >= sprite.game.map.tiles_wide: x = sprite.game.map.tiles_wide - 1
#    if y >= sprite.game.map.tiles_high: y = sprite.game.map.tiles_high - 1
#    return sprite.game.map.tmxdata.get_tile_properties(x, y, layer)

def set_tile_props(sprite): # sets a variable that keeps track of the important properties a sprite is on in order of their priority.
    x, y = get_tile_pos(sprite)
    sprite.tile_props = sprite.game.map.tile_props[y][x]

    # Sets sprite environmental state variables
    if 'water' in sprite.tile_props['material']:
        sprite.swimming = True
    else:
        sprite.swimming = False
    if 'shallows' in sprite.tile_props['material']:
        sprite.in_shallows = True
    else:
        sprite.in_shallows = False
    if 'long grass' in sprite.tile_props['material']:
        sprite.in_grass = True
    else:
        sprite.in_grass = False
    if sprite.tile_props['roof'] != '':
        sprite.inside = True
    else:
        sprite.inside = False

    # sets tile props for next tile. This is used for interacting with things that are in front of sprites like workstations or plants.
    next_x, next_y = get_next_tile_pos(sprite)
    sprite.next_tile_props = sprite.game.map.tile_props[next_y][next_x]
    check_tile_hits(sprite)
    check_harvest(sprite, x, y, next_x, next_y)
    check_tree(sprite, next_x, next_y)

def check_tile_hits(sprite):
    # player hit container/chest
    if 'chest' in sprite.next_tile_props['material']:
        if not sprite.npc:
            x, y = get_next_tile_pos(sprite)
            chest = sprite.game.map.chests[y][x]
            if not chest['locked']:
                sprite.game.message_text = True
                sprite.game.message = pg.key.name(sprite.game.key_map['interact']).upper() + ' to open chest.'
                if sprite.e_down:
                    play_relative_volume(sprite, 'door open')
                    sprite.game.make_work_station_menu('looting', chest['inventory'])
                    sprite.game.message_text = False
                    sprite.e_down = False
            else:
                sprite.game.message_text = True
                key_name = chest['name'] + ' key'
                if sprite.check_inventory('lock pick') or sprite.check_inventory(key_name):
                    sprite.game.message = pg.key.name(sprite.game.key_map['interact']).upper() + ' to unlock chest.'
                    if sprite.e_down:
                        if not sprite.game.in_lock_menu:
                            sprite.game.in_lock_menu = sprite.game.in_menu = True
                            sprite.game.make_lock_menu(chest)
                        sprite.game.message_text = False
                        sprite.e_down = False
                else:
                    sprite.game.message = 'This chest is locked.'

    elif ('window' in sprite.next_tile_props['material']) or ('door' in sprite.next_tile_props['material']):
        sprite.inside = True
        if ('door' in sprite.next_tile_props['material']):
            sprite.game.message_text = True
            x, y = get_next_tile_pos(sprite)
            if ('closed' in sprite.next_tile_props['material']):
                door = sprite.game.map.doors[y][x]
                if not door['locked']:
                    sprite.game.message = pg.key.name(sprite.game.key_map['interact']).upper() + ' to open door.'
                    if sprite.e_down:
                        play_relative_volume(sprite, 'door open')
                        door_name = sprite.next_tile_props['material'].replace('closed', 'open')
                        new_gid = sprite.game.map.gid_with_property('material', door_name) # Gets teh gid of the opposite kind of door (open/closed)
                        orig_gid = sprite.game.map.tmxdata.get_tile_gid(x, y, sprite.game.map.ocean_plants_layer) # gets the original gid of the door tile so we know it's rotation.
                        flags = sprite.game.map.get_tile_flags(orig_gid) # gets the rotational flags of the door
                        gid = sprite.game.map.get_new_rotated_gid(new_gid, flags)
                        sprite.game.map.tmxdata.layers[sprite.game.map.ocean_plants_layer].data[y][x] = gid
                        sprite.game.map.update_tile_props(x, y)  # Updates properties for tiles that have changed.
                        sprite.game.map.redraw()
                        sprite.game.message_text = False
                        sprite.e_down = False
                else:
                    sprite.game.message_text = True
                    key_name = door['name'] + ' key'
                    if sprite.check_inventory('lock pick') or sprite.check_inventory(key_name):
                        sprite.game.message = pg.key.name(sprite.game.key_map['interact']).upper() + ' to unlock ' + door['name'] + '.'
                        if sprite.e_down:
                            if not sprite.game.in_lock_menu:
                                sprite.game.in_lock_menu = sprite.game.in_menu = True
                                sprite.game.make_lock_menu(door)
                            sprite.game.message_text = False
                            sprite.e_down = False
                    else:
                        sprite.game.message = door['name'] + ' is locked.'

            else:
                sprite.game.message = pg.key.name(sprite.game.key_map['interact']).upper() + ' to close door.'
                if sprite.e_down:
                    play_relative_volume(sprite, 'door close')
                    door_name = sprite.next_tile_props['material'].replace('open', 'closed')
                    new_gid = sprite.game.map.gid_with_property('material',
                                                door_name)  # Gets teh gid of the opposite kind of door (open/closed)
                    orig_gid = sprite.game.map.tmxdata.get_tile_gid(x, y,
                                                                    sprite.game.map.ocean_plants_layer)  # gets the original gid of the door tile so we know it's rotation.
                    flags = sprite.game.map.get_tile_flags(orig_gid)  # gets the rotational flags of the door
                    gid = sprite.game.map.get_new_rotated_gid(new_gid, flags)
                    sprite.game.map.tmxdata.layers[sprite.game.map.ocean_plants_layer].data[y][x] = gid
                    sprite.game.map.update_tile_props(x, y)  # Updates properties for tiles that have changed.
                    sprite.game.map.redraw()
                    sprite.game.message_text = False
                    sprite.e_down = False

    # player hits work station (forge, grinder, work bench, etc)
    elif (sprite.next_tile_props['material'] in WORK_STATION_LIST) or (sprite.tile_props['material'] in WORK_STATION_LIST):
        if sprite.next_tile_props['material'] in WORK_STATION_LIST:
            station_type = sprite.next_tile_props['material']
        else:
            station_type = sprite.tile_props['material']
        if not sprite.npc:
            sprite.game.message_text = True
            sprite.game.message = pg.key.name(sprite.game.key_map['interact']).upper() + ' to use ' + station_type
            if sprite.e_down:
                sprite.game.in_station_menu = True
                sprite.game.in_menu = True
                sprite.game.make_work_station_menu(station_type)
                sprite.game.message_text = False
                sprite.e_down = False

    elif 'bed' in sprite.tile_props['material']:
        if not sprite.npc:
            sprite.game.message_text = True
            sprite.game.message = 'Press ' + pg.key.name(sprite.game.key_map['interact']).upper() + ' to sleep in bed.'
        if sprite.e_down:
            sprite.sleep_in_bed()
            sprite.game.message_text = False
            sprite.e_down = False

    elif 'toilet' in sprite.tile_props['material']:
        sprite.game.message_text = True
        sprite.game.message = pg.key.name(sprite.game.key_map['interact']).upper() + ' to use toilet'
        if sprite.e_down:
            sprite.use_toilet()
            sprite.game.message_text = False
            sprite.e_down = False

    elif 'lava' in sprite.tile_props['material'] and not (sprite.jumping or sprite.flying):
        sprite.gets_hit(20, 0, 0)
        now = pg.time.get_ticks()
        if now - sprite.last_fire > 300:
            play_relative_volume(sprite, 'fire blast')
            Stationary_Animated(sprite.game, sprite.pos, 'fire', 3000)
            sprite.last_fire = now

    elif 'electric entry' in sprite.tile_props['material']:
        if sprite.race not in ['mechanima', 'mechanima dragon', 'mech_suit']:
            sprite.gets_hit(15, 0, 50)
            now = pg.time.get_ticks()
            if now - sprite.last_fire > 300:
                play_relative_volume(sprite, 'fire blast')
                Stationary_Animated(sprite.game, sprite.pos, 'fire', 3000)
                sprite.last_fire = now
        else:
            sprite.add_health(0.02)

    elif 'charger' in sprite.tile_props['material']:
        if 'mechanima' in sprite.race:
            now = pg.time.get_ticks()
            if now - sprite.last_charge > 1000:
                sprite.game.last_charge = now
                if sprite.possessing:
                    if sprite.possessing.race == 'mech_suit':
                        sprite.possessing.add_health(4)
                else:
                    sprite.add_health(4)
                    try:
                        sprite.add_magica(4)
                        sprite.add_stamina(4)
                    except:
                        pass


def check_harvest(sprite, x, y, next_x, next_y):
    def check(sprite, x, y, props):
        if sprite not in sprite.game.flying_vehicles:
            if sprite in sprite.game.players:
                sprite.game.message_text = True
                sprite.game.message = pg.key.name(sprite.game.key_map['interact']).upper() + ' to harvest ' + props['plant']
            if sprite.e_down:
                harvest_plant(sprite, x, y, props)
                if sprite in sprite.game.players:
                    sprite.game.message_text = False
                    sprite.e_down = False
    # Checks for plants to harvest
    if sprite.tile_props['harvest'] != '':
        check(sprite, x, y, sprite.tile_props)
    elif sprite.next_tile_props['harvest'] != '':
        check(sprite, next_x, next_y, sprite.next_tile_props)

def harvest_plant(sprite, x, y, props):
    if sprite.add_inventory(props['plant'], 1):
        if props['harvest'] != 'none':
            sprite.game.map.tmxdata.layers[props['plant layer']].data[y][x] = sprite.game.map.gid_with_property('plant', props['harvest'])
        else:
            sprite.game.map.tmxdata.layers[props['plant layer']].data[y][x] = 0
        sprite.game.map.update_tile_props(x, y) # Updates properties for tiles that have changed.
        sprite.game.map.redraw()
        set_tile_props(sprite)

def check_equip_for(sprite, search_string):
    # Checks to see if you are holding a specic kind of item by name or type.
    if ('name' in sprite.hand_item) and (search_string in sprite.hand_item['name']):
        return True
    elif ('name' in sprite.hand2_item) and (search_string in sprite.hand2_item['name']):
        return True
    elif ('type' in sprite.hand_item) and (search_string in sprite.hand_item['type']):
        return True
    elif ('type' in sprite.hand2_item) and (search_string in sprite.hand2_item['type']):
        return True
    else:
        return False

def check_tree(sprite, x, y):
    if sprite.next_tile_props['tree'] != '':
        if sprite not in sprite.game.flying_vehicles:
            if (sprite in sprite.game.players) and check_equip_for(sprite, 'axe'):
                sprite.game.message_text = True
                sprite.game.message = pg.key.name(sprite.game.key_map['interact']).upper() + ' to chop down this ' + sprite.next_tile_props['tree']
            if sprite.e_down and check_equip_for(sprite, 'axe'):
                harvest_tree(sprite, x, y)
                if sprite in sprite.game.players:
                    sprite.game.message_text = False
                    sprite.e_down = False

def harvest_tree(sprite, x, y):
    size = ""
    amount = 10
    if 'large' in sprite.next_tile_props['tree']:
        yi = y - 3
        yf = y + 3
        xi = x - 3
        xf = x + 3
        size = 'large'
        name = sprite.next_tile_props['tree'].replace('large ', '')
        amount = 30
    elif 'medium' in sprite.next_tile_props['tree']:
        yi = y - 2
        yf = y + 2
        xi = x - 2
        xf = x + 2
        size = 'medium'
        name = sprite.next_tile_props['tree'].replace('medium ', '')
        amount = 20
    elif 'small' in sprite.next_tile_props['tree']:
        yi = y - 1
        yf = y + 1
        xi = x - 1
        xf = x + 1
        size = 'small'
        name = sprite.next_tile_props['tree'].replace('small ', '')
    sprite.game.channel6.play(sprite.game.effects_sounds['chopping wood'], loops=0) # This needs to be changed to be more active.
    while sprite.game.channel6.get_busy():
        pass
    sprite.game.channel6.play(sprite.game.effects_sounds['tree fall'], loops=0)
    for j in range(yi, yf + 1):
        for i in range(xi, xf + 1):
            sprite.game.map.tmxdata.layers[sprite.game.map.trees_layer].data[j][i] = 0
            sprite.game.map.update_tile_props(i, j)  # Updates properties for tiles that have changed.
    sprite.game.map.redraw()
    Falling_Tree(sprite, x, y, xi, xf, yi, yf, name, size)
    wear_out_tool(sprite, 'axe', amount)

def wear_out_tool(sprite, search_string, amount = 1):
    # Checks to see if you are holding a specic kind of item by name or type.
    if ('name' in sprite.hand_item) and (search_string in sprite.hand_item['name']):
        sprite.hand_item['hp'] -= amount
    elif ('name' in sprite.hand2_item) and (search_string in sprite.hand2_item['name']):
        sprite.hand2_item['hp'] -= amount
    elif ('type' in sprite.hand_item) and (search_string in sprite.hand_item['type']):
        sprite.hand_item['hp'] -= amount
        hand = sprite.hand_item
    elif ('type' in sprite.hand2_item) and (search_string in sprite.hand2_item['type']):
        sprite.hand2_item['hp'] -= amount
    for i, icon in enumerate(sprite.game.inventory_hud_icons):
        icon.update()
        icon.resize(HUD_ICON_SIZE)
    remove_drained_equipped(sprite)

def remove_drained_equipped(sprite):
    for key, value in sprite.equipped.items():
        if value and (key not in ['weapons', 'weapons2']):
            if ('hp' in value) and (value['hp'] <= 0):
                if sprite.hand_item == sprite.equipped[key]:
                    sprite.hand_item = {}
                    sprite.equipped['weapons'] = None
                    sprite.game.selected_hud_item.clear_item()
                    for i, icon in enumerate(sprite.game.inventory_hud_icons):
                        icon.update()
                        icon.resize(HUD_ICON_SIZE)
                elif sprite.hand2_item == sprite.equipped[key]:
                    sprite.hand2_item == {}
                    sprite.equipped['weapons2'] = None
                sprite.equipped[key] = {}
                sprite.body.update_animations()

def auto_crop(surf):
    rect = surf.get_bounding_rect()
    return surf.subsurface(rect)

def wall_check(sprite):  # Used for tile-based wall collisions
    if sprite.tile_props['wall'] == 'wall':
        return True
    else:
        return False

def next_wall_check(sprite, x_off = 0, y_off = 0):  # Used for tile-based wall detection
    pdir = vec(1, 0).rotate(-sprite.rot)
    x = int(sprite.pos.x / sprite.game.map.tile_size + pdir.x) + x_off
    y = int(sprite.pos.y / sprite.game.map.tile_size + pdir.y) + y_off
    return xy_wall_check(sprite, x, y)

def xy_wall_check(sprite, x, y):  # Used for tile-based wall checks
    if x < 0: return False
    if y < 0: return False
    if x >= sprite.game.map.tiles_wide: return False
    if y >= sprite.game.map.tiles_high: return False
    if sprite.tmxdata.walls[y][x]:
        return True
    else:
        return False

#def in_wall(game, group, pos):
#    for wall in group:
#        if wall not in game.door_walls:
#            if wall.rect.left < pos.x < wall.rect.right:
#                if wall.rect.top < pos.y < wall.rect.bottom:
#                    return wall
#    else:
#        return False

def set_elevation(sprite):
    # Sets elevation to the highest elevation you hit.
    hit_level = sprite
    hits = pg.sprite.spritecollide(sprite, sprite.game.elevations, False)
    if hits:
        for hit in hits:  # Uses only the highest elevation you hit.
            if hit not in sprite.game.climbables_and_jumpables:
                if hit.elevation > hit_level.elevation:
                    hit_level = hit
        sprite.elevation = hit_level.elevation

def color_image(image, color):
    temp_image = image.copy()
    color_image = pg.Surface(temp_image.get_size()).convert_alpha()
    color_image.fill(color)
    temp_image.blit(color_image, (0, 0), special_flags=pg.BLEND_RGBA_MULT)
    return temp_image

def get_surrounding_walls(sprite, x_off = 0, y_off = 0):
    pos = get_tile_pos(sprite)
    x = pos[0] + x_off
    y = pos[1] + y_off
    surrounding_tilesxy_list = [((x-1),(y-1)), (x,(y-1)), ((x+1),(y-1)), ((x-1),y), ((x+1),y), ((x-1),(y+1)), (x,(y+1)), ((x+1),(y+1))]
    surrounding_tile_rects = []
    for tile_pos in surrounding_tilesxy_list: # Makes a list of surrounding wall rects from the walls list.
        if sprite.game.map.walls[tile_pos[1]][tile_pos[0]]:
            surrounding_tile_rects.append(sprite.game.map.walls[tile_pos[1]][tile_pos[0]])
    return surrounding_tile_rects

def collide_with_tile_walls(sprite):
    sprite.hit_rect.centerx = sprite.pos.x
    surrounding_walls = get_surrounding_walls(sprite)
    for tile_rect in surrounding_walls:
        if tile_rect.colliderect(sprite.hit_rect):
            if sprite.vel.x > 0: # going right
                sprite.pos.x = tile_rect.left - sprite.hit_rect.width / 2
            if sprite.vel.x < 0: # going left
                sprite.pos.x = tile_rect.right + sprite.hit_rect.width / 2
            sprite.vel.x = 0
            sprite.hit_rect.centerx = sprite.pos.x
    sprite.hit_rect.centery = sprite.pos.y
    surrounding_walls = get_surrounding_walls(sprite)
    for tile_rect in surrounding_walls:
        if tile_rect.colliderect(sprite.hit_rect):
            if sprite.vel.y > 0: # going down
                sprite.pos.y = tile_rect.top - sprite.hit_rect.height / 2
            if sprite.vel.y < 0: # going up
                sprite.pos.y = tile_rect.bottom + sprite.hit_rect.height / 2
            sprite.vel.y = 0
            sprite.hit_rect.centery = sprite.pos.y
    sprite.rect.center = sprite.hit_rect.center

def collide_hit_rect(one, two):
    return one.hit_rect.colliderect(two.rect)

def collide_with_walls(sprite, group, dir):
    hits = pg.sprite.spritecollide(sprite, group, False, collide_hit_rect)
    if hits:
        if dir == 'x':
            if hits[0].rect.centerx > sprite.hit_rect.centerx: # going right
                sprite.pos.x = hits[0].rect.left - sprite.hit_rect.width / 2
            if hits[0].rect.centerx < sprite.hit_rect.centerx: # going left
                sprite.pos.x = hits[0].rect.right + sprite.hit_rect.width / 2
            sprite.vel.x = 0
            sprite.hit_rect.centerx = sprite.pos.x
        elif dir == 'y':
            if hits[0].rect.centery > sprite.hit_rect.centery: # going down
                sprite.pos.y = hits[0].rect.top - sprite.hit_rect.height / 2
            if hits[0].rect.centery < sprite.hit_rect.centery: # going up
                sprite.pos.y = hits[0].rect.bottom + sprite.hit_rect.height / 2
            sprite.vel.y = 0
            sprite.hit_rect.centery = sprite.pos.y

def moving_target_hit_rect(one, two):
    return one.hit_rect.colliderect(two.hit_rect)

def collide_with_moving_targets(sprite):
    sprite.remove(sprite.game.moving_targets_on_screen)
    hits = pg.sprite.spritecollide(sprite, sprite.game.moving_targets_on_screen, False, moving_target_hit_rect)
    if hits and not hits[0].flying:
        if hits[0].kind != sprite.kind:
            if hits[0].touch_damage:
                hits[0].does_melee_damage(sprite)
        if hits[0] in sprite.game.animals:
            if not hits[0].occupied:
                if hits[0] in sprite.game.grabable_animals:
                    if not sprite.npc:
                        sprite.game.message_text = True
                        sprite.game.message = pg.key.name(sprite.game.key_map['interact']).upper() + ' to catch'
                    if sprite.e_down:
                        sprite.add_inventory(hits[0].item)
                        hits[0].kill()
                        sprite.game.message_text = False
                        sprite.e_down = False
                elif hits[0].mountable:
                    sprite.game.message_text = True
                    sprite.game.message = pg.key.name(sprite.game.key_map['interact']).upper() + ' to mount, ' + pg.key.name(sprite.game.key_map['dismount']).upper() + ' to dismount'
                    if sprite.e_down:
                        hits[0].mount(sprite)
                        sprite.game.message_text = False
                        sprite.e_down = False

        sprite.hit_rect.centerx = sprite.pos.x
        if hits[0].hit_rect.centerx > sprite.hit_rect.centerx:  # going right
            sprite.pos.x = hits[0].hit_rect.left - sprite.hit_rect.width / 2
        if hits[0].hit_rect.centerx < sprite.hit_rect.centerx:  # going left
            sprite.pos.x = hits[0].hit_rect.right + sprite.hit_rect.width / 2
        sprite.vel.x = (sprite.vel.x + hits[0].vel.x) / 2
        sprite.hit_rect.centerx = sprite.pos.x
        sprite.hit_rect.centery = sprite.pos.y
        if hits[0].hit_rect.centery > sprite.hit_rect.centery:  # going down
            sprite.pos.y = hits[0].hit_rect.top - sprite.hit_rect.height / 2
        if hits[0].hit_rect.centery < sprite.hit_rect.centery:  # going up
            sprite.pos.y = hits[0].hit_rect.bottom + sprite.hit_rect.height / 2
        sprite.vel.y = (sprite.vel.y + hits[0].vel.y) / 2
        sprite.hit_rect.centery = sprite.pos.y
        sprite.rect.center = sprite.hit_rect.center
    sprite.add(sprite.game.moving_targets_on_screen)


def vehicle_collide_hit_rect(one, two):
    return one.hit_rect.colliderect(two.hit_rect)
def vehicle_collide_hit2_rect(one, two):
    return one.hit_rect.colliderect(two.hit_rect2)
def vehicle_collide_hit3_rect(one, two):
    return one.hit_rect.colliderect(two.hit_rect3)
def vehicle_collide_any(one, two):
    return (one.hit_rect.colliderect(two.hit_rect) or one.hit_rect.colliderect(two.hit_rect2) or one.hit_rect.colliderect(two.hit_rect3))
def wall_vehicle_collide_hit2_rect(one, two):
    return one.hit_rect2.colliderect(two.rect)
def wall_vehicle_collide_hit3_rect(one, two):
    return one.hit_rect3.colliderect(two.rect)

def collide_with_elevations(sprite, dir):
    xwall = False
    ywall = False
    hits = pg.sprite.spritecollide(sprite, sprite.game.elevations_on_screen, False, collide_hit_rect)
    if hits:
        hit_level = hits[0]
        for hit in hits: # Uses only the highest elevation you hit.
            if hit.elevation > hit_level.elevation:
                hit_level = hit
        if dir == 'x':
            if hit_level.elevation - sprite.elevation > 3:
                xwall = True
                sprite.climbing = False
            elif hit_level.elevation - sprite.elevation == 3:
                if not sprite.climbing:
                    xwall = True
            elif hit_level.elevation - sprite.elevation == 2:
                if True not in [sprite.jumping, sprite.climbing]:
                    xwall = True
            elif hit_level.elevation - sprite.elevation <= 1:
                if hit_level.elevation - sprite.elevation < -1:
                    sprite.falling = True
                    sprite.pre_jump()
                sprite.elevation = hit_level.elevation
            if xwall:
                if hit_level.rect.centerx > sprite.hit_rect.centerx:
                    sprite.pos.x = hit_level.rect.left - sprite.hit_rect.width / 2
                if hit_level.rect.centerx < sprite.hit_rect.centerx:
                    sprite.pos.x = hit_level.rect.right + sprite.hit_rect.width / 2
                sprite.vel.x = 0
                sprite.hit_rect.centerx = sprite.pos.x
        elif dir == 'y':
            if hit_level.elevation - sprite.elevation > 3:
                ywall = True
                sprite.climbing = False
            elif hit_level.elevation - sprite.elevation == 3:
                if not sprite.climbing:
                    ywall = True
                else:
                    sprite.elevation = hit_level.elevation
            elif hit_level.elevation - sprite.elevation == 2:
                if True not in [sprite.jumping, sprite.climbing]:
                    ywall = True
                else:
                    sprite.elevation = hit_level.elevation
            elif hit_level.elevation - sprite.elevation <= 1:
                if hit_level.elevation - sprite.elevation < -1:
                    sprite.falling = True
                    sprite.pre_jump()
                sprite.elevation = hit_level.elevation
            if ywall:
                if hit_level.rect.centery > sprite.hit_rect.centery:
                    sprite.pos.y = hit_level.rect.top - sprite.hit_rect.height / 2
                if hit_level.rect.centery < sprite.hit_rect.centery:
                    sprite.pos.y = hit_level.rect.bottom + sprite.hit_rect.height / 2
                sprite.vel.y = 0
                sprite.hit_rect.centery = sprite.pos.y


# Used for detecting when a fireball hits an obstacle
def fire_collide(one, two):
    if one.hit_rect.colliderect(two.rect):
        return True
    else:
        return False

def add_inventory(inventory, item_name, count = 1): # Accepts either an item in dictionary form or by item name.
    if isinstance(item_name, dict):
        item_dict = item_name
    else:
        if item_name in ITEMS:
            item_dict = ITEMS[item_name]
        else:
            return False
    # Checks to see if you already have that item and increments the number accordingly.
    for slot in inventory:
        if ('number' in slot) and (slot['name'] == item_dict['name']): # Some items have a different name than their key so you can harvest things like sticks from bushes.
            if 'number' in item_dict: # Adjusts the number if items come in units greater than one. Used for harvesting.
                count = count * item_dict['number']
            diff = (slot['number'] + count) - slot['max stack']
            if diff <= 0:
                slot['number'] += count
                return True # Leaves if no leftovers
            else:
                count = diff # Continues the loop for leftovers.

    # If no remaining slots of same type are found then it finds an empty slot
    for i, slot in enumerate(inventory):
        if slot == {}:
            if 'number' in item_dict:  # Adjusts the number if items come in units greater than one. Used for harvesting.
                count = count * item_dict['number']
                inventory[i] = item_dict.copy()
                inventory[i]['number'] = count
            else:
                inventory[i] = item_dict.copy()
                count -= 1
                if count > 0:
                    if add_inventory(inventory, item_name, count):
                        return True
            return True
    return False

def check_inventory(inventory, item_name, count = 1):
    num_of_items = 0
    for item in inventory:
        if ('name' in item) and (item_name == item['name']):
            if 'number' in item:
                num_of_items += item['number']
            else:
                num_of_items += 1
    if num_of_items >= count:
        return True
    return False

def random_hair(character):
    # Separates out items to match character's gender
    if character.equipped['gender'] == 'male':
        random_hair = choice(SHORT_HAIR_LIST)
    else:
        random_hair = choice(LONG_HAIR_LIST)
    if random_hair not in character.expanded_inventory['hair']:
        character.expanded_inventory['hair'].append(random_hair)
    character.equipped['hair'] = random_hair

def random_inventory(gender = choice(['male', 'female'])):
    """
    tops = []
    bottoms = []
    inventory = {'weapons': {}, 'hats': {}, 'tops': {}, 'bottoms': {}, 'gloves': {}, 'shoes': {}, 'items': {}, 'blocks':{}}
    # Separates out items to match character's gender
    if gender == 'male':
        tops = MALE_TOPS
        bottoms = MALE_BOTTOMS
    else:
        tops = FEMALE_TOPS
        bottoms = FEMALE_BOTTOMS
    # Adds random items to inventory
    add_inventory(inventory, choice(tops))
    add_inventory(inventory, choice(bottoms))
    add_inventory(inventory, choice(list(GLOVES.keys())))
    add_inventory(inventory, choice(list(SHOES.keys())))
    add_inventory(inventory, choice(list(ITEMS.keys())))"""
    pass

def random_inventory_item(orig_inventory, gender = None):
    """
    inventory = copy.deepcopy(orig_inventory)
    orig_gender = gender
    for item_type in ITEM_TYPE_LIST:
        for value in orig_inventory[item_type]:
            if orig_gender == None:
                gender = choice(['male', 'female'])
            if value:
                if 'random ' in value:
                    temp_value = value.replace('random ', '')
                    del inventory[item_type][value]
                    temp_list = eval(temp_value + item_type.upper())
                    if 'gender' in (list(eval(item_type.upper()).values())[0]).keys():
                        female_list = []
                        male_list = []
                        for x in temp_list:
                            if x:
                                if eval(item_type.upper())[x]['gender'] in ['female', 'other']:
                                    female_list.append(x)
                            else:
                                female_list.append(x)
                            if x:
                                if eval(item_type.upper())[x]['gender'] in ['male', 'other']:
                                    male_list.append(x)
                            else:
                                male_list.append(x)
                        if gender == 'female':
                            if len(female_list) > 0:
                                add_inventory(inventory, choice(female_list))
                            else:
                                add_inventory(inventory, choice(temp_list))
                        else:
                            if len(male_list) > 0:
                                add_inventory(inventory, choice(male_list))
                            else:
                                add_inventory(inventory, choice(temp_list))
                    else:
                        add_inventory(inventory, choice(temp_list))
                elif value == 'random':
                    del inventory[item_type][value]
                    if item_type == 'tops':
                        if gender == 'female':
                            add_inventory(inventory, choice(FEMALE_TOPS))
                        elif gender in ['male', 'other']:
                            add_inventory(inventory, choice((MALE_TOPS)))
                        else:
                            add_inventory(inventory, choice((list(TOPS.keys()))))
                    elif item_type == 'bottoms':
                        if gender == 'male':
                            add_inventory(inventory, choice(MALE_BOTTOMS))
                        elif gender in ['female', 'other']:
                            add_inventory(inventory, choice(FEMALE_BOTTOMS))
                        else:
                            add_inventory(inventory, choice(list(BOTTOMS.keys())))
                    else:
                        add_inventory(inventory, choice(list(eval(item_type.upper()).keys())))
    return inventory"""

    return orig_inventory

def drop_all_items(sprite, delete_items = False):
        if not delete_items:
            for i, item in enumerate(sprite.inventory):
                Dropped_Item(sprite.game, sprite.pos, item, None, True)
                sprite.inventory[i] = {}
            for key, item in sprite.equipped.items():
                if key not in ['hair', 'race', 'gender', 'weapons', 'weapons2']:
                    Dropped_Item(sprite.game, sprite.pos, item, None, True)
                    sprite.equipped[key] = {}
            sprite.equipped['weapons'] = None
            sprite.equipped['weapons2'] = None
            sprite.hand_item = {}
            sprite.hand2_item = {}
            sprite.body.update_animations()

def change_clothing(character, naked = False, best = False):
    if naked: # Takes all clothes off and puts them back in your inventory.
        for key, value in character.equipped.items():
            if key not in ['race', 'gender', 'hair', 'weapons', 'weapons2']:
                if 'name' in character.equipped[key].keys():
                    if add_inventory(character.inventory, character.equipped[key]['name']):
                        character.equipped[key] = {}
    else:
        # Adds items to equipped list
        item_types_dic = {}
        for item_type in EQUIP_TYPES:
            item_types_dic[item_type] = []
        for item in character.inventory:
            if item != {}:
                for item_type in EQUIP_TYPES:
                    if ('type' in item.keys()) and (item_type == item['type']):
                        item_types_dic[item_type].append(item)

        for item_type in EQUIP_TYPES:
            if len(item_types_dic[item_type]) > 0:
                selected_item = choice(item_types_dic[item_type])
                character.equipped[item_type] = selected_item
                for i, item in enumerate(character.inventory): # Removes equipped item from inventory slots so they aren't doubled.
                    if item == selected_item:
                        character.inventory[i] = {}
                        break

def lamp_check(character):
    if character.game.night:
        # checks for lamps
        add_light = False
        light_reach = 1
        for item in character.inventory['weapons']:
            if item in LIGHTS_LIST:
                if item['type'] in GUN_LIST:
                    character.equipped['weapons'] = item
                    character.lamp_hand = 'weapons'
                else:
                    character.equipped['weapons2'] = item
                    character.lamp_hand = 'weapons2'
                character.brightness = item['brightness']
                character.mask_kind = item['light mask']
                if 'light reach' in item:
                    light_reach = item['light reach']
                character.game.lights.add(character)
                character.light_mask_orig = pg.transform.scale(character.game.light_mask_images[character.mask_kind], (int(character.brightness * light_reach), character.brightness))
                character.light_mask = character.light_mask_orig.copy()
                character.light_mask_rect = character.light_mask.get_rect()
                if item['type'] in GUN_LIST:
                    character.light_mask_rect.center = character.body.melee_rect.center
                else:
                    character.light_mask_rect.center = character.body.melee2_rect.center
                character.body.update_animations()
                add_light = True
                break
        if not add_light:
            if character in character.game.lights:
                character.game.lights.remove(character)
        return
    if character.equipped['weapons2'] in LIGHTS_LIST:
        character.equipped['weapons2'] = None
    if character.equipped['weapons'] in LIGHTS_LIST:
        character.equipped['weapons'] = None
    if character in character.game.lights:
        character.game.lights.remove(character)
    character.body.update_animations()


def remove_nones(*my_lists):
    for my_list in my_lists:
        while True:
            if None in my_list and len(my_list)!=1:
                my_list.remove(None)
            elif len(my_list)==1 and None in my_list:
                break
            if None not in my_list:
                break

def toggle_equip(character, var): # Toggles whether weapons are equipped/drawn or not
    if var:  # Unequips weapons
        if character.equipped['weapons']:
            character.current_weapon = character.equipped['weapons']
            character.equipped['weapons'] = None
        if character.equipped['weapons2']:
            character.current_weapon2 = character.equipped['weapons2']
            character.equipped['weapons2'] = None
    else:  # Equips weapons
        character.equipped['weapons'] = character.current_weapon
        character.equipped['weapons2'] = character.current_weapon2

def fix_angle(ang): #fixes angle measures so they are never greater than abs(180) which makes it easier to work with quadrants.
    angle = ang
    if angle > 180:
        angle = angle - 360
    if angle < -180:
        angle = angle + 360
    return angle

class Turret(pg.sprite.Sprite):
    def __init__(self, game, mother):
        self.game = game
        self.mother = mother
        self._layer = self.game.map.bullet_layer
        self.groups = game.turrets
        pg.sprite.Sprite.__init__(self, self.groups)
        self.game.group.add(self)
        self.image_orig = self.game.player_tur
        self.image = self.image_orig.copy()
        self.rect = self.image.get_rect()
        #self.rect = self.rect.inflate(100, 100)
        self.rect.center = self.mother.rect.center
        self.hit_rect = SMALL_HIT_RECT.copy()
        self.hit_rect.center = self.rect.center
        self.light_mask = pg.transform.scale(self.game.light_mask_images[2], (300, 300))
        self.light_mask_rect = self.light_mask.get_rect()
        self.light_mask_rect.center = self.rect.center
        self.rot = 0
        self.rot_rel = 0
        self.rot_speed = 0
        self.last_shot = 0
        self.occupied = False
        self.equipped = 'tank turret'
        self.vel = vec(0, 0)
        self.max_rot_speed = 20
        self.direction = vec(1, 0)

    def rotate_to(self, vec):
        vector = vec
        angle = fix_angle(vector.angle_to(self.direction))
        if angle < -1:
            self.rot_speed = -self.max_rot_speed * 10 * abs(angle) / 180
        elif angle > 1:
            self.rot_speed = self.max_rot_speed * 10 * abs(angle) / 180
        else:
            self.rot_speed = 0

    def shoot(self):
        now = pg.time.get_ticks()
        if now - self.last_shot > self.equipped['rate']:
            self.last_shot = now
            dir = vec(1, 0).rotate(-self.rot)
            pos = self.game.player.pos + self.equipped['offset'].rotate(-self.rot)
            for i in range(self.equipped['bullet_count']):
                Bullet(self, self.game, pos, dir, self.rot, self.equipped)
                snd = choice(self.game.weapon_sounds[self.equipped['type']])
                play_relative_volume(self, 'snd')
            if self.equipped['type'] in GUN_LIST:
                MuzzleFlash(self.game, pos)

    def update(self):
        if self.occupied == True:
            if self.mother.driver == self.game.player:
                self.rotate_to(self.game.player.mouse_direction)
                if pg.mouse.get_pressed() in [(1, 0, 1), (1, 1, 1), (1, 0, 0), (1, 1, 0)]:
                    self.shoot()
            self.rect.center = self.mother.rect.center
            self.rot = (self.rot + self.rot_speed * self.game.dt) % 360
            self.direction = vec(1, 0).rotate(-self.rot)
            new_image = pg.transform.rotate(self.image_orig, self.rot)
            old_center = self.rect.center
            self.image = new_image
            self.rect = self.image.get_rect()
            self.rect.center = old_center
            self.rect.center = self.mother.rect.center
            self.hit_rect.center = self.rect.center
            self.light_mask_rect.center = self.rect.center
        if not self.mother.alive():
            self.kill()

class Vehicle(pg.sprite.Sprite):
    def __init__(self, game, center, kind):
        self.game = game
        self.kind = self.race = kind
        self.data = VEHICLES[kind]
        self._layer = eval(self.data['layer'])
        self.mountable = self.data['mountable']
        self.veh_acc = self.data['acceleration']
        self.rot_speed = self.data['rot speed']
        self.forward_sound_playing = False
        if 'run sound' in self.data.keys():
            self.run_sound = self.data['run sound']
        else:
            self.run_sound = None
        if 'drive sound' in self.data.keys():
            self.drive_sound = self.data['drive sound']
        else:
            self.drive_sound = None
        if 'fuel' in self.data.keys():
            self.fuel = self.data['fuel']
        else:
            self.fuel = None
        self.cat = self.data['cat']
        if self.cat in BOATS:
            self.flying = False
            self.groups = game.all_sprites, game.vehicles, game.boats, game.all_vehicles
        elif self.cat in AMPHIBIOUS_VEHICLES:
            self.flying = False
            self.groups = game.all_sprites, game.vehicles, game.amphibious_vehicles, game.all_vehicles
        elif self.cat in FLYING_VEHICLES:
            self.groups = game.all_sprites, game.flying_vehicles, game.all_vehicles
            self.flying = True
        else:
            self.flying = False
            self.groups = game.all_sprites, game.vehicles, game.land_vehicles, game.all_vehicles
        pg.sprite.Sprite.__init__(self, self.groups)
        self.game.group.add(self)
        self.image_orig = self.game.vehicle_images[self.data['image']]
        self.image = self.image_orig.copy()
        self.rect = self.image.get_rect()
        self.rect.center = center
        self.hit_rect = self.data['hit rect'].copy()
        self.hit_rect2 = pg.Rect(0, 0, int(self.hit_rect.width*(5/6)), int(self.hit_rect.width*(5/6)))
        self.hit_rect3 = self.hit_rect2.copy()
        self.hrect_offset2 = vec(self.hit_rect2.width/2, 0)
        self.hrect_offset3 = vec(-self.hit_rect3.width/2, 0)
        self.hit_rect2.center = self.rect.center + self.hrect_offset2
        self.hit_rect3.center = self.rect.center + self.hrect_offset3
        self.hit_rect.center = self.rect.center
        self.transparency = 255 # Used to make vehicles look like they are sinking
        self.player_walk_anim = self.data['walk animation']
        self.player_rattack_anim = self.data['rattack animation']
        self.player_lattack_anim = self.data['lattack animation']
        self.damage = self.data['damage']
        self.light_mask = None
        self.vel = vec(0, 0)
        self.pos = vec(center)
        self.rot = 0
        self.prev_rot = 0
        self.occupied = False
        self.damaged = False
        self.jumping = False
        self.climbing = False
        self.immaterial = False
        self.invisible = False
        self.protected = False
        self.offensive = False
        self.aggression = "vehicle"
        self._forward = False
        self.elevation = 0
        self.in_vehicle = self.in_player_vehicle = False
        if not health:
            self.stats = {'health': self.data['hp'], 'max health': self.data['hp']}
        else:
            self.stats = {'health': health, 'max health': self.data['hp']}
        self.last_hit = 0
        self.last_drain = 0
        self.living = True
        self.driver = None
        self.turret = None
        if self.cat == 'tank':
            self.turret = Turret(game, self)
            collide_list = ['walls']
        elif self.cat == 'boat':
            collide_list = ['walls', 'shallows']
        elif self.cat == 'airship':
            collide_list = []
        else:
            collide_list = ['walls', 'water']
        self.collide_list = []
        for item in collide_list:
            self.collide_list.append(eval("self.game." + item + "_on_screen"))

    @property
    def forward(self): #This is the method that is called whenever you access
        return self._forward
    @forward.setter #This is the method that is called whenever you set a value
    def forward(self, value):
        if value!=self._forward:
            self._forward = value
            if self.occupied:
                if value:
                    if self.drive_sound:
                        if not self.forward_sound_playing:
                            self.forward_sound_playing = True
                            self.game.channel7.stop()
                            self.game.channel7.play(self.game.effects_sounds[self.drive_sound], loops=-1)
                else:
                    if self.run_sound:
                        if self.forward_sound_playing:
                            self.game.channel7.stop()
                            self.game.channel7.play(self.game.effects_sounds[self.run_sound], loops=-1)
                            self.forward_sound_playing = False

    def add_health(self, amount):
        self.stats['health']+= amount
        if self.stats['health']> self.stats['max health']:
            self.stats['health']= self.stats['max health']
        if self.stats['health'] <= 0:
            self.living = False
            self.exit_vehicle()
        if self.game.hud_health_stats == self.stats:
            self.game.hud_health = self.stats['health'] / self.stats['max health']

    def get_keys(self):
        keys = pg.key.get_pressed()
        if keys[self.game.key_map['dismount']]:
            self.exit_vehicle()

    def reequip(self):
        if self.data['weapons']:
            self.driver.equipped['weapons'] = self.driver.current_weapon = self.data['weapons']
        if self.data['weapons2']:
            self.driver.equipped['weapons2'] = self.driver.current_weapon2 = self.data['weapons2']

    def enter_vehicle(self, driver):
        if driver == self.game.player:
            self.game.hud_health_stats = self.stats
        if self.run_sound:
            self.game.channel7.play(self.game.effects_sounds[self.run_sound], loops=-1)
        self.driver = driver
        self.driver.pos = vec(self.rect.center)# centers the driver in the vehicle.
        self.driver.rect.center = self.driver.hit_rect.center = self.rect.center
        self.driver.rot = self.rot # rotates the driver to fit the vehicle's rotation.
        self.occupied = True
        self.driver.in_vehicle = True
        self.driver.vehicle = self
        if self.data['weapons']:
            self.driver.last_weapon = self.driver.current_weapon
            self.driver.inventory['weapons'].append(self.data['weapons'])
            self.driver.equipped['weapons'] = self.driver.current_weapon = self.data['weapons']
        if self.data['weapons2'] or self.cat == 'tank':
            self.driver.last_weapon2 = self.driver.current_weapon2
            self.driver.inventory['weapons'].append(self.data['weapons2'])
            self.driver.equipped['weapons2'] = self.driver.current_weapon2 = self.data['weapons2']
        if self.data['weapons'] or self.data['weapons2']:
            self.driver.pre_reload()
        if self.cat == 'airship':
            self.light_mask = pg.transform.scale(self.game.light_mask_images[6], (400, 400))
            self.light_mask_rect = self.light_mask.get_rect()
            self.light_mask_rect.center = self.rect.center
            self.game.lights.add(self)
            self.game.flying_vehicles.add(self.driver)
            if self.driver == self.game.player:
                self.driver.in_flying_vehicle = True
                for companion in self.game.companions:
                    companion.in_player_vehicle = True
                    companion.in_flying_vehicle = True
        self.add(self.game.occupied_vehicles)
        self.add(self.game.moving_targets)
        self.driver.human_body.update_animations()
        if self.driver.has_dragon_body:
            self.driver.dragon_body.update_animations()
        if self.cat == 'tank':
            self.light_mask = self.game.flashlight_masks[int(self.rot/3)]
            self.light_mask_rect = self.light_mask.get_rect()
            self.light_mask_rect.center = self.rect.center
            self.game.lights.add(self)
            if self.driver == self.game.player:
                for companion in self.game.companions:
                    companion.in_player_vehicle = True
            self.turret.add(self.game.occupied_vehicles)
            self.turret.add(self.game.lights)
            self.turret.occupied = True
            self.driver.pre_reload()
        if self.kind == 'skiff':
            if self.driver == self.game.player:
                for companion in self.game.companions:
                    companion.in_player_vehicle = True
        self.game.beg = perf_counter()  # resets dt

    def exit_vehicle(self):
        if self.driver == self.game.player:
            self.game.hud_health_stats = self.driver.stats
        self.game.channel6.stop()
        self.forward_sound_playing = False
        self.pos = vec(self.rect.center)
        self.occupied = False
        self.driver.in_vehicle = False
        self.driver.friction = PLAYER_FRIC
        self.driver.acceleration = PLAYER_ACC
        if self.data['weapons']:
            self.driver.inventory['weapons'].remove(self.data['weapons'])
            if self.driver.last_weapon != self.data['weapons']:
                self.driver.equipped['weapons'] = self.driver.current_weapon = self.driver.last_weapon
            else:
                self.driver.equipped['weapons'] = None
        if self.data['weapons2']:
            self.driver.inventory['weapons'].remove(self.data['weapons2'])
            if self.driver.last_weapon2 != self.data['weapons2']:
                self.driver.equipped['weapons2'] = self.driver.current_weapon2 = self.driver.last_weapon2
            else:
                self.driver.equipped['weapons2'] = None
        self.driver.vehicle = None
        if self.cat == 'tank':
            self.light_mask = None
            self.game.lights.remove(self)
            self.turret.remove(self.game.occupied_vehicles)
            self.turret.remove (self.game.lights)
            self.turret.occupied = False
            if self.driver == self.game.player:
                for companion in self.game.companions:
                    companion.in_player_vehicle = False
        elif self.cat == 'airship':
            self.light_mask = None
            self.game.lights.remove(self)
            self.driver.remove(self.game.flying_vehicles)
            if self.driver == self.game.player:
                for companion in self.game.companions:
                    companion.in_player_vehicle = False
                    companion.in_flying_vehicle = False
        if self.kind == 'skiff':
            if self.driver == self.game.player:
                for companion in self.game.companions:
                    companion.in_player_vehicle = False
        self.remove(self.game.occupied_vehicles)
        self.remove(self.game.moving_targets)
        if self.driver == self.game.player:
            self.driver.empty_mags()
        self.driver.human_body.update_animations()
        if self.driver.has_dragon_body:
            self.driver.dragon_body.update_animations()
        self.driver.in_flying_vehicle = False
        self.driver = None
        self.game.beg = perf_counter()  # resets dt


    def gets_hit(self, damage, knockback = 0, rot = 0, dam_rate = DAMAGE_RATE):
        if self.living:
            now = pg.time.get_ticks()
            if now - self.last_hit > dam_rate * 2:
                play_relative_volume(self, self.data['hit sound'])
                self.last_hit = now
                self.add_health(-damage)
                self.transparency -= 2
                if self.transparency < 30:
                    self.transparency = 30

    def update(self):
        if self.occupied == True:
            now = pg.time.get_ticks()
            # Increases vehicle friction when not accelerating
            if self.cat == 'airship':
                self.driver.friction = -.03
            elif self.driver.is_moving():
                # Makes the friction greater when the vehicle is sliding in a direction that is not straight forward.
                angle_difference = abs(fix_angle(self.driver.vel.angle_to(self.driver.direction)))
                if angle_difference > 350:
                    angle_difference = 0
                if angle_difference < 0.1:
                    angle_difference = 0
                self.driver.friction = -(angle_difference/1000 + .015)
            else:
                self.driver.friction = -.28
            if self.driver.swimming:
                self.image = pg.transform.rotate(self.image_orig, self.rot)
                self.image.fill((255, 255, 255, self.transparency), None, pg.BLEND_RGBA_MULT)
            else:
                self.image = pg.transform.rotate(self.image_orig, self.rot)
                if now - self.last_drain > 50:
                    self.last_drain = now
                    self.transparency += 1
                    if self.transparency > 255:
                        self.transparency = 255
            self.driver.acceleration = self.veh_acc
            self.rot = self.driver.rot
            if self.turret: # Rotates the turret if you rotate the vehicle.
                delta_rot = self.prev_rot - self.rot
                if delta_rot != 0:
                    self.turret.rot -= delta_rot
                self.prev_rot = self.rot
            self.rect = self.image.get_rect()
            self.pos = self.driver.pos #vec(self.driver.rect.center)
            self.rect.center = self.pos
            self.hit_rect2.center = self.pos + self.hrect_offset2.rotate(-self.rot)
            self.hit_rect3.center = self.pos + self.hrect_offset3.rotate(-self.rot)
            # This puts the companions in the vehicle with the player
            if self.driver == self.game.player:
                offset_vec = vec(80, 0).rotate(-(self.rot + 180))
                for companion in self.game.companions:
                    if companion.in_player_vehicle:
                        if companion in self.game.npcs:
                            companion.pos = companion.rect.center = companion.talk_rect.center = self.driver.pos + offset_vec
            collide(self)
            self.get_keys() # this needs to be last in this method to avoid executing the rest of the update section if you exit
            if self.turret:
                self.turret.update()
            if self.light_mask:
                if self.cat == 'tank':
                    self.light_mask = self.game.flashlight_masks[int(self.turret.rot/3)]
                    self.light_mask_rect = self.light_mask.get_rect()
                self.light_mask_rect.center = self.rect.center


class Body(pg.sprite.Sprite):
    def __init__(self, game, mother, dragon = False):
        self.game = game
        self.mother = mother
        self.dragon = dragon
        if not self.dragon:
            self.race = self.mother.equipped['race']
        else:
            self.race = self.mother.equipped['race'] + 'dragon'
        self._layer = self.mother._layer
        self.groups = game.all_sprites, game.npc_bodies
        pg.sprite.Sprite.__init__(self, self.groups)
        self.game.group.add(self)
        self.surface_width = self.surface_height = 128
        self.body_surface = pg.Surface((self.surface_width, self.surface_height)).convert()
        self.body_surface.fill(TRANSPARENT)
        self.image = self.body_surface
        self.image.set_colorkey(TRANSPARENT) #makes transparent
        self.rect = self.image.get_rect()
        self.rect.center = self.mother.pos
        # Collission rects for left and right hands/weapons.
        self.melee_rect = pg.Rect(0, 0, MELEE_SIZE, MELEE_SIZE)
        self.weapon_melee_rect = pg.Rect(0, 0, MELEE_SIZE, MELEE_SIZE)
        self.mid_weapon_melee_rect = pg.Rect(0, 0, MELEE_SIZE, MELEE_SIZE)
        self.melee2_rect = pg.Rect(0, 0, MELEE_SIZE, MELEE_SIZE)
        self.weapon2_melee_rect = pg.Rect(0, 0, MELEE_SIZE, MELEE_SIZE)
        self.mid_weapon2_melee_rect = pg.Rect(0, 0, MELEE_SIZE, MELEE_SIZE)
        self.swing_weapon1 = False # Used for timing melee attacks for stinging vs stabbing weapons.
        self.swing_weapon2 = False  # Used for timing melee attacks for stinging vs stabbing weapons.
        # Default Animation lists
        if self.mother not in self.game.npcs:
            self.climbing_shoot_anim = self.render_animation([CP_CLIMB0])
            self.climbing_weapon_anim = self.render_animation(CLIMB)
            self.climbing_weapon_melee_anim = self.render_animation(CLIMB_MELEE)
            self.climbing_l_weapon_melee_anim = self.render_animation(L_CLIMB_MELEE)
            self.walk_melee_anim = self.render_animation(WALK_PUNCH)
            self.walk_l_melee_anim = self.render_animation(L_WALK_PUNCH)
            self.dual_melee_anim = self.render_animation(D_PUNCH)
            self.dual_reload_anim = self.render_animation(RELOAD + L_RELOAD)
            self.walk_reload_anim = self.render_animation(WALK_RELOAD)
            self.l_walk_reload_anim = self.render_animation(L_WALK_RELOAD)
            self.walk_dual_reload_anim = self.render_animation(WALK_RELOAD + L_WALK_RELOAD)
            self.l_shoot_anim = self.render_animation(L_SHOOT)
            self.l_reload_anim = self.render_animation(L_RELOAD)

        if self.mother.gun:
            self.shoot_anim = self.render_animation(SHOOT)
            self.reload_anim = self.render_animation(RELOAD)

        self.jump_anim = self.render_animation(JUMP)
        self.stand_anim = self.render_animation(STAND)
        self.run_anim = self.render_animation(RUNNING)
        self.walk_anim = self.render_animation(WALK)
        self.melee_anim = self.render_animation(PUNCH)
        self.l_melee_anim = self.render_animation(L_PUNCH)
        self.shallows_anim = self.render_animation(SHALLOWS_WALK)
        # These animations never have weapons
        toggle_equip(self.mother, True) # This makes it so these animations are not ever created with weapons
        if self.mother not in self.game.npcs:
            self.swim_jump_anim = self.render_animation(WATER_JUMP)
            self.climb_jump_anim = self.render_animation(CLIMB_JUMP)
            self.climbing_melee_anim = self.render_animation(CLIMB_MELEE)
            self.climbing_l_melee_anim = self.render_animation(L_CLIMB_MELEE)

        self.climbing_anim = self.render_animation(CLIMB)
        self.swim_anim = self.render_animation(SWIM, True)
        self.swim_melee_anim = self.render_animation(WATER_PUNCH, True)
        #self.animations_cache_list = [self.stand_anim, self.shoot_anim, self.climbing_shoot_anim, self.climbing_weapon_anim, self.climbing_weapon_melee_anim, self.climbing_l_weapon_melee_anim, self.run_anim, self.walk_anim, self.melee_anim, self.walk_melee_anim, self.walk_l_melee_anim, self.dual_melee_anim,  self.l_melee_anim,  self.jump_anim, self.shallows_anim, self.reload_anim, self.l_reload_anim, self.dual_reload_anim, self.swim_anim, self.swim_jump_anim, self.swim_melee_anim, self.climb_jump_anim, self.climbing_anim, self.climbing_melee_anim, self.climbing_l_melee_anim]
        toggle_equip(self.mother, False)
        self.frame = 0
        self.last_step = 0

        self.weapon_pos = vec(0, 0)
        self.weapon2_pos = vec(0, 0)
        self.update_weapon_width()
        self.weapon_angle = 0
        self.weapon2_angle = 0
        # Must be last line in init.
        self.body_surface = self.stand_anim[0][0]

    def render_animation(self, animation_list, swimming = False):
        if not self.mother.possessing:
            self.colors = self.mother.colors
        else:
            self.colors = self.mother.possessing.colors
        if not self.dragon:
            self.race = self.mother.equipped['race'].replace('dragon', '')
        else:
            if 'dragon' not in self.mother.equipped['race']:
                self.race = self.mother.equipped['race'] + 'dragon'
            else:
                self.race = self.mother.equipped['race']
        animation_images = []
        weapons_positions = []
        weapons2_positions = []
        torso_pos = []
        for part_placement in animation_list:
            surface_width = self.surface_width
            surface_height = self.surface_height
            body_surface = pg.Surface((surface_width, surface_height), pg.SRCALPHA).convert_alpha()
            rect = self.body_surface.get_rect()

            if self.mother.equipped['gender'] == 'other':
                body_part_images_list = 'male' + '_' + self.race + '_' + 'images'  # Used male images by default for 'other'
            else:
                body_part_images_list = self.mother.equipped['gender'] + '_' + self.race + '_' + 'images'
            part_image_dict = {0: 0, 1: 0, 2: 1, 3: 2, 4: 2, 5: 3, 6: 3, 7: 4, 8: 5, 9: 6, 10: 6}
            reverse_list = [1, 4, 6, 10]
            i = 0
            for part in part_placement:
                if i in range(0, 9):
                    if i == 0 and swimming: # draws swimming shadow (the part of the body that's under water).
                        temp_img = self.game.swim_shadow_image
                        colored_img = color_image(temp_img, self.colors['skin'])
                        temp_rect = colored_img.get_rect()
                        body_surface.blit(colored_img, (rect.centerx - (temp_rect.centerx + 20), rect.centery - (temp_rect.centery)))
                    temp_img = self.game.humanoid_images[body_part_images_list][part_image_dict[i]]
                    if i in reverse_list:
                        temp_img = pg.transform.flip(temp_img, False, True)
                    colored_img = color_image(temp_img, self.colors['skin'])
                    image = pg.transform.rotate(colored_img, part[2])
                    temp_rect = image.get_rect()
                    body_surface.blit(image, (rect.centerx - (temp_rect.centerx - part[0]), rect.centery - (temp_rect.centery - part[1])))
                    if i == 7 and 'mechanima' in self.mother.equipped['race']: # draws back lights on mechs.
                        temp_img = self.game.mech_back_image
                        colored_img = color_image(temp_img, self.colors['hair'])
                        temp_rect = colored_img.get_rect()
                        body_surface.blit(colored_img, (rect.centerx - (temp_rect.centerx - part[0]), rect.centery - (temp_rect.centery - part[1])))

                if i in [0, 1, 2, 3, 4, 7]: #Adds all clothing except weapons and hats.
                    if self.mother.equipped[EQUIP_DRAW_LIST[i]] != {}:
                        #imgpath = self.mother.equipped[EQUIP_DRAW_LIST[i]
                        try:
                            temp_img = self.game.item_images[correct_filename(self.mother.equipped[EQUIP_DRAW_LIST[i]])]
                        except: # Finds image for appropriate gendered clothing item if it is a gendered item (only tops and bottoms are ever gendered).
                            filename = correct_filename(self.mother.equipped[EQUIP_DRAW_LIST[i]]) + gender_tag(self.mother)
                            temp_img = self.game.item_images[filename]
                        if 'color' in self.mother.equipped[EQUIP_DRAW_LIST[i]]:
                            temp_img = color_image(temp_img, self.mother.equipped[EQUIP_DRAW_LIST[i]]['color'])
                        if i in reverse_list: # Flips gloves and shoes
                            temp_img = pg.transform.flip(temp_img, False, True)
                        image = pg.transform.rotate(temp_img, part[2])
                        temp_rect = image.get_rect()
                        body_surface.blit(image, (rect.centerx - (temp_rect.centerx - part[0]), rect.centery - (temp_rect.centery - part[1])))
                    if i == 7: #Adds shirt/top
                        torso_pos = part  # used to place the wings on at the correct location/angle

                elif i == 9:
                    weapon_pos = vec(part[0], part[1])
                    weapon_angle = part[2]
                    if self.mother.hand_item != {}:
                        if ('type' in self.mother.hand_item) and (self.mother.hand_item['type'] == 'block'):
                            gid = self.game.map.get_gid_by_prop_name(self.mother.hand_item['name'])
                            temp_img = self.game.map.tmxdata.get_tile_image_by_gid(gid).copy()
                            temp_img = temp_img.convert_alpha()
                            temp_img = pg.transform.rotate(temp_img, 90)
                        elif ('type' in self.mother.hand_item) and (self.mother.hand_item['type'] == 'magic'):
                            temp_img = self.game.magic_images[correct_filename(self.mother.hand_item)]
                        else:
                            temp_img = self.game.item_images[correct_filename(self.mother.hand_item)]
                        if 'color' in self.mother.hand_item:
                            temp_img = color_image(temp_img, self.mother.hand_item['color'])
                        if self.mother.hand_item['type'] not in EQUIP_TYPES: # Scales items that are not equipment so they show up the correct size in game. Because the images are larger in menu.
                            temp_img = pg.transform.scale(temp_img, (ITEM_SIZE, ITEM_SIZE))
                        image = pg.transform.rotate(temp_img, part[2])
                        temp_rect = image.get_rect()
                        body_surface.blit(image, (rect.centerx - (temp_rect.centerx - part[0]), rect.centery - (temp_rect.centery - part[1])))
                elif i == 10:
                    weapon2_pos = vec(part[0], part[1])
                    weapon2_angle = part[2]
                    if self.mother.hand2_item != {}:
                        if ('type' in self.mother.hand2_item) and (self.mother.hand2_item['type'] == 'block'):
                            gid = self.game.map.get_gid_by_prop_name(self.mother.hand2_item['name'])
                            temp_img = self.game.map.tmxdata.get_tile_image_by_gid(gid).copy()
                            temp_img = temp_img.convert_alpha()
                            temp_img = pg.transform.rotate(temp_img, 90)
                        elif ('type' in self.mother.hand2_item) and (self.mother.hand2_item['type'] == 'magic'):
                            temp_img = self.game.magic_images[correct_filename(self.mother.hand2_item)]
                        else:
                            temp_img = self.game.item_images[correct_filename(self.mother.hand2_item)]
                        if 'color' in self.mother.hand2_item:
                            temp_img = color_image(temp_img, self.mother.hand2_item['color'])
                        if self.mother.hand2_item['type'] not in EQUIP_TYPES: # Scales items that are not equipment so they show up the correct size in game. Because the images are larger in menu.
                            temp_img = pg.transform.scale(temp_img, (ITEM_SIZE, ITEM_SIZE))
                        image = pg.transform.rotate(temp_img, part[2])
                        temp_rect = image.get_rect()
                        body_surface.blit(image, (rect.centerx - (temp_rect.centerx - part[0]), rect.centery - (temp_rect.centery - part[1])))
                    if 'dragon' not in self.race:
                        if self.mother.equipped['hair']:
                            temp_img = self.game.hair_images[self.mother.equipped['hair']]
                            colored_img = color_image(temp_img, self.colors['hair'])
                            image = pg.transform.rotate(colored_img, part_placement[8][2])
                            temp_rect = image.get_rect()
                            body_surface.blit(image, (rect.centerx - (temp_rect.centerx - part_placement[8][0]), rect.centery - (temp_rect.centery - part_placement[8][1])))
                        if self.mother.equipped['head'] != {}:
                            temp_img = self.game.item_images[correct_filename(self.mother.equipped['head'])]
                            if 'color' in self.mother.equipped['head']:
                                temp_img = color_image(temp_img, self.mother.equipped['head']['color'])
                            image = pg.transform.rotate(temp_img, part_placement[8][2])
                            temp_rect = image.get_rect()
                            body_surface.blit(image, (rect.centerx - (temp_rect.centerx - part_placement[8][0]), rect.centery - (temp_rect.centery - part_placement[8][1])))
                # Places wings
                elif 'dragon' in self.race and i == 11:
                    wing1_pos = vec(WING1_OFFSET).rotate(-torso_pos[2])
                    wing2_pos = vec(WING2_OFFSET).rotate(-torso_pos[2])
                    temp_img = self.game.humanoid_images[body_part_images_list][6]
                    colored_img = color_image(temp_img, self.colors['skin'])
                    image = pg.transform.rotate(colored_img, part[0] + torso_pos[2])
                    temp_rect = image.get_rect()
                    body_surface.blit(image, (rect.centerx - (temp_rect.centerx - (torso_pos[0] + wing1_pos.x)), rect.centery - (temp_rect.centery - (torso_pos[1] + wing1_pos.y))))
                    temp_img = self.game.humanoid_images[body_part_images_list][6]
                    colored_img = color_image(temp_img, self.colors['skin'])
                    temp_img = pg.transform.flip(colored_img, False, True)
                    image = pg.transform.rotate(temp_img, part[1] + torso_pos[2])
                    temp_rect = image.get_rect()
                    body_surface.blit(image, (rect.centerx - (temp_rect.centerx - (torso_pos[0] + wing2_pos.x)), rect.centery - (temp_rect.centery - (torso_pos[1] + wing2_pos.y))))
                    if self.mother.equipped['head'] != {}:  # This makes it so horns on helmets are drawn over wings, not under them.
                        temp_img = self.game.item_images[correct_filename(self.mother.equipped['head'])]
                        if 'color' in self.mother.equipped['head']:
                            temp_img = color_image(temp_img, self.mother.equipped['head']['color'])
                        image = pg.transform.rotate(temp_img, part_placement[8][2])
                        temp_rect = image.get_rect()
                        body_surface.blit(image, (rect.centerx - (temp_rect.centerx - part_placement[8][0]), rect.centery - (temp_rect.centery - part_placement[8][1])))
                i += 1
            #body_surface = auto_crop(body_surface) # Crops off the dead space
            animation_images.append(body_surface)
            weapons_positions.append([weapon_pos, weapon_angle])
            weapons2_positions.append([weapon2_pos, weapon2_angle])
        return [animation_images, weapons_positions, weapons2_positions]

    def animate(self, animation_info, speed):
        animation_images = animation_info[0]
        weapon_info = animation_info[1]
        weapon2_info = animation_info[2]
        now = pg.time.get_ticks()
        if self.frame > len(animation_images) - 1: # Makes sure the frame isn't greater than current animation
            self.frame = 0
        if now - self.last_step > speed:
            self.body_surface = animation_images[self.frame]
            self.weapon_pos = weapon_info[self.frame][0]
            self.weapon_angle = weapon_info[self.frame][1]/2
            self.weapon2_pos = weapon2_info[self.frame][0]
            self.weapon2_angle = weapon2_info[self.frame][1]/2
            self.last_step = now
            self.frame += 1

    def update_animations(self): # This needs to be done whenever the player or an NPC switches a weapon or other animation dependent equipment
        if self.dragon and (self.mother.equipped['race'] not in list(RACE.keys())):
            return
        else:
            #Default animaitons if no weapons
            self.stand_anim = self.render_animation(STAND)
            if (self.mother not in self.game.npcs) or (self.mother in self.game.companions):
                if self.mother.bow:
                    self.l_reload_anim = self.render_animation(L_BOW_RELOAD)
                    self.l_shoot_anim = self.render_animation(L_BOW_SHOOT)
                else:
                    self.l_reload_anim = self.render_animation(L_RELOAD)
                    self.l_shoot_anim = self.render_animation(L_SHOOT)
                self.walk_reload_anim = self.render_animation(WALK_RELOAD)
                self.l_walk_reload_anim = self.render_animation(L_WALK_RELOAD)
                self.walk_dual_reload_anim = self.render_animation(WALK_RELOAD + L_WALK_RELOAD)
                self.climbing_shoot_anim = self.render_animation(CLIMB_SHOOT)
                self.climbing_weapon_anim = self.render_animation(CLIMB)
                self.climbing_weapon_melee_anim = self.render_animation(CLIMB_MELEE)
                self.climbing_l_weapon_melee_anim = self.render_animation(L_CLIMB_MELEE)
                self.dual_melee_anim = self.render_animation(D_PUNCH)
                self.walk_melee_anim = self.render_animation(WALK_PUNCH)
                self.walk_l_melee_anim = self.render_animation(L_WALK_PUNCH)

            if self.mother.bow:
                self.reload_anim = self.render_animation(BOW_RELOAD)
                self.shoot_anim = self.render_animation(BOW_SHOOT)
            elif self.mother.gun:
                self.reload_anim = self.render_animation(RELOAD)
                self.shoot_anim = self.render_animation(SHOOT)

            self.jump_anim = self.render_animation(JUMP)
            self.run_anim = self.render_animation(RUNNING)
            self.walk_anim = self.render_animation(WALK)
            self.melee_anim = self.render_animation(PUNCH)
            self.l_melee_anim = self.render_animation(L_PUNCH)
            self.shallows_anim = self.render_animation(SHALLOWS_WALK)

            # These animations never have weapons
            self.mother.current_weapon = self.mother.equipped['weapons']
            self.mother.current_weapon2 = self.mother.equipped['weapons2']
            toggle_equip(self.mother, True) # This makes it so these animations are not ever created with weapons
            if (self.mother not in self.game.npcs) or (self.mother in self.game.companions):
                self.swim_jump_anim = self.render_animation(WATER_JUMP)
                self.climb_jump_anim = self.render_animation(CLIMB_JUMP)
                self.climbing_melee_anim = self.render_animation(CLIMB_MELEE)
                self.climbing_l_melee_anim = self.render_animation(L_CLIMB_MELEE)

            self.climbing_anim = self.render_animation(CLIMB)
            self.swim_anim = self.render_animation(SWIM, True)
            self.swim_melee_anim = self.render_animation(WATER_PUNCH, True)
            toggle_equip(self.mother, False)

            # Default animations if right equipped
            if self.mother.equipped['weapons']:
                #self.reload_anim = self.render_animation(eval(self.mother.equipped['weapons']['reload animation']))
                self.stand_anim = self.shoot_anim = self.render_animation([eval(WEAPON_GRIPS[self.mother.equipped['weapons']['type']])])  # Change after animations are created
                self.walk_anim = self.render_animation(eval(WEAPON_WALKS[self.mother.equipped['weapons']['type']]))
                self.melee_anim = self.render_animation(eval(WEAPON_MELEE_ANIM[self.mother.equipped['weapons']['type']]))
                if WEAPON_MELEE_ANIM[self.mother.equipped['weapons']['type']] == 'SWIPE':
                    self.swing_weapon1 = True
                    self.walk_melee_anim = self.render_animation(WALK_SWIPE)
                else:
                    self.swing_weapon1 = False
            # Default animations if left equipped
            if self.mother.equipped['weapons2']:
                #self.l_reload_anim = self.render_animation(eval('L_' + self.mother.equipped['weapons2']['reload animation']))
                self.stand_anim = self.l_shoot_anim = self.render_animation([eval('L_' + WEAPON_GRIPS[self.mother.equipped['weapons2']['type']])])
                self.walk_anim = self.render_animation(eval('L_' + WEAPON_WALKS[self.mother.equipped['weapons2']['type']]))
                self.l_melee_anim = self.render_animation(eval('L_' + WEAPON_MELEE_ANIM[self.mother.equipped['weapons2']['type']]))
                if WEAPON_MELEE_ANIM[self.mother.equipped['weapons2']['type']] == 'SWIPE':
                    self.swing_weapon2 = True
                    self.walk_l_melee_anim = self.render_animation(L_WALK_SWIPE)
                else:
                    self.swing_weapon2 = False
            # Default animaitons for duel wielding
            if self.mother.equipped['weapons'] and self.mother.equipped['weapons2']:
                self.dual_reload_anim = self.render_animation(RELOAD + L_RELOAD)
                self.stand_anim = self.render_animation(STAND)
                self.shoot_anim = self.render_animation([CP_STANDING_ARMS_OUT0])
                self.l_shoot_anim = self.render_animation([CP_STANDING_ARMS_OUT0])
                self.walk_anim = self.render_animation(WALK)
            if self.mother.in_vehicle:
                if self.mother.vehicle.mountable:
                    self.walk_anim = self.run_anim = self.shallows_anim = self.swim_anim = self.shallows_anim = self.climbing_anim = self.climb_jump_anim = self.render_animation(RIDE)
                    self.melee_anim = self.walk_melee_anim = self.climbing_melee_anim = self.climbing_shoot_anim = self.climbing_weapon_anim = self.climbing_weapon_melee_anim = self.render_animation(SWIPE)
                    self.l_melee_anim = self.walk_l_melee_anim = self.climbing_l_melee_anim = self.climbing_l_weapon_melee_anim = self.render_animation(L_SWIPE)
                else:
                    self.walk_anim = self.swim_anim = self.run_anim = self.shallows_anim = self.render_animation(self.mother.vehicle.player_walk_anim)
                    self.melee_anim = self.walk_melee_anim = self.render_animation(self.mother.vehicle.player_rattack_anim)
                    self.l_melee_anim = self.walk_l_melee_anim = self.render_animation(self.mother.vehicle.player_lattack_anim)

            self.update_weapon_width()
            self.animate(self.stand_anim, 1) #Calling this automatically updates the image

    def update_weapon_width(self): #Gets the widths of the currently equipped weapons for melee attacks and bullet spawning locations.
        if self.mother.equipped['weapons'] == None:
            self.weapon_width = 0
        else:
            self.weapon_width = self.game.item_images[correct_filename(self.mother.equipped['weapons'])].get_width() / 2
        if self.mother.equipped['weapons2'] == None:
            self.weapon2_width = 0
        else:
            self.weapon2_width = self.game.item_images[correct_filename(self.mother.equipped['weapons2'])].get_width() / 2

    def update(self):
        self.rect.center = self.mother.pos

        # Sets up three collision points for melee attacks: the fist, the center and the tip of the weapon.
        self.weapon_offset_temp = self.weapon_pos.rotate(-self.mother.rot)
        self.melee_rect.center = self.mother.pos + self.weapon_offset_temp
        self.weapon2_offset_temp = self.weapon2_pos.rotate(-self.mother.rot)
        self.melee2_rect.center = self.mother.pos + self.weapon2_offset_temp
        if self.mother.equipped['weapons']:
            self.weapon_offset_temp = (self.weapon_pos + vec(self.weapon_width/2, 0)).rotate(-(self.mother.rot + self.weapon_angle))
            self.mid_weapon_melee_rect.center = self.mother.pos + self.weapon_offset_temp
            self.weapon_offset_temp = (self.weapon_pos + vec(self.weapon_width, 0)).rotate(-(self.mother.rot + self.weapon_angle))
            self.weapon_melee_rect.center = self.mother.pos + self.weapon_offset_temp
        else:
            self.mid_weapon_melee_rect.center = self.weapon_melee_rect.center = self.melee_rect.center
        if self.mother.equipped['weapons2']:
            self.weapon2_offset_temp = (self.weapon2_pos + vec(self.weapon2_width/2, 0)).rotate(-(self.mother.rot + self.weapon2_angle))
            self.mid_weapon2_melee_rect.center = self.mother.pos + self.weapon2_offset_temp
            self.weapon2_offset_temp = (self.weapon2_pos + vec(self.weapon2_width, 0)).rotate(-(self.mother.rot + self.weapon2_angle))
            self.weapon2_melee_rect.center = self.mother.pos + self.weapon2_offset_temp
        else:
            self.mid_weapon2_melee_rect.center = self.weapon2_melee_rect.center = self.melee2_rect.center

        if not self.mother.alive():
            self.kill()

class Character(pg.sprite.Sprite): # Used for things humanoid players and animals have in common so they can inherrit them.
    def __init__(self, game, x = 0, y = 0, kind = 'player', colors = None, animal = False):
        self.game = game

        # Motion vars
        self.vel = vec(0, 0)
        self.acc = vec(0, 0)
        self.pos = vec(x, y)
        self.elevation = 0
        self.direction = vec(1, 0) # A unit vector that represents the direction the player is facing.
        self.mouse_direction = vec(0, 0)
        self.mouse_pos = vec(0, 0)
        self.friction = PLAYER_FRIC
        self.rot = randrange(0, 360)
        self.rot_speed = 0
        self.approach_vector = vec(1, 0)

        # Tming vars
        self.last_hit = 0 # Used for the time between mob hits to make it so you only get damaged based on the DAMAGE_RATE
        self.last_stat_update = 0 # Used to level stats periodically based on activities
        self.stat_update_delay = 50000
        self.last_shot = 0
        self.last_shot2 = 0
        self.last_shift = 0
        self.last_stam_regen = 0
        self.last_move = 0
        self.last_damage = 0
        self.last_magica_drain = 0
        self.last_hunger = 0
        self.last_fireball = 0
        self.last_fire = 0
        self.last_charge = 0
        self.melee_rate = 800
        self.last_melee_sound = 0
        self.last_throw = 0
        self.last_climb = 0

        # vars for leveling
        self.last_kills = 0
        self.last_exercise = 0
        self.last_hits_taken = 0
        self.last_melee = 0
        self.last_stamina_regen = 0
        self.last_healing = 0
        self.last_casting = 0
        self.last_magica_regen = 0
        self.last_cast = 0

        # Counter vars
        self.jump_count = 0
        self.talk_counter = 0  # Used to keep track of how many times you talk to someone. So you can changed the dialogue based on it.

        # State vars
        self.e_down = False # Used for the interact button.
        self.dragon = False
        self.temp_equipped = None # Used for switching your body to a mech suit or for Wraith possession.
        self.possessing = None
        self.occupied = False # Used to tell if it's being ridden
        self.transformable = False # Used to tell if you have the Zhara talisman that lets you transform.
        self.weapon_hand = self.lamp_hand = 'weapons'
        self.flying = False
        self.jumping = False
        self.running = False
        self._climbing = False
        self._swimming = False
        self.in_shallows = False
        self._in_grass = False
        self.inside = False
        self.driver = None
        self.falling = False
        self.melee_playing = False
        self.dual_melee = False
        self.is_reloading = False
        self.in_vehicle = False
        self.in_player_vehicle = False
        self.in_flying_vehicle = False
        self.moving_melee = False
        self.living = True
        self.tile_props = {'material' : '', 'wall': '', 'roof': ''}
        self.next_tile_props = {'material': '', 'wall': '', 'roof': ''}
        #self.block_gid = None
        self.provoked = False
        self.offensive = False
        self.invisible = False

        # Associated objects
        self.vehicle = None
        self.turret = None
        self.arrow = None

        self.animal = animal
        self.kind = kind # The name of the character in the npcs.py dictionaries
        if self.animal:
            self.npc = True
            try:  # This makes it so you can load a saved game even if there were new animal variants added.
                self.kind_dict = self.game.animals_dict[self.kind]
            except:
                self.kind_dict = ANIMALS[self.kind]
                self.game.animals_dict[self.kind] = self.kind_dict
            # Sets layers and special state vars
            if 'flying' in self.kind_dict.keys():
                self.flying = self.kind_dict['flying']
            if self.flying:
                self._layer = self.game.map.sky_layer
                self.in_flying_vehicle = True
            elif 'horse' in self.kind:
                self._layer = self.game.map.bullet_layer
            else:
                self._layer = self.game.map.mob_layer
            # Sets groups
            if 'grabable' in self.kind_dict.keys() and self.kind_dict['grabable']:
                self.groups = game.all_sprites, game.mobs, game.animals, game.grabable_animals, game.detectables, game.moving_targets
            else:
                self.groups = game.all_sprites, game.mobs, game.animals, game.moving_targets
        else:
            try:  # This makes it so you can load a saved game even if there were new/changed NPCs added.
                self.kind_dict = self.game.people[self.kind]
            except:
                self.kind_dict = PEOPLE[self.kind]
                self.game.people[self.kind] = self.kind_dict
            # Sets layers
            try:
                self._layer = self.game.map.player_layer
            except:
                self._layer = PLAYER_LAYER
            # Sets groups
            if self.kind == 'player':
                self.npc = False
                self.groups = game.all_sprites, game.players, game.player_group, game.moving_targets
            else:
                self.npc = True
                if self.kind == 'mech suit':
                    self.groups = game.all_sprites, game.mobs, game.npcs, game.detectables, game.moving_targets, game.mechsuits
                else:
                    self.groups = game.all_sprites, game.mobs, game.npcs, game.detectables, game.moving_targets
        self.original_layer = self._layer
        pg.sprite.Sprite.__init__(self, self.groups)
        self.game.group.add(self)


        # Illuminescensce properties
        self.brightness = 1
        self.mask_kind = 0
        self.light_on = False
        self.light_mask_orig = pg.transform.scale(self.game.light_mask_images[0], (self.brightness, self.brightness))
        self.light_mask = self.light_mask_orig.copy()
        self.light_mask_rect = self.light_mask.get_rect()

        # Creates a blank inventory and generic equipment to be filled later
        #self.expanded_inventory = {'gender': list(GENDER.keys()), 'hair': list(HAIR.keys()), 'race': list(RACE.keys()), 'magic': [None]}
        #self.equipped = {'gender': 'female', 'race': 'osidine', 'hair': None, 'magic': None, 'weapons': None, 'weapons2': None,
        #                 'hats': None, 'tops': None, 'bottoms': None, 'shoes': None, 'gloves': None, 'items': None, 'blocks': None}
        # Character stats and inventories
        self.inventory = fix_inventory(self.kind_dict['inventory'].copy())
        self.expanded_inventory = {'gender': list(GENDER.keys()), 'hair': list(HAIR.keys()), 'race': list(RACE.keys()), 'magic': [{'name': 'fireball', 'type': 'magic', 'fireballs': 1, 'damage': 30, 'cost': 20, 'sound': 'fire blast'}]}
        self.equipped = EMPTY_EQUIP.copy()
        self.hand_item = self.equipped[0]
        self.hand2_item = self.equipped[6]
        self.stats = self.kind_dict['stats'].copy()
        #self.inventory = random_inventory_item(self.inventory, self.equipped['gender']) # assignes random items where it says 'random' in the inventory.

        self.colors = copy.deepcopy(self.kind_dict['colors'])
        if 'random' in self.colors['skin']:
            skin_list = eval(self.colors['skin'].replace('random', ''))
            self.colors['skin'] = choice(skin_list)
        if 'random' in self.colors['hair']:
            hair_list = eval(self.colors['hair'].replace('random', ''))
            self.colors['hair'] = choice(hair_list)
        if 'random' in self.kind_dict['hair']:
            random_hair(self)
        else:
            self.equipped['hair'] = self.kind_dict['hair']
        self.detect_radius = self.default_detect_radius = self.kind_dict['detect radius']
        self.avoid_radius = self.kind_dict['avoid radius']
        self.name = self.kind_dict['name']
        self.touch_damage = self.stats['touch damage']
        self.touch_knockback = self.stats['touch knockback']
        self.default_acceleration = self.acceleration = self.stats['acceleration']
        self.run_acc = self.default_acceleration + RUN_INCREASE
        self.jum_acc = self.default_acceleration + RUN_INCREASE
        self.climb_acc = self.default_acceleration / 2
        self.grass_acc = self.default_acceleration * (3/4)
        self.shallows_acc = self.default_acceleration * (2/3)
        if 'dialogue' in self.kind_dict.keys():
            self.dialogue = self.kind_dict['dialogue']
        else:
            self.dialogue = None
        self.aggression = self.kind_dict['aggression']
        self.protected = self.kind_dict['protected']
        self.race = self.equipped['race'] = self.kind_dict['race']
        self.equipped['gender'] = self.kind_dict['gender']
        if self.equipped['gender'] == 'random':
            self.equipped['gender'] = choice(['male', 'female'])
        #self.expanded_inventory['magic'] = self.kind_dict['magic']
        self.last_weapon = self.equipped['weapons'] # This string is used to keep track of what the player's last weapon was for equipping and unequipping toggling weapons and keeping track of bullets from old weapons
        self.last_weapon2 = self.equipped['weapons2']
        self.current_weapon = self.equipped['weapons']# weapon you had for autoequipping when your weapon is sheathed.
        self.current_weapon2 = self.equipped['weapons2'] # weapon you had for autoequipping when your weapon is sheathed.

        # Character qualities
        self.hungers = True
        self.guard = False
        self.magical_being = False
        self.immaterial = False
        self.spell_caster = False
        self.mountable = False
        self.hideable = False
        if len(self.expanded_inventory['magic']) > 0:
            self.spell_caster = True
        if 'Guard' in self.kind_dict['name']:
            self.guard = True
        if self.equipped['race'] in ['wraith', 'spirit', 'skeleton', 'mechanima']:
            self.hungers = False
        if self.race in ['wraith', 'spirit']:
            self.immaterial = True
        if self.equipped['race'] in ['wraith', 'spirit', 'skeleton']:
            self.magical_being = True

        self.talk_rect = XLARGE_HIT_RECT.copy()
        self.hit_rect = copy.deepcopy(self.kind_dict['hit rect'])

        # Assigns AI to character
        self.ai = AI(self)

    def accelerate(self, power = 1, direction = "forward"): # Calculates the acceleration, but def move does the moving
        self.acceleration = self.default_acceleration
        self.run_acc = self.default_acceleration + RUN_INCREASE + self.stats['agility'] / 4
        if self.run_acc > MAX_RUN:
            self.run_acc = MAX_RUN
        self.jum_acc = self.default_acceleration + RUN_INCREASE
        self.climb_acc = self.default_acceleration / 2
        self.grass_acc = self.default_acceleration * (3/4)
        self.shallows_acc = self.default_acceleration * (2/3)

    def move(self):
        self.rot = (self.rot + self.rot_speed * self.game.dt) % 360
        self.direction = self.approach_vector.rotate(-self.rot)
        self.rect.center = self.pos
        self.acc += self.vel * self.friction
        self.vel += self.acc
        self.pos += self.vel * self.game.dt + 0.5 * self.acc * self.game.dt ** 2

    def rotate_to(self, vec):
        vector = vec
        angle = fix_angle(vector.angle_to(self.direction))
        if self.in_vehicle:
            rot_speed = self.vehicle.rot_speed/3
            if self.vehicle.turret == None:
                self.set_rot_speed(rot_speed, angle)
        else:
            rot_speed = PLAYER_ROT_SPEED
            self.set_rot_speed(rot_speed, angle)

    def set_rot_speed(self, rot_speed, angle):
        if angle < 0:
            self.rot_speed = -rot_speed * 10 * abs(angle) / 180
        else:
            self.rot_speed = rot_speed * 10 * abs(angle) / 180

    def can_run(self):
        if (self.arrow == None) and self.is_moving() and (not self.in_vehicle) and (self.stats['stamina'] > 10):
            return True
        else:
            return False

    def use_toilet(self):
        self.add_health(5)
        self.add_stamina(30)
        self.add_hunger(-4)
        toilet_sounds = ['fart', 'pee']
        play_relative_volume(self, choice(toilet_sounds))
        if self in self.game.players:
            sleep(2)
        play_relative_volume(self, 'toilet')
        self.game.beg = perf_counter()  # resets dt

    def sleep_in_bed(self):
        if self in self.game.players:
            self.game.sleep_in_bed()
        else: # I will add a sleeping animation later.
            self.add_health(50)
            self.add_stamina(50)
            self.add_magica(50)

    def make_companion(self):
        self.remove(self.game.mobs)
        self.game.player_group.add(self)
        self.game.companions.add(self)
        self.guard = True

    def unfollow(self):
        self.game.mobs.add(self)
        self.remove(self.game.player_group)
        self.remove(self.game.companions)
        self.guard = False

    def pre_jump(self):
        pass
    def jump(self):
        pass

    def draw_health(self):
        pass

    def death(self, silent = False):
        if self in self.game.companions:
            self.unfollow()
        if not silent:
            play_relative_volume(self, choice(self.game.zombie_hit_sounds), False)
        self.living = False

    def does_melee_damage(self, mob):
        damage_reduction = self.stats['stamina'] / self.stats['max stamina']
        now = pg.time.get_ticks()
        if now - self.last_damage > self.melee_rate:
            if self.equipped[self.weapon_hand] == None:
                damage = damage_reduction * self.stats['strength']
                mob.vel = vec(0, 0)
                play_relative_volume(self, choice(self.game.punch_sounds), False)
                mob.gets_hit(damage, 2, self.rot)
                self.game.hud_mobhp = mob.stats['health'] / mob.stats['max health']
                self.game.last_mobhp_update = pg.time.get_ticks()
                self.game.show_mobhp = True
            else:
                weapon_damage = self.equipped[self.weapon_hand]['damage']
                damage = damage_reduction * (self.stats['strength'] + weapon_damage) + weapon_damage/4
                mob.vel = vec(0, 0)
                if 'knockback' in self.equipped[self.weapon_hand]:
                    knockback = self.equipped[self.weapon_hand]['knockback']
                else:
                    knockback = self.equipped[self.weapon_hand]['weight'] * 3
                self.play_weapon_hit_sound()
                mob.gets_hit(damage, knockback, self.rot)
                self.game.hud_mobhp = mob.stats['health'] / mob.stats['max health']
                self.game.last_mobhp_update = pg.time.get_ticks()
                self.game.show_mobhp = True
            # add mob hit sounds here
            self.stats['melee'] += 0.1
            self.last_damage = now
            mob.ai.target = self
        if not self.game.guard_alerted:
            if mob.protected:
                self.alert_guard()

    def gets_hit(self, damage, knockback = 0, rot = 0, dam_rate = DAMAGE_RATE):
        if self.in_vehicle:
            self.vehicle.gets_hit(damage, knockback, rot)
        elif self.possessing:
            self.possessing.gets_hit(damage, knockback, rot)
        else:
            now = pg.time.get_ticks()
            if now - self.last_hit > dam_rate:
                self.last_hit = now
                # Player takes damage based on their armor rating/
                temp_val = (damage + self.stats['armor']) # This part prevents division by 0 in the damage_reduction_factor calculation
                if temp_val == 0:
                    temp_val = 1
                damage_reduction_factor = damage/temp_val
                damage_done = damage * damage_reduction_factor
                if damage_done > 0:
                    if self not in self.game.animals:
                        if self.equipped['gender'] == 'male':
                            play_relative_volume(self, choice(self.game.male_player_hit_sounds), False)
                        else:
                            play_relative_volume(self, choice(self.game.female_player_hit_sounds), False)
                    self.add_health(-damage_done)
                self.pos += vec(knockback, 0).rotate(-rot)
                if pg.sprite.spritecollide(self, self.game.barriers, False): #Prevents sprite from being knocked through a wall.
                    self.pos -= vec(knockback, 0).rotate(-rot)
                self.rect.center = self.hit_rect.center = self.pos
                self.stats['hits taken'] += 1

    def cast_spell(self, spell):
        if self.weapon_hand == 'weapons':
            mpos = self.body.melee_rect.center
        else:
            mpos = self.body.melee2_rect.center
        now = pg.time.get_ticks()
        if now - self.last_cast > self.game.effects_sounds[spell['sound']].get_length() * 1000:
            if self.stats['magica'] >= spell['cost']:
                if True: #self.check_materials('magic', self.equipped['magic']):
                    play_relative_volume(self, spell['sound'])
                    Spell_Animation(self.game, spell['name'], mpos, self.rot, self.vel)
                    pos = vec(0, 0)
                    pos = self.pos + vec(60, 0).rotate(-self.rot)
                    if 'possession' in spell:
                        if self.possessing == None:
                            if 'wraith' in self.equipped['race']:
                                if self.equipped['race'] == 'spirit': # Turns you into a black wraith for using dark magic.
                                    self.equipped['race'] = 'wraith'
                                    self.race = 'wraith'
                                    self.human_body.update_animations()
                                    if self.dragon:
                                        self.dragon_body.update_animations()
                                else:
                                    hits = pg.sprite.spritecollide(self, self.game.npcs, False, False)
                                    if hits:
                                        if hits[0].race not in ['spirit', 'wraith', 'demon', 'skeleton']:
                                            drop_all_items(self, False)
                                            hits[0].possess(self, True)
                            else:
                                self.equipped['race'] = 'wraith'
                                self.race = 'wraith'
                                drop_all_items(self, True)
                                corpse = Player(self.game, self.pos.x, self.pos.y, 'villager')
                                corpse.inventory = self.inventory
                                corpse.death()
                                self.human_body.update_animations()
                                if self.dragon:
                                    self.dragon_body.update_animations()
                                self.game.beg = perf_counter() # resets the counter so dt doesn't get messed up.
                        else:
                            self.add_health(self.possessing.stats['health'])
                            self.possessing.gets_hit(self.stats['stamina'])
                            self.possessing.depossess()

                    if 'summon' in spell:
                        if spell['summon'] in PEOPLE:
                            summoned = Player(self.game, mpos.x + 128, mpos.y, MAGIC[self.equipped['magic']]['summon'])
                            summoned.make_companion()
                        elif spell['summon'] in ANIMALS:
                            Animal(self.game, mpos.x, mpos.y, spell['summon'])
                    if 'healing' in spell:
                        self.add_health(spell['healing'] + (self.stats['healing'] / 20) + (self.stats['casting'] / 100))
                    if 'fireballs' in spell:
                        balls = spell['fireballs']
                        damage = spell['damage'] + (self.stats['casting'] / 100)
                        for i in range(0, balls):
                            Fireball(self, self.game, mpos, self.rot + (36 * i), damage, 30, 1300, 250, self.vel, 'fire', False, self.in_flying_vehicle)
                    self.add_magica(-spell['cost'])
                    self.stats['casting'] += spell['cost'] / 10

                    #dir = vec(1, 0).rotate(-self.rot)
                    self.last_cast = now

    def alert_guard(self):
        pass

    def update_hud_stats(self, stat = False):
        if stat == 'health':
            if self.game.hud_health_stats == self.stats:
                self.game.hud_health = self.stats['health'] / self.stats['max health']
        if not self.npc:
            if stat == 'stamina':
                self.game.hud_stamina = self.stats['stamina'] / self.stats['max stamina']
            elif stat == 'magica':
                self.game.hud_magica = self.stats['magica'] / self.stats['max magica']
            elif stat == 'hunger':
                self.game.hud_hunger = self.stats['hunger'] / self.stats['max hunger']
            elif stat == 'ammo':
                if self.ammo_cap1 + self.mag1 != 0:
                    self.game.hud_ammo1 = "Right Ammo: " + str(self.mag1) + '/' + str(self.ammo_cap1)
                else:
                    self.game.hud_ammo1 = ""
                if self.ammo_cap2 + self.mag2 != 0:
                    self.game.hud_ammo2 = "Left Ammo: " + str(self.mag2) + '/' + str(self.ammo_cap2)
                else:
                    self.game.hud_ammo2 = ""

    def add_health(self, amount):
        if amount > 20:
            self.stats['healing'] += 1
        self.stats['health'] += amount
        if self.stats['health'] > self.stats['max health']:
            self.stats['health'] = self.stats['max health']
        if self.stats['health'] < 0:
            self.death()
        self.update_hud_stats('health')

    def add_stamina(self, amount, percent = 0):
        if percent != 0:
            amount = amount * self.stats['stamina']
        if amount < 0:
            self.stats['exercise'] -= amount/10
        if amount > 20:
            self.stats['stamina regen'] += 1
        self.stats['stamina'] += amount
        if self.stats['stamina'] > self.stats['max stamina']:
            self.stats['stamina'] = self.stats['max stamina']
        elif (self.stats['stamina'] < 11) and (self.stats['hunger'] > 50):
            self.add_hunger(-1) # Makes you more hungry if you use your stamina.
        elif self.stats['stamina'] < 0:
            self.add_health(self.stats['stamina']) # Subtracts from your health if your stamina is too low.
            self.stats['stamina'] = 0
        self.update_hud_stats('stamina')

    def add_magica(self, amount):
        if amount > 20:
            self.stats['magica regen'] += 1
        self.stats['magica'] += amount
        if self.stats['magica'] > self.stats['max magica']:
            if self.magical_being:
                self.add_health(self.stats['magica regen'] / 80)  # You heal based on your skill if your magic is full if you are a magical being
            self.stats['magica'] = self.stats['max magica']
        elif self.stats['magica'] < 0:
            self.stats['magica'] = 0
        self.update_hud_stats('magica')

    def add_hunger(self, amount):
        self.stats['hunger'] += amount
        if self.stats['hunger'] > self.stats['max hunger']:
            self.stats['hunger'] = self.stats['max hunger']
        elif self.stats['hunger'] < 0:
            self.add_stamina(self.stats['hunger']) # Subtracts from your stamina if you're too hungry.
            self.stats['hunger'] = 0
        self.update_hud_stats('hunger')

    def add_inventory(self, item_name, count = 1):
        return add_inventory(self.inventory, item_name, count)

    def check_inventory(self, item, count = 1):
        return check_inventory(self.inventory, item, count)
    """
    def check_materials(self, item_type, chosen_item, subtract_materials = True):
        if 'materials' not in eval(item_type.upper())[chosen_item]:
            return True
        else:
            materials_list = eval(item_type.upper())[chosen_item]['materials']
            if self.check_materials_list(materials_list):
                if subtract_materials:
                    self.subract_material_list(materials_list)
                    return True

    def subract_material_list(self, materials_list):
        for item, count in materials_list.items():
            self.add_inventory(item, -count)

    def check_materials_list(self, materials_list):
        for material in materials_list:
            if material in self.inventory['items']:  # Sees if you have any of the required material
                if materials_list[material] > self.inventory['items'][material]:  # Sees if you have enough of the required material
                    return False
            elif material in self.inventory['blocks']:  # Sees if you have any of the required material
                if materials_list[material] > self.inventory['blocks'][material]:  # Sees if you have enough of the required material
                    return False
            else:
                return False
        return True"""

class Player(Character):  # Used for humanoid NPCs and Players
    def __init__(self, game, x = 0, y = 0, kind = 'player', colors = None, animal = False):
        super().__init__(game, x, y, kind, colors, animal)
        self.image = self.game.body_surface
        self.rect = self.image.get_rect()
        self.hit_rect.center = self.rect.center
        self.talk_rect.center = self.rect.center
        self.light_mask_rect.center = self.rect.center

        self.gun = True # determines if gun animations are rendered
        self.bow = True
        self.ammo = {'pistol': 100, 'submachine gun': 100, 'shotgun': 100, 'rifle': 100, 'sniper rifle': 100, 'rocket launcher': 100, 'grenades': 100, 'turret': 1000, 'laser': 100, 'crystals': 100, 'bow': 100}
        self.mag1 = 0
        self.mag2 = 0
        self.ammo_cap1 = 0
        self.ammo_cap2 = 0

        change_clothing(self)
        # Create Body object (keep this as the last attribute.
        self.human_body = Body(self.game, self)
        if 'is dragon' in self.kind_dict.keys():
            self.has_dragon_body = self.kind_dict[
                'is dragon']  # Used to define whether or not a character can transform into a dragon.
            self.dragon_body = Body(self.game, self, True)
            self.dragon_body.remove(self.game.all_sprites)
        else:
            self.has_dragon_body = False
        self.body = self.human_body
        if self.npc:
            lamp_check(self)
        self.animation_playing = self.body.stand_anim

        # Used for breathing fire and the special after effect of the fire.
        self.fire_damage = self.start_fire_damage = 20
        self.after_effect = None

        # Used for equipment perks
        self.equipped_after_effect = False
        self.fireball_rate = self.original_fireball_rate = 400
        self.fireball_rate_perk = 0
        self.health_perk = self.old_health_perk = 0
        self.stamina_perk = self.old_stamina_perk = 0
        self.magica_perk = self.old_magica_perk = 0

        set_elevation(self)

    @property
    def in_grass(self):
        return self._in_grass
    @in_grass.setter
    def in_grass(self, value): # Doesn't do anything yet but return the value
        if value!=self._in_grass:
            self._in_grass = value
    @property
    def swimming(self):
        return self._swimming
    @swimming.setter
    def swimming(self, value):
        if value!=self._swimming:
            if not self.in_vehicle:
                toggle_equip(self, value)
            self._swimming = value
        else:
            pass
    @property
    def climbing(self):
        return self._climbing
    @climbing.setter
    def climbing(self, value):
        if value!=self._climbing:
            if value:
                self.last_climb = pg.time.get_ticks()
                self.pre_jump()
            toggle_equip(self, value)
            self._climbing = value
        else:
            pass

    def death(self, silent = False):
        super().death()
        self.depossess()
        if 'dead' in self.game.people[self.kind]: # Keeps track of if special NPCs have been killed or not.
            self.game.people[self.name.lower()]['dead'] = True
        self.body.kill()
        if self.npc:
            self.remove(self.game.mobs)
            self.remove(self.game.npcs)
        else:
            self.remove(self.game.players)
            self.game.playing = False
        self.remove(self.game.moving_targets)
        self.add(self.game.corpses)
        self.game.group.add(self)
        self.game.group.change_layer(self, self.game.map.items_layer)  # Switches the corpse to items layer
        if self.equipped['race'] == 'demon':
            Player(self.game, self.pos.x, self.pos.y, 'wraith')
        if self.equipped['race'] in RACE_CORPSE_DICT:
            self.image = pg.transform.rotate(self.game.corpse_images[RACE_CORPSE_DICT[self.equipped['race']]], self.rot)
        else:
            self.image = pg.transform.rotate(self.game.corpse_images[0], self.rot)
        self.rect = self.image.get_rect()
        self.rect.center = self.pos

    def make_companion(self):
        super().make_companion(self)
        self.game.companion_bodies.add(self.body)
        self.body.update_animations()
        #self.target = self.game.player
        #self.approach_vector = vec(1, 0)
        #self.default_detect_radius = self.detect_radius = self.game.screen_height
        #self.speed = self.walk_speed = 400
        #self.run_speed = 500

    def unfollow(self):
        super().unfollow()
        self.body.remove(self.game.companion_bodies)
        #self.default_detect_radius = self.detect_radius = 250
        #self.speed = self.walk_speed = 80
        #self.run_speed = 100

    def get_keys(self):
        self.rot_speed = 0
        self.acc = vec(0, 0) # Makes it so the player doesn't accelerate when no key is pressed.

        # Controlls shooting/automatic shooting
        mouse_buttons_down = pg.mouse.get_pressed()
        if self.equipped[self.weapon_hand]:
            if 'bullet_count' in self.equipped[self.weapon_hand]:
                if ('auto' in self.equipped[self.weapon_hand]) and self.equipped[self.weapon_hand]['auto']:
                    if mouse_buttons_down == (0, 0, 1) or mouse_buttons_down == (0, 1, 1):
                        self.weapon_hand = 'weapons'
                        self.shoot()
                    if mouse_buttons_down == mouse_buttons_down == (1, 0, 0) or mouse_buttons_down == (1, 1, 0):
                        self.weapon_hand = 'weapons2'
                        self.shoot()
                if mouse_buttons_down == (1, 0, 1) or mouse_buttons_down == (1, 1, 1):
                    self.dual_shoot(True)

        keys = pg.key.get_pressed()
        if keys[self.game.key_map['melee']]:
            self.pre_melee()

        # WASD keys for forward/rev and rotation
        if self.in_vehicle == False:
            if keys[self.game.key_map['strafe left']] and (keys[self.game.key_map['forward']] or mouse_buttons_down == (0, 1, 0) or mouse_buttons_down == (0, 1, 1) or mouse_buttons_down == (1, 1, 0)):
                self.accelerate(0.8, "diagonal left")
            elif keys[self.game.key_map['strafe right']] and (keys[self.game.key_map['forward']] or mouse_buttons_down == (0, 1, 0) or mouse_buttons_down == (0, 1, 1) or mouse_buttons_down == (1, 1, 0)):
                self.accelerate(0.8, "diagonal right")
            elif keys[self.game.key_map['strafe left']]:
                self.accelerate(0.8, "left")
            elif keys[self.game.key_map['strafe right']]:
                self.accelerate(0.8, "right")
            elif keys[self.game.key_map['forward']] or (mouse_buttons_down == (0, 1, 0) or mouse_buttons_down == (0, 1, 1) or mouse_buttons_down == (1, 1, 0)):
                self.accelerate()
            elif keys[self.game.key_map['back']]:
                self.accelerate(0.5, "rev")
            if keys[self.game.key_map['rot left']]:
                self.rot_speed = PLAYER_ROT_SPEED
            if keys[self.game.key_map['rot right']]:
                self.rot_speed = -PLAYER_ROT_SPEED
        else:
            if keys[self.game.key_map['rot left']]:
                self.rot_speed = self.vehicle.rot_speed
            if keys[self.game.key_map['rot right']]:
                self.rot_speed = -self.vehicle.rot_speed
            if keys[self.game.key_map['forward']] or (mouse_buttons_down == (0, 1, 0) or mouse_buttons_down == (0, 1, 1) or mouse_buttons_down == (1, 1, 0)):
                self.accelerate()
                self.vehicle.forward = True
            else:
                self.vehicle.forward = False
            if keys[self.game.key_map['back']]:
                self.accelerate(0.5, "rev")
        now = pg.time.get_ticks()

        # Running
        if keys[self.game.key_map['sprint']] and self.can_run():
            self.running = True
            if now - self.last_shift > 100:
                self.add_stamina(-0.8)
                self.last_shift = now
        else:
            self.running = False

        #Mouse aiming
        mouse_movement = vec(pg.mouse.get_rel()).length()
        if mouse_movement > 0:
            self.rotate_to(self.mouse_direction)

    def accelerate(self, power = 1, direction = "forward"): # Calculates the acceleration, but def move does the moving
        super().accelerate()

        perp = 0
        if self.melee_playing:
            self.moving_melee = True
        elif self.jumping:
            if self.climbing:
                self.acceleration = self.climb_acc
            else:
                self.acceleration = self.jum_acc
        else:
            self.moving_melee = False
            #Chooses Character's Walking and Running Animations
            # Plays sounds based on what you are walking on or swimming in
            now = pg.time.get_ticks()
            if self.swimming:
                self.animation_playing = self.body.swim_anim
                animate_speed = 120
                if now - self.last_move > self.game.effects_sounds['swim'].get_length() * 1000:
                    self.last_move = now
                    play_relative_volume(self, 'swim')
                    if not self.in_vehicle:
                        self.add_stamina(-1)
            elif self.in_shallows:
                self.acceleration = self.shallows_acc
                self.animation_playing = self.body.shallows_anim
                animate_speed = 120
                if now - self.last_move > self.game.effects_sounds['shallows'].get_length() * 1000:
                    self.last_move = now
                    play_relative_volume(self, 'shallows')
            elif self.in_grass:
                self.acceleration = self.grass_acc
                self.animation_playing = self.body.shallows_anim
                animate_speed = 120
                if now - self.last_move > self.game.effects_sounds['grass'].get_length() * 1000:
                    self.last_move = now
                    play_relative_volume(self, 'grass')
            elif self.climbing:
                self.acceleration = self.climb_acc
                if self.equipped['weapons'] or self.equipped['weapons2']:
                    self.animation_playing = self.body.climbing_weapon_anim
                else:
                    self.animation_playing = self.body.climbing_anim
                animate_speed = 250
                if now - self.last_move > self.game.effects_sounds['climb'].get_length() * 1000: # I really should reuse this code for parts where I need to end the sound before playing another.
                    self.last_move = now
                    play_relative_volume(self, 'climb')
                    if not self.in_vehicle:
                        self.add_stamina(-8)
            elif self.is_reloading:
                animate_speed = 120 # This animation is set up in the reload method
            elif self.running:
                self.acceleration = self.run_acc
                self.animation_playing = self.body.run_anim
                animate_speed = 80
            else:
                self.animation_playing = self.body.walk_anim
                animate_speed = 120
            if self.in_vehicle:
                if self.vehicle.mountable:
                    animate_speed = 200
            # Animates character
            if not self.is_reloading:
                self.body.animate(self.animation_playing, animate_speed)

        if not ((self.melee_playing and (self.climbing or self.swimming)) or self.dual_melee):
            if direction == "rev":
                speed = -self.acceleration
            elif direction == "forward":
                speed = self.acceleration
            elif direction == "right":
                speed = 0
                perp = self.acceleration
            elif direction == "left":
                speed = 0
                perp = -self.acceleration
            elif direction == "diagonal right":
                speed = self.acceleration
                perp = self.acceleration
            elif direction == "diagonal left":
                speed = self.acceleration
                perp = -self.acceleration
            self.acc = vec(speed * power, perp * power).rotate(-self.rot)

    def update_player_only(self):
        now = pg.time.get_ticks()
        # Stops you from climbing after a certain time if you aren't on an object that requires you climb on it.
        if self.climbing:
            if now - self.last_climb > CLIMB_TIME:
                if not pg.sprite.spritecollide(self, self.game.climbs, False):
                    self.climbing = False

        # makes you more hungry if you are a race that eats
        if self.hungers:
            if now - self.last_hunger > GAME_HOUR:
                self.add_hunger(-5)
                self.last_hunger = now
        # drains magica if you are a dragon
        if self.dragon:
            if now - self.last_magica_drain > 2000:
                self.stats['magica'] -= 5
                if self.stats['magica'] < 0:
                    self.stats['magica'] = 0
                    self.transform()
                self.last_magica_drain = now
        # recharges magica when not a dragon
        else:
            time_delay = 3000
            time_reduction_factor = time_delay / (time_delay + self.stats['magica regen'])
            regen_delay = time_delay * time_reduction_factor + time_delay / 6
            if now - self.last_magica_drain > regen_delay:
                self.add_magica(4 + self.stats['magica regen']/50)
                self.last_magica_drain = pg.time.get_ticks()
        #recharge stamina and health
        if not (self.swimming or self.climbing):
            if self.stats['stamina'] < self.stats['max stamina']:
                time_delay = 3000
                time_reduction_factor = time_delay / (time_delay + self.stats['stamina regen'])
                regen_delay = time_delay * time_reduction_factor + time_delay/6
                if now - self.last_stam_regen > regen_delay:
                    keys = pg.key.get_pressed()
                    if not (keys[self.game.key_map['climb']] or self.is_attacking()):
                        if not self.running and self.is_moving():
                            self.add_stamina((6 + self.stats['stamina regen']/50) * self.stats['hunger']/self.stats['max hunger']) # Stamina regenerates based off of your hunger level
                            if (self.stats['hunger'] > 75) or not self.hungers:  # You only heal when you're not too hungry.
                                self.add_health(self.stats['healing'] / 150)
                            self.last_stam_regen = pg.time.get_ticks()
        # Upgrades stats
        if now - self.last_stat_update > self.stat_update_delay:
            self.level_stats()
            self.last_stat_update = now

        # Mouse aiming vectors
        mouse_loc = vec(pg.mouse.get_pos())
        self.mouse_pos = vec(mouse_loc.x -self.game.camera.x, mouse_loc.y - self.game.camera.y)
        self.mouse_direction = vec(self.mouse_pos.x - self.pos.x, self.mouse_pos.y - self.pos.y) #gets the direciton from the character to mouse cursor.
        # Process key events and move character
        self.get_keys()

    def update(self):
        if self.living:
            # This parts synchs the body sprite with the player's soul.
            self.body.rot = self.rot
            self.body.image = pg.transform.rotate(self.body.body_surface, self.rot)
            self.body.rect = self.body.image.get_rect()
            self.body.rect.center = self.rect.center

            if self.melee_playing:
                self.melee()
            if self.jumping:
                self.jump()
            if self.is_reloading:
                self.reload()

            if self.npc and self.living:
                self.ai.update()
            else:
                self.update_player_only()

            self.move()

            if not self.in_vehicle:
                if ('wraith' not in self.race):
                    collide_with_tile_walls(self)
                    collide_with_moving_targets(self)
            if self.light_on:
                if self in self.game.lights:
                    if self.race == 'mechanima':
                        self.light_mask_rect.center = self.rect.center
                    elif self.lamp_hand == 'weapons':
                        self.light_mask_rect.center = self.body.melee_rect.center
                    else:
                        self.light_mask_rect.center = self.body.melee2_rect.center
                    if self.mask_kind in DIRECTIONAL_LIGHTS:
                        new_image = self.game.flashlight_masks[int(self.rot/3)] # Uses preloaded rotated images to save on CPU usage.
                        old_center = self.light_mask_rect.center
                        self.light_mask = new_image
                        self.light_mask_rect = self.light_mask.get_rect()
                        self.light_mask_rect.center = old_center
            else:
                self.light_mask_rect.center = (-2000, -2000) # Moves light off screen when off
            self.check_map_pos() # Used for changing to a new map when you get pass over the edge.
            set_tile_props(self)

    def play_weapon_sound(self, default = None):
        if default == None:
            snd = choice(self.game.weapon_sounds[self.equipped[self.weapon_hand]['type']])
        else:
            snd = choice(self.game.weapon_sounds['mace'])
        if snd.get_num_channels() > 2:
            snd.stop()
        play_relative_volume(self, snd, False)

    def play_weapon_hit_sound(self):
        snd = choice(self.game.weapon_hit_sounds[self.equipped[self.weapon_hand]['type']])
        if snd.get_num_channels() > 2:
            snd.stop()
        play_relative_volume(self, snd, False)

    def pre_melee(self, shot = False): # Used to get the timing correct between each melee strike, and for the sounds
        if True not in [self.jumping, self.is_reloading, self.arrow]:
            if not self.melee_playing:
                # Subtracts stamina
                if self.equipped[self.weapon_hand]:
                    self.add_stamina(-self.equipped[self.weapon_hand]['weight']/50, 100)
                else:
                    self.add_stamina(-0.04, 100)

                now = pg.time.get_ticks()
                if self.equipped[self.weapon_hand]:
                    rate =  self.equipped[self.weapon_hand]['weight'] * 50
                    if now - self.last_melee_sound > rate:
                        self.last_melee_sound = now
                        if shot:  # Used for weapons that shoot and attack at the same time.
                            self.fire_bullets()
                        if self.equipped[self.weapon_hand]['type'] in GUN_LIST:
                            self.play_weapon_sound()
                        else:
                            self.play_weapon_sound('gun')
                else:
                    if now - self.last_melee_sound > 100:
                        self.last_melee_sound = now
                self.melee_playing = True
                self.body.frame = 0
                self.melee()

    def melee(self): # Used for the melee animations
        # Default values if no weapons
        rate = 200 #default timing between melee attacks if no agility. Reduces with higher agility
        rate_reduction_factor = rate/(rate + self.stats['agility'])
        def_speed = 60 #default speed of melee attacks
        speed_reduction_factor = def_speed/(def_speed + self.stats['agility'])
        self.melee_rate = rate * rate_reduction_factor + 90 # Makes it so the timing can't drop bellow 90
        speed = def_speed * speed_reduction_factor + 10 # Makes it so the timing can't drop bellow 10

        if self.weapon_hand == 'weapons':
            climbing_anim = self.body.climbing_melee_anim
            climbing_weapon_anim = self.body.climbing_weapon_melee_anim
            if self.moving_melee:
                melee_anim = self.body.walk_melee_anim
            else:
                melee_anim = self.body.melee_anim
        else:
            climbing_anim = self.body.climbing_l_melee_anim
            climbing_weapon_anim = self.body.climbing_l_weapon_melee_anim
            if self.moving_melee:
                melee_anim = self.body.walk_l_melee_anim
            else:
                melee_anim = self.body.l_melee_anim

        if self.climbing:
            self.animation_playing = climbing_anim
        else:
            self.animation_playing = melee_anim
        if self.equipped[self.weapon_hand]:
            if self.equipped[self.weapon_hand]['type'] == 'shield':
                self.melee_rate = self.melee_rate + self.equipped[self.weapon_hand]['weight'] * 2
                speed = self.equipped[self.weapon_hand]['weight'] * 4
            else:
                self.melee_rate = self.melee_rate + self.equipped[self.weapon_hand]['weight'] * 20
                speed = speed + self.equipped[self.weapon_hand]['weight'] * 5
                if self.climbing:
                    self.animation_playing = climbing_weapon_anim

        if self.dual_melee:
            if self.climbing and (self.equipped['weapons'] or self.equipped['weapons2']):
                self.animation_playing = choice([self.body.climbing_l_weapon_melee_anim, self.body.climbing_weapon_melee_anim])
            elif self.climbing:
                self.animation_playing = choice([self.body.climbing_l_melee_anim, self.body.climbing_melee_anim])
            else:
                self.animation_playing = self.body.dual_melee_anim
            if self.equipped['weapons'] and self.equipped['weapons2']:
                self.melee_rate = self.melee_rate + (self.equipped['weapons']['weight'] + self.equipped['weapons2']['weight'])/2 * 30
                speed = speed + (self.equipped['weapons']['weight'] + self.equipped['weapons2']['weight'])/2
            elif self.equipped['weapons']:
                self.melee_rate = self.melee_rate + self.equipped['weapons']['weight'] * 20
                speed = speed + self.equipped['weapons']['weight']/2 * 5
            elif self.equipped['weapons2']:
                self.melee_rate = self.melee_rate + self.equipped['weapons2']['weight'] * 20
                speed = speed + self.equipped['weapons2']['weight']/2 * 5

        if not self.in_vehicle:
            if self.swimming:
                self.animation_playing = self.body.swim_melee_anim

        now = pg.time.get_ticks()
        if now - self.last_shot > self.melee_rate:
            if self.melee_playing:
                self.body.animate(self.animation_playing, speed)
                if self.body.frame > len(self.animation_playing[0]) - 1:
                    self.melee_playing = False
                    self.dual_melee = False
                    self.last_shot = pg.time.get_ticks()

    def pre_jump(self):
        if not (self.melee_playing or self.in_vehicle or self.is_reloading):
            if self.stats['stamina'] > 10 or self.falling:
                if 'dragon' not in self.equipped['race']:
                    if not self.jumping :
                        self.add_stamina(-2)
                        self.jumping = True
                        self.body.frame = 0
                        self.jump()
                else:
                    if self.jumping:
                        if self.jump_count < 4:
                            self.add_stamina(-2)
                            self.jump_count += 1
                    else:
                        self.add_stamina(-2)
                        self.body.frame = 0
                        self.jumping = True
                        self.jump()

    def jump(self):
        delay = 500
        speed = 135
        if 'dragon' not in self.equipped['race']:
            if self.climbing:
                self.animation_playing = self.body.climb_jump_anim
                speed = 40
            elif self.falling:
                self.animation_playing = self.body.jump_anim
                speed = 20
                delay = 0
        else:
            delay = 60
        if self.swimming:
            if 'dragon' not in self.equipped['race']:
                self.animation_playing = self.body.swim_jump_anim
        else:
            self.animation_playing = self.body.jump_anim

        now = pg.time.get_ticks()
        if now - self.last_shot > delay:
            if self.jumping:
                self.body.animate(self.animation_playing, speed)
                if self.body.frame > len(self.animation_playing[0]) - 1:
                    if 'dragon' not in self.equipped['race']:
                        self.jumping = False
                        self.falling = False
                        if self.swimming or self.in_shallows:
                            play_relative_volume(self, 'splash')
                        else:
                            play_relative_volume(self, 'jump')
                        self.last_shot = pg.time.get_ticks()
                    else:
                        self.add_stamina(-2)
                        if self.stats['stamina'] == 0:
                            self.jumping = False
                            self.falling = False
                            self.jump_count = 0
                            if self.swimming or self.in_shallows:
                                play_relative_volume(self, 'splash')
                            else:
                                play_relative_volume(self, 'jump')
                            self.last_shot = pg.time.get_ticks()
                        elif self.jump_count < 1:
                            self.jump_count = 0
                            self.jumping = False
                            self.falling = False
                            if self.swimming or self.in_shallows:
                                play_relative_volume(self, 'splash')
                            else:
                                play_relative_volume(self, 'jump')
                            self.last_shot = pg.time.get_ticks()
                        else:
                            self.jump_count -= 1

    def alert_guard(self):
        pass

    def toggle_previous_weapons(self):
        if not self.swimming:
            self.equipped['weapons'] = self.last_weapon
            self.last_weapon = self.current_weapon
            self.current_weapon = self.equipped['weapons']
            self.equipped['weapons2'] = self.last_weapon2
            self.last_weapon2 = self.current_weapon2
            self.current_weapon2 = self.equipped['weapons2']
            self.human_body.update_animations()
            self.dragon_body.update_animations()

    def use_item(self, item, hud_slot = None, dict = 'equipped'):
        remove = False
        if 'name' in item:
            if item['name'] == 'airship fuel':
                if self.in_vehicle:
                    if self.vehicle.cat == 'airship':
                        self.vehicle.fuel += 100
                        play_relative_volume(self, 'pee')
                        remove = True
            #if 'spell' in item:
            #    if item['spell'] not in self.expanded_inventory['magic']:
            #        self.expanded_inventory['magic'].append(ITEMS[self.equipped['items']]['spell'])
            #        play_relative_volume(self, 'page turn')
            #        play_relative_volume(self, ITEMS[self.equipped['items']]['sound'])
            if 'ammo' in item:
                self.ammo[item['type']] += item['ammo']
                self.pre_reload()
                remove = True
            if item['type'] == 'food':
                if self.hungers or 'mechanima' in self.race:  # Makes it so only races that can eat can eat.
                    if self.stats['hunger'] < 100: # You can only eat when you are hungry
                        if 'health' in item:
                            self.add_health(item['health'] + (self.stats['healing'] / 20))
                            remove = True
                        if 'stamina' in item:
                            self.add_stamina(item['stamina'] + (self.stats['stamina regen'] / 20))
                            remove = True
                        if 'magica' in item:
                            self.add_magica(Iitem['magica'] + (self.stats['magica regen'] / 20))
                            remove = True
                        if 'hunger' in item:
                            self.add_hunger(item['hunger'])
                            remove = True
                        play_relative_volume(self, 'eat')
                    else:
                        return "You are too full to eat that."
            else:
                if 'health' in item:
                    self.add_health(item['health'] + (self.stats['healing'] / 20))
                    remove = True
                if 'stamina' in item:
                    self.add_stamina(item['stamina'] + (self.stats['stamina regen'] / 20))
                    remove = True
                if 'magica' in item:
                    self.add_magica(item['magica'] + (self.stats['magica regen'] / 20))
                    remove = True
                if 'hunger' in item:
                    self.add_hunger(item['hunger'])
                    remove = True
            if 'change race' in item:
                self.equipped['race'] = item['change race']
                self.human_body.update_animations()
                self.dragon_body.update_animations()
                remove = True
            if 'change sex' in item:
                self.equipped['gender'] = item['change sex']
                if self.equipped['gender'] == 'female':
                    #random_dress_top = choice(DRESS_TOPS_LIST)
                    #random_dress_skirt = choice(DRESS_BOTTOMS_LIST)
                    random_hair = choice(LONG_HAIR_LIST)
                    #self.add_inventory(random_dress_top)
                    #self.add_inventory(random_dress_skirt)
                    self.expanded_inventory['hair'].append(random_hair)
                    #self.equipped['tops'] = random_dress_top
                    #self.equipped['bottoms'] = random_dress_skirt
                    self.equipped['hair'] = random_hair
                else:
                    random_hair = choice(SHORT_HAIR_LIST)
                    #self.add_inventory('tshirt M')
                    #self.add_inventory('jeans M')
                    self.expanded_inventory['hair'].append(random_hair)
                    #self.equipped['tops'] = 'tshirt M'
                    #self.equipped['bottoms'] = 'jeans M'
                    self.equipped['hair'] = random_hair
                self.human_body.update_animations()
                self.dragon_body.update_animations()
                remove = True
            if 'flint and steel' in item:
                if self.change_used_item('items', item):
                    play_relative_volume(self, 'fire blast')
                    Stationary_Animated(self.game, self.pos + vec(64, 0).rotate(-self.rot), 'fire', 500)
                else: # Makes it so it doesn't try to use a None Type in the other if statements.
                    return
            if 'potion' in item:
                if not self.add_inventory('empty bottle'): # lets you keep the bottle to use for creating new potions.
                    Dropped_Item(self.game,self.pos,ITEMS['empty bottle'])
            if 'fuel' in item:
                if not self.add_inventory('empty barrel'):
                    Dropped_Item(self.game, self.pos, ITEMS['empty barrel'])
            if remove:
                self.reduce_hand_item_number(item, hud_slot, dict)
                return
            if item['type'] == 'book':
                return False
            return "You can't use that item here." # Used to verify the item was used. False means it used the item.

    def reduce_hand_item_number(self, item, slot, dict = 'equipped'):
        if item == self.hand_item:
            hand_item = True
        else:
            hand_item = False
        if dict == 'equipped':
            if 'number' in item:
                if item['number'] == 1:
                    self.equipped[slot] = {}
                    if hand_item:
                        self.hand_item = {}
                        self.game.selected_hud_item.clear_item()
                        self.body.update_animations()
                else:
                    item['number'] -= 1
            else:
                self.equipped[slot] = {}
                if hand_item:
                    self.hand_item = {}
                    self.game.selected_hud_item.clear_item()
                    self.body.update_animations()
            if hand_item:
                for i, icon in enumerate(self.game.inventory_hud_icons):
                    icon.update()
                    icon.resize(HUD_ICON_SIZE)
        elif dict == 'inventory':
            if 'number' in item:
                item['number'] -= 1
                if item['number'] < 1:
                    self.inventory[slot] = {}
            else:
                self.inventory[slot] = {}


    def change_used_item(self, item_type, item, return_new_name = False): # This is broken and needs to be repaired.
        print('change_used_item needs to be replaced')

    def place_item(self, hud_slot):
        if self.hand_item != {}:
            Dropped_Item(self.game, self.pos + vec(27, 0).rotate(-self.rot), self.hand_item, self.rot - 90)
            self.reduce_hand_item_number(self.hand_item, hud_slot)

    #def get_equipped_block_gid(self):
    #    if ('type' in self.hand2_item) and ('type' == 'block'):
    #        self.block_gid = gid_with_property(self.game.map.tmxdata,'material', self.hand2_item['name'])
    #        if not self.block_gid:
    #            self.block_gid = gid_with_property(self.game.map.tmxdata, 'plant', self.hand2_item['name'])

    def place_block(self, hand):
        if hand == 1:
            hand_item = self.hand_item
            hud_slot = int(self.game.selected_hud_item.slot_text) - 1
        else:
            hand_item = self.hand2_item
            hud_slot = 6

        gid = self.game.map.get_gid_by_prop_name(hand_item['name'])
        x, y = get_next_tile_pos(self)
        if True not in ['water' in self.next_tile_props['material'], 'shallows' in self.next_tile_props['material'], self.next_tile_props['tree'] != '']: # Prevents you from building on water and trees.
            if (self.next_tile_props['material'] != hand_item['name']) and (self.next_tile_props['plant'] != hand_item['name']): # Makes sure you're not placing the same block.
                if ('roof' in hand_item['name']) and not (self.game.map.is_next_to(x, y, 'roof') or self.game.map.is_next_to(x, y, 'wall')): # Only lets you attach roofs to walls and roofs.
                    return
                if (self.next_tile_props['wall'] == 'wall') and ('door' in hand_item['name']):  # Prevents you from placing doors on walls
                    return
                props = self.game.map.tmxdata.get_tile_properties_by_gid(gid)
                layer = eval("self.game.map." + hand_item['layer'] + "_layer")
                if layer == self.game.map.base_layer: # Makes it so you don't have plants on top of walls and stuff you build.
                    if self.next_tile_props['wall'] == 'wall': # Prevents you from placing walls on walls
                        return
                    self.game.map.tmxdata.layers[self.game.map.ocean_plants_layer].data[y][x] = 0
                    self.game.map.tmxdata.layers[self.game.map.river_layer].data[y][x] = 0
                play_relative_volume(self, 'click')
                temp_gid = self.game.map.gid_to_nearest_angle(gid, self.rot)
                self.game.map.tmxdata.layers[layer].data[y][x] = temp_gid
                self.game.map.update_tile_props(x, y)  # Updates properties for tiles that have changed.
                self.game.map.redraw()
                set_tile_props(self)
                if hand_item['number'] == 1:
                    self.equipped[hud_slot] = {}
                    if hud_slot == 6:
                        self.hand2_item = {}
                    else:
                        self.hand_item = {}
                    self.game.selected_hud_item.clear_item()
                    self.body.update_animations()
                else:
                    hand_item['number'] -= 1
                # Updates hud icons so correct number show after placing blocks
                for i, icon in enumerate(self.game.inventory_hud_icons):
                    icon.update()
                    icon.resize(HUD_ICON_SIZE)

    def is_moving(self):
        keys = pg.key.get_pressed()
        mouse_buttons_down = pg.mouse.get_pressed()
        return (keys[self.game.key_map['forward']] or mouse_buttons_down == (0, 1, 0) or mouse_buttons_down == (0, 1, 1) or mouse_buttons_down == (1, 1, 0))
    def is_attacking(selfself):
        mouse_buttons_down = pg.mouse.get_pressed()
        return (mouse_buttons_down == (1, 0, 0) or mouse_buttons_down == (0, 0, 1) or mouse_buttons_down == (1, 1, 0) or mouse_buttons_down == (0, 1, 1))

    def check_map_pos(self):
        if self.pos.x < 0:
            self.game.change_map('west')
        if self.pos.x > self.game.map.width:
            self.game.change_map('east')
        if self.pos.y < 0:
            self.game.change_map('north')
        if self.pos.y > self.game.map.height:
            self.game.change_map('south')

    def level_stats(self):
        level_kills = self.stats['kills'] - self.last_kills
        level_exercise = self.stats['exercise'] - self.last_exercise
        level_hits = self.stats['hits taken'] - self.last_hits_taken
        level_melee = self.stats['melee'] - self.last_melee
        level_stam = self.stats['stamina regen'] - self.last_stamina_regen
        level_healing = self.stats['healing'] - self.last_healing
        level_casting = self.stats['casting'] - self.last_casting
        level_magica = self.stats['magica regen'] - self.last_magica_regen

        self.calculate_fire_power()

        self.stats['agility'] += level_exercise / 37
        self.stats['strength'] += (level_exercise + level_hits + level_melee + level_kills)/100
        self.stats['max health'] += level_exercise/20 + level_healing
        self.stats['max stamina'] += level_exercise/20 + level_stam
        self.stats['max magica'] +=  level_casting/20 + level_magica

        self.last_kills = self.stats['kills']
        self.last_exercise = self.stats['exercise']
        self.last_hits_taken = self.stats['hits taken']
        self.last_melee = self.stats['melee']
        self.last_stamina_regen = self.stats['stamina regen']
        self.last_healing = self.stats['healing']
        self.last_casting = self.stats['casting']
        self.last_magica_regen = self.stats['magica regen']

    def possess(self):
        pass
    def depossess(self):
        pass

    def calculate_perks(self):
        # Calculates equipment based perks:
        fire_perks = 0 # Used to count how many armor items are dragon fire enchanted
        health_perks = 0
        stamina_perks = 0
        magica_perks = 0
        invisibility_perks = 0
        self.health_perk = 0
        self.stamina_perk = 0
        self.magica_perk = 0
        self.fireball_rate_perk = 0
        self.invisible = False
        for item_type in self.equipped:
            if item_type == 'race' and (self.equipped['race'] not in list(RACE.keys())):
                continue
            if item_type == 'weapons2':
                temp_item_type = 'weapons'
            else:
                temp_item_type = item_type
            item_dict = eval(temp_item_type.upper())
            if self.equipped[item_type]:
                if 'fire enhance' in item_dict[self.equipped[item_type]]:
                    self.after_effect = item_dict[self.equipped[item_type]]['fire enhance']['after effect']
                    self.fire_damage += item_dict[self.equipped[item_type]]['fire enhance']['damage']
                    self.fireball_rate_perk += item_dict[self.equipped[item_type]]['fire enhance']['rate reduction']
                    fire_perks += 1
                if 'reinforce magica' in item_dict[self.equipped[item_type]]:
                    self.magica_perk += item_dict[self.equipped[item_type]]['reinforce magica']
                    magica_perks += 1
                if 'reinforce stamina' in item_dict[self.equipped[item_type]]:
                    self.stamina_perk += item_dict[self.equipped[item_type]]['reinforce stamina']
                    stamina_perks += 1
                if 'reinforce health' in item_dict[self.equipped[item_type]]:
                    self.health_perk += item_dict[self.equipped[item_type]]['reinforce health']
                    health_perks += 1
                if 'property' in item_dict[self.equipped[item_type]]:
                    if item_dict[self.equipped[item_type]]['property'] == 'invisibility':
                        invisibility_perks += 1
        if invisibility_perks > 0:
            if self.body in self.game.group:
                self.game.group.remove(self.body)
                self.invisible = True
        else:
            if self.body not in self.game.group:
                self.game.group.add(self.body)
                self.invisible = False
        if fire_perks == 0:
            self.equipped_after_effect = False
            self.fireball_rate_perk = 0
        else:
            self.equipped_after_effect = True
        if magica_perks == 0: # Removes perks if there are none
            self.stats['magica'] -= self.old_magica_perk
            self.stats['max magica'] -= self.old_magica_perk
            if self.stats['magica'] < 0:
                self.stats['magica'] = 0
            self.old_magica_perk = 0
        else: # Adds new perks based on equipment changes
            self.stats['magica'] += self.magica_perk - self.old_magica_perk
            self.stats['max magica'] += self.magica_perk - self.old_magica_perk
            self.old_magica_perk = self.magica_perk

        if stamina_perks == 0: # Removes perks if there are none
            self.stats['stamina'] -= self.old_stamina_perk
            self.stats['max stamina'] -= self.old_stamina_perk
            if self.stats['stamina'] < 0:
                self.stats['stamina'] = 0
            self.old_stamina_perk = 0
        else: # Adds new perks based on equipment changes
            self.stats['stamina'] += self.stamina_perk - self.old_stamina_perk
            self.stats['max stamina'] += self.stamina_perk - self.old_stamina_perk
            self.old_stamina_perk = self.stamina_perk

        if health_perks == 0: # Removes perks if there are none
            health_percent = self.stats['health']/self.stats['max health']
            self.stats['max health'] -= self.old_health_perk
            self.stats['health'] = int(self.stats['max health'] * health_percent) # Gives you the same percentage of health after removing health perks
            if self.stats['health'] < 1:
                self.stats['health'] = 1
            self.old_health_perk = 0
        else: # Adds new perks based on equipment changes
            self.stats['health'] += self.health_perk - self.old_health_perk
            self.stats['max health'] += self.health_perk - self.old_health_perk
            self.old_health_perk = self.health_perk


        self.fireball_rate = self.original_fireball_rate - self.fireball_rate_perk
        if self.fireball_rate < 1:
            self.fireball_rate = 1
    # dragon related methods
    def transform(self):
        self.invisible = False
        self.stats['casting'] += 0.5
        if 'dragon' not in self.equipped['race']:
            if self.stats['magica'] > 50:
                if self.transformable:
                    self.equipped['race'] = self.race + 'dragon'
                    explosion = Explosion(self.game, self)
                    self.human_body.remove(self.game.all_sprites)
                    self.human_body.remove(self.game.npc_bodies)
                    self.dragon_body.add(self.game.all_sprites)
                    self.dragon_body.add(self.game.npc_bodies)
                    self.game.group.add(self.dragon_body)
                    self.game.group.remove(self.human_body)
                    self.body = self.dragon_body
                    self.body.update()
                    self.stats['magica'] -= 10
                    self.dragon = True
        else:
            self.equipped['race'] = self.race
            explosion = Explosion(self.game, self)
            self.dragon_body.remove(self.game.all_sprites)
            self.dragon_body.remove(self.game.npc_bodies)
            self.human_body.add(self.game.all_sprites)
            self.human_body.add(self.game.npc_bodies)
            self.game.group.add(self.human_body)
            self.game.group.remove(self.dragon_body)
            self.body = self.human_body
            self.body.update()
            self.dragon = False
    def breathe_fire(self):
        now = pg.time.get_ticks()
        if now - self.last_fireball > self.fireball_rate:
            if self.stats['magica'] > 5:
                Fireball(self, self.game, self.pos, self.rot, self.fire_damage, 5, 1000, 300, self.vel, self.after_effect, False, self.in_flying_vehicle)
                self.last_fireball = now
                self.stats['magica'] -= 5
                if self.stats['magica'] < 0:
                    self.stats['magica'] = 0
    def calculate_fire_power(self):
        self.fire_damage = self.start_fire_damage + self.stats['casting']
        if self.fire_damage > 30:
            self.fire_damage = 30 + self.stats['casting']/10
        elif self.fire_damage > 80:
            self.fire_damage = 80 + self.stats['casting']/100
        elif self.fire_damage > 120:
            self.fire_damage = 120 + self.stats['casting']/1000
        if self.fire_damage > 200:
            self.fire_damage = 200
        if not self.equipped_after_effect:
            if self.fire_damage > 75:
                self.after_effect = 'fire'
            else:
                self.after_effect = None
    # methods related to guns
    def throw_grenade(self):
        """
        now = pg.time.get_ticks()
        if now - self.last_throw > 1000:
            if self.equipped['weapons'] == None:
                body_pos = self.body.weapon_pos
                self.weapon_hand = 'weapons'
            else:
                body_pos = self.body.weapon2_pos
                self.weapon_hand = 'weapons2'
            if not self.is_moving() and not self.melee_playing:
                self.pre_melee()
            dir = vec(1, 0).rotate(-(self.rot))

            pos = self.pos + (body_pos + ITEMS['grenade']['offset']).rotate(-(self.rot))
            Bullet(self, self.game, pos, dir, self.rot, 'grenade', False, self.in_flying_vehicle)
            self.ammo['grenades'] -= 1
            self.last_throw = now"""
        pass
    def shoot(self):
        if not self.is_moving():
            if self.weapon_hand == 'weapons2':
                self.animation_playing = self.body.l_shoot_anim
            else:
                self.animation_playing = self.body.shoot_anim
            if self.climbing:
                self.animation_playing = self.body.climbing_shoot_anim

        if self.equipped[self.weapon_hand]:
            if 'bullet_count' in self.equipped[self.weapon_hand]:
                if self.equipped[self.weapon_hand]['type'] not in GUN_LIST: # Makes it so you attack with melee weapons that also shoot things (enchanted weapons, slings, etc.)
                    self.pre_melee(True)
                    return
                keys = pg.key.get_pressed()
                if not self.is_moving() and not self.melee_playing:
                    self.body.animate(self.animation_playing, 120)
                if self.equipped[self.weapon_hand]['type'] in GUN_LIST:
                    now = pg.time.get_ticks()
                    if now - self.last_shot > self.equipped[self.weapon_hand]['rate']:
                        self.last_shot = now
                        self.fire_bullets()
            else:
                self.pre_melee()
        else:
            self.pre_melee()
    def dual_shoot(self, auto = False):
        if self.equipped['weapons'] and self.equipped['weapons2']:
            if ('bullet_count' in self.equipped['weapons']) and ('bullet_count' in self.equipped['weapons2']):
                temp_list = ['weapons', 'weapons2']
                now = pg.time.get_ticks()
                for weapon_hand in temp_list:
                    self.weapon_hand = weapon_hand
                    if auto:
                        if ('auto' in self.equipped[self.weapon_hand]) and self.equipped[self.weapon_hand]['auto']:
                            if weapon_hand == 'weapons':
                                if now - self.last_shot > self.equipped[weapon_hand]['rate']:
                                    self.last_shot = now
                                    self.fire_bullets()
                            else:
                                if now - self.last_shot2 > self.equipped[weapon_hand]['rate']:
                                    self.last_shot2 = now
                                    self.fire_bullets()
                    else:
                        if weapon_hand == 'weapons':
                            if now - self.last_shot > self.equipped[weapon_hand]['rate']:
                                self.last_shot = now
                                self.fire_bullets()
                        else:
                            if now - self.last_shot2 > self.equipped[weapon_hand]['rate']:
                                self.last_shot2 = now
                                self.fire_bullets()
            else:
                self.dual_melee = True
                self.pre_melee()

        else:
            self.dual_melee = True
            self.pre_melee()
    def fire_bullets(self):
        if self.arrow: # Gets rid of arrow shown in bow before firing.
            self.arrow.kill()
            self.arrow = None

        if self.weapon_hand == 'weapons':
            angle = self.body.weapon_angle
            mag_selected = self.mag1
        else:
            angle = self.body.weapon2_angle
            mag_selected = self.mag2
        if mag_selected > 0:
            if not self.in_vehicle:
                self.vel += vec(-self.equipped[self.weapon_hand]['kickback'], 0).rotate(-self.rot)
            dir = vec(1, 0).rotate(-(self.rot + angle))
            if self.weapon_hand == 'weapons':
                pos = self.pos + (self.body.weapon_pos + self.equipped['weapons']['offset']).rotate(-(self.rot + angle))
            else:
                pos = self.pos + (self.body.weapon2_pos + vec(self.equipped['weapons2']['offset'].x, -self.equipped['weapons2']['offset'].y)).rotate(-(self.rot + angle))
            for i in range(self.equipped[self.weapon_hand]['bullet_count']):
                Bullet(self, self.game, pos, dir, self.rot, self.equipped[self.weapon_hand], False, self.in_flying_vehicle)
                if self.weapon_hand == 'weapons':
                    self.use_ammo(1)
                else:
                    self.use_ammo(2)
                self.play_weapon_sound()
                self.stats['marksmanship shots fired'] += 1
                self.stats['marksmanship accuracy'] = self.stats['marksmanship hits'] / self.stats['marksmanship shots fired']
            if self.equipped[self.weapon_hand]['type'] in GUN_LIST:
                MuzzleFlash(self.game, pos)
        else:
            self.out_of_ammo()
    def use_ammo(self, mag):
        if mag == 1:
            self.mag1 -= 1
            if self.mag1 < 0:
                self.mag1 = 0
        if mag == 2:
            self.mag2 -= 1
            if self.mag2 < 0:
                self.mag2 = 0
        self.update_hud_stats('ammo')
    def out_of_ammo(self):
        if not self.is_moving():
            self.pre_melee()
        else:
            self.moving_melee = True
            self.pre_melee()
    def pre_reload(self):
        if not (self.melee_playing or self.jumping or self.swimming):
            if self.arrow:  # Gets rid of arrow shown in bow before reloading them.
                self.arrow.kill()
                self.arrow = None
            if self.equipped['weapons']:
                if self.equipped['weapons']['type'] == 'bow':
                    play_relative_volume(self, 'bow reload')
            if self.equipped['weapons2']:
                if self.equipped['weapons2']['type'] == 'bow':
                    play_relative_volume(self, 'bow reload')
            self.is_reloading = True
            self.body.frame = 0
            self.reload()
    def reload(self):
        speed = 100
        speed1 = 0
        speed2 = 0
        delay = 500
        if self.equipped['weapons'] and ('bullet_count' in self.equipped['weapons']): # checks if you are holding a gun
            if self.is_moving():
                self.animation_playing = self.body.walk_reload_anim
            else:
                self.animation_playing = self.body.reload_anim
            speed1 = self.equipped['weapons']['reload speed']
            speed = speed1
            right = True
        else:
            right = False
        if self.equipped['weapons2'] and ('bullet_count' in self.equipped['weapons2']): # checks if you are holding a gun
            if self.is_moving():
                self.animation_playing = self.body.l_walk_reload_anim
            else:
                self.animation_playing = self.body.l_reload_anim
            speed2 = self.equipped['weapons2']['reload speed']
            speed = speed2
            left = True
        else:
            left = False

        if left and right:
            if self.is_moving():
                self.animation_playing = self.body.walk_dual_reload_anim
            else:
                self.animation_playing = self.body.dual_reload_anim
            speed = speed1 + speed2

        if not(left or right):
            self.animation_playing = self.body.stand_anim

        now = pg.time.get_ticks()
        if now - self.last_shot > delay:
            if self.is_reloading:
                self.body.animate(self.animation_playing, speed)
                if self.body.frame > len(self.animation_playing[0]) - 1:
                    # Reloads magazines
                    if self.equipped['weapons']:
                        if 'enchanted' in self.equipped['weapons'] and (self.equipped['weapons']['type'] in GUN_LIST):
                            if self.ammo['crystals'] - (self.equipped['weapons']['magazine size'] - self.mag1) < 0:
                                self.ammo['crystals'] = 0
                            else:
                                self.ammo['crystals'] -= (self.equipped['weapons']['magazine size'] - self.mag1)
                            if self.ammo[self.equipped['weapons']['type']] - (self.equipped['weapons']['magazine size'] - self.mag1) < 0:
                                self.mag1 = self.mag1 + self.ammo[self.equipped['weapons']['type']]
                                self.ammo[self.equipped['weapons']['type']] = 0
                            else:
                                self.ammo[self.equipped['weapons']['type']] -= (self.equipped['weapons']['magazine size'] - self.mag1)
                                self.mag1 = self.equipped['weapons']['magazine size']
                            self.ammo_cap1 = self.ammo[self.equipped['weapons']['type']]  # Used for HUD display value to improve frame rate by not looking up the value every cycle
                        else:
                            if 'enchanted' in self.equipped['weapons'] and ('bullet_count' in self.equipped['weapons']['bullet_count']):
                                if self.ammo['crystals'] - (self.equipped['weapons']['magazine size'] - self.mag1) < 0:
                                    self.mag1 = self.mag1 + self.ammo['crystals']
                                    self.ammo['crystals'] = 0
                                else:
                                    self.ammo['crystals'] -= (self.equipped['weapons']['magazine size'] - self.mag1)
                                    self.mag1 = self.equipped['weapons']['magazine size']
                                self.ammo_cap1 = self.ammo['crystals'] # Used for HUD display value to improve frame rate by not looking up the value every cycle

                            if (self.equipped['weapons']['type'] in GUN_LIST):
                                if self.ammo[self.equipped['weapons']['type']] - (self.equipped['weapons']['magazine size'] - self.mag1) < 0:
                                    self.mag1 = self.mag1 + self.ammo[self.equipped['weapons']['type']]
                                    self.ammo[self.equipped['weapons']['type']] = 0
                                else:
                                    self.ammo[self.equipped['weapons']['type']] -= (self.equipped['weapons']['magazine size'] - self.mag1)
                                    self.mag1 = self.equipped['weapons']['magazine size']
                                self.ammo_cap1 = self.ammo[self.equipped['weapons']['type']]  # Used for HUD display value to improve frame rate by not looking up the value every cycle
                        if self.equipped['weapons']['type'] != 'bow':
                            play_relative_volume(self, 'gun_pickup')
                        else:
                            if self.mag1 > 0:
                                Arrow(self.game, self, self.equipped['weapons'])
                    else:
                        self.mag1 = self.ammo_cap1 = 0

                    if self.equipped['weapons2']:
                        if 'enchanted' in self.equipped['weapons2'] and (self.equipped['weapons2']['type'] in GUN_LIST):
                            if self.ammo['crystals'] - (self.equipped['weapons2']['magazine size'] - self.mag2) < 0:
                                self.ammo['crystals'] = 0
                            else:
                                self.ammo['crystals'] -= (self.equipped['weapons2']['magazine size'] - self.mag2)
                            if self.ammo[self.equipped['weapons2']['type']] - (self.equipped['weapons2']['magazine size'] - self.mag2) < 0:
                                self.mag2 = self.mag2 + self.ammo[self.equipped['weapons2']['type']]
                                self.ammo[self.equipped['weapons2']['type']] = 0
                            else:
                                self.ammo[self.equipped['weapons2']['type']] -= (self.equipped['weapons2']['magazine size'] - self.mag2)
                                self.mag2 = self.equipped['weapons2']['magazine size']
                            self.ammo_cap2 = self.ammo[self.equipped['weapons2']['type']]  # Used for HUD display value to improve frame rate by not looking up the value every cycle
                        else:
                            if 'enchanted' in self.equipped['weapons2'] and ('bullet_count' in self.equipped['weapons2']):
                                if self.ammo['crystals'] - (self.equipped['weapons2']['magazine size'] - self.mag2) < 0:
                                    self.mag2 = self.mag2 + self.ammo['crystals']
                                    self.ammo['crystals'] = 0
                                else:
                                    self.ammo['crystals'] -= (self.equipped['weapons2']['magazine size'] - self.mag2)
                                    self.mag2 = self.equipped['weapons2']['magazine size']
                                self.ammo_cap2 = self.ammo['crystals'] # Used for HUD display value to improve frame rate by not looking up the value every cycle
                            if ('bullet_count' in self.equipped['weapons2']):
                                if self.equipped['weapons']:
                                    if 'enchanted' in self.equipped['weapons'] and 'enchanted' in self.equipped['weapons2']:
                                        self.ammo_cap1 = self.ammo_cap2 # Makes sure if both your weapons use the same ammo they display the same ammo capacity.

                            if self.equipped['weapons2']['type'] in GUN_LIST:
                                if self.ammo[self.equipped['weapons2']['type']] - (self.equipped['weapons2']['magazine size'] - self.mag2) < 0:
                                    self.mag2 = self.mag2 + self.ammo[self.equipped['weapons2']['type']]
                                    self.ammo[self.equipped['weapons2']['type']] = 0
                                else:
                                    self.ammo[self.equipped['weapons2']['type']] -= (self.equipped['weapons2']['magazine size'] - self.mag2)
                                    self.mag2 = self.equipped['weapons2']['magazine size']
                                self.ammo_cap2 = self.ammo[self.equipped['weapons2']['type']] # Used for HUD display value to improve frame rate by not looking up the value every cycle
                        if self.equipped['weapons']:
                            if not 'enchanted' in self.equipped['weapons'] or not 'enchanted' in self.equipped['weapons2']:
                                if ('bullet_count' in self.equipped['weapons']) and ('bullet_count' in self.equipped['weapons2']):
                                    if self.ammo[self.equipped['weapons']['type']] == self.ammo[self.equipped['weapons2']['type']]:
                                        self.ammo_cap1 = self.ammo_cap2 # Makes sure if both your weapons use the same ammo they display the same ammo capacity.
                        if self.equipped['weapons2']['type'] != 'bow':
                            play_relative_volume(self, 'gun_pickup')
                        else:
                            if self.mag2 > 0:
                                Arrow(self.game, self, self.equipped['weapons2'])
                    else:
                        self.mag2 = self.ammo_cap2 = 0
                    self.is_reloading = False
                    self.last_shot = pg.time.get_ticks()
        self.update_hud_stats('ammo')
    def empty_mags(self):
        # Empties previous weapon mags back into ammo inventory:
        if self.equipped['weapons']:
            if 'enchanted' in self.equipped['weapons'] and (self.equipped['weapons']['type'] not in GUN_LIST):
                if self.equipped['weapons'] and ('bullet_count' in self.equipped['weapons']):
                    self.ammo['crystals'] += self.mag1
                    self.mag1 = 0
        if self.equipped['weapons2']:
            if 'enchanted' in self.equipped['weapons2'] and not (self.equipped['weapons2']['type'] not in GUN_LIST):
                if self.equipped['weapons2'] and ('bullet_count' in self.equipped['weapons2']):
                    self.ammo['crystals'] += self.mag2
                    self.mag2 = 0
        if self.equipped['weapons'] and (self.equipped['weapons']['type'] in GUN_LIST):
                self.ammo[self.equipped['weapons']['type']] += self.mag1
                self.mag1 = 0
        if self.equipped['weapons2'] and (self.equipped['weapons2']['type'] in GUN_LIST):
                self.ammo[self.equipped['weapons2']['type']] += self.mag2
                self.mag2 = 0
        self.update_hud_stats('stats')

class AI(): # Used for assigning artificial intelligence to mobs/players, etc.
    def __init__(self, sprite):
        self.sprite = sprite
        self.game = self.sprite.game
        self.target = choice(sprite.game.moving_targets.sprites())
        self.avoid_radius = self.sprite.avoid_radius
        self.detect_radius = self.sprite.detect_radius
        self.aggression = self.sprite.aggression
        self.offensive = self.sprite.offensive
        self.eating_corpse = 0
        self.last_wall_hit = 0
        self.last_target_seek = 0
        self.hit_wall = False
        if 'a' in self.aggression:
            self.aggressive = self.offensive = True
        else:
            self.aggressive = False
        #Changes animals behavior to be more friendly towards elves. I need to change this because it will make all animals friendly to everyone if you are an elf.
        #if 'elf' in self.game.player.race:
            #if self.aggression == 'awd':
            #    self.aggression = 'awp'
        #    if self.aggression == 'fwd':
        #        self.aggression = 'fwp'
        if self.aggression in ['fwd', 'fup']:
            self.detect_vector = vec(-1, 0)
        if self.aggression == 'fup':
            self.detect_vector = vec(-1, 0)
        if self.aggression in ['awd', 'fwp', 'awp']:
            self.detect_vector  = vec(1, 0)

    def update(self):
        self.sprite.rotate_to(self.target.pos - self.sprite.pos)
        self.sprite.accelerate()
        self.avoid_mobs()

    def avoid_mobs(self):
        for mob in self.game.mobs_on_screen:
            if mob != self.sprite:
                dist = self.sprite.pos - mob.pos
                if 0 < dist.length() < self.avoid_radius:
                    self.sprite.acc += dist.normalize()
        # Makes it so non aggressive mobs don't cling to you.
        if not self.aggressive:
            dist = self.sprite.pos - self.game.player.pos
            if 0 < dist.length() < self.avoid_radius:
                self.sprite.acc += dist.normalize()

    def seek_random_target(self):
        self.target = choice(list(self.game.random_targets))
        self.detect_radius = self.game.map.height / 2
        temp_dist = self.target.pos - self.pos
        temp_dist = temp_dist.length()
        if temp_dist > self.detect_radius:
            self.target = choice(list(self.game.random_targets))
        if temp_dist < 200:
            self.target = choice(list(self.game.random_targets))

    def seek_mobs(self):
        last_dist = 100000
        player_dist = self.game.player.pos - self.sprite.pos
        player_dist = player_dist.length()

        # Used for setting random NPC targets if the player isn't visible.
        if self.game.player.invisible:
            if self.target == self.game.player:
                self.seek_random_target()

        elif self.game.player.in_vehicle:
            if self.game.player.vehicle.kind_dict == 'airship':
                if not self.flying:
                    self.seek_random_target()
            else:
                if player_dist < self.detect_radius:
                    self.target = self.game.player.vehicle
                else:
                    if self.target == self.game.player.vehicle:
                        self.seek_random_target()
        else:
            if self.target not in self.game.npcs:
                if player_dist < self.detect_radius * 2:
                    self.target = self.game.player
                else:
                    if self.target == self.game.player:
                        self.seek_random_target()

        if self.aggression == 'awd':
            self.offensive = True
            for mob in self.game.moving_targets_on_screen: # Only looks at mobs that are on screen
                if mob != self:
                    if mob.aggression != 'awd' or mob in self.game.npcs_on_screen:
                        dist = self.sprite.pos - mob.pos
                        dist = dist.length()
                        if 0 < dist < self.detect_radius:
                            if last_dist > dist:  # Finds closest NPC
                                if player_dist > dist: # Only targets player if you are closer than the others NPCs
                                    self.target = mob
                                    self.approach_vector = vec(1, 0)
                                    last_dist = dist
                                else:
                                    if self.game.player.invisible:
                                        self.target = mob
                                    else:
                                        self.target = self.game.player

            if self.target == self.game.player or not self.target.living:
                for item in self.game.dropped_items_on_screen:# animals target dead animals
                    if 'dead' in item.name:
                        dist = self.sprite.pos - item.pos
                        dist = dist.length()
                        if 0 < dist < self.detect_radius:
                            if last_dist > dist:  # Finds closest item
                                if player_dist > dist: # Only targets player if you are closer than the others NPCs
                                    self.target = item
                                    self.approach_vector = vec(1, 0)
                                    last_dist = dist

            if not self.target.living: # Kills corps after so many hits.
                if self.target in self.game.animals_on_screen:
                    self.target.kill()
                    self.target = self.game.player
                else:
                    self.eating_corpse += 1
                    if self.eating_corpse > 4:
                        self.target.kill()
                        self.target = self.game.player
                        self.eating_corpse = 0
                        self.sprite.stats['health']= self.sprite.stats['max health'] # heals animal
            else:
                self.eating_coprse = 0

        if self.target not in self.game.random_targets:
            self.detect_radius = self.default_detect_radius




class Animal(Character):
    def __init__(self, game, x=0, y=0, kind='rabbit', colors=None, animal = True):
        super().__init__(game, x, y, kind, colors, animal)

        self.walk_animate_speed = self.default_acceleration * 15
        self.run_animate_speed = self.default_acceleration + 100
        self.rotate_direction = randrange(-1, 1)

        # Animal qualities
        if 'climbing' in self.kind_dict.keys() and self.kind_dict['climbing']:
            self.climbing = True
        if 'mountable' in self.kind_dict.keys():
            self.mountable = self.kind_dict['mountable']
        if self.kind_dict['hit rect'] == SMALL_HIT_RECT:
            if not self.flying:
                self.hideable = True # Used for animals that can hide in long grass

        self.item = self.kind_dict['item'] # dropped item when it dies
        self.item_type = self.kind_dict['item type'] # For adding to inventory

        # Images stuff
        self.walk_image_list = self.game.animal_animations[self.kind]['walk']
        if 'run' in list(self.game.animal_animations[self.kind].keys()):
            self.run_image_list = self.game.animal_animations[self.kind]['run']
        else:
            self.run_image_list = self.walk_image_list
        if 'swim' in list(self.game.animal_animations[self.kind].keys()):
            self.swim_image_list = self.game.animal_animations[self.kind]['swim']
        else:
            self.swim_image_list = self.walk_image_list
        self.old_run_image_list = None
        self.old_walk_image_list = None
        self.selected_image_list = self.walk_image_list
        self.image = self.walk_image_list[1].copy()
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        self.width = self.hit_rect.width
        self.hit_rect.center = self.pos
        self.rect.center = self.pos
        self.talk_rect.center = self.rect.center
        self.light_mask_rect.center = self.rect.center
        self.frame = 0 #used to keep track of what frame the animation is on.

        self.rot_speed = self.orig_rot_speed = 6 * self.default_acceleration / self.width

        set_elevation(self)

    @property
    def in_grass(self):
        return self._in_grass
    @in_grass.setter
    def in_grass(self, value): # This hides small animals when they go into long grass by changing their images to a tiny shadow.
        if value!=self._in_grass:
            if self.hideable:
                if value:
                    self.old_run_image_list = self.run_image_list
                    self.old_walk_image_list = self.walk_image_list
                    self.walk_image_list = self.run_image_list = [self.game.invisible_image, self.game.invisible_image]
                    self.frame = 0
                else:
                    self.run_image_list = self.old_run_image_list
                    self.walk_image_list = self.old_walk_image_list
            self._in_grass = value
    @property
    def swimming(self):
        return self._swimming
    @swimming.setter
    def swimming(self, value):
        if value!=self._swimming:
            if not self.in_vehicle:
                toggle_equip(self, value)
            self._swimming = value
        else:
            pass
    @property
    def climbing(self):
        return self._climbing
    @climbing.setter
    def climbing(self, value):
        if value!=self._climbing:
            if value:
                self.last_climb = pg.time.get_ticks()
                self.pre_jump()
            toggle_equip(self, value)
            self._climbing = value
        else:
            pass

    def death(self, silent = False):
        super().death()
        if self.occupied:
            self.unmount()
        if 'dead' in self.game.animals_dict[self.kind]: # Keeps track of if special NPCs have been killed or not.
            self.game.animals_dict[self.name.lower()]['dead'] = True
        if 'corpse' in self.kind_dict.keys() and self.kind_dict['corpse']:
            self.remove(self.game.mobs)
            self.remove(self.game.animals)
            self.remove(self.game.moving_targets)
            self.add(self.game.corpses)
            self.game.group.change_layer(self, self.game.map.items_layer) # Switches the corpse to items layer
            self.image = pg.transform.rotate(self.game.corpse_images[self.kind_dict['corpse']], self.rot)
            self.rect = self.image.get_rect()
            self.rect.center = self.pos
        else:
            for item in self.inventory: # Empties animal's inventory.
                if 'name' in item:
                    number = 1
                    if 'number' in item:
                        number = item['number']
                    for i in range(0, number):
                        if random() < .5:
                            Dropped_Item(self.game, self.pos, ITEMS[item['name']], self.rot, True)
            Dropped_Item(self.game, self.pos, ITEMS['dead ' + self.kind], self.rot, False, self.image.get_width()) # dropps item based corpse for small animals.
            #if self.kind_dict['name'] == 'sea turtle':
            #    Breakable(self.game, self.pos, self.pos.x - 60, self.pos.y - 60, 120, 120, BREAKABLES['empty turtle shell'], 'empty turtle shell')
            self.kill()

    def make_companion(self):
        super().make_companion(self)
        self.update_collide_list()
        self.target = self.game.player
        self.approach_vector = vec(1, 0)
        self.aggression = 'awp'
        self.default_detect_radius = self.detect_radius = self.game.screen_height
        self.guard = True
        #self.speed = self.walk_speed = 200
        #self.run_speed = 480

    def unfollow(self):
        super().unfollow(self)
        self.default_detect_radius = self.detect_radius = 250
        #self.speed = self.walk_speed = 80
        #self.run_speed = 100

    def animate(self, images):
        self.frame += 1
        if self.frame > len(images) - 1:
            self.frame = 0

    def rotate_image(self, image_list):
        self.image = pg.transform.rotate(image_list[self.frame], self.rot)
        old_center = self.rect.center
        self.rect = self.image.get_rect()
        self.rect.center = self.pos
        self.hit_rect.center = vec(old_center) #+ self.rect_offset.rotate(-self.rot)

    def accelerate(self):
        super().accelerate()
        self.selected_image_list = self.walk_image_list
        animate_speed = self.walk_animate_speed
        if self.running:
            self.selected_image_list = self.run_image_list
            self.acceleration = self.run_acc
            animate_speed = self.run_animate_speed
        elif self.in_shallows:
            self.acceleration = self.shallows_acc
            animate_speed = self.walk_animate_speed - 50
        elif self.in_grass:
            self.acceleration = self.grass_acc
            animate_speed = self.walk_animate_speed - 40
        elif self.climbing:
            self.acceleration = self.climb_acc
            animate_speed = self.walk_animate_speed - 50
        elif self.jumping:
            self.acceleration = self.jump_acc
        elif self.swimming:
            self.selected_image_list = self.swim_image_list
        self.acc = vec(self.acceleration, 0).rotate(-self.rot)
        now = pg.time.get_ticks()
        if now - self.last_move > animate_speed:  # animates animal
            self.animate(self.selected_image_list)
            self.last_move = now
        if self.frame > len(self.selected_image_list) - 1:
            self.frame = 0

    def get_keys(self):
        keys = pg.key.get_pressed()
        if keys[self.game.key_map['sprint']]:
            self.driver.acceleration = self.run_speed / 40
            self.running = True
        else:
            self.driver.acceleration = self.walk_speed / 14
            self.running = False
        if keys[self.game.key_map['dismount']]:
            self.unmount()

    def mount(self, driver):
        if driver == self.game.player:
            self.game.hud_health_stats = self.stats
        self.rot_speed = 60 * self.walk_speed / self.width
        if driver.possessing:
            if driver.possessing.race == 'mech_suit':
                return
        self.game.group.change_layer(self, self.game.mob_layer)
        self.frame = 0
        self.occupied = True
        self.knockback = 0
        self.driver = driver
        self.driver.in_vehicle = True
        self.driver.vehicle = self
        self.driver.human_body.update_animations()
        if self.driver.has_dragon_body:
            self.driver.dragon_body.update_animations()
        self.add(self.game.occupied_vehicles)
        self.add(self.game.all_vehicles)
        self.remove(self.game.mobs)
        if self.kind == 'horse':
            if self.driver == self.game.player:
                if 'horse bridle' in self.game.player.inventory['items']:
                    self.make_companion()
        self.game.beg = perf_counter() # resets the counter so dt doesn't get messed up.

    def unmount(self):
        if self.driver == self.game.player:
            self.game.hud_health_stats = self.driver.stats
        self.rot_speed = self.orig_rot_speed
        self.game.group.change_layer(self, self.original_layer)
        self.occupied = False
        self.knockback = self.kind_dict['knockback']
        self.driver.in_vehicle = False
        self.driver.friction = PLAYER_FRIC
        self.driver.acceleration = PLAYER_ACC
        if self.driver.swimming:
            self.driver.equipped['weapons'] = None
            self.driver.current_weapon = self.driver.last_weapon
            self.driver.equipped['weapons2'] = None
            self.driver.current_weapon2 = self.driver.last_weapon2
        self.driver.vehicle = None
        self.remove(self.game.occupied_vehicles)
        self.remove(self.game.all_vehicles)
        self.add(self.game.mobs)
        self.driver.human_body.update_animations()
        if self.driver.has_dragon_body:
            self.driver.dragon_body.update_animations()
        self.driver.pos = self.driver.pos + (80, 80)
        self.driver = None
        self.frame = 0
        self.game.beg = perf_counter()  # resets dt

    def update_collide_list(self):
        self.collide_list = [self.game.walls_on_screen]

    def update(self):
        if self.living:
            if not self.occupied:
                self.ai.update()
                self.move()
                self.rotate_image(self.selected_image_list)
                #now0 = pg.time.get_ticks()
                #if now0 - self.last_target_seek > 4000:
                #    self.seek_mobs()
                #    self.last_target_seek = now0
                #target_dist = self.target.pos - self.pos

                # This part makes the animal avoid walls
                #if self.climbing:
                #    hits = pg.sprite.spritecollide(self, self.game.walls_on_screen, False)
                #else:
                #    hits = pg.sprite.spritecollide(self, self.game.barriers_on_screen, False)# This part makes the animal avoid walls
                #if hits:
                #    self.hit_wall = True
                #    now = pg.time.get_ticks()
                #    if now - self.last_wall_hit > randrange(300, 1000):
                #        self.animate(self.selected_image_list)
                #        self.last_wall_hit = now
                #        if random() < 0.5:
                #            self.rotate_direction = choice([-1, 0, 1])
                #    self.rot += (3 * (self.walk_speed / self.width) * self.rotate_direction) % 360
                #    self.avoid_mobs()
                #    self.accelerate(self.walk_speed)

                """
                if (target_dist.length_squared() < self.detect_radius**2) and (self.target not in self.game.random_targets):
                    #if random() < 0.002:
                    #    choice(self.game.zombie_moan_sounds).play()
                    if self.spell_caster:
                        direction_vec = self.pos + vec(self.detect_radius, 0).rotate(-self.rot)
                        difx = abs(self.target.pos.x - direction_vec.x)
                        dify = abs(self.target.pos.y - direction_vec.y)
                        if difx < 300:
                            if dify < 300:
                                magic_chance = randrange(0, 10)
                                if magic_chance == 1:
                                    self.equipped['magic'] = choice(self.expanded_inventory['magic'])
                                    self.cast_spell()

                    now = pg.time.get_ticks()
                    if now - self.last_move > self.run_animate_speed: # What animal does when you are close it.
                        self.animate(self.selected_image_list)
                        self.last_move = now
                    elif now - self.last_wall_hit > randrange(3000, 5000):
                        self.last_wall_hit = now
                        self.hit_wall = False
                    if not self.hit_wall:
                        self.rot = target_dist.angle_to(self.approach_vector)
                    self.rotate_image(self.selected_image_list)
                    self.acc = vec(1, 0).rotate(-self.rot)
                    self.avoid_mobs()
                    self.accelerate(self.run_speed)"""
                #self.acc = vec(1, 0).rotate(-self.rot)
                #self.avoid_mobs()
                #self.accelerate(self.walk_speed)

            else: # This is what the animal does if you are riding it
                # Increases animal friction when not accelerating
                if self.driver.swimming:
                    self.swimming = True
                else:
                    self.swimming = False
                if self.driver.is_moving():
                    # Makes the friction greater when the vehicle is sliding in a direction that is not straight forward.
                    angle_difference = abs(fix_angle(self.driver.vel.angle_to(self.driver.direction)))
                    if angle_difference > 350:
                        angle_difference = 0
                    if angle_difference < 0.1:
                        angle_difference = 0
                    self.driver.friction = -(angle_difference / 1000 + .015)
                    # Animates the animal
                    now = pg.time.get_ticks()
                    if self.swimming:
                        animate_speed = self.walk_animate_speed
                        self.selected_image_list = self.swim_image_list
                    elif self.running:
                        animate_speed = self.run_animate_speed
                        self.selected_image_list = self.run_image_list
                    else:
                        animate_speed = self.walk_animate_speed
                        self.selected_image_list = self.walk_image_list

                    if now - self.last_move > walk_animate_speed:  # animates animal
                        self.animate(self.selected_image_list)
                        self.last_move = now
                    if self.frame > len(self.selected_image_list) - 1:
                        self.frame = 0
                else:
                    self.driver.friction = -.28
                self.rot = self.driver.rot
                self.pos = self.driver.pos
                self.rotate_image(self.selected_image_list)
                self.get_keys()  # this needs to be last in this method to avoid executing the rest of the update section if you exit
            if not self.flying:
                collide_with_tile_walls(self)
                collide_with_moving_targets(self)
        set_tile_props(self)

    def check_empty(self): # Gets rid of empty carcases
        if len(self.inventory['items']) == 0 or (self.inventory['items'][0] == None and len(self.inventory['items']) == 1):
            self.kill()

# Used for arrows shown in loaded bows (not ones being shot)
class Arrow(pg.sprite.Sprite):
    def __init__(self, game, mother, weapon):
        self.game = game
        self._layer = self.game.map.bullet_layer
        self.groups = game.all_sprites, game.arrows
        pg.sprite.Sprite.__init__(self, self.groups)
        self.mother = mother
        self.game.group.add(self)
        self.weapon = weapon
        self.image_orig = self.game.bullet_images[self.weapon['bullet_size']]
        self.image = self.image_orig.copy()
        self.rect = self.image.get_rect()
        if self.mother.weapon_hand == 'weapons':
            self.offset = self.mother.body.weapon_pos
        else:
            self.offset = self.mother.body.weapon2_pos
        self.rect.center = self.mother.pos + self.offset.rotate(-self.mother.rot)
        self.mother.arrow = self

    def update(self):
        self.image = pg.transform.rotate(self.image_orig, self.mother.rot)
        self.rect = self.image.get_rect()
        self.rect.center = self.mother.pos + self.offset.rotate(-self.mother.rot)


class Bullet(pg.sprite.Sprite):
    def __init__(self, mother, game, pos, dir, rot, weapon, enemy = False, sky = False):
        self.game = game
        self.sky = sky
        if self.sky:
            self._layer = self.game.map.sky_layer
        else:
            self._layer = self.game.map.bullet_layer
        self.mother = mother
        self.enemy = enemy
        if self.enemy:
            self.groups = game.all_sprites, game.bullets, game.enemy_bullets
        else:
            self.groups = game.all_sprites, game.bullets
        pg.sprite.Sprite.__init__(self, self.groups)
        self.game.group.add(self)
        self.weapon = weapon
        self.target = None
        self.size = self.weapon['bullet_size']
        self.rot = rot
        self.image = pg.transform.rotate(game.bullet_images[self.weapon['bullet_size']], self.rot)
        self.rect = self.image.get_rect()
        self.hit_rect = self.rect
        self.pos = vec(pos)
        self.knockback = self.weapon['knockback']
        self.rect.center = pos
        spread = uniform(-self.weapon['spread'], self.weapon['spread'])
        self.dir = dir.rotate(spread)
        self.vel = self.dir * self.weapon['bullet_speed'] * uniform(0.9, 1.1) + self.mother.vel
        self.lifetime = self.weapon['bullet_lifetime']

        self.spawn_time = pg.time.get_ticks()
        self.damage = self.weapon['damage']
        self.exp_damage = self.damage
        self.exp = False
        self.energy = False
        self.fire = False
        self.shock = False
        self.rob_health = False
        for bullet in EXPLOSIVE_BULLETS:
            if bullet in self.size:
                self.exp = True
                if '10' in bullet:
                    self.exp_damage = self.damage * 3
                else:
                    self.exp_damage = self.damage * 25
        for bullet in ENCHANTED_BULLETS:
            if bullet in self.size:
                self.energy = True
        for bullet in ROB_HEALTH_BULLETS:
            if bullet in self.size:
                self.rob_health = True
        for bullet in FIRE_BULLETS:
            if bullet in self.size:
                self.fire = True
        for bullet in SHOCK_BULLETS:
            if bullet in self.size:
                if '12' not in self.size:
                    self.shock = True


    def update(self):
        self.pos += self.vel * self.game.dt
        self.rect.center = self.pos
        if pg.sprite.spritecollideany(self, self.game.walls_on_screen):
            self.death()
        # Kills bullets of current and previous weapons
        if pg.time.get_ticks() - self.spawn_time > self.lifetime:
            self.death()

    def death(self, target = None):
        if target == None:
            self.target = self
        else:
            self.target = target
        if self.exp:
            if self.fire:
                self.explode('fire')
            elif self.shock:
                self.explode('shock')
            elif self.rob_health:
                if self.target != self:
                    self.mother.add_health(int(self.damage / 2))
                self.explode()
            else:
                self.explode()
        else:
            if self.fire:
                Stationary_Animated(self.game, self.target.pos, 'fire', 1000, True)
            if self.shock:
                Stationary_Animated(self.game, self.target.pos, 'shock', 333)
            if self.rob_health:
                if self.target != self:
                    self.mother.add_health(int(self.damage / 2))
            self.kill()

    def explode(self, after_effect = None):
        pos = self.pos
        Explosion(self.game, self.target, 0.5, self.exp_damage, pos, after_effect, self.sky)
        self.kill()

class MuzzleFlash(pg.sprite.Sprite):
    def __init__(self, game, pos):
        self.game = game
        self._layer = self.game.map.effects_layer
        self.groups = game.all_sprites, game.lights
        pg.sprite.Sprite.__init__(self, self.groups)
        self.game.group.add(self)
        size = randint(10, 25)
        self.image = pg.transform.scale(choice(game.gun_flashes), (size, size))
        self.rect = self.image.get_rect()
        self.pos = pos
        self.rect.center = pos
        self.spawn_time = pg.time.get_ticks()
        self.light_mask = pg.transform.scale(self.game.light_mask_images[0], (75, 75))
        self.light_mask_rect = self.light_mask.get_rect()
        self.light_mask_rect.center = self.rect.center


    def update(self):
        if pg.time.get_ticks() - self.spawn_time > FLASH_DURATION:
            self.kill()

class Dropped_Item(pg.sprite.Sprite):
    def __init__(self, game, pos, item, rot = None, random_spread = False, width = None, gendertag = None):
        self.game = game
        self.brightness = 0
        self._layer = self.game.map.items_layer
        if 'brightness' in item:
            if 'flashlight' not in item:
                self.groups = game.all_sprites, game.dropped_items, game.detectables, game.lights
                self.light = True
                self.brightness = item['brightness']
                self.mask_type = item['light mask']
            else:
                self.groups = game.all_sprites, game.dropped_items, game.detectables
        else:
            self.groups = game.all_sprites, game.dropped_items, game.detectables
        pg.sprite.Sprite.__init__(self, self.groups)
        self.game.group.add(self)
        self.item = item
        self.name = item['name']
        self.rot = rot
        self.dropped_fish = False
        self.lit = False
        self.floats = False
        self.random_spread = random_spread
        self.pos = pos
        self.living = False

        if gendertag == None:
            self.gender = choice(['_M', '_F'])
        else:
            self.gender = gendertag

        filename = correct_filename(self.item)
        try:
            file = filename + '_side'
            self.item_image = self.game.item_images[file]
        except:
            try:
                file = filename + self.gender + '_side'
                self.item_image = self.game.item_images[file]
            except:
                self.item_image = self.game.item_images[filename]

        if 'color' in self.item:
            self.item_image = color_image(self.item_image, self.item['color'])
        if self.rot == None:
            self.rot = randrange(0, 360)
        if width:
            size = width
            spread = int(width/2)
        else:
            spread = 24
            size = ITEM_SIZE
        self.item_image = pg.transform.scale(self.item_image, (size, size))
        self.image = pg.transform.rotate(self.item_image, self.rot)
        self.rect = self.hit_rect = self.image.get_rect()
        if self.random_spread:
            self.pos = self.pos + (randrange(-spread, spread), randrange(-spread, spread))
        self.rect.center = self.hit_rect.center = self.pos
        if self.brightness > 0:
            self.light_mask = pg.transform.scale(self.game.light_mask_images[self.mask_type], (self.brightness, self.brightness))
            self.light_mask = pg.transform.rotate(self.light_mask, self.rot)
            self.light_mask_rect = self.light_mask.get_rect()
            self.light_mask_rect.center = self.rect.center

        count = 0
        for i in FLOAT_LIST:
            if i in self.item:
                count += 1
        if count != 0:
            self.floats = True

        # Controls dropping live animals
        if self.item['name'][:4] == 'live':
            temp_item = self.item['name'].replace('live ', '')
            if 'fish' in temp_item:
                fish = Dropped_Item(self.game, self.pos, ITEMS['dead ' + temp_item])
                fish.dropped_fish = True
            else:
                Animal(self.game, self.pos.x, self.pos.y, temp_item)
            self.kill()

        # Dropping items in grass
        #hits = pg.sprite.spritecollide(self, self.game.long_grass, False)
        #if hits:
        #    self.image = self.game.invisible_image
        #    self.rect = self.hit_rect = self.image.get_rect()
        #    self.rect.center = self.pos

    def update(self):
        pass

class LightSource(pg.sprite.Sprite):
    def __init__(self, game, x, y, w, h, kind = 1, rot = 0):
        self.groups = game.lights, game.all_static_sprites
        pg.sprite.Sprite.__init__(self, self.groups)
        self.game = game
        self.kind = kind
        self.rot = rot
        self.rect = pg.Rect(x, y, w, h)
        self.hit_rect = self.rect
        self.x = x
        self.y = y
        self.rect.x = x
        self.rect.y = y
        self.light_mask = pg.transform.scale(self.game.light_mask_images[self.kind], (int(w * 3.5), int(h * 3.5)))
        if self.rot != 0:
            self.light_mask = pg.transform.rotate(self.light_mask, self.rot)
        self.light_mask_rect = self.light_mask.get_rect()
        self.light_mask_rect.center = self.rect.center


class Stationary_Animated(pg.sprite.Sprite): # Used for fires and other stationary animated sprites
    def __init__(self, game, obj_center, kind, lifetime = None, offset = False, sky = False):
        self.game = game
        self.sky = sky
        if self.sky:
            self._layer = self.game.map.sky_layer
        else:
            self._layer = self.game.map.bullet_layer
        self.center = vec(obj_center)
        self.kind = kind
        self.offset = offset
        if self.kind == 'fire':
            self.image_list = self.game.fire_images
            self.groups = game.all_sprites, game.fires, game.lights
            self.damage = 1
            self.animate_speed = 50
            self.light_radius = FIRE_LIGHT_RADIUS
            if not self.offset:
                self.center.y -= 20
                self.center.x -= 4
            else:
                self.center.y += 20
                self.center.x += 10
        elif self.kind == 'shock':
            self.light_radius = (75, 75)
            self.image_list = self.game.shock_images
            self.groups = game.all_sprites, game.fires, game.lights #game.shocks
            self.damage = 1
            self.animate_speed = 10
        else:
            self.light_radius = LIGHT_RADIUS
            self.groups = game.all_sprites
            self.damage = 0
        pg.sprite.Sprite.__init__(self, self.groups)
        self.game.group.add(self)
        self.image = self.image_list[1].copy()
        self.rect = self.image.get_rect()
        self.rect.center = self.center
        self.hit_rect = self.rect
        self.hit_rect.center = self.rect.center
        self.light_mask = pg.transform.scale(self.game.light_mask_images[2], self.light_radius)
        self.light_mask_rect = self.light_mask.get_rect()
        self.light_mask_rect.center = self.rect.center
        self.frame = 0
        self.last_move = 0
        self.knockback = 0
        self.spawn_time = pg.time.get_ticks()
        self.lifetime = lifetime
        self.last_sound = 0
        self.pos = self.center

    def update(self):
        now = pg.time.get_ticks()
        if now - self.last_move > self.animate_speed:
            self.animate(self.image_list)
            self.last_move = now
            self.image = self.image_list[self.frame]
            if not self.offset:
                self.rect.center = self.center
                self.light_mask_rect.center = self.rect.center
            else:
                self.rect.center = self.center + vec(-8, -40)
                self.light_mask_rect.center = self.rect.center


        if self.lifetime:
            if now - self.spawn_time > self.lifetime:
                self.kill()

    def animate(self, images):
        self.frame += 1
        if self.frame > len(images) - 1:
            self.frame = 0

class Entryway(pg.sprite.Sprite):
    def __init__(self, game, x, y, orientation = 'L', kind = 'wood', name = 'generic', locked = False):
        self.game = game
        self._layer = self.game.map.items_layer
        self.groups = game.all_sprites, game.entryways
        pg.sprite.Sprite.__init__(self, self.groups)
        self.game.group.add(self)
        self.name = name
        self.kind = kind
        self.orientation = orientation
        self.locked = locked
        self.combo = randrange(10, 350)
        self.difficulty = randrange(0, 30)
        self.length = 88
        self.stats = {'health': DOOR_STYLES[self.kind]['hp'], 'max health': DOOR_STYLES[self.kind]['hp']}
        self.protected = False
        self.orig_rot = 0
        temp_img = self.game.door_images[DOOR_STYLES[self.kind]['image']]
        if self.orientation in 'L':
            self.image_orig = temp_img
            self.image = self.image_orig.copy()
            self.rect = self.image.get_rect()
            self.rect.x = x - 19
            self.rect.y = y
            self.wall = Obstacle(self.game, self.rect.x, self.rect.y, 20, self.length)
            self.wall.add(self.game.door_walls)
        elif self.orientation == 'R':
            self.image_orig = pg.transform.rotate(temp_img, 180)
            self.image = self.image_orig.copy()
            self.rect = self.image.get_rect()
            self.rect.x = x - 10
            self.rect.y = y - self.length
            self.wall = Obstacle(self.game, self.rect.x, self.rect.y + self.length, 20, self.length)
            self.wall.add(self.game.door_walls)
            self.orig_rot = 180
        elif self.orientation == 'D':
            self.image_orig = pg.transform.rotate(temp_img, 90)
            self.image = self.image_orig.copy()
            self.rect = self.image.get_rect()
            self.rect.x = x
            self.rect.y = y - 10
            self.wall = Obstacle(self.game, self.rect.x, self.rect.y, self.length, 20)
            self.wall.add(self.game.door_walls)
            self.orig_rot = 90
        elif self.orientation == 'U':
            self.image_orig = pg.transform.rotate(temp_img, -90)
            self.image = self.image_orig.copy()
            self.rect = self.image.get_rect()
            self.rect.x = x - self.length
            self.rect.y = y - 19
            self.wall = Obstacle(self.game, self.rect.x + self.length, self.rect.y, self.length, 20)
            self.wall.add(self.game.door_walls)
            self.orig_rot = -90
        self.last_move = 0
        self.rot = 0
        self.animate_speed = 10
        self.rotate_amount = 5
        self.open = False
        self.close = False
        self.opened = False
        self.hit_rect = self.wall.rect
        self.hit_rect.center = self.wall.rect.center
        self.sound_played = False
        self.inventory = {'locked': self.locked, 'combo': self.combo,'difficulty': self.difficulty}
        self.last_hit = 0
        self.living = True
        self.frame = 0
        self.pos = vec(self.hit_rect.centerx, self.hit_rect.centery)
        self.vel = vec(0, 0)
        self.acc = vec(0, 0)

    def update(self):
        if self.open:
            now = pg.time.get_ticks()
            if now - self.last_move > self.animate_speed:
                self.animate_open()
                self.rotate_image()
                self.last_move = now

        if self.close:
            now = pg.time.get_ticks()
            if now - self.last_move > self.animate_speed:
                self.animate_close()
                self.rotate_image()
                self.last_move = now

        if not self.living:
            now = pg.time.get_ticks()
            if now - self.last_move > self.animate_speed:
                self.animate_death()
                self.last_move = now


    def rotate_image(self):
        new_image = pg.transform.rotate(self.image_orig, self.rot)
        old_center = self.rect.center
        self.image = new_image
        self.rect = self.image.get_rect()
        self.rect.center = old_center

    def animate_open(self):
        if not self.sound_played:
            play_relative_volume(self,'door open')
            self.sound_played = True
        self.rot += self.rotate_amount
        if self.rot > 90:
            self.rot = 90
            self.open = False
            self.opened = True
            self.wall.kill()
            if self.orientation == 'L':
                self.wall = Obstacle(self.game, self.rect.x, self.rect.y, self.length, 20)
            elif self.orientation == 'D':
                self.wall = Obstacle(self.game, self.rect.x, self.rect.y + self.length, 20, self.length)
            elif self.orientation == 'R':
                self.wall = Obstacle(self.game, self.rect.x + self.length, self.rect.y, self.length, 20)
            elif self.orientation == 'U':
                self.wall = Obstacle(self.game, self.rect.x, self.rect.y, 20, self.length)
            self.hit_rect = self.wall.rect
            self.hit_rect.center = self.wall.rect.center
            self.sound_played = False

    def animate_close(self):
        self.rot -= self.rotate_amount
        if self.rot < 0:
            self.rot = 0
            self.close = False
            self.opened = False
            self.wall.kill()
            if self.orientation == 'L':
                self.wall = Obstacle(self.game, self.rect.x, self.rect.y, 20, self.length)
                self.wall.add(self.game.door_walls)
            elif self.orientation == 'D':
                self.wall = Obstacle(self.game, self.rect.x, self.rect.y, self.length, 20)
                self.wall.add(self.game.door_walls)
            elif self.orientation == 'R':
                self.wall = Obstacle(self.game, self.rect.x, self.rect.y + self.length, 20, self.length)
                self.wall.add(self.game.door_walls)
            elif self.orientation == 'U':
                self.wall = Obstacle(self.game, self.rect.x + self.length, self.rect.y, self.length, 20)
                self.wall.add(self.game.door_walls)
            self.hit_rect = self.wall.rect
            self.hit_rect.center = self.wall.rect.center
            play_relative_volume(self, 'door close')

    def animate_death(self):
        if len(self.game.door_break_images) > self.frame:
            temp_image = self.game.door_break_images[self.frame]
            self.frame += 1
            new_image = pg.transform.rotate(temp_image, self.rot + self.orig_rot)
            old_center = self.rect.center
            self.image = new_image
            self.rect = self.image.get_rect()
            self.rect.center = old_center
        else:
            self.wall.kill()
            self.kill()

    def gets_hit(self, damage, knockback = 0, rot = 0, dam_rate = DAMAGE_RATE):
        now = pg.time.get_ticks()
        if now - self.last_hit > dam_rate:
            self.last_hit = now
            self.stats['health'] -= damage
        if self.stats['health'] <= 0:
            if self.living:
                play_relative_volume(self, 'rocks')
                self.animate_speed = 50
            self.living = False

class ElectricDoor(pg.sprite.Sprite): # Used for fires and other stationary animated sprites
    def __init__(self, game, x, y, w, h, locked = False):
        self.game = game
        self._layer = self.game.map.bullet_layer
        self.image_list = self.game.electric_door_images
        self.groups = game.all_sprites, game.entryways, game.lights, game.electric_doors
        pg.sprite.Sprite.__init__(self, self.groups)
        self.animate_speed = 50
        self.game.group.add(self)
        if h > w:
            self.orientation = 'v'
            self.image = pg.transform.rotate(self.image_list[0], 90)
        else:
            self.orientation = 'h'
            self.image = self.image_list[0]
        self.rect = self.image.get_rect()
        self.center = (x + w/2, y + h/2)
        self.hit_rect = self.rect
        self.hit_rect.center = self.rect.center = self.center
        self.w = w
        self.h = h
        self.light_mask = pg.transform.scale(self.game.light_mask_images[4], (int(self.w + 90), int(self.h + 90)))
        self.light_mask_rect = self.light_mask.get_rect()
        self.light_mask_rect.center = self.rect.center
        self.frame = 0
        self.last_move = 0
        self.locked = locked
        self.combo = randrange(10, 350)
        self.difficulty = randrange(0, 30)
        self.length = 88
        self.stats = {'health': 100, 'max health': 100}
        self.protected = False
        self.open = False
        self.close = False
        self.opened = False
        self.inventory = {'locked': self.locked, 'combo': self.combo,'difficulty': self.difficulty}
        self.last_hit = 0
        self.living = True
        self.pos = vec(self.rect.centerx, self.rect.centery)
        self.vel = vec(0, 0)
        self.acc = vec(0, 0)
        self.damage = 50

    def update(self):
        now = pg.time.get_ticks()
        if now - self.last_move > self.animate_speed:
            self.animate()
            self.last_move = now
            if self.orientation == 'v':
                self.image = pg.transform.rotate(self.image_list[self.frame], 90)
                self.rect = self.image.get_rect()
            else:
                self.image = self.image_list[self.frame]
            self.rect.center = self.center
            self.light_mask_rect.center = self.rect.center

        if self.open:
            now = pg.time.get_ticks()
            if now - self.last_move > self.animate_speed:
                self.animate_open()
                self.last_move = now

        if self.close:
            now = pg.time.get_ticks()
            if now - self.last_move > self.animate_speed:
                self.animate_close()
                self.last_move = now

    def animate(self):
        self.frame += 1
        if self.frame > len(self.image_list) - 1:
            self.frame = 0

    def animate_open(self):
        self.open = False
        self.opened = True

    def animate_close(self):
        self.close = False
        self.opened = False
        #self.game.effects_sounds['door close'].play()

    def gets_hit(self, damage, knockback = 0, rot = 0, dam_rate = DAMAGE_RATE, player = None):
        if not player:
            return
        elif 'plasma' in player.equipped[player.weapon_hand]:  #makes it so plasma weapons can kill electric doors.
            now = pg.time.get_ticks()
            if now - self.last_hit > dam_rate:
                self.last_hit = now
                self.stats['health'] -= damage
                play_relative_volume(self, self.game.weapon_hit_sounds['plasma'][0], False)
            if self.stats['health'] <= 0:
                self.kill()


class Explosion(pg.sprite.Sprite):
    def __init__(self, game, target = None, knockback = 0, damage = 0, center = None, after_effect = None, sky = False):
        self.game = game
        self.sky = sky
        if self.sky:
            self._layer = self.game.map.sky_layer
        else:
            self._layer = self.game.map.bullet_layer
        self.groups = game.all_sprites, game.explosions, game.lights
        pg.sprite.Sprite.__init__(self, self.groups)
        self.game.group.add(self)
        self.target = target
        self.center = center
        self.after_effect = after_effect
        self.damage = damage
        # Scales explosion's size based on damage
        self.scale = int(5 * damage)
        if self.scale > 600:
            self.scale = 600
        self.image_list = []
        if damage == 0:
            self.scale = 200
            self.image_list = self.game.explosion_images
        else:
            for image in self.game.explosion_images:
                new_img = pg.transform.scale(image, (self.scale, self.scale))
                self.image_list.append(new_img)
        self.image = self.image_list[0]
        self.rect = self.image.get_rect()
        self.hit_rect = pg.Rect(0, 0, int(self.scale/8), int(self.scale/8))
        self.light_mask = pg.transform.scale(self.game.light_mask_images[2], (self.scale + 100, self.scale + 100))
        self.light_mask_rect = self.light_mask.get_rect()
        self.light_mask_rect.center = self.rect.center
        if self.target == None:
            self.rect.center = self.center
            if self.center == None:
                self.center = (0, 0)
        else:
            self.rect.center = self.target.pos
        self.pos = vec(self.rect.centerx, self.rect.centery)
        self.hit_rect.center = self.rect.center
        self.frame = 0
        self.last_update = pg.time.get_ticks()
        self.frame_rate = 40
        self.knockback = knockback

    def update(self):
        now = pg.time.get_ticks()
        if now -self.last_update > self.frame_rate:
            self.last_update = now
            self.frame += 1
            if self.frame == 1:
                play_relative_volume(self, 'fire blast')
            if self.frame == len(self.image_list):
                if self.target == None:
                    if self.after_effect == 'fire':
                        Stationary_Animated(self.game, self.rect.center, 'fire', 1000, True, self.sky)
                    elif self.after_effect == 'shock':
                        Stationary_Animated(self.game, self.rect.center, 'shock', 333, False, self.sky)
                else:
                    if self.after_effect == 'fire':
                        Stationary_Animated(self.game, self.target.pos, 'fire', 1000, True, self.sky)
                    elif self.after_effect == 'shock':
                        Stationary_Animated(self.game, self.target.pos, 'shock', 333, False, self.sky)
                self.kill()
            else:
                center = self.rect.center
                self.image = self.image_list[self.frame]
                self.rect = self.image.get_rect()
                if self.target == None:
                    self.rect.center = self.center
                    self.hit_rect.center = self.rect.center
                    self.light_mask_rect.center = self.rect.center
                else:
                    self.rect.center = self.target.pos
                    self.hit_rect.center = self.rect.center
                    self.light_mask_rect.center = self.rect.center
        self.pos = vec(self.rect.centerx, self.rect.centery)

class Fireball(pg.sprite.Sprite):
    def __init__(self, mother, game, pos, rot, damage, knockback = 2, lifetime = 1000, speed = 100, source_vel = 0, after_effect = None, enemy = False, sky = False):
        self.game = game
        self.sky = sky
        if self.sky:
            self._layer = self.game.map.sky_layer
        else:
            self._layer = self.game.map.mob_layer
        self.mother = mother
        self.enemy = enemy
        if self.enemy:
            self.groups = game.all_sprites, game.fireballs, game.enemy_fireballs, game.lights
        else:
            self.groups = game.all_sprites, game.fireballs, game.lights
        pg.sprite.Sprite.__init__(self, self.groups)
        self.game.group.add(self)
        self.rot = rot
        self.image = pg.transform.rotate(self.game.fireball_images[0], self.rot + 90)
        self.rect = self.image.get_rect()
        self.rect.center = pos
        self.hit_rect = FIREBALL_HIT_RECT.copy()
        self.offset = vec(22, 0).rotate(-self.rot)
        self.hit_rect.center = vec(pos) + self.offset # A separate hitbox is used bexause the fireball is offset from the center of the image
        self.light_mask = pg.transform.scale(self.game.light_mask_images[1], FIREBALL_LIGHT_RADIUS)
        self.light_mask_rect = self.light_mask.get_rect()
        self.light_mask_rect.center = self.hit_rect.center
        self.frame = 0
        self.last_update = pg.time.get_ticks()
        self.spawn_time = pg.time.get_ticks()
        self.frame_rate = 40
        self.damage = damage
        self.after_effect = after_effect
        self.knockback = knockback
        self.pos = vec(pos)
        self.vel = vec(1, 0).rotate(-self.rot) * speed + source_vel
        self.lifetime = lifetime

    def animate(self):
        self.frame += 1
        if self.frame == 1:
            play_relative_volume(self, 'fire blast')
        if self.frame == len(self.game.fireball_images):
            self.frame = 0
        self.image = pg.transform.rotate(self.game.fireball_images[self.frame], self.rot + 90)

    def update(self):
        self.pos += self.vel * self.game.dt
        self.rect.center = self.pos
        now = pg.time.get_ticks()
        if now -self.last_update > self.frame_rate:
            self.last_update = now
            self.animate()
        self.rect = self.image.get_rect()
        self.rect.center = self.pos
        self.hit_rect.center = self.pos + self.offset
        self.light_mask_rect.center = self.hit_rect.center

        if pg.sprite.spritecollideany(self, self.game.walls_on_screen, fire_collide):
            self.explode()
        # Kills bullets of current and previous weapons
        if pg.time.get_ticks() - self.spawn_time > self.lifetime:
            self.explode()

    def explode(self, target = None):
        if target == None:
            pos = self.pos + self.offset
        else:
            pos = target.pos
        Explosion(self.game, target, 0.5, self.damage, pos, self.after_effect, self.sky)
        self.kill()

class FirePot(pg.sprite.Sprite):
    def __init__(self, game, center, number, elev = 2):
        self.groups = game.elevations, game.all_sprites, game.firepots
        pg.sprite.Sprite.__init__(self, self.groups)
        self.game = game
        self.game.group.add(self)
        self.image = self.game.body_surface.copy()
        self.rect = pg.Rect(0, 0, 64, 64)
        self.hit_rect = self.rect
        self.rect.center = center
        self.center = center
        self.number = number
        self.hit = False
        self.lit = False
        self.lit_time = 0
        self.life_time = 8000
        self.elevation = elev
        self.orient = choice(['h', 'v'])

    def update(self):
        now = pg.time.get_ticks()
        if self.hit:
            self.hit = False
            if not self.lit:
                Stationary_Animated(self.game, self.center, 'fire', self.life_time)
                self.lit = True
                self.lit_time = now
                self.center = vec(self.rect.center)
                self.game.portal_combo += self.number
        if now - self.lit_time > self.life_time:
            self.lit = False
            self.game.portal_combo = self.game.portal_combo.replace(self.number, '')


class Spell_Animation(pg.sprite.Sprite):
    def __init__(self, game, kind, pos, rot, source_vel = None, damage = 0, knockback = 0, lifetime = 1000, speed = 0, after_effect = None, loop = False):
        self.game = game
        self._layer = self.game.map.effects_layer
        self.groups = game.all_sprites
        pg.sprite.Sprite.__init__(self, self.groups)
        self.game.group.add(self)
        self.rot = rot
        self.kind = kind
        self.loop = loop
        if source_vel == None:
            source_vel = vec(0, 0)
        self.image_list = self.game.magic_animation_images[self.kind]
        self.image = self.image_list[0]
        self.rect = self.image.get_rect()
        self.rect.center = pos
        self.hit_rect = self.rect
        self.hit_rect.center = self.rect.center
        self.frame = 0
        self.last_update = pg.time.get_ticks()
        self.spawn_time = pg.time.get_ticks()
        self.frame_rate = 40
        self.damage = damage
        self.after_effect = after_effect
        self.knockback = knockback
        self.pos = vec(pos)
        self.vel = vec(1, 0).rotate(-self.rot) * speed + source_vel
        self.lifetime = lifetime

    def animate(self):
        self.frame += 1
        if self.frame == len(self.image_list):
            self.frame = 0
            if not self.loop:
                self.explode()
        self.image = self.image_list[self.frame]

    def update(self):
        self.pos += self.vel * self.game.dt
        self.rect.center = self.pos
        now = pg.time.get_ticks()
        if now -self.last_update > self.frame_rate:
            self.last_update = now
            self.animate()
        self.rect = self.image.get_rect()
        self.rect.center = self.pos
        self.hit_rect.center = self.pos

        # Kills bullets of current and previous weapons
        if pg.time.get_ticks() - self.spawn_time > self.lifetime:
            self.explode()

    def explode(self):
        pos = self.pos
        #Explosion(self.game, None, 0.5, self.damage, pos, self.after_effect)
        self.kill()



class Portal(pg.sprite.Sprite):
    def __init__(self, game, obj_center, coordinate, location):
        self.game = game
        self._layer = self.game.map.effects_layer
        self.coordinate = coordinate
        self.location = location
        self.center = obj_center
        self.groups = game.all_sprites, game.portals
        pg.sprite.Sprite.__init__(self, self.groups)
        self.game.group.add(self)
        self.image_list = self.game.portal_images
        self.image = self.image_list[1].copy()
        self.rect = self.image.get_rect()
        self.rect.center = self.center
        self.frame = 0
        self.animate_speed = 50
        self.last_move = 0
        self.spawn_time = pg.time.get_ticks()
        self.lifetime = 80000
        self.rot = 0

    def update(self):
        now = pg.time.get_ticks()
        if now - self.last_move > self.animate_speed:  # What animal does when you are close it.
            self.animate(self.image_list)
            self.last_move = now
            new_image = pg.transform.rotate(self.game.portal_images[self.frame], self.rot)
            old_center = self.rect.center
            self.image = new_image
            self.rect = self.image.get_rect()
            self.rect.center = old_center

        if self.lifetime:
            if now - self.spawn_time > self.lifetime:
                self.kill()

    def animate(self, images):
        self.frame += 1
        self.rot = (self.rot + 150 * self.game.dt) % 360
        if self.frame > len(images) - 1:
            self.frame = 0

class Falling_Tree(pg.sprite.Sprite): # animation of trees falling when you chop them down.
    def __init__(self, sprite, x, y, xi, xf, yi, yf, name, size, rot = 0):
        self.sprite = sprite
        self.game = sprite.game
        self._layer = self.game.map.trees_layer
        self.name = name
        self.size = size
        self.x = x
        self.y = y
        self.xi = xi
        self.xf = xf
        self.yf = yf
        self.yi = yi
        self.image_list = self.game.tree_images[self.size + ' ' + self.name]
        self.groups = self.game.all_sprites
        pg.sprite.Sprite.__init__(self, self.groups)
        self.game.group.add(self)
        self.rot = rot
        if self.rot:
            self.image = pg.transform.rotate(self.image_list[0].copy(), self.rot)
        else:
            self.image = self.image_list[0].copy()
        self.center = (x * self.game.map.tile_size + self.game.map.tile_size/2, y * self.game.map.tile_size + self.game.map.tile_size/2)
        self.rect = self.image.get_rect()
        self.rect.center = self.center
        # Animation vars
        self.animate_speed = 70
        self.frame = 0
        self.last_move = 0

    def update(self):
        now = pg.time.get_ticks()
        if now - self.last_move > self.animate_speed:
            self.animate(self.image_list)
            self.last_move = now
            if self.rot:
                self.image = pg.transform.rotate(self.image_list[self.frame], self.rot)
            else:
                self.image = self.image_list[self.frame]
            self.rect.center = self.center

    def animate(self, images):
        self.frame += 1
        if self.frame >= len(images) - 1:
            self.remove_tree()

    def remove_tree(self):
        for j in range(self.yi, self.yf + 1):
            for i in range(self.xi, self.xf + 1):
                if randrange(0, 10) < 4:
                    if (i != self.x) and (j != self.y): # Makes sure it doesn't replace tree trunks.
                        if self.name == 'palm tree':
                            kind = choice(['logs', 'logs', 'logs', 'palm branches'])
                        else:
                            kind = choice(['logs', 'logs', 'branches'])
                        self.game.map.tmxdata.layers[self.game.map.river_layer].data[j][i] = self.game.map.gid_with_property('plant', kind)
                self.game.map.update_tile_props(i, j)  # Updates properties for tiles that have changed.
        self.game.map.redraw()
        set_tile_props(self.sprite)
        self.kill()

"""
class Breakable(pg.sprite.Sprite): # Used for breakable things
    def __init__(self, game, obj_center, w, h, name, fixed_rot = None, size = None):
        self.game = game
        under = False
        self._layer = self.game.map.items_layer
        self.w = wmap
        self.h = h
        self.center = obj_center
        x = int(self.center.x - (w/2))
        y = int(self.center.y - (h/2))
        self.size = size
        self.name = name
        self.kind =  BREAKABLES[self.name]
        self.image_list = self.game.breakable_images[self.name]
        self.scale_factor = 1

        self.groups = game.all_sprites, game.breakable
        pg.sprite.Sprite.__init__(self, self.groups)
        self.game.group.add(self)
        # Image vars
        if fixed_rot == None:
            self.rot = randrange(0, 360)
        else:
            self.rot = fixed_rot
        self.image = pg.transform.rotate(self.image_list[0].copy(), self.rot)
        self.rect = self.image.get_rect()
        self.rect.center = self.center
        self.trunk = Obstacle(self.game, x, y, w, h)
        self.hit_rect = self.trunk.rect
        self.hit_rect.center = self.trunk.rect.center
        # Animation vars
        self.animate_speed = self.kind['animate speed']
        self.frame = 0
        self.last_hit = 0
        self.last_move = 0
        self.dead = False
        self.hit = False
        self.hits = 0
        self.right_hits = 0
        self.hit_weapon = None
        self.hit_sound = self.game.effects_sounds[self.kind['hit sound']]
        self.right_hit_sound = self.game.effects_sounds[self.kind['right weapon hit sound']]
        self.break_sound = self.game.effects_sounds[self.kind['break sound']]
        self.protected = self.kind['protected']
        self.damage = self.kind['damage']
        self.knockback = self.kind['knockback']
        self.hp = self.kind['health']
        self.items = self.kind['items']
        self.rare_items = self.kind['rare items']
        self.weapon_required = self.kind['weapon required']
        self.break_type = self.kind['break type']
        self.wobble = self.kind['wobble']
        self.min_drop = 0
        if 'min drop' in self.kind:
            self.min_drop = self.kind['min drop']
        self.random_drop_number = self.kind['random drop number']
        self.rect.center = self.trunk.rect.center

    def update(self):
        if self.hit and not self.dead:
            now = pg.time.get_ticks()
            if now - self.last_move > 80:
                self.hit = False
                if self.wobble: # Used for objects that rustle like bushes
                    self.animate_hit()
                    self.last_move = now
                    new_image = pg.transform.rotate(self.image_list[0], self.rot - randrange(-20, 20))
                    old_center = self.rect.center
                    self.image = new_image
                    self.rect = self.image.get_rect()
                    self.rect.center = self.trunk.rect.center = self.hit_rect.center = old_center
            if self.break_type == 'gradual':
                if self.hit_weapon in self.weapon_required:
                    self.frame = self.right_hits
                    if self.frame > len(self.image_list) - 2:
                        self.frame = 0
                    self.last_move = now
                    self.image = pg.transform.rotate(self.image_list[self.frame], self.rot)
                    self.rect.center = self.trunk.rect.center = self.hit_rect.center = self.center

        elif self.dead:
            now = pg.time.get_ticks()
            if now - self.last_move > self.animate_speed:
                self.animate_death(self.image_list)
                self.last_move = now
                self.image = pg.transform.rotate(self.image_list[self.frame], self.rot)
                self.rect.center = self.trunk.rect.center = self.hit_rect.center = self.center
        else:
            pass

    def animate_death(self, images):
        self.frame += 1
        if self.frame > len(images) - 2:
            self.remove_breakable()

    def animate_hit(self):
        self.frame += 1
        if self.frame > 1:
            self.frame = 0
            self.image = pg.transform.rotate(self.image_list[0], self.rot)
            self.rect.center = self.trunk.rect.center = self.hit_rect.center = self.center

    def gets_hit(self, weapon_type, knockback = 0, rot = 0, dam_rate = DAMAGE_RATE):
        now = pg.time.get_ticks()
        if now - self.last_hit > dam_rate * 10:
            if not self.hit:
                if self.hp > 0:
                    if weapon_type in self.weapon_required:
                        play_relative_volume(self, self.right_hit_sound, False)
                    else:
                        play_relative_volume(self, self.hit_sound, False)
                else:
                    play_relative_volume(self, self.break_sound, False)
            self.hit = True
            self.hit_weapon = weapon_type
            self.last_hit = now
            self.hits += 1
            if weapon_type in self.weapon_required:
                self.hp -= 1
                self.right_hits += 1
            elif weapon_type == 'explosion':
                self.hp -= 1
                self.right_hits += 1
            elif weapon_type == 'tank':
                if ('block' not in self.name) and ('vein' not in self.name):
                    self.hp -= 1
                    self.right_hits += 1
            if self.hp < 1:
                self.dead = True

    def remove_breakable(self):
        random_value = randrange(0, 100)  # random number in range [0.0,1.0)
        for thing in self.items:
            if self.random_drop_number:
                drop_number = randrange(self.min_drop, self.items[thing])
            else:
                drop_number = self.items[thing]
            for i in range(0, drop_number):
                if thing in ANIMALS:
                    Animal(self.game, self.center.x, self.center.y, thing)
                #else:
                #    for kind in ITEM_TYPE_LIST:
                #        if thing in eval(kind.upper()):
                #            rand_rot = randrange(0, 360)
                #            Dropped_Item(self.game, self.center, kind, thing, rand_rot, True)

        if None not in self.rare_items:
            if random_value < 5: # Chance of getting a rare item
                random_item = choice(self.rare_items)
                if random_item in ANIMALS:
                    Animal(self.game, self.center.x, self.center.y, random_item)
                else:
                    Dropped_Item(self.game, self.center, 'items', random_item)
        self.trunk.kill()
        self.kill()
"""

# The rest of these sprites are static sprites that are never updated: water, walls, etc.

class Obstacle(pg.sprite.Sprite):
    def __init__(self, game, x, y, w, h):
        self.groups = game.obstacles, game.walls, game.all_static_sprites, game.barriers
        pg.sprite.Sprite.__init__(self, self.groups)
        self.game = game
        self.rect = pg.Rect(x, y, w, h)
        self.hit_rect = self.rect
        self.x = x
        self.y = y
        self.rect.x = x
        self.rect.y = y
        if self.rect.width > self.rect.height:
            self.orient = 'h'
        else:
            self.orient = 'v'

class Charger(pg.sprite.Sprite):
    def __init__(self, game, x, y, w, h, amount = 4, rate = 2000):
        self.groups = game.chargers, game.all_static_sprites
        pg.sprite.Sprite.__init__(self, self.groups)
        self.game = game
        self.rect = pg.Rect(x, y, w, h)
        self.hit_rect = self.rect
        self.pos = vec(self.rect.center)
        self.x = x
        self.y = y
        self.rect.x = x
        self.rect.y = y
        self.energy = 1000
        self.last_charge = 0
        self.rate = rate
        self.amount = amount

    def charge(self, hit):
        player_dist = self.game.player.pos - self.pos
        player_dist = player_dist.length()
        now = pg.time.get_ticks()
        if now - self.last_charge > self.rate:
            self.last_charge = now
            if hit.possessing:
                if hit.possessing.race == 'mech_suit':
                    hit.possessing.add_health(self.amount)
            else:
                hit.add_health(self.amount)
                try:
                    hit.add_magica(self.amount)
                    hit.add_stamina(self.amount)
                except:
                    pass
            play_relative_volume(self, 'charge')

class Inside(pg.sprite.Sprite):
    def __init__(self, game, x, y, w, h):
        self.groups = game.inside, game.all_static_sprites
        pg.sprite.Sprite.__init__(self, self.groups)
        self.game = game
        self.rect = pg.Rect(x, y, w, h)
        self.hit_rect = self.rect
        self.x = x
        self.y = y
        self.rect.x = x
        self.rect.y = y

class NoSpawn(pg.sprite.Sprite):
    def __init__(self, game, x, y, w, h):
        self.groups = game.nospawn, game.all_static_sprites
        pg.sprite.Sprite.__init__(self, self.groups)
        self.game = game
        self.rect = pg.Rect(x, y, w, h)
        self.hit_rect = self.rect
        self.x = x
        self.y = y
        self.rect.x = x
        self.rect.y = y

class Elevation(pg.sprite.Sprite):
    def __init__(self, game, x, y, w, h, elev, climb = False, kind = None):
        if climb:
            self.groups = game.elevations, game.all_static_sprites, game.climbs, game.barriers
        elif kind:
            self.groups = game.elevations, game.all_static_sprites, game.climbables_and_jumpables, game.barriers
        else:
            self.groups = game.elevations, game.all_static_sprites, game.barriers
        pg.sprite.Sprite.__init__(self, self.groups)
        self.game = game
        self.rect = pg.Rect(x, y, w, h)
        self.hit_rect = self.rect
        self.x = x
        self.y = y
        self.rect.x = x
        self.rect.y = y
        self.elevation = elev
        self.climb = climb
        if kind == 'jumpable':
            set_elevation(self)
            self.elevation += 2
        if kind == 'climbable':
            set_elevation(self)
            self.elevation += 3
        if self.rect.width > self.rect.height:
            self.orient = 'h'
        else:
            self.orient = 'v'

class Water(pg.sprite.Sprite):
    def __init__(self, game, x, y, w, h):
        self.groups = game.water, game.obstacles, game.all_static_sprites
        pg.sprite.Sprite.__init__(self, self.groups)
        self.game = game
        self.rect = pg.Rect(x, y, w, h)
        self.hit_rect = self.rect
        self.x = x
        self.y = y
        self.rect.x = x
        self.rect.y = y

class Shallows(pg.sprite.Sprite):
    def __init__(self, game, x, y, w, h):
        self.groups = game.shallows, game.obstacles, game.all_static_sprites
        pg.sprite.Sprite.__init__(self, self.groups)
        self.game = game
        self.rect = pg.Rect(x, y, w, h)
        self.hit_rect = self.rect
        self.x = x
        self.y = y
        self.rect.x = x
        self.rect.y = y

class LongGrass(pg.sprite.Sprite):
    def __init__(self, game, x, y, w, h):
        self.groups = game.long_grass, game.all_static_sprites
        pg.sprite.Sprite.__init__(self, self.groups)
        self.game = game
        self.rect = pg.Rect(x, y, w, h)
        self.hit_rect = self.rect
        self.x = x
        self.y = y
        self.rect.x = x
        self.rect.y = y

class Door(pg.sprite.Sprite):
    def __init__(self, game, x, y, w, h, name):
        self.groups = game.doors, game.all_static_sprites
        pg.sprite.Sprite.__init__(self, self.groups)
        self.game = game
        self.name = name
        self.rect = pg.Rect(x, y, w, h)
        self.hit_rect = self.rect
        self.x = x
        self.y = y
        self.rect.x = x
        self.rect.y = y
        self.map = self.name[:-5]
        locx = int(self.name[-4:-2])
        locy = int(self.name[-2:])
        self.loc = vec(locx, locy)
        self.map = self.map[4:] + '.tmx'

class Detector(pg.sprite.Sprite): # Used to rest in
    def __init__(self, game, x, y, w, h, name):
        self.groups = game.detectors, game.all_static_sprites
        pg.sprite.Sprite.__init__(self, self.groups)
        self.game = game
        self.name = name
        self.quest = 'None'
        self.item = None
        self.action = 'None'
        self.detected = False
        self.kill_item = False
        _, self.item, self.action, self.quest, self.kill_item = self.name.split('_')
        self.kill_item = eval(self.kill_item)
        self.rect = pg.Rect(x, y, w, h)
        self.hit_rect = self.rect
        self.x = x
        self.y = y
        self.rect.x = x
        self.rect.y = y

    def trigger(self, detectable):
        if not self.detected:
            if self.action != 'None':
                self.do_action(detectable)
            if self.quest != 'None':
                self.game.quests[self.quest]['completed'] = True
            self.detected = True

    def do_action(self, detectable):
        if self.action == 'changeKimmy':
            detectable.kind['dialogue'] = 'KIMMY_DLG2'
            detectable.kind['aggression'] = 'awp'
        if self.action == 'changeFelius':
            detectable.remove(self.game.companions)
            try:
                detectable.body.remove(self.game.companion_bodies)
            except:
                pass
            detectable.default_detect_radius = detectable.detect_radius = 250
            detectable.guard = False
            detectable.speed = detectable.walk_speed = 80
            detectable.run_speed = 100
            self.game.people['catrina']['dialogue'] = 'CATRINA_DLG2'

# This class generates random points for NPCs and animals to walk towards
class Target(pg.sprite.Sprite): # Used for fires and other stationary animated sprites
    def __init__(self, game, x = 0, y = 0):
        self.game = game
        self._layer = self.game.map.items_layer
        self.groups = game.all_static_sprites, game.random_targets
        self.rect_size = 60
        pg.sprite.Sprite.__init__(self, self.groups)
        if x == 0:
            x = randrange(200, self.game.map.width - 200)
            y = randrange(200, self.game.map.height - 200)
        self.rect = self.hit_rect = pg.Rect(x, y, self.rect_size, self.rect_size)
        self.pos = vec(self.rect.centerx, self.rect.centery)
        self.vel = vec(0, 0)
        self.acc = vec(0, 0)
        self.living = True

    def new_position(self, npc_loc):
        x = randrange(self.game.screen_width, self.game.map.width - self.game.screen_width)
        y = randrange(self.game.screen_width, self.game.map.height - self.game.screen_width)
        self.rect = self.hit_rect = pg.Rect(x, y, self.rect_size, self.rect_size)
        self.pos = vec(self.rect.centerx, self.rect.centery)

    def set_position(self, x, y):
        self.rect = self.hit_rect = pg.Rect(x - self.rect_size/2, y - self.rect_size/2, self.rect_size, self.rect_size)
        self.pos = vec(self.rect.centerx, self.rect.centery)

class AIPath(pg.sprite.Sprite):
    def __init__(self, game, x, y, w, h, kind):
        self.groups = game.aipaths, game.all_static_sprites
        pg.sprite.Sprite.__init__(self, self.groups)
        self.game = game
        self.rect = pg.Rect(x, y, w, h)
        self.hit_rect = self.rect
        self.x = x
        self.y = y
        self.rect.x = x
        self.rect.y = y
        self.kind = kind
        self.pos = vec(self.rect.centerx, self.rect.centery)