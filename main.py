# The Legend of Sky Realm by Raven Ironwing

import tracemalloc
import gc
import pygame as pg
import sys
import pickle
import pygame.surfarray as surfarray
from random import choice, random, choices
from os import path, makedirs
from settings import *
from npcs import *
from quests import *
from menu import *
from sprites import *
from tilemap import *
import datetime
from time import sleep, perf_counter
import math
from menu import Item_Icon
from pygame.locals import *
from pytmx.util_pygame import load_pygame
import pyscroll
import pyscroll.data
from pyscroll.group import PyscrollGroup

tracemalloc.start()

#npc_q = Queue()

#def get_tile_number(sprite, layer):  # Gets the type of tile a sprite is on.
#    x = int(sprite.pos.x / sprite.game.map.tile_size)
#    y = int(sprite.pos.y / sprite.game.map.tile_size)
#    if x < 0: x = 0
#    if y < 0: y = 0
#    if x >= sprite.game.map.tiles_wide: x = sprite.game.map.tiles_wide - 1
#    if y >= sprite.game.map.tiles_high: y = sprite.game.map.tiles_high - 1
#    return sprite.game.map.tmxdata.get_tile_gid(x, y, layer)

#def get_tile_props(sprite, layer):  # Gets the type of tile a sprite is on.
#    x = int(sprite.pos.x / sprite.game.map.tile_size)
#    y = int(sprite.pos.y / sprite.game.map.tile_size)
#    if x < 0: x = 0
#    if y < 0: y = 0
#    if x >= sprite.game.map.tiles_wide: x = sprite.game.map.tiles_wide - 1
#    if y >= sprite.game.map.tiles_high: y = sprite.game.map.tiles_high - 1
#    return sprite.game.map.tmxdata.get_tile_properties(x, y, layer)


def trace_mem():
    snapshot = tracemalloc.take_snapshot()
    top_stats = snapshot.statistics('lineno')

    print("[ Top 10 ]")
    for stat in top_stats[:10]:
        print(stat)

# HUD functions
def draw_player_stats(surf, x, y, pct, color = GREEN, bar_length = 100):
    if pct < 0:
        pct = 0
    bar_height = 20
    fill = pct * bar_length
    outline_rect = pg.Rect(x, y, bar_length, bar_height)
    fill_rect = pg.Rect(x, y, fill, bar_height)
    if pct > 0.6:
        col = color
    elif pct > 0.3:
        col = YELLOW
    else:
        col = RED
    pg.draw.rect(surf, col, fill_rect)
    pg.draw.rect(surf, WHITE, outline_rect, 2)

# Used for loading sprite sheet images into a list of images

def load_spritesheet(sheet, size):
    image_list = []
    sheet_width = sheet.get_width()
    sheet_height = sheet.get_height()
    columns = int(sheet_width / size)
    rows = int(sheet_height / size)
    # Create a new blank image

    for col in range(0, columns):
        y = col * size
        for row in range(0, rows):
            x = row * size
            image = pg.Surface([size, size], pg.SRCALPHA).convert_alpha()
            # Copy the sprite from the large sheet onto the smaller image
            image.blit(sheet, (0, 0), (x, y, size, size))
            image_list.append(image)
    # Return the separate images stored in a list.
    return image_list

# Used to see if the player is in talking range of an Npc
def npc_talk_rect(one, two):
    if one.hit_rect.colliderect(two.talk_rect):
        return True
    else:
        return False

def mob_hit_rect(one, two):
    if one.hit_rect.colliderect(two.hit_rect):
        return True
    else:
        return False

def breakable_melee_hit_rect(one, two):
    if one.mother.weapon_hand == 'weapons':
        if True in (one.mid_weapon_melee_rect.colliderect(two.trunk.hit_rect), one.weapon_melee_rect.colliderect(two.trunk.hit_rect), one.melee_rect.colliderect(two.trunk.hit_rect)):
            if one.swing_weapon1: # This differentiates between weapons that are being swung and those that are thrusted.
                if one.frame > 6:
                    return True
            elif one.frame < 6:
                return True
        else:
            return False

    elif one.mother.weapon_hand == 'weapons2':
        if True in (one.mid_weapon2_melee_rect.colliderect(two.trunk.hit_rect), one.weapon2_melee_rect.colliderect(two.trunk.hit_rect), one.melee2_rect.colliderect(two.trunk.hit_rect)):
            if one.swing_weapon2:
                if one.frame > 6:
                    return True
            elif one.frame < 6:
                return True
    return False

# Used to define fireball hits
def fire_collide(one, two):
    if one.hit_rect.colliderect(two.hit_rect):
        return True
    else:
        return False

def entryway_collide(one, two):
    if one.rect.colliderect(two.hit_rect):
        return True
    else:
        return False

class Game:
    def __init__(self):
        self.screen_width = WIDTH
        self.screen_height = HEIGHT
        #self.flags = pg.NOFRAME
        self.flags = pg.SCALED # | pg.FULLSCREEN
        #self.screen = pg.display.set_mode((self.screen_width, HEIGHT), pg.FULLSCREEN)
        icon_image = pg.image.load(path.join(img_folder, ICON_IMG))
        pg.display.set_icon(icon_image)
        self.screen = pg.display.set_mode((self.screen_width, self.screen_height), self.flags)
        pg.display.set_caption(TITLE)
        self.clock = pg.time.Clock()
        self.dt = 0.0001
        # Loads Mutant Python Logo Faid in/out.
        mpy_logo_image = pg.image.load(path.join(img_folder, LOGO_IMAGE)).convert_alpha()
        mpy_logo_image = pg.transform.scale(mpy_logo_image, (int(self.screen_height/4), int(self.screen_height/4)))
        logo_width = mpy_logo_image.get_width()
        logo_placement = ((self.screen_width - logo_width)/2, (self.screen_height - logo_width)/2)
        mpy_words_image = pg.image.load(path.join(img_folder, MPY_WORDS)).convert_alpha()
        mpy_words_image = pg.transform.scale(mpy_words_image, (int(self.screen_width/4), int(self.screen_height/8)))
        words_height = mpy_words_image.get_height()
        words_width = mpy_words_image.get_width()
        words_placement = ((self.screen_width - words_width)/2, (self.screen_height - words_height)/2)
        for i in range(0, 256):
            self.clock.tick(120)
            self.screen.fill(BLACK)
            pg.display.flip()
        for i in range(0, 256):
            self.clock.tick(120)
            self.screen.fill(BLACK)
            mpy_logo_image.set_alpha(i)
            if i == 10:
                pg.mixer.Sound(path.join(snd_folder, 'mutant_python.ogg')).play()
            self.screen.blit(mpy_logo_image, logo_placement)
            pg.display.flip()
        self.load_data()
        for i in range(255, 0, -1):
            self.clock.tick(120)
            self.screen.fill(BLACK)
            mpy_logo_image.set_alpha(i)
            self.screen.blit(mpy_logo_image, logo_placement)
            pg.display.flip()
        for i in range(0, 256):
            self.clock.tick(120)
            self.screen.fill(BLACK)
            pg.display.flip()
        self.channel2 = pg.mixer.Channel(2)
        self.channel3 = pg.mixer.Channel(3)
        self.channel4 = pg.mixer.Channel(4)
        self.channel5 = pg.mixer.Channel(5)
        self.channel6 = pg.mixer.Channel(6)
        self.channel7 = pg.mixer.Channel(7)
        self.channel_list = [self.channel2, self.channel3, self.channel4, self.channel5, self.channel6, self.channel7]

    def on_screen(self, sprite, threshold = 50):
        rect = self.camera.apply(sprite)
        if rect.right < -threshold or rect.bottom < -threshold or rect.left > self.screen_width + threshold or rect.top > self.screen_height + threshold:
            return False
        else:
            return True

#    def on_screen_no_edge(self, sprite): #no threashold for slightly faster draw.
#        rect = self.camera.apply(sprite)
#        if rect.right < 0 or rect.bottom < 0 or rect.left > self.screen_width or rect.top > self.screen_height:
#            return False
#        else:
#            return True

    def is_living(self, npc_kind):
        if 'dead' in self.people[npc_kind]:
            if self.people[npc_kind]['dead']:
                return False
            else:
                return True
        else:
            return True

    def format_date(self):
        directive = "%m-%d-%Y_%H-%M-%S"
        return datetime.datetime.now().strftime(directive)

    def save_sprite_locs(self):
        # This block stores all sprite locations and their health/inventories in the map_sprite_data_list so the game remembers where everything is.
        npc_list = []
        animal_list = []
        item_list = []
        vehicle_list = []
        breakable_list = []
        if not self.underworld:
            for npc in self.npcs:
                if npc not in self.companions:
                    npc_list.append({'name': npc.kind, 'location': npc.pos})
                    self.map_sprite_data_list[int(self.world_location.x)][int(self.world_location.y)].npcs = npc_list
            for animal in self.animals:
                if animal not in self.companions:
                    if animal != self.player.vehicle:
                        animal_list.append({'name': animal.kind, 'location': animal.pos})
                        self.map_sprite_data_list[int(self.world_location.x)][int(self.world_location.y)].animals = animal_list
            for item in self.dropped_items:
                item_list.append({'name': item.name, 'location': item.pos, 'rotation': item.rot})
                self.map_sprite_data_list[int(self.world_location.x)][int(self.world_location.y)].items = item_list
            for vehicle in self.vehicles:
                if vehicle.driver != self.player:
                    vehicle_list.append({'name': vehicle.kind, 'location': vehicle.pos})
                    self.map_sprite_data_list[int(self.world_location.x)][int(self.world_location.y)].vehicles = vehicle_list
            for breakable in self.breakable:
                breakable_list.append({'name': breakable.name, 'location': breakable.center, 'w': breakable.w, 'h': breakable.h,  'rotation': breakable.rot})
                self.map_sprite_data_list[int(self.world_location.x)][int(self.world_location.y)].breakable = breakable_list
        else:
            for npc in self.npcs:
                if npc not in self.companions:
                    npc_list.append({'name': npc.kind, 'location': npc.pos})
                    self.underworld_sprite_data_dict[self.previous_map].npcs = npc_list
            for animal in self.animals:
                if animal not in self.companions:
                    if animal != self.player.vehicle:
                        animal_list.append({'name': animal.kind, 'location': animal.pos})
                        self.underworld_sprite_data_dict[self.previous_map].animals = animal_list
            for item in self.dropped_items:
                item_list.append({'name': item.name, 'location': item.pos, 'rotation': item.rot})
                self.underworld_sprite_data_dict[self.previous_map].items = item_list
            for vehicle in self.vehicles:
                vehicle_list.append({'name': vehicle.kind, 'location': vehicle.pos})
                self.underworld_sprite_data_dict[self.previous_map].vehicles = vehicle_list
            for breakable in self.breakable:
                breakable_list.append({'name': breakable.name, 'location': breakable.center, 'w': breakable.w, 'h': breakable.h,  'rotation': breakable.rot})
                self.underworld_sprite_data_dict[self.previous_map].breakable = breakable_list

    def save(self, slot):
        self.screen.fill(BLACK)
        self.save_sprite_locs()
        possessing = self.player.possessing
        if self.player.possessing:
            self.player.possessing.depossess()
        self.player.dragon = False
        if 'dragon' in self.player.equipped['race']: # Makes it so you aren't a dragon when you load a game.
            self.player.equipped['race'] = self.player.equipped['race'].replace('dragon', '')
            self.player.body.update_animations()
        self.draw_text('Saving....', self.script_font, 50, WHITE, self.screen_width / 2, self.screen_height / 2, align="topright")
        pg.display.flip()
        sleep(0.5)
        companion_list = []
        for companion in self.companions:
            companion_list.append(companion.kind)
        vehicle_name = None
        if self.player.in_vehicle:
            vehicle_name = self.player.vehicle.kind

        # self.previous_map is used keep track of the last map you were on.
        save_list = [self.player.inventory, self.player.equipped, self.player.stats, self.player.expanded_inventory, [self.player.pos.x, self.player.pos.y], self.previous_map, [self.world_location.x, self.world_location.y], self.overworld_map, vehicle_name, companion_list, self.map_sprite_data_list, self.key_map, self.animals_dict, self.people, self.quests]
        if not path.isdir(saves_folder): makedirs(saves_folder)

        with open(path.join(saves_folder, str(slot) + "_" + self.format_date() + ".sav"), "wb", -1) as FILE:
            pickle.dump(save_list, FILE)
        if possessing:
            possessing.possess(self.player)

    def load_save(self, file_name):
        self.continued_game = True
        load_file = []
        with open(file_name, "rb", -1) as FILE:
            load_file = pickle.load(FILE)
        self.player.inventory = load_file[0]
        self.player.equipped = load_file[1]
        self.player.stats = load_file[2]
        self.player.expanded_inventory = load_file[3]
        self.player.pos = vec(load_file[4])
        self.previous_map = load_file[5]
        self.world_location = vec(load_file[6])
        self.overworld_map = load_file[7]
        self.saved_vehicle = load_file[8]
        self.saved_companions = [9]
        self.map_sprite_data_list = load_file[10]
        self.key_map = load_file[11]
        self.animals_dict = load_file[12]
        self.people = load_file[13]
        self.quests = load_file[14]
        self.load_over_map(self.overworld_map)
        self.load_map(self.previous_map)
        self.map.stored_map_data = self.map_sprite_data_list[int(self.world_location.x)][int(self.world_location.y)] # Sets the map stored data object to the one that was saved for that map location.
        self.map.load_stored_data() # Loads the stored data into the map
        self.player.human_body.update_animations()
        self.player.dragon_body.update_animations()
        self.player.calculate_fire_power()
        #self.player.calculate_perks()
        #Update hud stats
        self.hud_health_stats = self.player.stats
        self.hud_health = self.hud_health_stats['health'] / self.hud_health_stats['max health']
        self.hud_stamina = self.hud_health_stats['stamina'] / self.hud_health_stats['max stamina']
        self.hud_magica = self.hud_health_stats['magica'] / self.hud_health_stats['max magica']
        self.hud_hunger = self.hud_health_stats['hunger'] / self.hud_health_stats['max hunger']
        # Loads saved companions
        for companion in self.saved_companions:
            for npc_type in NPC_TYPE_LIST:
                if companion in eval(npc_type.upper()):
                    rand_angle = randrange(0, 360)
                    random_vec = vec(170, 0).rotate(-rand_angle)
                    follower_center = vec(self.player.pos + random_vec)
                    if npc_type == 'animals':
                        if companion != self.saved_vehicle: #Makes it so it doesn't double load companions you are riding.
                            follower = Animal(self, follower_center.x, follower_center.y, companion)
                            follower.offensive = False
                            follower.make_companion()
                    else:
                        follower = Player(self, follower_center.x, follower_center.y, companion)
                        follower.offensive = False
                        follower.make_companion()
        self.saved_companions = []
        # Enters vehicle if you saved it inside a vehicle
        for vehicle in self.vehicles:
            if vehicle.kind == self.saved_vehicle:
                vehicle.enter_vehicle(self.player)
        for vehicle in self.flying_vehicles:
            if vehicle.kind == self.saved_vehicle:
                vehicle.enter_vehicle(self.player)
        if self.saved_vehicle in self.animals_dict:
            mount = Animal(self, self.player.pos.x, self.player.pos.y, self.saved_vehicle)
            mount.mount(self.player)

    def update_old_save(self, file_name):
        load_file = []
        with open(file_name, "rb", -1) as FILE:
            load_file = pickle.load(FILE)
        # Loads saved upgraded equipment:
        self.people = PEOPLE # Updates NPCs
        self.animals_dict = ANIMALS
        self.quests = QUESTS # Updates Quests from save
        self.key_map = KEY_MAP
        self.player.inventory = load_file[0]
        self.player.equipped = load_file[1]
        self.player.stats = load_file[2]
        self.player.expanded_inventory = load_file[3]
        self.player.pos = vec(load_file[4])
        self.previous_map = load_file[5]
        self.world_location = vec(load_file[6])
        self.overworld_map = load_file[7]
        self.saved_vehicle = load_file[8]
        self.saved_companions = [9]
        self.map_sprite_data_list = load_file[10]
        self.key_map = load_file[11]
        self.animals_dict = load_file[12]
        self.people = load_file[13]
        self.quests = load_file[14]
        self.load_map(self.previous_map)
        self.player.pos = vec(load_file[3])
        self.player.human_body.update_animations()
        self.player.dragon_body.update_animations()
        self.player.calculate_fire_power()
        #self.player.calculate_perks()
        self.overworld_map = load_file[7]
        self.load_over_map(self.overworld_map)

    def draw_text(self, text, font_name, size, color, x, y, align="topleft"):
        font = pg.font.Font(font_name, size)
        text_surface = font.render(text, True, color)
        text_rect = text_surface.get_rect(**{align: (x, y)})
        self.screen.blit(text_surface, text_rect)


    def load_data(self):
        self.title_font = HEADING_FONT
        self.hud_font = HUD_FONT
        self.script_font = SCRIPT_FONT
        self.dim_screen = pg.Surface(self.screen.get_size()).convert_alpha()
        self.dim_screen.fill((SHADOW))
        self.body_surface = pg.Surface((64, 64)).convert()
        self.body_surface.set_colorkey(BLACK)
        self.open_book_image = pg.image.load(path.join(img_folder, 'open_book.png')).convert()
        self.open_book_image = pg.transform.scale(self.open_book_image, (self.screen_width, self.screen_height - 30))
        self.open_letter_image = pg.image.load(path.join(img_folder, 'open_letter.png')).convert()
        self.open_letter_image = pg.transform.scale(self.open_letter_image, (self.screen_width, self.screen_height - 30))
        self.over_minimap_image = pg.image.load(path.join(img_folder, OVERWORLD_MAP_IMAGE)).convert()
        self.over_minimap_image = pg.transform.scale(self.over_minimap_image, (self.screen_height, self.screen_height))
        self.compass_image = pg.image.load(path.join(img_folder, 'compass.png')).convert_alpha()
        self.crosshair_image = pg.image.load(path.join(img_folder, 'crosshair.png')).convert_alpha()
        self.crosshair_offset = int(self.crosshair_image.get_width()/2)
        self.player_tur = pg.image.load(path.join(img_folder, PLAYER_TUR)).convert_alpha()
        #self.player_tank = pg.image.load(path.join(img_folder, PLAYER_TANK)).convert_alpha()
        #self.tank_in_water = pg.image.load(path.join(img_folder, TANK_IN_WATER)).convert_alpha()
        #self.sunken_tank = pg.image.load(path.join(img_folder, SUNKEN_TANK)).convert_alpha()
        self.lock_image = pg.image.load(path.join(img_folder, 'lock.png')).convert_alpha()
        self.lock_keyway_image = pg.image.load(path.join(img_folder, 'lock_keyway.png')).convert_alpha()
        self.keyed_keyway_image = pg.image.load(path.join(img_folder, 'keyed_keyway.png')).convert_alpha()
        self.lock_pick_image = pg.image.load(path.join(img_folder, 'lock_pick.png')).convert_alpha()
        self.swim_shadow_image = pg.image.load(path.join(img_folder, 'swim_shadow.png')).convert_alpha()
        self.mech_back_image = pg.image.load(path.join(img_folder, 'mech_back_lights.png')).convert_alpha()
        self.clear_box_image = pg.image.load(path.join(img_folder, 'clear_box.png')).convert_alpha()
        self.black_box_image = pg.image.load(path.join(img_folder, 'black_box.png')).convert()
        self.dark_grey_box_image = pg.image.load(path.join(img_folder, 'dark_grey_box.png')).convert()
        self.grey_box_image = pg.image.load(path.join(img_folder, 'grey_box.png')).convert()
        self.start_icon_image = pg.image.load(path.join(img_folder, 'start_icon.png')).convert()
        self.right_arrow_image = pg.transform.scale(pg.image.load(path.join(img_folder, 'right_arrow.png')).convert(), (ICON_SIZE, ICON_SIZE))
        self.back_arrow_image = pg.transform.scale(pg.image.load(path.join(img_folder, 'back_arrow.png')).convert(), (ICON_SIZE, ICON_SIZE))
        self.trash_image = pg.image.load(path.join(img_folder, 'trash.png')).convert()
        self.book_images = []
        for i in range(0, 6):
            image = pg.image.load(path.join(book_animation_folder, 'book{}.png'.format(i))).convert()
            image = pg.transform.scale(image, (self.screen_width, self.screen_height))
            self.book_images.append(image)
        #self.rock_shadow_image = pg.image.load(path.join(img_folder, 'rock_shadow.png')).convert_alpha()
        self.invisible_image = pg.image.load(path.join(img_folder, 'invisible.png')).convert_alpha()
        # creates a dictionary of animal images. This is not in the settings file like the others because of the order it needs to import info.
        ANIMAL_IMAGES = {}
        for animal in ANIMAL_ANIMATIONS:
            temp_list = []
            number_of_files = len([name for name in os.listdir(animals_folder) if animal in name if os.path.isfile(os.path.join(animals_folder, name))])
            for i in range(1, number_of_files + 1):
                filename = animal + '{}.png'.format(i)
                temp_list.append(filename)
            ANIMAL_IMAGES[animal] = temp_list
        # Loads animal images
        self.animal_images = {}
        for kind in ANIMAL_IMAGES:
            temp_list = []
            for i, picture in enumerate(ANIMAL_IMAGES[kind]):
                img = pg.image.load(path.join(animals_folder, ANIMAL_IMAGES[kind][i])).convert_alpha()
                temp_list.append(img)
            self.animal_images[kind] = temp_list
        # associates the animation frames with the animal images
        self.animal_animations = {}
        for kind in ANIMAL_ANIMATIONS:
            temp_dict = {}
            for animation in ANIMAL_ANIMATIONS[kind]:
                temp_list = []
                for frame in ANIMAL_ANIMATIONS[kind][animation]:
                    temp_list.append(self.animal_images[kind][frame - 1])
                temp_dict[animation] = temp_list
            self.animal_animations[kind] = temp_dict
        self.bullet_images = {}
        for x, size in enumerate(BULLET_SIZES):
            for i, item in enumerate(BULLET_IMAGES):
                bullet_img = pg.image.load(path.join(bullets_folder, BULLET_IMAGES[i])).convert_alpha()
                if size != 'ar':
                    if i != 0:
                        img = pg.transform.scale(bullet_img, (3*(x + 1), 2*(x + 1)))
                    else:
                        img = pg.transform.scale(bullet_img, (6 * (x + 1), 2 * (x + 1)))
                else:
                    img = pg.transform.scale(bullet_img, (40, 5))
                bullet_name = size + str(i)
                self.bullet_images[bullet_name] = img

        self.enchantment_images = []
        for i, item in enumerate(ENCHANTMENT_IMAGES):
            img = pg.image.load(path.join(enchantments_folder, ENCHANTMENT_IMAGES[i])).convert_alpha()
            self.enchantment_images.append(img)

        self.hair_images = {}
        for item in HAIR_IMAGES:
            img = pg.image.load(path.join(hair_folder, HAIR_IMAGES[item])).convert_alpha()
            self.hair_images[item] = img

        self.race_images = {}
        for item in RACE_IMAGES:
            img = pg.image.load(path.join(race_folder, RACE_IMAGES[item])).convert_alpha()
            self.race_images[item] = img

        self.item_images = {}
        for item in NEW_ITEM_IMAGES:
            img = pg.image.load(path.join(new_items_folder, NEW_ITEM_IMAGES[item])).convert_alpha()
            self.item_images[item] = img

        self.workstation_images = {}
        for item in WORKSTATION_IMAGES:
            img = pg.image.load(path.join(workstations_folder, WORKSTATION_IMAGES[item])).convert_alpha()
            self.workstation_images[item] = img

        """
        self.weapon_images = []
        for i, weapon in enumerate(WEAPON_IMAGES):
            img = pg.image.load(path.join(weapons_folder, WEAPON_IMAGES[i])).convert_alpha()
            self.weapon_images.append(img)
        self.hat_images = []
        for i, hat in enumerate(HAT_IMAGES):
            img = pg.image.load(path.join(hats_folder, HAT_IMAGES[i])).convert_alpha()
            self.hat_images.append(img)
        self.top_images = []
        for i, top in enumerate(TOP_IMAGES):
            img = pg.image.load(path.join(tops_folder, TOP_IMAGES[i])).convert_alpha()
            self.top_images.append(img)
        self.bottom_images = []
        for i, bottom in enumerate(BOTTOM_IMAGES):
            img = pg.image.load(path.join(bottoms_folder, BOTTOM_IMAGES[i])).convert_alpha()
            self.bottom_images.append(img)
        self.shoe_images = []
        for i, shoe in enumerate(SHOE_IMAGES):
            img = pg.image.load(path.join(shoes_folder, SHOE_IMAGES[i])).convert_alpha()
            self.shoe_images.append(img)
        self.glove_images = []
        for i, glove in enumerate(GLOVE_IMAGES):
            img = pg.image.load(path.join(gloves_folder, GLOVE_IMAGES[i])).convert_alpha()
            self.glove_images.append(img)"""

        self.light_mask_images = []
        for i, val in enumerate(LIGHT_MASK_IMAGES):
            img = pg.image.load(path.join(light_masks_folder, LIGHT_MASK_IMAGES[i])).convert_alpha()
            self.light_mask_images.append(img)

        # Prescaling of lights
        self.flame_light_mask = pg.transform.scale(self.light_mask_images[1], (FLAME_TILE_BRIGHTNESS, FLAME_TILE_BRIGHTNESS))
        self.flame_light_mask_rect = self.flame_light_mask.get_rect()
        self.coals_light_mask = pg.transform.scale(self.light_mask_images[0], (FLAME_TILE_BRIGHTNESS, FLAME_TILE_BRIGHTNESS))
        self.coals_light_mask_rect = self.coals_light_mask.get_rect()
        self.candle_light_mask = pg.transform.scale(self.light_mask_images[1], (CANDLE_BRIGHTNESS, CANDLE_BRIGHTNESS))
        self.candle_light_mask_rect = self.candle_light_mask.get_rect()

        self.flashlight_masks = []
        temp_img = pg.transform.scale(self.light_mask_images[3], (int(300 * 2.8), 300))
        for rot in range(0, 120):
            new_image = pg.transform.rotate(temp_img, rot*3)
            self.flashlight_masks.append(new_image)

        self.magic_images = {}
        for item in MAGIC_IMAGES:
            img = pg.image.load(path.join(magic_folder, MAGIC_IMAGES[item])).convert_alpha()
            self.magic_images[item] = img

        self.magic_animation_images = {}
        for key, image in self.magic_images.items():
            image_list = []
            # enlarge image animation
            for i in range(0, 5):
                new_image = pg.transform.scale(image, (13*i, 13*i))
                image_list.append(new_image)
            # shrink animation
            for i in range(1, 10):
                new_image = pg.transform.scale(image, (int(70/i), int(70/i)))
                image_list.append(new_image)
            self.magic_animation_images[key] = image_list

        self.gender_images = []
        for i, gender in enumerate(GENDER_IMAGES):
            img = pg.image.load(path.join(gender_folder, GENDER_IMAGES[i])).convert_alpha()
            self.gender_images.append(img)
        self.corpse_images = []
        for i, corpse in enumerate(CORPSE_IMAGES):
            img = pg.image.load(path.join(corpse_folder, CORPSE_IMAGES[i])).convert_alpha()
            self.corpse_images.append(img)
        self.vehicle_images = []
        for i, x in enumerate(VEHICLES_IMAGES):
            img = pg.image.load(path.join(vehicles_folder, VEHICLES_IMAGES[i])).convert_alpha()
            self.vehicle_images.append(img)
        self.color_swatch_images = []
        for i, x in enumerate(COLOR_SWATCH_IMAGES):
            img = pg.image.load(path.join(color_swatches_folder, COLOR_SWATCH_IMAGES[i])).convert()
            self.color_swatch_images.append(img)
        self.fire_images = []
        for i, x in enumerate(FIRE_IMAGES):
            img = pg.image.load(path.join(fire_folder, FIRE_IMAGES[i])).convert_alpha()
            self.fire_images.append(img)
        self.shock_images = []
        for i, x in enumerate(SHOCK_IMAGES):
            img = pg.image.load(path.join(shock_folder, SHOCK_IMAGES[i])).convert_alpha()
            self.shock_images.append(img)
        self.electric_door_images = []
        for i, x in enumerate(ELECTRIC_DOOR_IMAGES):
            img = pg.image.load(path.join(electric_door_folder, ELECTRIC_DOOR_IMAGES[i])).convert_alpha()
            self.electric_door_images.append(img)
        self.loading_screen_images = []
        for i, screen in enumerate(LOADING_SCREEN_IMAGES):
            img = pg.image.load(path.join(loading_screen_folder, LOADING_SCREEN_IMAGES[i])).convert()
            img = pg.transform.scale(img, (self.screen_width, self.screen_height))
            self.loading_screen_images.append(img)
        self.tree_images = {}
        self.breakable_images = {}
        for kind in BREAKABLE_IMAGES:
            temp_list = []
            for i, picture in enumerate(BREAKABLE_IMAGES[kind]):
                img = pg.image.load(path.join(breakable_folder, BREAKABLE_IMAGES[kind][i])).convert_alpha()
                temp_list.append(img)
            self.breakable_images[kind] = temp_list
        for kind in TREES:
            temp_list = []
            temp_list2 = []
            temp_list3 = []
            for i, picture in enumerate(TREE_IMAGES[kind]):
                img = pg.image.load(path.join(tree_folder, TREE_IMAGES[kind][i])).convert_alpha()
                scaled_image = pg.transform.scale(img, (TREE_SIZES['small'], TREE_SIZES['small']))
                temp_list.append(scaled_image)
                scaled_image = pg.transform.scale(img, (TREE_SIZES['medium'], TREE_SIZES['medium']))
                temp_list2.append(scaled_image)
                scaled_image = pg.transform.scale(img, (TREE_SIZES['large'], TREE_SIZES['large']))
                temp_list3.append(scaled_image)
            self.tree_images['small ' + kind] = temp_list
            self.tree_images['medium ' + kind] = temp_list2
            self.tree_images['large ' + kind] = temp_list3

        self.portal_sheet = pg.image.load(PORTAL_SHEET).convert_alpha()
        self.portal_images = load_spritesheet(self.portal_sheet, 256)

        self.fireball_images = []
        for i, x in enumerate(FIREBALL_IMAGES):
            img = pg.image.load(path.join(fireball_folder, FIREBALL_IMAGES[i])).convert_alpha()
            self.fireball_images.append(img)
        self.explosion_images = []
        for i, x in enumerate(EXPLOSION_IMAGES):
            img = pg.image.load(path.join(explosion_folder, EXPLOSION_IMAGES[i])).convert_alpha()
            self.explosion_images.append(img)

        self.humanoid_images = {}
        for kind in HUMANOID_IMAGES:
            temp_list = []
            for i, picture in enumerate(HUMANOID_IMAGES[kind]):
                temp_folder = kind.replace('images', 'parts_folder')
                img = pg.image.load(path.join(eval(temp_folder), HUMANOID_IMAGES[kind][i])).convert_alpha()
                temp_list.append(img)
            self.humanoid_images[kind] = temp_list

        self.gun_flashes = []
        for img in MUZZLE_FLASHES:
            self.gun_flashes.append(pg.image.load(path.join(img_folder, img)).convert_alpha())
        # lighting effect
        self.fog = pg.Surface((self.screen_width, self.screen_height))
        self.fog.fill(NIGHT_COLOR)
        # Sound loading
        self.effects_sounds = {}
        for key in EFFECTS_SOUNDS:
            self.effects_sounds[key] = pg.mixer.Sound(path.join(snd_folder, EFFECTS_SOUNDS[key]))
        self.weapon_sounds = {}
        for weapon in WEAPON_SOUNDS:
            self.weapon_sounds[weapon] = []
            for snd in WEAPON_SOUNDS[weapon]:
                s = pg.mixer.Sound(path.join(snd_folder, snd))
                s.set_volume(0.3)
                self.weapon_sounds[weapon].append(s)
        self.weapon_hit_sounds = {}
        for weapon in WEAPON_HIT_SOUNDS:
            self.weapon_hit_sounds[weapon] = []
            for snd in WEAPON_HIT_SOUNDS[weapon]:
                s = pg.mixer.Sound(path.join(snd_folder, snd))
                s.set_volume(0.3)
                self.weapon_hit_sounds[weapon].append(s)
        self.weapon_reload_sounds = {}
        for weapon, snd in WEAPON_RELOAD_SOUNDS.items():
            s = pg.mixer.Sound(path.join(snd_folder, snd))
            s.set_volume(0.3)
            self.weapon_reload_sounds[weapon] = s
        self.zombie_moan_sounds = []
        for snd in ZOMBIE_MOAN_SOUNDS:
            s = pg.mixer.Sound(path.join(snd_folder, snd))
            s.set_volume(0.2)
            self.zombie_moan_sounds.append(s)
        self.wraith_sounds = []
        for snd in WRAITH_SOUNDS:
            s = pg.mixer.Sound(path.join(snd_folder, snd))
            s.set_volume(0.2)
            self.wraith_sounds.append(s)
        self.punch_sounds = []
        for snd in PUNCH_SOUNDS:
            s = pg.mixer.Sound(path.join(snd_folder, snd))
            s.set_volume(0.2)
            self.punch_sounds.append(s)
        self.male_player_hit_sounds = []
        for snd in MALE_PLAYER_HIT_SOUNDS:
            self.male_player_hit_sounds.append(pg.mixer.Sound(path.join(snd_folder, snd)))
        self.female_player_hit_sounds = []
        for snd in FEMALE_PLAYER_HIT_SOUNDS:
            self.female_player_hit_sounds.append(pg.mixer.Sound(path.join(snd_folder, snd)))
        self.zombie_hit_sounds = []
        for snd in ZOMBIE_HIT_SOUNDS:
            self.zombie_hit_sounds.append(pg.mixer.Sound(path.join(snd_folder, snd)))
        self.lock_picking_sounds = []
        for snd in LOCK_PICKING_SOUNDS:
            self.lock_picking_sounds.append(pg.mixer.Sound(path.join(snd_folder, snd)))

    def new(self):
        pg.mixer.music.load(path.join(music_folder, TITLE_MUSIC))
        pg.mixer.music.play(loops=-1)
        title_image = pg.image.load(path.join(img_folder, TITLE_IMAGE)).convert()
        title_image = pg.transform.scale(title_image, (self.screen_width, self.screen_height))
        self.map = None
        self.continued_game = False
        waiting = True
        i = 0
        while waiting:
            self.clock.tick(FPS)
            self.screen.fill(BLACK)
            title_image.set_alpha(i)
            self.screen.blit(title_image, (0, 0))
            if i > 240:
                self.draw_text('Press any key to start your adventure.', self.script_font, 18, WHITE, self.screen_width / 2, int(self.screen_height * 0.85),
                               align="center")

            for event in pg.event.get():
                if event.type == pg.QUIT:
                    pg.quit()
                    sys.exit()
                if event.type == pg.MOUSEBUTTONDOWN:
                    waiting = False
                if event.type == pg.KEYDOWN:
                    if event.key == pg.K_n:  # Enters the NPC creation tool
                        if event.mod & pg.KMOD_CTRL:
                            pass  # I removed this but will add it again later.
                        else:
                            waiting = False

                    elif event.key != pg.K_n:
                        if not event.mod & pg.KMOD_CTRL:
                            waiting = False

            pg.display.flip()
            i += 1
            if i > 255:
                i = 255

        # initialize all variables and do all the setup for a new game

        # Used for controlling day and night
        self.darkness = 0
        self.dark_color = (255, 255, 255)
        self.time_of_day = 0
        self.nightfall = False
        self.sunrise = False
        self.night = False
        self.last_darkness_change = 0
        self.day_start_time = pg.time.get_ticks()

        self.map_sprite_data_list = []
        self._player_inside = False
        self.compass_rot = 0
        self.people = PEOPLE
        self.animals_dict = ANIMALS
        self.saved_vehicle = []
        self.saved_companions = []
        self.underworld = False
        self.quests = QUESTS
        self.key_map = KEY_MAP
        self.bg_music = BG_MUSIC
        self.previous_music = TITLE_MUSIC
        self.portal_location = vec(0, 0)
        self.portal_combo = ''
        self.guard_alerted = False
        self.hud_map = False
        self.hud_overmap = False

        self.message_text = True
        self.message = ''
        self.map_type = None
        self.ais = []
        self.group = PyscrollGroup(0) # 0 is the map base layer, but I set it later to self.map.map_layer.
        self.all_sprites = pg.sprite.LayeredUpdates() # Used for all non_static sprites
        self.all_static_sprites = pg.sprite.Group() # used for all static sprites
        self.inventory_hud_icons = pg.sprite.Group()
        self.sprites_on_screen = pg.sprite.Group()
        self.moving_targets = pg.sprite.Group() # Used for all moving things bullets interact with
        self.moving_targets_on_screen = pg.sprite.Group()
        self.mobs = pg.sprite.Group()
        self.mobs_on_screen = pg.sprite.Group()
        self.npc_bodies = pg.sprite.Group()
        self.npc_bodies_on_screen = pg.sprite.Group()
        self.npcs = pg.sprite.Group()
        self.npcs_on_screen = pg.sprite.Group()
        self.animals = pg.sprite.Group()
        self.animals_on_screen = pg.sprite.Group()
        self.fires = pg.sprite.Group()
        self.fires_on_screen = pg.sprite.Group()
        self.breakable = pg.sprite.Group()
        self.breakable_on_screen = pg.sprite.Group()
        self.corpses = pg.sprite.Group()
        self.corpses_on_screen = pg.sprite.Group()
        self.dropped_items = pg.sprite.Group()
        self.dropped_items_on_screen = pg.sprite.Group()
        self.obstacles = pg.sprite.Group()
        self.obstacles_on_screen = pg.sprite.Group()
        self.walls = pg.sprite.Group()
        self.walls_on_screen = pg.sprite.Group()
        self.barriers = pg.sprite.Group()
        self.barriers_on_screen = pg.sprite.Group()
        self.elevations = pg.sprite.Group()
        self.elevations_on_screen = pg.sprite.Group()
        self.inside = pg.sprite.Group()
        self.inside_on_screen = pg.sprite.Group()
        self.climbs = pg.sprite.Group()
        self.climbs_on_screen = pg.sprite.Group()
        self.vehicles = pg.sprite.Group()
        self.vehicles_on_screen = pg.sprite.Group()
        self.lights = pg.sprite.Group()
        self.lights_on_screen = pg.sprite.Group()

        self.aipaths = pg.sprite.Group()
        self.firepots = pg.sprite.Group()
        self.arrows = pg.sprite.Group()
        self.chargers = pg.sprite.Group()
        self.mechsuits = pg.sprite.Group()
        self.detectors = pg.sprite.Group()
        self.detectables = pg.sprite.Group()
        self.portals = pg.sprite.Group()
        self.door_walls = pg.sprite.Group()
        self.nospawn = pg.sprite.Group()
        self.doors = pg.sprite.Group()
        self.player_group = pg.sprite.Group()
        self.players = pg.sprite.Group()
        self.grabable_animals = pg.sprite.Group()
        self.explosions = pg.sprite.Group()
        self.shocks = pg.sprite.Group()
        self.fireballs = pg.sprite.Group()
        self.firepits = pg.sprite.Group()
        self.containers = pg.sprite.Group()
        self.bullets = pg.sprite.Group()
        self.enemy_bullets = pg.sprite.Group()
        self.enemy_fireballs = pg.sprite.Group()
        self.work_stations = pg.sprite.Group()
        self.climbables_and_jumpables = pg.sprite.Group()
        self.all_vehicles = pg.sprite.Group()
        self.companions = pg.sprite.Group()
        self.companion_bodies = pg.sprite.Group()
        self.boats = pg.sprite.Group()
        self.amphibious_vehicles  = pg.sprite.Group()
        self.flying_vehicles  = pg.sprite.Group()
        self.land_vehicles  = pg.sprite.Group()
        self.turrets = pg.sprite.Group()
        self.occupied_vehicles = pg.sprite.Group()
        self.random_targets = pg.sprite.Group()
        self.clicked_sprites = []
        self.target_list = [self.random_targets, self.moving_targets,  self.aipaths]
        self.new_game = True
        self.respawn = False
        self.previous_map = "1.tmx"
        self.world_location = vec(1, 1)
        self.underworld_sprite_data_dict = {}
        self.player = Player(self) # Creates initial player object
        self.continued_game = False
        if self.new_game:  # Why do I have to variables: new_game and conitnued_game
            self.character_menu = MainMenu(self, self.player, 'Character')
        if not self.continued_game:
            self.overworld_map = START_WORLD
            self.load_over_map(self.overworld_map) # Loads world map for first world. This will allow me to load other world maps later.
            self.change_map(None, RACE[self.player.equipped['race']]['start map'], RACE[self.player.equipped['race']]['start pos'])
        self.fly_menu = None
        self.in_menu = False
        self.in_lock_menu = False
        self.in_dialogue_menu = False
        self.dialogue_menu = None
        self.dialogue_menu_npc = None
        self.last_hud_update = 0
        self.last_fire = 0
        self.last_dialogue = 0
        self.hud_health_stats = self.player.stats
        self.hud_health = self.hud_health_stats['health'] / self.hud_health_stats['max health']
        self.hud_stamina = self.hud_health_stats['stamina'] / self.hud_health_stats['max stamina']
        self.hud_magica = self.hud_health_stats['magica'] / self.hud_health_stats['max magica']
        self.hud_mobhp = 0
        self.selected_hud_item = None
        self.show_mobhp = False
        self.last_mobhp_update = 0
        self.hud_hunger = 1
        self.hud_ammo1 = ''
        self.hud_ammo2 = ''
        self.draw_debug = False
        self.paused = False
        self.effects_sounds['level_start'].play()

    @property
    def portal_combo(self):  # This is the method that is called whenever you access portal_combo
        return self._portal_combo
    @portal_combo.setter # Runs whenever you set a value for portal_combo, it checks portal combos
    def portal_combo(self, value):
        self._portal_combo = value
        if value != '':
            if value in PORTAL_CODES:
                coordinate = vec(PORTAL_CODES[value][0], PORTAL_CODES[value][1])
                location = vec(PORTAL_CODES[value][2], PORTAL_CODES[value][3])
                self.portal_combo = ''
                Portal(self, self.portal_location, coordinate, location)
    @property
    def player_inside(self): #This is the method that is called whenever you access
        return self._player_inside
    @player_inside.setter #This is the method that is called whenever you set a value
    def player_inside(self, value):
        if value!=self._player_inside:
            self._player_inside = value
            self.map.toggle_visible_layers()
        else:
            pass

    def load_over_map(self, overmap):
        # Loads data from overworld tmx file
        file = open(path.join(map_folder, overmap), "r")
        map_data = file.readlines()
        self.overworld_map = overmap
        self.map_data_list = []
        for row in map_data:
            if '<' not in row: # Ignores all tags in tmx file
                row = row.replace(',\n', '') #gets rid of commas at the the end
                row = row.replace(' ', '') #gets rid of spaces between entries
                row = row.replace('\n', '') #gets rid of new lines
                row = row.split(',')
                row = list(map(int, row)) # Converts from list of strings strings to integers
                self.map_data_list.append(row)
        self.world_width = len(self.map_data_list[0])
        self.world_height = len(self.map_data_list)

        # This creates a map data object to store which sprites are on each map. This keeps track of where sprites are when they more around or when you drop things.
        if self.map_sprite_data_list == []:
            for x in range(0, self.world_width):
                row = []
                for y in range(0, self.world_height):
                    row.append(None)
                self.map_sprite_data_list.append(row)

        #world_mini_map = WorldMiniMap(self, self.map_data_list) # Only uncomment this to create a new overworld map if you edit the old one. Otherwise it will take literally forever to load every time.
        #self.load_map(str(self.map_data_list[int(self.world_location.y)][int(self.world_location.x)]) + '.tmx')

    """
    def in_surrounding_tiles(self, x, y, num, layer):
        if (x < self.map.tiles_wide-1) and (y < self.map.tiles_high-1):
            if 0 not in [x, y]:
                return num in [self.map.tmxdata.get_tile_gid(x - 1, y, layer), self.map.tmxdata.get_tile_gid(x + 1, y, layer), self.map.tmxdata.get_tile_gid(x + 1, y + 1, layer), self.map.tmxdata.get_tile_gid(x - 1, y - 1, layer), self.map.tmxdata.get_tile_gid(x, y + 1, layer), self.map.tmxdata.get_tile_gid(x, y - 1, layer), self.map.tmxdata.get_tile_gid(x - 1, y + 1, layer), self.map.tmxdata.get_tile_gid(x + 1, y - 1, layer)]
            elif x == 0 and y != 0:
                return num in [self.map.tmxdata.get_tile_gid(x + 1, y, layer), self.map.tmxdata.get_tile_gid(x + 1, y + 1, layer), self.map.tmxdata.get_tile_gid(x, y + 1, layer), self.map.tmxdata.get_tile_gid(x, y - 1, layer), self.map.tmxdata.get_tile_gid(x + 1, y - 1, layer)]
            elif x != 0 and y == 0:
                return num in [self.map.tmxdata.get_tile_gid(x - 1, y, layer), self.map.tmxdata.get_tile_gid(x + 1, y, layer), self.map.tmxdata.get_tile_gid(x + 1, y + 1, layer), self.map.tmxdata.get_tile_gid(x, y + 1, layer), self.map.tmxdata.get_tile_gid(x - 1, y + 1, layer)]
            else:
                return num in [self.map.tmxdata.get_tile_gid(x + 1, y, layer), self.map.tmxdata.get_tile_gid(x + 1, y + 1, layer), self.map.tmxdata.get_tile_gid(x, y + 1, layer)]
        elif (x == self.map.tiles_wide-1) and (y == self.map.tiles_high-1):
            if 0 not in [x, y]:
                return num in [self.map.tmxdata.get_tile_gid(x - 1, y, layer), self.map.tmxdata.get_tile_gid(x - 1, y - 1, layer), self.map.tmxdata.get_tile_gid(x, y - 1, layer)]
            elif x == 0 and y != 0:
                return num in [self.map.tmxdata.get_tile_gid(x, y - 1, layer)]
            elif x != 0 and y == 0:
                return num in [self.map.tmxdata.get_tile_gid(x - 1, y, layer)]
        elif (x == self.map.tiles_wide-1) and (y != self.map.tiles_high-1):
            if 0 not in [x, y]:
                return num in [self.map.tmxdata.get_tile_gid(x - 1, y, layer), self.map.tmxdata.get_tile_gid(x - 1, y - 1, layer), self.map.tmxdata.get_tile_gid(x, y + 1, layer), self.map.tmxdata.get_tile_gid(x, y - 1, layer), self.map.tmxdata.get_tile_gid(x - 1, y + 1, layer)]
            elif x == 0 and y != 0:
                return num in [self.map.tmxdata.get_tile_gid(x, y + 1, layer), self.map.tmxdata.get_tile_gid(x, y - 1, layer)]
            elif x != 0 and y == 0:
                return num in [self.map.tmxdata.get_tile_gid(x - 1, y, layer), self.map.tmxdata.get_tile_gid(x, y + 1, layer), self.map.tmxdata.get_tile_gid(x - 1, y + 1, layer)]
            else:
                return num in [self.map.tmxdata.get_tile_gid(x, y + 1, layer)]
        elif (x != self.map.tiles_wide-1) and (y == self.map.tiles_high-1):
            if 0 not in [x, y]:
                return num in [self.map.tmxdata.get_tile_gid(x - 1, y, layer), self.map.tmxdata.get_tile_gid(x + 1, y, layer), self.map.tmxdata.get_tile_gid(x - 1, y - 1, layer), self.map.tmxdata.get_tile_gid(x, y - 1, layer),
                               self.map.tmxdata.get_tile_gid(x + 1, y - 1, layer)]
            elif x == 0 and y != 0:
                return num in [self.map.tmxdata.get_tile_gid(x + 1, y, layer), self.map.tmxdata.get_tile_gid(x, y - 1, layer), self.map.tmxdata.get_tile_gid(x + 1, y - 1, layer)]
            elif x != 0 and y == 0:
                return num in [self.map.tmxdata.get_tile_gid(x - 1, y, layer), self.map.tmxdata.get_tile_gid(x + 1, y, layer)]
            else:
                return num in [self.map.tmxdata.get_tile_gid(x + 1, y, layer)]"""

    def on_map(self, sprite):
        offset = 0
        if sprite['location'].x <= 0:
            sprite['location'].x = self.map.width - offset
            return [False, -1, 0]
        if sprite['location'].y <= 0:
            sprite['location'].y = self.map.height - offset
            return [False, 0, -1]
        if sprite['location'].x >= self.map.width:
            sprite['location'].x = offset
            return [False, 1, 0]
        if sprite['location'].y >= self.map.height:
            sprite['location'].y = offset
            return [False, 0, 1]
        return [True, 0, 0]

    # Used for switching to the next map after you go north, south, east or west at the end of the current map.
    def change_map(self, cardinal = None, coordinate = None, location = None, undermap = None):
        self.save_sprite_locs()
        # This for loop moves npcs and animals to other maps when they go off the screen.
        if not self.underworld and self.map:
            for npc in self.map_sprite_data_list[int(self.world_location.x)][int(self.world_location.y)].npcs:
                temp_loc = self.on_map(npc)
                if not temp_loc[0]:
                    if self.map_sprite_data_list[int(self.world_location.x) + temp_loc[1]][int(self.world_location.y) + temp_loc[2]].visited:
                        self.map_sprite_data_list[int(self.world_location.x) + temp_loc[1]][int(self.world_location.y) + temp_loc[2]].npcs.append(npc)
                    else:
                        self.map_sprite_data_list[int(self.world_location.x) + temp_loc[1]][int(self.world_location.y) + temp_loc[2]].moved_npcs.append(npc)
                    self.map_sprite_data_list[int(self.world_location.x)][int(self.world_location.y)].npcs.remove(npc)
            for animal in self.map_sprite_data_list[int(self.world_location.x)][int(self.world_location.y)].animals:
                temp_loc = self.on_map(animal)
                if not temp_loc[0]:
                    if self.map_sprite_data_list[int(self.world_location.x) + temp_loc[1]][int(self.world_location.y) + temp_loc[2]].visited:
                        self.map_sprite_data_list[int(self.world_location.x) + temp_loc[1]][int(self.world_location.y) + temp_loc[2]].animals.append(animal)
                    else:
                        self.map_sprite_data_list[int(self.world_location.x) + temp_loc[1]][int(self.world_location.y) + temp_loc[2]].moved_animals.append(animal)
                    self.map_sprite_data_list[int(self.world_location.x)][int(self.world_location.y)].animals.remove(animal)
            for vehicle in self.map_sprite_data_list[int(self.world_location.x)][int(self.world_location.y)].vehicles:
                temp_loc = self.on_map(vehicle)
                if not temp_loc[0]:
                    if self.map_sprite_data_list[int(self.world_location.x) + temp_loc[1]][int(self.world_location.y) + temp_loc[2]].visited:
                        self.map_sprite_data_list[int(self.world_location.x) + temp_loc[1]][int(self.world_location.y) + temp_loc[2]].vehicles.append(vehicle)
                    else:
                        self.map_sprite_data_list[int(self.world_location.x) + temp_loc[1]][int(self.world_location.y) + temp_loc[2]].moved_vehicles.append(vehicle)
                    self.map_sprite_data_list[int(self.world_location.x)][int(self.world_location.y)].vehicles.remove(vehicle)

        self.guard_alerted = False # Makes it so guards stop attacking you after you change maps
        self.player.vel = vec(0, 0)
        self.player.acc = vec(0, 0)
        direction = cardinal
        offset = 64
        if cardinal:
            if direction == 'north':
                self.world_location -= vec(0, 1)
                self.player.rect.top = self.map.height - offset
                self.player.pos = vec(self.player.rect.center)
            elif direction == 'south':
                self.world_location += vec(0, 1)
                self.player.rect.bottom = offset
                self.player.pos = vec(self.player.rect.center)
            elif direction == 'east':
                self.world_location += vec(1, 0)
                self.player.rect.right = offset
                self.player.pos = vec(self.player.rect.center)
            elif direction == 'west':
                self.world_location -= vec(1, 0)
                self.player.rect.left = self.map.width - offset
                self.player.pos = vec(self.player.rect.center)
            # This part of the code wraps around creating a globe like world
            if self.world_location.x == self.world_width:
                self.world_location.x = 0
            if self.world_location.x < 0:
                self.world_location.x = self.world_width - 1
            if self.world_location.y == self.world_height:
                self.world_location.y = 0
            if self.world_location.y < 0:
                self.world_location.y = self.world_height - 1

        if coordinate:
            # Sets player's location of world map
            self.world_location = vec(coordinate)
            # Sets player's location on local map
            loc = vec(location)
            self.player.rect.center = (int(loc.x * TILESIZE), int(loc.y * TILESIZE))
            self.player.pos = vec(self.player.rect.center)
        if undermap == None:
            selected_map = str(self.map_data_list[int(self.world_location.y)][int(self.world_location.x)] - 1) + '.tmx'
        else:
            selected_map = undermap

        # This block of code sets the positions of the player's followers so they are randomly arranged in a circular orientation around the player.
        for companion in self.companions:
            rand_angle = randrange(0, 360)
            random_vec = vec(170, 0).rotate(-rand_angle)
            companion.rect.center = self.player.rect.center + random_vec
            companion.pos = vec(companion.rect.center)
            companion.offensive = False
            companion.map = selected_map
        self.load_map(selected_map)

    def make_work_station_menu(self, station_type, inventory):
        station = WORK_STATION_DICT[station_type]
        MainMenu(self, self.player, station, inventory)

    def make_lock_menu(self, lock):
        self.lock_menu = Lock_Menu(self, lock)

    def sleep_in_bed(self):
        self.screen.fill(BLACK)
        pg.mixer.music.stop()
        self.draw_text('Sweet dreams....', self.script_font, 25, WHITE, self.screen_width / 2, self.screen_height / 2, align="topright")
        pg.display.flip()
        self.player.add_health(50)
        self.player.add_stamina(50)
        self.player.add_magica(50)
        self.effects_sounds['snore'].play()
        sleep(10)
        self.beg = perf_counter() # resets dt
        pg.mixer.music.play(loops=-1)
        # Changes it to sunrise when you sleep.
        self.darkness = 225
        color_val = 255 - self.darkness
        self.dark_color = (color_val, color_val, color_val)
        self.night = True
        self.day_start_time = pg.time.get_ticks() - NIGHT_LENGTH

    def garbage_collect(self): # This block of code removes everything in memory from previous maps
        for sprite in self.all_sprites:
            if self.player.possessing:
                if sprite in [self.player.possessing, self.player.possessing.body]:
                    continue
            if self.player.in_vehicle:
                if sprite in [self.player.vehicle]:
                    continue
            if sprite in self.companions:
                continue
            elif sprite in self.companion_bodies:
                continue
            elif sprite in [self.player, self.player.human_body, self.player.dragon_body, self.player.body]:
                continue
            else:
                sprite.kill()
                del sprite
        for sprite in self.turrets:
            if not sprite.mother.alive():
                sprite.kill()
                del sprite

        for sprite in self.all_static_sprites:
            sprite.kill()
            del sprite

        del self.map
        gc.collect()  # Forces garbage collection. Without this the game will quickly run out of memory.

    def layer_num_by_name(self, name):
        for i, layer in enumerate(self.map.tmxdata.visible_layers):
            if isinstance(layer, pytmx.TiledTileLayer):
                if layer.name == 'name':
                    return i
                else:
                    return None

    def load_map(self, temp_map):
        #self.sprite_data = self.map_sprite_data_list[int(self.world_location.x)][int(self.world_location.y)]
        self.compass_rot = -math.atan2(49 - self.world_location.y, 89 - self.world_location.x)
        self.compass_rot = math.degrees(self.compass_rot)
        map = self.map_data_list[int(self.world_location.y)][int(self.world_location.x)]
        self.minimap_image = pg.image.load(path.join(map_folder, str(map - 1) + '.png')).convert()

        # Checks to see if the map is bellow the main world level
        map = temp_map
        self.underworld = False

        self.map_type = None
        self.screen.fill(BLACK)
        loading_screen = choice(self.loading_screen_images)
        self.screen.blit(loading_screen, (0, 0))
        self.draw_text('Loading....', self.script_font, 35, WHITE, self.screen_width / 4, self.screen_height * 3/4, align="topright")
        pg.display.flip()
        if not self.new_game:
            self.garbage_collect()
        self.map = TiledMap(self, map)
        if not self.map_sprite_data_list[int(self.world_location.x)][int(self.world_location.y)]:  # Stores the stored map data object so it can be accessed from any map even after the map object dies.
            self.map_sprite_data_list[int(self.world_location.x)][int(self.world_location.y)] = self.map.stored_map_data
        self.sprite_data = self.map_sprite_data_list[int(self.world_location.x)][int(self.world_location.y)]
        self.group = PyscrollGroup(self.map.map_layer)
        self.group.add(self.player)
        self.group.add(self.player.human_body)
        self.group.add(self.player.dragon_body)
        #self.group.change_layer(self.player, self.original_layer)
        #self.group._map_layer = self.map.map_layer # Sets the map as the Pyscroll group base layer.
        self.camera = Camera(self, self.map.width, self.map.height)

        # This block of code is supposed to save edited tile maps, but it's all gooped up.
        #if self.sprite_data.tiledata:
        #    for i, layer in enumerate(self.map.tmxdata.layers):
        #        if isinstance(layer, pytmx.TiledTileLayer): # Excludes object layers
        #            self.map.tmxdata.layers[i].data = self.sprite_data.tiledata[i]
        #else:
        #    self.sprite_data.tiledata = []
        #    for i, layer in enumerate(self.map.tmxdata.layers):
        #        if isinstance(layer, pytmx.TiledTileLayer):# Excludes object layersee
        #            self.sprite_data.tiledata.append(self.map.tmxdata.layers[i].data)

        for i in range(0, 10): # Creates random targets for Npcs
            target = Target(self)
            hits = pg.sprite.spritecollide(target, self.walls, False)  # Kills targets that appear in walls.
            if hits:
                target.kill()

        if self.sprite_data.visited: # Loads stored map data for sprites if you have visited before.
            companion_names = []
            for companion in self.companions:
                companion_names.append(companion.kind)
            for npc in self.sprite_data.npcs:
                if npc['name'] not in companion_names: # Makes it so it doesn't double load your companions.
                    Player(self, npc['location'].x, npc['location'].y, npc['name'])
            for animal in self.sprite_data.animals:
                Animal(self, animal['location'].x, animal['location'].y, animal['name'])
            for vehicle in self.sprite_data.vehicles:
                Vehicle(self, vehicle['location'], vehicle['name'])
            #for breakable in self.sprite_data.breakable:
            #    Breakable(self, breakable['location'], breakable['w'], breakable['h'], breakable['name'], breakable['rotation'])
            for item in self.sprite_data.items:
               if item['name'] in ITEMS:
                    Dropped_Item(self, item['location'], ITEMS[item['name']], item['rotation'])
        else: # Loads animals and NPCs that have moved onto unvisited maps.
            companion_names = []
            for companion in self.companions:
                companion_names.append(companion.kind)
            for npc in self.sprite_data.moved_npcs:
                if npc['name'] not in companion_names: # Makes it so it doesn't double load your companions.
                    Player(self, npc['location'].x, npc['location'].y, npc['name'])
            self.sprite_data.moved_npcs = []
            for animal in self.sprite_data.moved_animals:
                Animal(self, animal['location'].x, animal['location'].y, animal['name'])
            self.sprite_data.moved_animals = []

        # Creates elevation objects if layers have EL in their names. I realize this is inefficient, and hopefully I can find a way to minimize the number of elevation objects created.
        for i, layer in enumerate(self.map.tmxdata.visible_layers):
            if 'EL' in layer.name:
                EL = layer.name
                EL = EL.replace('EL', '')
                EL = int(EL)
                if isinstance(layer, pytmx.TiledTileLayer):
                    for x, y, gid, in layer:
                        if gid != 0:
                            cliff = self.in_surrounding_tiles(x, y, 0, i)
                            elev = Elevation(self, x * self.map.tile_size, y * self.map.tile_size, self.map.tile_size, self.map.tile_size, EL, cliff)
                            hits = pg.sprite.spritecollide(elev, self.elevations, False)  # Kills redundant elevations on top of others.
                            for hit in hits:
                                if hit != elev:
                                    hit.kill()

        # Creates wall and ore block objects if layers have WALLS in their names.
        #exception_tile = 0
        #experimenting with changing tiles
        #print(self.map.tmxdata.tiledgidmap)
        #layer = self.map.tmxdata.layers[2].data
        #layer[0][0] = 2
        """
        if self.map.tmxdata.get_tile_gid(0, 0, 0) != self.map.tmxdata.get_tile_gid(0, 1, 0): # Sees if there is a different tile in the upper left corner to use as a zero tile where no walls will spawn.
            exception_tile = self.map.tmxdata.get_tile_gid(0, 0, 0)  # Tile type to ignore and treat as a zero.
        if self.map.tmxdata.get_tile_gid(1, 0, 0) != self.map.tmxdata.get_tile_gid(0, 1, 0): # Sees if there is a different tile in the upper corner (2nd x pos) to use as an ore tile.
            block_tile = self.map.tmxdata.get_tile_gid(1, 0, 0)
        for i, layer in enumerate(self.map.tmxdata.visible_layers):
            if 'WALLS' in layer.name:
                if isinstance(layer, pytmx.TiledTileLayer):
                    for x, y, gid, in layer:
                        if gid != 0:
                            if gid == block_tile: # Makes ore block objects where the block_tile type tile is.
                                if not self.sprite_data.visited: # Only generates ores if you haven't been here before. Otherwise it generates the remaining ores from the map data object.
                                    block_type = choice(choices(BLOCK_LIST, BLOCK_PROB, k=10))
                                    center = vec(x * self.map.tile_size + self.map.tile_size / 2, y * self.map.tile_size + self.map.tile_size / 2)
                                    Breakable(self, center, self.map.tile_size, self.map.tile_size, block_type)
                            elif self.in_surrounding_tiles(x, y, 0, i):#Checks to see if surrounding tiles are zeros and spawns a wall if they are.
                                wall = Obstacle(self, x * self.map.tile_size, y * self.map.tile_size, self.map.tile_size, self.map.tile_size)
                                hits = pg.sprite.spritecollide(wall, self.walls, False)  # Kills redundant walls on top of others.
                                for hit in hits:
                                    if hit != wall:
                                        hit.kill()
                            elif (gid != exception_tile) and self.in_surrounding_tiles(x, y, exception_tile, i):#Checks to see if surrounding tiles are exceptions and spawns a wall if they are.
                                wall = Obstacle(self, x * self.map.tile_size, y * self.map.tile_size, self.map.tile_size, self.map.tile_size)
                                hits = pg.sprite.spritecollide(wall, self.walls, False)  # Kills redundant walls on top of others.
                                for hit in hits:
                                    if hit != wall:
                                        hit.kill()
        """

        # This section creates ores based off of which tile is used in the map rather than having to create ore objects
        #if self.map_type:
        #    for type in UNDERWORLD:
        #        if type in self.map_type:
        #            # This section generates ore blocks to time in all the spaces with the tile specified in the position (0, 0).
        #            if not self.sprite_data.visited:
        #                block_tile = self.map.tmxdata.get_tile_gid(1, 0, 0)
        #                for location in self.map.tmxdata.get_tile_locations_by_gid(block_tile):
        #                    block_type = choice(choices(BLOCK_LIST, BLOCK_PROB, k = 10))
        #                    center = vec(location[0] * self.map.tile_size + self.map.tile_size/2, location[1] * self.map.tile_size + self.map.tile_size/2)
        #                    block = Breakable(self, center, self.map.tile_size, self.map.tile_size, block_type)
        #                    hits = pg.sprite.spritecollide(block, self.walls, False)  # Kills walls blocks spawn on top of.
        #                    for hit in hits:
        #                        if hit != hit.trunk:
        #                            hit.kill()

        for tile_object in self.map.tmxdata.objects:
            if tile_object.name:
                obj_center = vec(tile_object.x + tile_object.width / 2, tile_object.y + tile_object.height / 2)
                # These are paths for the AIs to follow.
                # if tile_object.name in AIPATHS:
                #     AIPath(self, tile_object.x, tile_object.y, tile_object.width, tile_object.height, tile_object.name)
                # It's super important that all elevations spawn before the player and mobs.
                if 'EL' in tile_object.name:
                    try:
                        _, elev, climb = tile_object.name.split('_')
                        climb = eval(climb)
                    except:
                        _, elev = tile_object.name.split('_')
                        climb = False
                    elev = int(elev)
                    Elevation(self, tile_object.x, tile_object.y, tile_object.width, tile_object.height, elev, climb)
                if tile_object.name == 'jumpable':
                    elev = Elevation(self, tile_object.x, tile_object.y,
                             tile_object.width, tile_object.height, 0, False, 'jumpable')
                if tile_object.name == 'climbable':
                    Elevation(self, tile_object.x, tile_object.y,
                             tile_object.width, tile_object.height, 0, False, 'climbable')
                if tile_object.name == 'player':
                    self.player.pos = vec(obj_center)
                    self.player.rect.center = self.player.pos

                if not self.sprite_data.visited: # Only executes if you have never been to this map before. Otherwise it pulls the data from the stored list.
                    # Loads NPCs from NPC_TYPE_LIST
                    for npc_type in NPC_TYPE_LIST:
                        if tile_object.name in eval(npc_type.upper()):
                            if npc_type == 'animals':
                                Animal(self, obj_center.x, obj_center.y, tile_object.name)
                            else:
                                if self.is_living(tile_object.name):
                                    Player(self, obj_center.x, obj_center.y, tile_object.name)
                    # Loads vehicles
                    for vehicle in VEHICLES:
                        if vehicle == tile_object.name:
                            Vehicle(self, obj_center, vehicle)
                    # Loads items, weapons, and armor placed on the map
                    if tile_object.name in ITEMS:
                        Dropped_Item(self, obj_center, ITEMS[tile_object.name])
                    # Loads fixed rotated items:
                    if '@' in tile_object.name:
                        item, rot = tile_object.name.split('@')
                        rot = int(rot)
                        if item in ITEMS:
                            Dropped_Item(self, obj_center, ITEMS[item], rot)
                    # Used for destructable plants, rocks, ore veins, walls, etc
                    """
                    for item in BREAKABLES:
                        if item in tile_object.name:
                            size = None
                            if '@' in tile_object.name:
                                temp_item, rot = tile_object.name.split('@')
                                rot = int(rot)
                            else:
                                rot = None
                            if 'SZ' in tile_object.name:
                                size, temp_item = tile_object.name.split('SZ')
                            Breakable(self, obj_center, tile_object.width, tile_object.height, item, rot, size)"""

                # Loads detectors used to detect whether quest items have be delivered to the correct locations.
                if 'detector' in tile_object.name:  # These are invisible objects used to detect other objects touching them.
                    Detector(self, tile_object.x, tile_object.y, tile_object.width, tile_object.height, tile_object.name)
                # Loads items/npcs that only appear after their corresponding quests are completed.
                if 'QC' in tile_object.name:
                    _, quest, quest_item = tile_object.name.split('_')
                    if self.quests[quest]['completed']:
                        if quest_item in VEHICLES:
                            Vehicle(self, obj_center, quest_item)
                        if quest_item in self.animals_dict:
                            Animal(self, obj_center.x, obj_center.y, quest_item)
                        if quest_item in self.people:
                            if self.is_living(quest_item):
                                Player(self, obj_center.x, obj_center.y, quest_item)
                        if quest_item in ITEMS:
                            Dropped_Item(self, obj_center, ITEMS[quest_item])
                # Loads items/npcs that should only be there if a quest hasn't been completed
                if 'QU' in tile_object.name:
                    _, quest, quest_item = tile_object.name.split('_')
                    if not self.quests[quest]['completed']:
                        if quest_item in VEHICLES:
                            Vehicle(self, obj_center, quest_item)
                        if quest_item in self.animals_dict:
                            Animal(self, obj_center.x, obj_center.y, quest_item)
                        if quest_item in self.people:
                            if self.is_living(quest_item):
                                Player(self, obj_center.x, obj_center.y, quest_item)
                        if quest_item in ITEMS:
                            Dropped_Item(self, obj_center, ITEMS[quest_item])
                # Loads items/npcs that only appear after a quest has been accepted.
                if 'QA' in tile_object.name:
                    _, quest, quest_item = tile_object.name.split('_')
                    if self.quests[quest]['accepted']:
                        if quest_item in VEHICLES:
                            Vehicle(self, obj_center, quest_item)
                        if quest_item in self.animals_dict:
                            Animal(self, obj_center.x, obj_center.y, quest_item)
                        if quest_item in self.people:
                            if self.is_living(quest_item):
                                Player(self, obj_center.x, obj_center.y, quest_item)
                        if quest_item in ITEMS:
                            Dropped_Item(self, obj_center, ITEMS[quest_item])
                # Loads items/npcs that should only be there if a quest hasn't been accepted
                if 'QN' in tile_object.name:
                    _, quest, quest_item = tile_object.name.split('_')
                    if not self.quests[quest]['accepted']:
                        if quest_item in VEHICLES:
                            Vehicle(self, obj_center, quest_item)
                        if quest_item in self.animals_dict:
                            Animal(self, obj_center.x, obj_center.y, quest_item)
                        if quest_item in self.people:
                            if self.is_living(quest_item):
                                Player(self, obj_center.x, obj_center.y, quest_item)
                        if quest_item in ITEMS:
                            Dropped_Item(self, obj_center, ITEMS[quest_item])
                if 'COMMAND' in tile_object.name: # I used this block of code for killing Alex's body: the character that the black wraith comes out of in the beginning.
                    _, command, npc = tile_object.name.split('_')
                    if npc != 'None':
                        if self.is_living(npc):
                            temp_npc = Player(self, obj_center.x, obj_center.y, npc)
                            if command == 'kill':
                                temp_npc.death()
                # if tile_object.name == 'fire':
                #     Stationary_Animated(self, obj_center, 'fire')
                # if tile_object.name == 'shock':
                #     Stationary_Animated(self, obj_center, 'shock')
                # if tile_object.name == 'charger':
                #     Charger(self, tile_object.x, tile_object.y, tile_object.width, tile_object.height)
                if tile_object.name == 'portal':
                    self.portal_location = obj_center
                if 'firepot' in tile_object.name:
                    number = tile_object.name[-1:]
                    FirePot(self, obj_center, number)
                # if tile_object.name == 'wall':
                #     Obstacle(self, tile_object.x, tile_object.y, tile_object.width, tile_object.height)
                # if tile_object.name == 'light':
                #     LightSource(self, tile_object.x, tile_object.y,
                #              tile_object.width, tile_object.height)
                # if 'lightsource' in tile_object.name:
                #     numvars = tile_object.name.count('_')
                #     if numvars == 2:
                #         _, kind, rot = tile_object.name.split('_')
                #     elif numvars == 1:
                #         _, kind = tile_object.name.split('_')
                #         rot = 0
                #     kind = int(kind)
                #     if rot == 'R':
                #         rot = 0
                #     elif rot == 'U':
                #         rot = 90
                #     elif rot == 'L':
                #         rot = 180
                #     elif rot == 'D':
                #         rot = 270
                #     else:
                #         rot = int(rot)
                #     LightSource(self, tile_object.x, tile_object.y,
                #              tile_object.width, tile_object.height, kind, rot)
                # if tile_object.name == 'inside':
                #     Inside(self, tile_object.x, tile_object.y,
                #              tile_object.width, tile_object.height)
                if tile_object.name == 'nospawn':
                    NoSpawn(self, tile_object.x, tile_object.y,
                             tile_object.width, tile_object.height)
                # if tile_object.name == 'electric entry':
                #     ElectricDoor(self, tile_object.x, tile_object.y, tile_object.width, tile_object.height)
                # if 'entryway' in tile_object.name:  # Used for animated doors that can be opened, closed or locked.
                #     numvars = tile_object.name.count('_')
                #     if numvars == 0:
                #         entryway = Entryway(self, tile_object.x, tile_object.y)
                #     elif numvars == 1:
                #         _, orientation  = tile_object.name.split('_')
                #         entryway = Entryway(self, tile_object.x, tile_object.y, orientation)
                #     elif numvars == 2:
                #         _, orientation, kind  = tile_object.name.split('_')
                #         entryway = Entryway(self, tile_object.x, tile_object.y, orientation, kind)
                #     elif numvars == 3:
                #         _, orientation, kind, name = tile_object.name.split('_')
                #         locked = eval(locked)
                #         entryway = Entryway(self, tile_object.x, tile_object.y, orientation, kind, name)
                #     elif numvars == 4:
                #         _, orientation, kind, name, locked = tile_object.name.split('_')
                #         locked = eval(locked)
                #         entryway = Entryway(self, tile_object.x, tile_object.y, orientation, kind, name, locked)
                if 'door' in tile_object.name:  # This block of code positions the player at the correct door when changing maps
                    door = Door(self, tile_object.x, tile_object.y,
                             tile_object.width, tile_object.height, tile_object.name)
                    if self.previous_map[3:][:-4] == door.name[4:]:
                        # This sets up the direction vector which has x and y values of 1 but the signs tell what direction the player was last heading. So the player will appear on the correct side of the door.
                        direction_x = vec(self.player.direction.x, 0).normalize()
                        direction_y = vec(0, self.player.direction.y).normalize()
                        direction_vector = vec(direction_x.x, direction_y.y)
                        if door.rect.width > 512: # For wide doors/connection points to other maps. This makes it so the player appears in the correct x position on the map
                            self.player.pos.y = door.rect.y + (direction_vector.y * self.map.tile_size)
                            self.player.rect.center = self.player.pos
                        elif door.rect.height > 512: # For wide doors/connection points to other maps. This makes it so the player appears in the correct y position on the map
                            self.player.pos.x = door.rect.x + (direction_vector.x * self.map.tile_size)
                            self.player.rect.center = self.player.pos
                        else:
                            self.player.pos = vec(obj_center) + direction_vector * 64
                            self.player.rect.center = self.player.pos

                try:
                    if 'maptype' in tile_object.name:
                        self.map_type = tile_object.name[8:]
                except:
                    pass

        # Generates trees
        # if len(self.breakable) < 1:
        #    for y in range(0, self.map.tiles_high):
        #        for x in range(0, self.map.tiles_wide):
        #            props = self.map.tmxdata.get_tile_properties(x, y, self.river_layer)
        #            if props == None:
        #                pass
        #            elif 'stump' in props:
        #                tree = props['stump']
        #                Breakable(self, vec(x * TILESIZE + TILESIZE / 2, y * TILESIZE + TILESIZE / 2), TILESIZE, TILESIZE, tree)

            #gids = []
            #for gid, props in self.map.tmxdata.tile_properties.items():
            #    if props and ('stump' in props):
            #        gids.append(gid)
            #for gid in gids:
            #    for x, y, layer in self.map.tmxdata.get_tile_locations_by_gid(gid):
            #        Breakable(self, vec(x * TILESIZE + TILESIZE / 2, y * TILESIZE + TILESIZE / 2), TILESIZE, TILESIZE, tree)


        # Generates random drop items
        """
        if self.map_type in ['mountain', 'forest', 'grassland', 'desert', 'beach']:
            for i in range(0, randrange(1, 15)):
                for item in ITEMS:
                    if 'random drop' in ITEMS[item].keys():
                        if randrange(0, ITEMS[item]['random drop']) < 2:
                            centerx = randrange(200, self.map.width - 200)
                            centery = randrange(200, self.map.height - 200)
                            center = vec(centerx, centery)
                            Dropped_Item(self, center, 'items', item)"""

        # Generates random animals/Npcs on maps that don't have existing animals on them. The type of animal depends on the maptype object in the tmx file.
        if (len(self.mobs) - len(self.companions)) < 4:
            if self.map_type:
                for i in range(0, randrange(10, 30)):
                    animal = choice(list(eval(self.map_type.upper() + '_ANIMALS')))
                    centerx = randrange(200, self.map.width - 200)
                    centery = randrange(200, self.map.height - 200)
                    if animal in self.people:
                        npc = Player(self, centerx, centery, animal)
                        # check for NPCs that spawn in walls and kills them
                        hits = pg.sprite.spritecollide(npc, self.walls, False)
                        if hits:
                            npc.kill()

                    else:
                        anim = Animal(self, centerx, centery, animal)
                        # checks for animals that spawn in walls and kills them.
                        hits = pg.sprite.spritecollide(anim, self.walls, False)
                        if hits:
                            anim.kill()

        # Kills breakables that spawn in water or no spawn areas.
        hits = pg.sprite.groupcollide(self.breakable, self.nospawn, False, False)
        for hit in hits:
            hit.trunk.kill()
            hit.kill()
        #hits = pg.sprite.groupcollide(self.breakable, self.water, False, False)
        #for hit in hits:
        #    hit.trunk.kill()
        #    hit.kill()
        #hits = pg.sprite.groupcollide(self.breakable, self.shallows, False, False)
        #for hit in hits:
        #    hit.trunk.kill()
        #    hit.kill()
        #hits = pg.sprite.groupcollide(self.breakable, self.long_grass, False, False)
        #for hit in hits:
        #    hit.trunk.kill()
        #    hit.kill()


        # check for fish out of water and kills them
        #hits = pg.sprite.groupcollide(self.animals, self.water, False, False)
        #for animal in self.animals:
        #    if 'fish' in animal.kind['name']:
        #        if animal not in hits:
        #            animal.death(True)
        #    if 'shark' in animal.kind['name']:
        #        if animal not in hits:
        #            animal.death(True)

        # Adds all players and companions
        #self.group.add(self.player.body)
        #for sprite in self.companions:
        #    if sprite not in self.animals:
        #        self.group.add(sprite.body)
        #    else:
        #        self.group.add(sprite)
        # Adds vehicles back to group
        #if self.player.in_vehicle:
        #    self.group.add(self.player.vehicle)
        #    if self.player.vehicle.cat == 'tank':
        #        self.group.add(self.player.vehicle.turret)
        self.sprite_data.visited = True
        self.previous_map = map
        self.respawn = False
        if self.new_game:
            self.new_game = False

        # Starts music based on map
        if self.map_type == None:
            self.bg_music = BG_MUSIC
        else:
            self.bg_music = eval(self.map_type.upper() + '_MUSIC')
        if self.bg_music != self.previous_music: #Only starts new music if type of map changes
            self.previous_music = self.bg_music
            pg.mixer.music.fadeout(300)
            pg.mixer.music.load(path.join(music_folder, self.bg_music))
            pg.mixer.music.play(loops=-1)

        # sets up NPC target list for map
        self.target_list = [self.random_targets, self.work_stations, self.moving_targets, self.aipaths]
        for x in self.target_list:  # Replaces empty sprite groups with the random targets group.
            if list(x) == []:
                x = self.random_targets

        self.clock.tick(FPS)  # resets dt


    def run(self):
        # game loop - set self.playing = False to end the game
        self.playing = True
        self.beg = perf_counter()
        while self.playing:
            self.events()
            if not self.paused:
                self.update()
            self.draw()

    def quit(self):
        pg.quit()
        sys.exit()

    def night_transition(self):
        now = pg.time.get_ticks()
        if now - self.last_darkness_change > NIGHTFALL_SPEED:
            self.darkness += 1
            self.last_darkness_change = now
            if self.darkness > MAX_DARKNESS:
                self.darkness = MAX_DARKNESS
                self.day_start_time = now
                self.night = True
                self.nightfall = False
            #color_val = 255 - self.darkness
            self.dark_color = (self.darkness, self.darkness, self.darkness)

    def day_transition(self):
        now = pg.time.get_ticks()
        if now - self.last_darkness_change > NIGHTFALL_SPEED:
            self.darkness -= 1
            if self.darkness < 0:
                self.darkness = 0
                self.day_start_time = now
                self.night = False
                self.sunrise = False
            #color_val = 255 - self.darkness
            self.dark_color = (self.darkness, self.darkness, self.darkness)

    def update(self):
        # update portion of the game loop
        # Controls the day turning to night and vice versa
        now = pg.time.get_ticks()
        if self.night:
            if now - self.day_start_time > NIGHT_LENGTH:
                self.sunrise = True
                self.day_transition()
        elif now - self.day_start_time > DAY_LENGTH:
            self.nightfall = True
            self.night_transition()
        if now - self.last_mobhp_update > MOB_HEALTH_SHOW_TIME: # Turns off mob hp bar if when you aren't attacking the mob.
            self.show_mobhp = False

        # updates all sprites that are on screen and puts on screen sprites into groups for hit checks.
        self.message_text = False
        # finds static sprites (ones you don't see) on screen.
        self.obstacles_on_screen.empty()
        self.walls_on_screen.empty()
        self.barriers_on_screen.empty()
        self.elevations_on_screen.empty()
        self.climbs_on_screen.empty()
        self.inside_on_screen.empty()
        for sprite in self.all_static_sprites:
            if self.on_screen(sprite, 400):
                if sprite in self.obstacles:
                    self.obstacles_on_screen.add(sprite)
                    if sprite in self.walls:
                        self.walls_on_screen.add(sprite)
                        self.barriers_on_screen.add(sprite)
                elif sprite in self.elevations:
                    self.elevations_on_screen.add(sprite)
                    self.barriers_on_screen.add(sprite)
                    if sprite in self.climbs:
                        self.climbs_on_screen.add(sprite)
                elif sprite in self.inside:
                    self.inside_on_screen.add(sprite)

        # dynamic sprites on screen
        self.vehicles_on_screen.empty()
        #self.entryways_on_screen.empty()
        #self.electric_doors_on_screen.empty()
        self.breakable_on_screen.empty()
        self.corpses_on_screen.empty()
        self.dropped_items_on_screen.empty()
        self.fires_on_screen.empty()
        self.mobs_on_screen.empty()
        self.npcs_on_screen.empty()
        self.npc_bodies_on_screen.empty()
        self.animals_on_screen.empty()
        self.moving_targets_on_screen.empty()
        self.sprites_on_screen.empty()
        self.lights_on_screen.empty()
        for sprite in self.all_sprites:
            if self.on_screen(sprite):
                self.sprites_on_screen.add(sprite)
                # if sprite in self.entryways:
                #     self.entryways_on_screen.add(sprite)
                #     if sprite in self.electric_doors:
                #         self.electric_doors_on_screen.add(sprite)
                if sprite in self.vehicles:
                    self.vehicles_on_screen.add(sprite)
                    if sprite in self.walls:
                        self.walls_on_screen.add(sprite)
                elif sprite in self.fires:
                    self.fires_on_screen.add(sprite)
                elif sprite in self.breakable:
                        self.breakable_on_screen.add(sprite)
                elif sprite in self.corpses:
                        self.corpses_on_screen.add(sprite)
                elif sprite in self.dropped_items:
                        self.dropped_items_on_screen.add(sprite)
                elif sprite in self.npc_bodies:
                    self.npc_bodies_on_screen.add(sprite)
                elif sprite in self.moving_targets:
                    self.moving_targets_on_screen.add(sprite)
                    if sprite in self.mobs:
                        self.mobs_on_screen.add(sprite)
                        if sprite in self.animals:
                            self.animals_on_screen.add(sprite)
                        elif sprite in self.npcs:
                            self.npcs_on_screen.add(sprite)
            elif self.on_screen(sprite, 200):
                if sprite in self.lights:
                    self.lights_on_screen.add(sprite)
            elif sprite in self.bullets: # Kills bullets not on screen.
                sprite.kill()
            elif sprite == self.player.vehicle:
                sprite.update()
            elif sprite in self.companions:
                sprite.update()
            elif sprite in self.companion_bodies:
                sprite.update()
        self.sprites_on_screen.update()
        self.camera.update(self.player)
        self.group.center(self.player.rect.center)

        # Kills certain off screen sprites
        for corpse in self.corpses:
            if corpse not in self.corpses_on_screen:
                corpse.kill()

        ## Used for playing fire sounds at set distances:
        #closest_fire = None
        #previous_distance = 30000
        #for sprite in self.fires_on_screen:    # Finds the closest fire and ignores the others.
        #    player_dist = self.player.pos - sprite.pos
        #    player_dist = player_dist.length()
        #    if previous_distance > player_dist:
        #        closest_fire = sprite
        #        previous_distance = player_dist

        #if closest_fire:
        #    if previous_distance < 400:  # This part makes it so the fire volume decreases as you walk away from it.
        #        volume = 150 / (previous_distance * 2 + 0.001)
        #        self.channel4.set_volume(volume)
        #        if not self.channel4.get_busy():
        #            self.channel4.play(self.effects_sounds['fire crackle'], loops=-1)
        #    else:
        #        self.channel4.stop()
        #else:
        #    self.channel4.stop()

        # The following are hit checks between moving objects. All tile-based hit checks are done in teh sprites.py using each sprites tile_props/next_tile_props
        # These hit checks only happen if the player insn't in a flying vehicle.
        if self.player not in self.flying_vehicles:

            # player hits portal
            hits = pg.sprite.spritecollide(self.player, self.portals, False, pg.sprite.collide_circle_ratio(0.35))
            if hits:
                now = pg.time.get_ticks()
                if now - hits[0].spawn_time > 1500: # Makes it so you can see the portal appear before it transfers you to a new map
                    self.change_map(None, hits[0].coordinate, hits[0].location)

            # player hits entrance to other map
            hits = pg.sprite.spritecollide(self.player, self.doors, False)
            if hits:
                # Sets player's location on local map
                loc = hits[0].loc
                self.player.rect.center = (int(loc.x * self.map.tile_size), int(loc.y * self.map.tile_size))
                self.player.pos = vec(self.player.rect.center)
                self.change_map(None, None, None, hits[0].map)

            # player melee hits entryway (door)
            #if self.player.melee_playing:
            #    hits = pg.sprite.spritecollide(self.player.body, self.entryways_on_screen, False, melee_hit_rect)
            #    if hits:
            #        if hits[0] in self.electric_doors_on_screen:
            #            hits[0].gets_hit(40, 0, 0, 100, self.player)
            #        else:
            #            self.player.does_melee_damage(hits[0])

            # player hits entryway (a door)
            #hits = pg.sprite.spritecollide(self.player, self.entryways_on_screen, False, entryway_collide)
            #if hits:
            #    self.message_text = True
            #    if hits[0].locked:
            #        self.message = hits[0].name + ' is locked. ' + pg.key.name(self.key_map['interact']).upper() + ' to unlock'
            #        if self.player.e_down:
            #            if not self.in_lock_menu:
            #                self.in_lock_menu = self.in_menu = True
            #                self.lock_menu = Lock_Menu(self, hits[0])
            #                self.message_text = False
            #             self.player.e_down = False
            #     elif not hits[0].opened:
            #         self.message = pg.key.name(self.key_map['interact']).upper() + ' to open'
            #         if self.player.e_down:
            #             hits[0].open = True
            #             hits[0].close = False
            #             self.message_text = False
            #             self.player.e_down = False
            #     elif hits[0].opened:
            #         self.message = pg.key.name(self.key_map['interact']).upper() + ' to close'
            #         if self.player.e_down:
            #             hits[0].close = True
            #             hits[0].open = False
            #             self.message_text = False
            #             self.player.e_down = False

            # player hit corps
            hits = pg.sprite.spritecollide(self.player, self.corpses_on_screen, False)
            if hits:
                self.message_text = True
                self.message = pg.key.name(self.key_map['interact']).upper() + " to loot"
                if self.player.e_down:
                    MainMenu(self, self.player, 'Looting', hits[0].inventory)
                    self.message_text = False
                    self.player.e_down = False

            # Player is in talking range of NPC
            if True not in [self.message_text, self.in_menu]:
                hits = pg.sprite.spritecollide(self.player, self.npcs_on_screen, False, npc_talk_rect)
                if hits:
                    if hits[0].dialogue:
                        if not self.in_dialogue_menu:
                            now = pg.time.get_ticks()
                            if now - self.last_dialogue > 2000:
                                self.message_text = True
                                self.message = pg.key.name(self.key_map['interact']).upper() + ' to talk'
                                if self.player.e_down:
                                    hits[0].ai.target = self.player
                                    hits[0].talk_attempt = True
                                    self.message_text = False
                                    self.player.e_down = False
            if self.dialogue_menu_npc:
                self.dialogue_menu = Dialogue_Menu(self, self.dialogue_menu_npc)

            # player hits elevation change
            hits = pg.sprite.spritecollide(self.player, self.elevations_on_screen, False)
            if hits:
                keys = pg.key.get_pressed()
                if keys[self.key_map['climb']]:
                    if self.player.stats['stamina'] > 10 and not self.player.in_vehicle:
                        self.player.climbing = True
                    else:
                        if self.player.in_vehicle:
                            if 'climbables' not in self.player.vehicle.collide_list:
                                if 'obstacles' not in self.player.vehicle.collide_list:
                                    self.player.climbing = True
            else:
                self.player.climbing = False
                if not self.player.jumping:
                    if self.player.elevation > 1:
                        self.player.falling = True
                        self.player.pre_jump()
                    self.player.elevation = 0

            # player hits dropped item
            hits = pg.sprite.spritecollide(self.player, self.dropped_items_on_screen, False, pg.sprite.collide_circle_ratio(0.75))
            for hit in hits:
                if hit.name not in ['fire pit']:
                    self.message_text = True
                    if self.message != "You are carrying too much weight.":
                        self.message = pg.key.name(self.key_map['interact']).upper() + 'to pick up'
                    if self.player.e_down:
                        if self.player.add_inventory(hit.item):
                            #self.player.calculate_weight()
                            self.player.e_down = False
                            self.message_text = False
                            hit.kill()
                        else:
                            self.message = "You are carrying too much weight."

            # player melee hits breakable: a bush, tree, rock, ore vein, shell, glass, etc.
            if self.player.melee_playing:
                hits = pg.sprite.spritecollide(self.player.body, self.breakable_on_screen, False, breakable_melee_hit_rect)
                for bush in hits:
                    if self.player.equipped[self.player.weapon_hand] == None:
                        weapon_type = None
                    else:
                        weapon_type = WEAPONS[self.player.equipped[self.player.weapon_hand]]['type']
                        if not self.player.change_used_item('weapons', self.player.equipped[self.player.weapon_hand]): # Makes it so pickaxes and other items deplete their hp
                            weapon_type = None
                    bush.gets_hit(weapon_type)

            # player hits empty vehicle or mech suit
            if not self.player.in_vehicle:
                if self.player.possessing == None:
                    hits = pg.sprite.spritecollide(self.player, self.mechsuits, False)
                    if hits:
                        if (hits[0].driver == None) and hits[0].living:
                            self.message_text = True
                            self.message = pg.key.name(self.key_map['interact']).upper() + " to enter, T to exit"
                        if self.player.e_down:
                            if hits[0].living:
                                hits[0].possess(self.player)
                            self.message_text = False
                            self.player.e_down = False

                hits = pg.sprite.spritecollide(self.player, self.vehicles_on_screen, False, pg.sprite.collide_circle_ratio(0.95))
                if hits:
                    if not hits[0].occupied and hits[0].living:
                        self.message_text = True
                        self.message = pg.key.name(self.key_map['interact']).upper() + ' to enter, ' + pg.key.name(self.key_map['dismount']).upper() + ' to exit'
                    if self.player.e_down:
                        if hits[0].living:
                            hits[0].enter_vehicle(self.player)
                        self.message_text = False
                        self.player.e_down = False
                hits = pg.sprite.spritecollide(self.player, self.flying_vehicles, False)
                if hits:
                    if not hits[0].occupied and hits[0].living:
                        self.message_text = True
                        if self.message != "You need a key to operate this vehicle.":
                            self.message = pg.key.name(self.key_map['interact']).upper() + ' to enter, ' + pg.key.name(self.key_map['dismount']).upper() + ' to exit'
                    if self.player.e_down:
                        self.player.e_down = False
                        if hits[0].living:
                            if hits[0].kind == 'airship':
                                if 'airship key' in self.player.inventory['items']:
                                    hits[0].enter_vehicle(self.player)
                                    self.message_text = False
                                elif len(self.companions.sprites()) > 0:
                                    self.message_text = False
                                    is_felius = False
                                    for companion in self.companions:
                                        if companion.name == 'Felius':
                                            is_felius = True
                                    if is_felius:
                                        hits[0].enter_vehicle(self.player)
                                else:
                                    self.message = "You need a key to operate this vehicle."
                            else:
                                hits[0].enter_vehicle(self.player)
        else:
            self.player.swimming = False
            self.player.in_shallows = False
            self.player.in_grass = False


        """
        #Moving into Player class into the melee def. It makes way more sense to check hits in there.
        # NPC or Player melee hits moving_target
        hits = pg.sprite.groupcollide(self.npc_bodies_on_screen, self.moving_targets_on_screen, False, False, melee_hit_rect)
        for body in hits:
            if body.mother.in_player_vehicle:
                pass
            for mob in hits[body]:
                if mob.immaterial:
                    if body.mother.equipped[body.mother.weapon_hand]:
                        if ('aetherial' not in body.mother.equipped[body.mother.weapon_hand]) or ('plasma' not in body.mother.equipped[body.mother.weapon_hand]):
                            continue
                if mob.in_player_vehicle:
                    continue
                elif body.mother == mob:
                    continue
                elif mob in self.flying_vehicles:
                    continue
                elif mob.in_vehicle:
                    continue
                elif body.mother.in_vehicle: # Makes it so you can't attack your own vehicle
                    if mob == body.mother.vehicle:
                        continue
                if body.mother.melee_playing:
                    if body.mother == self.player:
                        if mob not in self.companions:
                            mob.offensive = True
                            mob.provoked = True
                    if body.mother == self.player.possessing:
                        if mob not in self.companions:
                            mob.offensive = True
                            mob.provoked = True
                    body.mother.does_melee_damage(mob)
        """

        # fire hit moving target
        hits = pg.sprite.groupcollide(self.moving_targets, self.fires_on_screen, False, False, pg.sprite.collide_circle_ratio(0.5))
        for mob in hits:
            if mob in self.occupied_vehicles:
                pass
            elif mob.in_vehicle:
                pass
            elif mob.in_player_vehicle:
                pass
            else:
                if 'dragon' not in mob.equipped['race']:
                    if 'wyvern' not in mob.equipped['race']:
                        for fire in hits[mob]:
                            mob.gets_hit(fire.damage, 0, mob.rot - 180)

        # explosion hit moving target
        hits = pg.sprite.groupcollide(self.moving_targets, self.explosions, False, False, pg.sprite.collide_circle_ratio(0.5))
        for mob in hits:
            if mob in self.occupied_vehicles:
                pass
            elif mob.in_vehicle:
                pass
            elif mob.in_player_vehicle:
                pass
            else:
                for fire in hits[mob]:
                    mob.gets_hit(fire.damage, 0, mob.rot - 180)

        # fireball hit moving target
        hits = pg.sprite.groupcollide(self.moving_targets, self.fireballs, False, False, fire_collide)
        for mob in hits:
            for bullet in hits[mob]:
                if mob in self.occupied_vehicles:
                    if bullet.mother == mob.driver: # Ignores fireballs from driver
                        pass
                    elif bullet.mother in self.companions:
                        pass
                    elif mob.driver == self.player:
                        if bullet.mother in self.player_group:
                            pass
                        else: # When enemy fireballs hit vehicle player is in.
                            mob.gets_hit(bullet.damage, 0, bullet.rot)
                            bullet.explode(mob)
                    else: # When fireball hits non player vehicle
                        mob.gets_hit(bullet.damage, 0, bullet.rot)
                        bullet.explode(mob)
                elif bullet.mother != mob:
                    if not mob.in_player_vehicle:
                        if bullet.mother == self.player:
                            mob.provoked = True
                        mob.gets_hit(bullet.damage, bullet.knockback, bullet.rot)
                        bullet.explode(mob)
                        if bullet.mother == self.player:
                            self.player.stats['marksmanship hits'] += 1

        # bullets hit moving_target
        hits = pg.sprite.groupcollide(self.moving_targets, self.bullets, False, False, pg.sprite.collide_circle_ratio(0.5))
        for mob in hits:
            for bullet in hits[mob]:
                if mob in self.occupied_vehicles:
                    if bullet.mother == mob.driver: # Ignores bullet from driver that hit vehicle
                        pass
                    elif bullet.mother in self.companions:
                        pass
                    elif bullet.mother in self.turrets: # Ignores bullets from turrets of vehicle that's shooting
                        if bullet.mother.mother == mob:
                            pass
                    elif mob.driver == self.player:
                        if bullet.mother in self.player_group:
                            pass
                        else: # When enemy bullet hit vehicle player is in.
                            mob.gets_hit(bullet.damage, 0, bullet.rot)
                            bullet.death(mob)
                    else: # When bullet hits non player vehicle
                        mob.gets_hit(bullet.damage, 0, bullet.rot)
                        bullet.death(mob)
                elif bullet.mother != mob:
                    if not mob.immaterial or bullet.energy:
                        if not mob.in_player_vehicle:
                            if mob != self.player:
                                if bullet.mother == self.player: # Makes it so NPCs attack you if you shoot them.
                                    #if mob.aggression in ['awd', 'sap', 'fup']:
                                    #    mob.offensive = True
                                    #    mob.provoked = True
                                    mob.gets_hit(bullet.damage, bullet.knockback, bullet.rot)
                                    self.hud_mobhp = mob.stats['health'] / mob.stats['max health']
                                    self.show_mobhp = True
                                    self.last_mobhp_update = pg.time.get_ticks()
                                    bullet.death(mob)
                                else:
                                    mob.gets_hit(bullet.damage, bullet.knockback, bullet.rot)
                                    bullet.death(mob)
                            else:
                                if not mob.immaterial or bullet.energy:
                                    if not mob.immaterial or bullet.energy:
                                        mob.gets_hit(bullet.damage, bullet.knockback, bullet.rot)
                                    bullet.death(mob)
                            if bullet.mother == self.player:
                                mob.provoked = True
                                self.player.stats['marksmanship hits'] += 1



        """
        # mob hit elevation object
        hits = pg.sprite.groupcollide(self.mobs_on_screen, self.elevations_on_screen, False, False)
        for mob in self.mobs_on_screen:
            if mob in hits:
                for elev in hits[mob]: # Makes it so NPCs can climb and jump.
                    if elev.elevation - mob.elevation > 2:
                        if (not mob.flying) and (mob in self.animals_on_screen):
                            mob.hit_wall = True
                            mob.last_wall_hit = pg.time.get_ticks()
                            mob.seek_random_target()
                        elif (mob in self.companions) or mob.target == self.player:
                            mob.running = False
                            mob.climbing = True
                            mob.last_climb = pg.time.get_ticks()
                        elif mob in self.npcs_on_screen:
                            chance = randrange(0, 600)
                            if chance == 1:
                                mob.climbing = True
                            else:
                                mob.hit_wall = True
                                mob.last_wall_hit = pg.time.get_ticks()
                                mob.seek_random_target()
                    elif elev.elevation - mob.elevation > 1:
                        if (not mob.flying) and (mob in self.animals_on_screen):
                            mob.hit_wall = True
                        elif (mob in self.companions) or mob.target == self.player:
                            mob.jumping = True
                            mob.last_climb = pg.time.get_ticks()
                        elif mob in self.npcs_on_screen:
                            chance = randrange(0, 200)
                            if chance == 1:
                                mob.jumping = True
                            else:
                                mob.hit_wall = True
                                mob.last_wall_hit = pg.time.get_ticks()
                                mob.seek_random_target()
            else:
                mob.climbing = False
                if not mob.jumping:
                    if mob.elevation > 1:
                        mob.falling = True
                        mob.pre_jump()
                    mob.elevation = 0
        
        # fireball hits firepit
        hits = pg.sprite.groupcollide(self.firepits, self.fireballs, False, False, fire_collide)
        for item in hits:
            for bullet in hits[item]:
                if not item.lit:
                    bullet.explode(item)
                    item.lit = True
                    center = vec(item.rect.center)
                    Stationary_Animated(self, center, 'fire')
                    #Work_Station(self, center.x - self.map.tile_size/2, center.y - self.map.tile_size/2, self.map.tile_size, self.map.tile_size, 'cooking fire')
        # fire hits firepit
        hits = pg.sprite.groupcollide(self.firepits, self.fires_on_screen, False, False, pg.sprite.collide_circle_ratio(0.5))
        for item in hits:
            if not item.lit:
                item.lit = True
                center = vec(item.rect.center)
                Stationary_Animated(self, center, 'fire')
                #Work_Station(self, center.x - self.map.tile_size/2, center.y - self.map.tile_size/2, self.map.tile_size, self.map.tile_size, 'cooking fire')


        # vehicle hit breakable
        hits = pg.sprite.groupcollide(self.breakable_on_screen, self.vehicles_on_screen, False, False, vehicle_collide_any)
        for breakable in hits:
           for vehicle in hits[breakable]:
               if not vehicle.flying:
                    breakable.gets_hit(vehicle.cat, 0, 0, 0)

        # explosion hit breakable
        hits = pg.sprite.groupcollide(self.breakable_on_screen, self.explosions, False, False, pg.sprite.collide_circle_ratio(0.5))
        for breakable in hits:
            for exp in hits[breakable]:
                if exp.damage > 200:
                    breakable.gets_hit('explosion', 0, 0, 0)
        
        # fireball hits firepot
        hits = pg.sprite.groupcollide(self.firepots, self.fireballs, False, False, fire_collide)
        for pot in hits:
            pot.hit = True
            for bullet in hits[pot]:
                bullet.explode()
            self.player.stats['marksmanship hits'] += 1

        # dropped item hit water
        hits = pg.sprite.groupcollide(self.dropped_items_on_screen, self.water_on_screen, False, False)
        for hit in hits:
            if 'dead' in hit.item and 'fish' in hit.item:
                if hit.dropped_fish:
                    animal_dict = self.animals_dict[hit.item[5:]]
                    animal_name = animal_dict['name']
                    Animal(self, hit.pos.x, hit.pos.y, animal_name)
                    hit.kill()
            elif not hit.floats:
                hit.kill()

        # detectable hit detector
        hits = pg.sprite.groupcollide(self.detectors, self.detectables, False, False)
        for detector in hits:
            if not detector.detected:
                for detectable in hits[detector]:
                    if detector.item in detectable.name:
                        detector.trigger(detectable)
                        if detector.kill_item:
                            detectable.kill()

        # npc hits doors and opens them
        hits = pg.sprite.groupcollide(self.npcs_on_screen, self.entryways_on_screen, False, False, entryway_collide)
        for npc in hits:
            for entryway in hits[npc]:
                if not entryway.locked:
                    if not entryway.opened:
                        entryway.open = True
                        entryway.close = False
                    elif npc.target in self.entryways_on_screen:
                        if not entryway.open:
                            entryway.close = True

        # land vehicle hits water
        hits = pg.sprite.groupcollide(self.land_vehicles, self.water_on_screen, False, False)
        for vcle in hits:
            vcle.gets_hit(2, 0, 0)

        # npc hit AI path
        hits = pg.sprite.groupcollide(self.npcs_on_screen, self.aipaths, False, False)
        for npc in self.npcs_on_screen:
            if npc in hits:
                now = pg.time.get_ticks()
                if now - npc.last_path_change > 3000:
                    npc.aipath = hits[npc]  #sets aipath to list of paths hit
            else:
                npc.aipath = None"""

    def render_lighting(self, underworld = False):
        for sprite in self.sprites_on_screen:
            if sprite in self.lights:
                self.lights_on_screen.add(sprite)

        # draw the light mask (gradient) onto fog image
        if self.underworld:
            self.fog.fill((180, 180, 180))
        else:
            self.fog.fill(self.dark_color)

        # tile_based flame lights
        xi, xf, yi, yf = self.map.get_tiles_on_screen(self.player.pos.x, self.player.pos.y)
        for y in range(yi, yf):
            for x in range(xi, xf):
                # When you are outside, lights inside should be off, otherwise all lights should be on.
                if self.map.stored_map_data.lights[y][x]:
                    if (not self.player_inside and not ('roof' in self.map.tile_props[y][x] and (self.map.tile_props[y][x]['roof'] != ''))) or self.player_inside and (('roof' in self.map.tile_props[y][x] and (self.map.tile_props[y][x]['roof'] != ''))):  # Prevents drawing lights inside houses so they don't shine through roofs when you are outside.
                        if self.map.stored_map_data.lights[y][x] == 'flame':
                            light_mask = self.flame_light_mask
                            light_mask_rect = self.flame_light_mask_rect
                        elif self.map.stored_map_data.lights[y][x] == 'coals':
                            light_mask = self.coals_light_mask
                            light_mask_rect = self.coals_light_mask_rect
                        elif self.map.stored_map_data.lights[y][x] == 'candle':
                            light_mask = self.candle_light_mask
                            light_mask_rect = self.candle_light_mask_rect
                        light_mask_rect.center = (x * self.map.tile_size + self.map.tile_size/2, y * self.map.tile_size + self.map.tile_size/2)
                        lightrect = self.camera.apply_rect(light_mask_rect)
                        self.fog.blit(light_mask, lightrect)

        for light in self.lights_on_screen:
            x, y = self.map.get_tile_pos(light.pos.x, light.pos.y)
            if (light == self.player) or (not self.player_inside and not ('roof' in self.map.tile_props[y][x] and (self.map.tile_props[y][x]['roof'] != ''))) or self.player_inside and (('roof' in self.map.tile_props[y][x] and (self.map.tile_props[y][x]['roof'] != ''))):  # Prevents drawing lights inside houses so they don't shine through roofs.
                lightrect = self.camera.apply_rect(light.light_mask_rect)
                self.fog.blit(light.light_mask, lightrect)

        self.screen.blit(self.fog, (0, 0), special_flags=pg.BLEND_RGB_SUB)

    def rot_center(self, image, angle):
        orig_rect = image.get_rect()
        rot_image = pg.transform.rotate(image, angle)
        rot_rect = orig_rect.copy()
        rot_rect.center = rot_image.get_rect().center
        rot_image = rot_image.subsurface(rot_rect).copy()
        return rot_image

    def draw_minimap(self):
        mini_rect = pg.Rect((self.screen_width - self.map.minimap.rect.width), 0, self.map.minimap.rect.width, self.map.minimap.rect.height)
        width = self.screen_width - self.map.minimap.rect.width
        scale = self.map.minimap.rect.width / self.map.width
        map_pos = vec(self.player.rect.center) * scale
        pos_rect = pg.Rect(0, 0, 20, 20)
        pos_rect.center = (int(map_pos.x + width), int(map_pos.y))
        temp_compass_img = self.rot_center(self.compass_image.copy(), self.compass_rot)
        self.screen.blit(self.map.minimap.image, (width, 0))
        self.screen.blit(temp_compass_img, (width - self.map.tile_size, 0))
        pg.draw.rect(self.screen, WHITE, mini_rect, 2)
        pg.draw.rect(self.screen, YELLOW, pos_rect, 1)

    def draw_overmap(self):
        cell_width = self.screen_height / len(self.map_data_list[0])
        cell_height = self.screen_height / len(self.map_data_list)
        offsetx = int(self.world_location.x * cell_width)
        offsety = int(self.world_location.y * cell_height)
        scalex = cell_width / self.map.width
        scaley = cell_height / self.map.height
        currentmap_rect = pg.Rect(0, 0, cell_width, cell_height)
        currentmap_rect.topleft = (offsetx, offsety)
        map_pos = vec(self.player.rect.centerx * scalex, self.player.rect.centery * scaley)
        pos_rect = pg.Rect(0, 0, 3, 3)
        pos_rect.center = (int(map_pos.x + offsetx), int(map_pos.y + offsety))
        self.screen.blit(self.over_minimap_image, (0, 0))
        pg.draw.rect(self.screen, YELLOW, currentmap_rect, 4)
        pg.draw.rect(self.screen, RED, pos_rect, 4)


    def draw(self):
        pg.display.set_caption("Legends of Zhara")
        #self.group.draw(self.screen, self) # Used with my monkey patched version of the old pyscroll.
        self.group.draw(self.screen)

        # Only draws roofs when outside of buildings
        hits = pg.sprite.spritecollide(self.player, self.inside_on_screen, False)
        if not (hits or self.player.inside):
            self.player_inside = False
        else:
            self.player_inside = True
            if self.player.in_vehicle:
                if self.player.vehicle in self.flying_vehicles:
                    self.player_inside = False

        # Draws flying vehicle sprites after roves.
        #for sprite in self.flying_vehicles:
        #    self.screen.blit(sprite.image, self.camera.apply(sprite))

        if self.underworld:
            self.render_lighting(True)
        elif True in [self.night, self.sunrise, self.nightfall]:
            self.render_lighting()
        #if self.hud_map:
        #    self.draw_minimap()
        if self.hud_overmap:
            self.draw_overmap()

        if self.draw_debug: # Draws hit rects for debugging
            #for wall_rect in self.map.walls_list:
            #    pg.draw.rect(self.screen, CYAN, self.camera.apply_rect(wall_rect), 1)
            for ai in self.ais:
                for i, path in enumerate(ai.found_path):
                    pathrect = pg.Rect(path.pos[0] * self.map.tile_size, path.pos[1] * self.map.tile_size, self.map.tile_size, self.map.tile_size)
                    pg.draw.rect(self.screen, RED, self.camera.apply_rect(pathrect), 1)
                if ai.meander:
                    pathrect = pg.Rect(ai.temp_target[0] * self.map.tile_size, ai.temp_target[1] * self.map.tile_size, self.map.tile_size,
                                       self.map.tile_size)
                    pg.draw.rect(self.screen, RED, self.camera.apply_rect(pathrect), 1)
            for vehicle in self.vehicles_on_screen:
                pg.draw.rect(self.screen, CYAN, self.camera.apply_rect(vehicle.hit_rect), 1)
                pg.draw.rect(self.screen, GREEN, self.camera.apply_rect(vehicle.hit_rect2), 1)
                pg.draw.rect(self.screen, RED, self.camera.apply_rect(vehicle.hit_rect3), 1)
            for mob in self.mobs_on_screen:
                pg.draw.rect(self.screen, YELLOW, self.camera.apply_rect(mob.hit_rect), 1)
            for item in self.dropped_items:
                pg.draw.rect(self.screen, YELLOW, self.camera.apply_rect(item.hit_rect), 1)
            #for npc in self.npcs_on_screen:
            #    pg.draw.rect(self.screen, WHITE, self.camera.apply_rect(npc.temp_target.hit_rect), 1)
            for target in self.random_targets:
                pg.draw.rect(self.screen, BLUE, self.camera.apply_rect(target.rect), 1)
            pg.draw.rect(self.screen, YELLOW, self.camera.apply_rect(self.player.hit_rect), 1)
            pg.draw.rect(self.screen, YELLOW, self.camera.apply_rect(self.player.body.mid_weapon_melee_rect), 1)
            pg.draw.rect(self.screen, YELLOW, self.camera.apply_rect(self.player.body.weapon_melee_rect), 1)
            pg.draw.rect(self.screen, YELLOW, self.camera.apply_rect(self.player.body.melee_rect), 1)
            pg.draw.rect(self.screen, YELLOW, self.camera.apply_rect(self.player.body.mid_weapon2_melee_rect), 1)
            pg.draw.rect(self.screen, YELLOW, self.camera.apply_rect(self.player.body.weapon2_melee_rect), 1)
            pg.draw.rect(self.screen, YELLOW, self.camera.apply_rect(self.player.body.melee2_rect), 1)
            #for elev in self.elevations_on_screen:
            #    pg.draw.rect(self.screen, BLUE, self.camera.apply_rect(elev.rect), 1)

        self.inventory_hud_icons.draw(self.screen)
        if self.selected_hud_item:
            pg.draw.rect(self.screen, YELLOW, self.selected_hud_item.rect, 1)

        if ('type' in self.player.hand2_item) and (self.player.hand2_item['type'] == 'block') or ('type' in self.player.hand_item) and (self.player.hand_item['type'] == 'block'):
            x, y = get_next_tile_pos(self.player)
            pg.draw.rect(self.screen, YELLOW, self.camera.apply_rect(pg.Rect(x * self.map.tile_size, y * self.map.tile_size,  self.map.tile_size,  self.map.tile_size)), 1)

        # HUD functions
        draw_player_stats(self.screen, 10, 10, self.hud_health)
        draw_player_stats(self.screen, 10, 40, self.hud_stamina, BLUE)
        draw_player_stats(self.screen, 10, 70, self.hud_magica, CYAN)
        if self.show_mobhp:
            draw_player_stats(self.screen, int(self.screen_width/2 - 150), self.screen_height - 70, self.hud_mobhp, BLUE, 300)
        if self.player.hungers:
            draw_player_stats(self.screen, 10, 100, self.hud_hunger, BROWN)
            self.draw_text("HGR {:.0f}".format(self.player.stats['hunger']), self.hud_font, 20, WHITE, 120, 100, align="topleft")
        draw_crosshair = False
        if self.hud_ammo1 != '':
            self.draw_text(self.hud_ammo1, self.hud_font, 20, WHITE, 50, self.screen_height - 100, align="topleft")
            draw_crosshair = True
        if self.hud_ammo2 != '':
            self.draw_text(self.hud_ammo2, self.hud_font, 20, WHITE, 50, self.screen_height - 50, align="topleft")
            draw_crosshair = True
        if draw_crosshair:
            pg.mouse.set_visible(False)
            mouse_pos = pg.mouse.get_pos()
            self.screen.blit(self.crosshair_image, (mouse_pos[0] - self.crosshair_offset, mouse_pos[1] - self.crosshair_offset))
        elif not pg.mouse.get_visible():
            pg.mouse.set_visible(True)
        if self.paused:
            self.screen.blit(self.dim_screen, (0, 0))
            self.draw_text("Paused", self.title_font, 105, RED, self.screen_width / 2, self.screen_height / 2, align="center")
        if self.message_text == True:
            self.draw_text(self.message, self.hud_font, 30, WHITE, self.screen_width / 2, self.screen_height / 2 + 100, align="center")
        self.draw_text("FPS {:.0f}".format(1/self.dt), self.hud_font, 20, WHITE, self.screen_width/2, 10, align="topleft")
        self.draw_text("HP {:.0f}".format(self.hud_health_stats['health']), self.hud_font, 20, WHITE, 120, 10, align="topleft")
        self.draw_text("ST {:.0f}".format(self.player.stats['stamina']), self.hud_font, 20, WHITE, 120, 40, align="topleft")
        self.draw_text("MP {:.0f}".format(self.player.stats['magica']), self.hud_font, 20, WHITE, 120, 70, align="topleft")

        pg.display.flip()
        self.wt = self.beg + (1 / FPS)
        while (perf_counter() < self.wt):
            pass
        self.dt = perf_counter() - self.beg
        if self.dt > 0.2: # Caps dt at 200 ms.
            self.dt = 0.2
        self.beg = perf_counter()
        if self.in_lock_menu:
            self.lock_menu.update()
        if self.in_dialogue_menu:
            self.dialogue_menu.update()

    def change_right_equipped(self, slot):
        self.player.empty_mags() # unloads old weapon
        self.player.hand_item = self.player.equipped[slot]
        if ('type' in self.player.hand_item) and (self.player.hand_item['type'] in WEAPON_TYPES):
            self.player.equipped['weapons'] = self.player.hand_item
        else:
            self.player.equipped['weapons'] = None
        for icon in self.inventory_hud_icons:
            if int(icon.slot_text) == slot + 1:
                self.selected_hud_item = icon
        self.player.lamp_check()
        self.player.human_body.update_animations()  # Updates animations for newly equipped or removed weapons etc.
        self.player.dragon_body.update_animations()
        self.player.pre_reload() # reloads new weapon

    def use_item(self, slot):
        self.change_right_equipped(slot)
        self.player.use_item(self.selected_hud_item.item, slot)

    def place_item(self):
        if self.selected_hud_item:
            slot = int(self.selected_hud_item.slot_text) - 1
            self.player.place_item(slot)

    def events(self):
        # catch all events here
        for event in pg.event.get():
            if event.type == pg.QUIT:
                self.quit()
            # Shooting/attacking
            if event.type == pg.MOUSEBUTTONDOWN:
                pos = pg.mouse.get_pos()
                # get a list of all heading sprites that are under the mouse cursor
                self.clicked_sprites = [s for s in self.inventory_hud_icons if s.rect.collidepoint(pos)]
                if self.clicked_sprites:
                    if pg.mouse.get_pressed() == (1, 0, 0):
                        self.change_right_equipped(int(self.clicked_sprites[0].slot_text) - 1)
                    elif pg.mouse.get_pressed() == (0, 0, 1):
                        self.use_item(int(self.clicked_sprites[0].slot_text) - 1)
                if pg.mouse.get_pressed() == (1, 0, 1):
                    self.player.dual_shoot()
                elif pg.mouse.get_pressed() == (0, 0, 1) or pg.mouse.get_pressed() == (0, 1, 1):
                    if ('type' in self.player.hand_item) and (self.player.hand_item['type'] == 'block'):
                        self.player.place_block(1)
                    elif ('type' in self.player.hand_item) and (self.player.hand_item['type'] == 'magic'):
                        self.player.weapon_hand = 'weapons'
                        self.player.cast_spell(self.player.hand_item)
                    else:
                        self.player.weapon_hand = 'weapons'
                        self.player.shoot()
                elif pg.mouse.get_pressed() == (1, 0, 0) or pg.mouse.get_pressed() == (1, 1, 0):
                    if ('type' in self.player.hand2_item) and (self.player.hand2_item['type'] == 'block'):
                        self.player.place_block(2)
                    elif ('type' in self.player.hand2_item) and (self.player.hand2_item['type'] == 'magic'):
                        self.player.weapon_hand = 'weapons2'
                        self.player.cast_spell(self.player.hand2_item)
                    else:
                        self.player.weapon_hand = 'weapons2'
                        self.player.shoot()
                else: # Prevents e_down from getting stuck on true
                    self.player.e_down = False
            if event.type == pg.MOUSEBUTTONUP: # Updates which hand should be attacking when mouse buttons change.
                if pg.mouse.get_pressed() == (0, 0, 1) or pg.mouse.get_pressed() == (0, 1, 1):
                    self.player.weapon_hand = 'weapons'
                elif pg.mouse.get_pressed() == (1, 0, 0) or pg.mouse.get_pressed() == (1, 1, 0):
                    self.player.weapon_hand = 'weapons2'
                else: # Prevents e_down from getting stuck on true
                    self.player.e_down = False
            if event.type == pg.KEYDOWN:
                if event.key == pg.K_1:
                    self.change_right_equipped(0)
                elif event.key == pg.K_2:
                    self.change_right_equipped(1)
                elif event.key == pg.K_3:
                    self.change_right_equipped(2)
                elif event.key == pg.K_4:
                    self.change_right_equipped(3)
                elif event.key == pg.K_5:
                    self.change_right_equipped(4)
                elif event.key == pg.K_6:
                    self.change_right_equipped(5)
                if event.key == pg.K_ESCAPE:
                    MainMenu(self, self.player, 'Game')
                if event.key == self.key_map['inventory']:
                    self.player.empty_mags() # This makes sure the bullets in your clip don't transfer to the wrong weapons if you switch weapons in your inventory
                    MainMenu(self, self.player)
                if event.key == self.key_map['interact']:
                    self.player.e_down = True
                else:
                    self.player.e_down = False
                #if event.key == pg.K_BACKQUOTE:  # Switches to last weapon
                #    self.player.toggle_previous_weapons()
                if event.key == self.key_map['reload']:
                    self.player.pre_reload()
                if event.key == self.key_map['hitbox']:
                    self.draw_debug = not self.draw_debug
                if event.key == self.key_map['pause']:
                    trace_mem()
                    self.paused = not self.paused
                    self.beg = perf_counter() # resets dt.
                if event.key == pg.K_EQUALS:
                    self.map.minimap.resize()
                if event.key == pg.K_MINUS:
                    self.map.minimap.resize(False)
                if event.key == self.key_map['minimap']: # Toggles hud mini map
                    self.hud_map = not self.hud_map
                if event.key == self.key_map['place']:
                    self.place_item()
                if event.key == self.key_map['block']:
                    self.player.place_block()
                if event.key == self.key_map['grenade']:
                    self.player.throw_grenade()
                if event.key == self.key_map['transform']:
                    if self.player.possessing == None:
                        self.player.transform()
                    else:
                        self.player.possessing.depossess()

                if event.key == self.key_map['fire']:
                    if self.player.dragon:
                        self.player.breathe_fire()
                if event.key == self.key_map['lamp']:
                    self.player.light_on = not self.player.light_on
                if event.key == self.key_map['up']:
                    if self.player.in_vehicle:
                        if self.player.vehicle in self.flying_vehicles:
                            self.fly_menu = Fly_Menu(self)
                if event.key == pg.K_RETURN:   # Toggles fullscreen mode when you press ALT+ENTER
                    if event.mod & pg.KMOD_ALT:
                        self.flags ^=  pg.FULLSCREEN
                        if self.flags & pg.FULLSCREEN:
                            self.screen_height = HEIGHT
                        else:
                            self.screen_height = HEIGHT
                        pg.display.set_mode((self.screen_width, self.screen_height), self.flags)
                if event.key ==  pg.K_s: # Saves game
                    if event.mod & pg.KMOD_CTRL:
                        self.save()
                if event.key ==  pg.K_l: # loads game
                    if event.mod & pg.KMOD_CTRL:
                        pass
                if event.key == self.key_map['jump']:
                    self.player.pre_jump()

    def show_go_screen(self):
        self.screen.fill(BLACK)
        self.draw_text("GAME OVER", self.title_font, 100, RED,
                       self.screen_width / 2, self.screen_height / 2, align="center")
        self.draw_text("Press Escape to quit, C to continue or N to start a new game.", self.script_font, 16, WHITE,
                       self.screen_width / 2, self.screen_height * 3 / 4, align="center")
        pg.display.flip()
        self.wait_for_key()
        self.garbage_collect()

    def wait_for_key(self):
        pg.event.wait()
        waiting = True
        while waiting:
            self.clock.tick(FPS)
            for event in pg.event.get():
                if event.type == pg.QUIT:
                    waiting = False
                    self.quit()
                if event.type == pg.KEYDOWN:
                    if event.key == pg.K_ESCAPE:
                        waiting = False
                        self.quit()
                    elif event.key == pg.K_c:
                        waiting = False
                        self.player.stats['health'] = self.player.stats['max health']
                        #self.in_load_menu = True
                        self.run()
                    elif event.key == pg.K_n:
                        waiting = False

# create the game object
g = Game()
while True:
    g.new()
    g.run()
    g.show_go_screen()
