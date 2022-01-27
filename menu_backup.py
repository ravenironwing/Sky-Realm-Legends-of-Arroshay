import pygame as pg
from sprites import Dropped_Item, toggle_equip, remove_nones, change_clothing, color_image, add_inventory, gid_with_property, correct_filename, gender_tag
from random import uniform, choice, randint, random, randrange
from settings import *
from npcs import *
from quests import *
#from tilemap import collide_hit_rect
from os import path
import sys
from random import choice, shuffle
from collections import Counter
from glob import glob
from textwrap import wrap
import copy
from dialogue import *
import re
from npc_design import Npc_Info_Designer
from math import ceil
#from sprites import Npc, Animal
from time import perf_counter
from recipes import *

vec = pg.math.Vector2

#default_font = pg.font.match_font('arial') #python looks for closest match to arial on whatever computer
default_font = MENU_FONT

#def empty_dictionary(d):
#    for x in d:
#        if x not in ['race', 'gender']
#            d[x] = [None]

def convert_to_item_dict(b):
    new_list = b.copy()
    new_list.pop(0)
    for i, val in enumerate(new_list):
        if val == 0:
            new_list[i] = {}
        else:
            new_list[i] = ITEMS[val]
    return new_list

def eliminate_numbers(a): # This is used to make it so you can craft items from stacks of multiple items. I temporarily gets rid of the numbers in the stack so they match the recipies wich are just made for one item.
    new_list = copy.deepcopy(a)
    for i, value in enumerate(new_list):
        if 'number' in value:
            new_list[i]['number'] = 1
    return new_list

def list_pattern(searchlist, b): # a is the list you are searching through, b is the list you are searching for.
    b = convert_to_item_dict(b)
    a = eliminate_numbers(searchlist)
    if b[0] in a:
        index = a.index(b[0])
        for i, x in enumerate(range(index, index + len(b))):
            try:
                if a[x] == b[i]:
                    continue
                else:
                    return False
            except:
                return False

        for i in range(0, index):  # Returns false if there are extra items thrown in
            if a[i] != {}:
                return False
        for i in range(index + len(b), len(a)):
            if a[i] != {}:
                return False
        return True
    return False

# This makes sure the player or any other sprite is not equipping items they don't have. Also makes sure players aren't equipping armor in mechsuits
def check_equip(sprite):
    """
    for item_type in ITEM_TYPE_LIST:
        if sprite.equipped[item_type] not in sprite.inventory[item_type]:
            sprite.equipped[item_type] = None
        if item_type == 'weapons':
            if sprite.equipped['weapons2'] not in sprite.inventory[item_type]:
                sprite.equipped['weapons2'] = None
    if sprite.equipped['race'] in NO_CLOTHES_RACES:
        for item_type in ['hair', 'tops', 'bottoms', 'shoes', 'hats', 'gloves']:
            sprite.equipped[item_type] = None"""
    pass

class Draw_Text():
    def draw_text(self, text, font_name, size, color, x, y, align="topleft"):
        font = pg.font.Font(font_name, size)
        text_surface = font.render(text, True, color)
        text_rect = text_surface.get_rect(**{align: (x, y)})
        self.game.screen.blit(text_surface, text_rect)

class Text(pg.sprite.Sprite):
    def __init__(self, mother, text, font_name, size, color, x, y, align="topleft"):
        self.mother = mother
        #self.type = type
        self.size = size
        self.groups = self.mother.menu_sprites
        pg.sprite.Sprite.__init__(self, self.groups)
        font = pg.font.Font(font_name, size)
        self.image = font.render(text, True, color)
        self.rect = self.image.get_rect(**{align: (x, y)})
        self.text = text

class Picture(pg.sprite.Sprite):
    def __init__(self, game, mother, item_image, x, y):
        self.game = game
        self.mother = mother
        self.groups = self.mother.menu_sprites, self.mother.item_pictures
        pg.sprite.Sprite.__init__(self, self.groups)
        self.image = pg.transform.scale2x(item_image)
        self.image.set_colorkey(BLACK)
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)

class Item_Icon(pg.sprite.Sprite):
    def __init__(self, mother, slot, item, font_name, size, color, x, y, slot_text = None, dict = 'inventory'):
        self.font = pg.font.Font(font_name, size)
        self.mother = mother
        self.game = self.mother.game
        self.gender = gender_tag(self.game.player)
        self.dict = dict
        self.font_size = size
        self.slot = slot
        self.color = color
        self.slot_text = slot_text
        self.groups = self.mother.menu_sprites, self.mother.item_sprites
        self.item = item
        pg.sprite.Sprite.__init__(self, self.groups)
        self.x = x
        self.y = y
        self.update()

    def update(self):
        if 'type' in self.item.keys():
            self.type = self.item['type']
        elif self.item in self.mother.character.expanded_inventory['magic']:
            self.type = 'magic'
        elif (self.slot_text and (self.slot_text != 'hand2')) and (self.slot_text not in ['1', '2', '3', '4', '5', '6']):
            self.type = self.slot_text
        else:
            self.type = None
        if self.item == {}: # Draws empty slots
            self.box_image = pg.transform.scale(self.game.dark_grey_box_image, (ICON_SIZE, ICON_SIZE))
            self.image = self.box_image
            if self.slot_text:
                self.text_image = self.font.render(self.slot_text, True, self.color)
                self.image.blit(self.text_image, (0, 0))
        else: # Gets image for the item.
            self.box_image = pg.transform.scale(self.game.grey_box_image, (ICON_SIZE, ICON_SIZE))
            self.image = self.box_image
            if self.type == 'magic':
                self.item_image = pg.transform.scale(self.game.black_box_image, (ICON_SIZE - 2, ICON_SIZE - 2))
                mag_img = pg.transform.scale(self.game.magic_images[self.item['name']], (ICON_SIZE - 2, ICON_SIZE - 2))
                self.item_image.blit(mag_img, (0, 0))
            elif ('type' in self.item) and (self.item['type'] == 'block'):
                gid = gid_with_property(self.game.map.tmxdata, 'material', self.item['name'])
                self.item_image = self.game.map.tmxdata.get_tile_image_by_gid(gid)
            else:
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

                if 'color' in self.item.keys():
                    self.item_image = color_image(self.item_image, ITEMS[self.item['name']]['color'])

            self.item_image = pg.transform.scale(self.item_image, (ICON_SIZE - 2, ICON_SIZE - 2))
            self.image.blit(self.item_image,(1, 1))
        #if 'name' in self.item.keys():
        #    self.text = self.item['name']
        #    self.text_image = self.font.render(self.text, True, self.color)
        #    self.image.blit(self.text_image,(0, 0))
        if ('number' in self.item.keys()) and (self.item['number'] > 1):
            self.text = str(self.item['number'])
            self.text_image = self.font.render(self.text, True, self.color)
            self.image.blit(self.text_image,(ICON_SIZE - self.font_size - 3, ICON_SIZE - self.font_size + 2))
        if ('hp' in self.item.keys()) and ('max hp' in self.item.keys()): # Displays item health if it is lower than 100%
            if self.item['hp'] != self.item['max hp']:
                self.draw_hp_bar(self.image, 2, ICON_SIZE - 8, self.item['hp']/self.item['max hp'])


        self.rect = self.image.get_rect()
        self.rect.x = self.x
        self.rect.y = self.y
        self.size = self.rect.width

    def resize(self, size):
        self.image = pg.transform.scale(self.image, (size, size))
        self.rect = self.image.get_rect()
        self.rect.x = self.x
        self.rect.y = self.y
        self.size = self.rect.width

    def clear_item(self):
        self.item = {}
        self.image = self.box_image
        if self.slot_text:
            self.text_image = self.font.render(self.slot_text, True, self.color)
            self.image.blit(self.text_image, (0, 0))

    def draw_hp_bar(self, surf, x, y, pct, color=GREEN, bar_length=ICON_SIZE - 4):
        if pct < 0:
            pct = 0
        bar_height = 7
        fill = pct * bar_length
        outline_rect = pg.Rect(x, y, bar_length, bar_height)
        fill_rect = pg.Rect(x, y, fill, bar_height)
        if pct > 0.6:
            col = color
        elif pct > 0.3:
            col = YELLOW
        else:
            col = RED
        pg.draw.rect(surf, BLACK, outline_rect)
        pg.draw.rect(surf, col, fill_rect)
        pg.draw.rect(surf, BLACK, outline_rect, 1)

class Text(pg.sprite.Sprite):
    def __init__(self, mother, text, font_name, size, color, x, y, align="topleft"):
        self.mother = mother
        self.size = size
        self.groups = self.mother.menu_sprites
        pg.sprite.Sprite.__init__(self, self.groups)
        font = pg.font.Font(font_name, size)
        self.image = font.render(text, True, color)
        self.rect = self.image.get_rect(**{align: (x, y)})
        self.text = text

class Picture_Icon(pg.sprite.Sprite):
    def __init__(self, mother, item_image, x, y, size):
        self.mother = mother
        self.game = self.mother.game
        self.groups = self.mother.menu_sprites
        pg.sprite.Sprite.__init__(self, self.groups)
        self.image = pg.transform.scale(item_image, (size, size))
        self.image.set_colorkey(BLACK)
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        self.original_image = item_image
        self.x = x
        self.y = y
        self.size = size

    def hide(self):
        self.image = pg.transform.scale(self.game.black_box_image, (self.size, self.size))
        self.image.set_colorkey(BLACK)
        self.rect = self.image.get_rect()
        self.rect.center = (self.x, self.y)

    def un_hide(self):
        self.image = pg.transform.scale(self.original_image, (self.size, self.size))
        self.image.set_colorkey(BLACK)
        self.rect = self.image.get_rect()
        self.rect.center = (self.x, self.y)


class MainMenu():  # used as the parent class for other menus.
    def __init__(self, game, character = 'player', menu_type = 'Crafting', container = [{}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}]):
        self.game = game
        self.over_minimap_image = pg.transform.scale(self.game.over_minimap_image, (self.game.screen_height - 80, self.game.screen_height - 80))
        self.minimap_image = pg.transform.scale(self.game.minimap_image, (self.game.screen_height - 80, self.game.screen_height - 80))
        if character == 'player':
            self.character = self.game.player
        else:
            self.character = character
        self.menu_type = menu_type
        if self.menu_type == 'Game':
            self.menu_type = 'Crafting'
        self.container = container
        if self.menu_type not in ['Looting']:
            self.recipies = RECIPIES[self.menu_type]
        else:
            self.recipies = {}
        self.magic_dict = self.character.expanded_inventory['magic'].copy()
        self.running = True
        self.menu_sprites = pg.sprite.Group()
        self.menu_heading_sprites = pg.sprite.Group()
        self.item_sprites = pg.sprite.Group()
        self.text_sprites = pg.sprite.Group()
        self.variable_equip = pg.sprite.Group()
        self.magic_icons = pg.sprite.Group()
        self.inventory_icons = pg.sprite.Group()
        self.loot_icons = pg.sprite.Group()
        self.read_menu_icons = pg.sprite.Group()
        self.item_tags_sprites = pg.sprite.Group()  # Used to show things like if the item is equipped
        self.selected_item = None
        self.previous_selected_item = None
        self.selected_text = None
        self.previous_text = None
        self.crafted_item = {}
        self.crafted_icon = None
        self.printable_stat_list = []
        self.last_click = 0
        self.frame = 0
        self.last_frame = 0
        self.book_data = []
        # These items are changed for inherrited menus.
        self.action_keys = [pg.K_b, pg.K_x, pg.K_y]
        self.spacing = 20  # Spacing between headings
        self.heading_list = ['Game', 'Map', 'Quests', 'Stats', 'Equipment']  # This is the list of headings
        self.inventory_heading_list = ['Inventory', 'Magic', self.menu_type]  # This is the list of headings
        self.game_heading_list = ['Settings', 'Save/Load Game', 'Exit Menu', 'Quit Game']
        self.quest_heading_list = ['Active Quests', 'Completed Quests']
        self.settings_heading_list = ['Controls']
        self.save_heading_list = ['Save Game', 'Load Game']
        self.controls_menu_list = self.game.key_map.keys()
        if menu_type == 'Game':
            self.selected_heading_list = self.heading_list
        else:
            self.selected_heading_list = self.inventory_heading_list
        self.moving_item = None
        self.draw_map = False
        self.trash = Picture_Icon(self, self.game.trash_image, 932, 25, 40)
        self.back_arrow = Picture_Icon(self, self.game.back_arrow_image, 25, 25, 40)
        self.read_menu_icons.add(self.back_arrow)
        self.generate_headings(True)
        self.icon_offset = (0, 0) # Used for telling where you clicked on an icon to make the motion fluid.
        self.crafting_slots = []
        for i in range (0, 9): # generates list of slots to be used in the crafting menu to craft items.
            self.crafting_slots.append({})
        self.run()

    def run(self):
        if self.running:
            self.update()

    def click_text_icon(self, item): # Used for when you click a text based icon under a listing
        self.selected_text = item
        if self.selected_heading.text == 'Load Game':
            if self.previous_text:
                if self.selected_text.text == self.previous_text.text:
                    self.game.load_save(path.join(saves_folder, self.selected_text.text))
                    self.running = False
        elif self.selected_heading.text in self.quest_heading_list:
            self.display_quest_info(item)
        elif self.selected_text.text == 'Save/Load Game':
            self.change_headings(self.save_heading_list)
        elif self.selected_text.text == 'Settings':
            self.change_headings(self.settings_heading_list)
        elif self.selected_text.text == 'Exit Menu':
            self.running = False
        elif self.selected_text.text == 'Quit Game':
            self.game.quit()
        self.previous_text = self.selected_text

    def draw_overmap(self):
        draw_offsetx = 16
        draw_offsety = 53
        playerx = 400 #self.game.player.rect.centerx
        playery = 400 #self.game.player.rect.centery
        map_width = 1000 #self.game.map.width
        map_height = 1000 #self.game.map.height
        cell_width = self.over_minimap_image.get_width() / len(self.game.map_data_list[0])
        cell_height = self.over_minimap_image.get_height() / len(self.game.map_data_list)
        offsetx = int(self.game.world_location.x * cell_width + draw_offsetx)
        offsety = int(self.game.world_location.y * cell_height + draw_offsety)
        scalex = cell_width / map_width
        scaley = cell_height / map_height
        currentmap_rect = pg.Rect(0, 0, cell_width, cell_height)
        currentmap_rect.topleft = (offsetx, offsety)
        map_pos = vec(playerx * scalex, playery * scaley)
        pos_rect = pg.Rect(0, 0, 3, 3)
        pos_rect.center = (int(map_pos.x + offsetx), int(map_pos.y + offsety))
        self.game.screen.blit(self.over_minimap_image, (draw_offsetx, draw_offsety))
        pg.draw.rect(self.game.screen, YELLOW, currentmap_rect, 1)
        pg.draw.rect(self.game.screen, RED, pos_rect, 6)

        draw_offsetx = 16 + self.game.screen_width/2 - 5
        cell_width = self.minimap_image.get_width() / map_width
        cell_height = self.minimap_image.get_height() / map_height
        offsetx = int(self.game.world_location.x * cell_width + draw_offsetx)
        offsety = int(self.game.world_location.y * cell_height + draw_offsety)
        scalex = cell_width
        scaley = cell_height
        map_pos = vec(playerx * scalex, playery * scaley)
        pos_rect = pg.Rect(0, 0, 10, 10)
        pos_rect.center = (int(map_pos.x + offsetx), int(map_pos.y + offsety))
        self.game.screen.blit(self.minimap_image, (draw_offsetx, draw_offsety))
        pg.draw.rect(self.game.screen, YELLOW, pos_rect, 2)

    def check_crafting(self):
        for key, value in self.recipies.items():
            if list_pattern(self.crafting_slots, value):
                self.crafted_item = ITEMS[key].copy()
                smallest_num = 10000
                # This section finds the number of items you are crafting based on how many items you stick on the table
                for i, item in enumerate(self.crafting_slots):
                    if 'number' in item:
                        if item['number'] < smallest_num:
                            smallest_num = item['number']
                if smallest_num != 10000:
                    if 'number' in self.crafted_item:
                        self.crafted_item['number'] = smallest_num * self.recipies[self.crafted_item['name']][0]
                return
        else:
            self.crafted_item = {}

    def generate_headings(self, new = False):
        for sprite in self.menu_heading_sprites:
            sprite.kill()
        self.menu_heading_sprites.empty()
        previous_rect_right = 35
        for i, heading in enumerate(self.selected_heading_list):
            heading_sprite = Text(self, heading, default_font, 30, LIGHT_BLUE, previous_rect_right + self.spacing, 10, "topleft")
            if i == 0 and new:
                self.selected_heading = heading_sprite
            if (heading_sprite.text == self.menu_type) and (self.menu_type != 'Crafting'):
                self.selected_heading = heading_sprite
            previous_rect_right = heading_sprite.rect.right
            self.menu_heading_sprites.add(heading_sprite)

    def events(self):
        use_item = False
        now = pg.time.get_ticks()
        if now - self.last_click > DOUBLE_CLICK_TIME:
            self.previous_selected_item = None
        # catch all events here
        for event in pg.event.get():
            if event.type == pg.QUIT:
                self.game.quit()
            if event.type == pg.KEYDOWN:
                if event.key == pg.K_ESCAPE:
                    self.clear_menu()
                    self.running = False
                if event.key == self.action_keys[0]: # use/buy
                    if self.selected_item:
                        self.use_item()
                if event.key == self.action_keys[1]:  # drop/sell item
                    if self.selected_item:
                        self.drop_item()
                        self.clear_item_info()
                if self.selected_text and (self.selected_text.text in self.controls_menu_list) and event.key: # This part is used for remapping player controls.
                    if event.key != pg.K_ESCAPE:
                        old_key = self.game.key_map[self.selected_text.text]
                        for key, value in self.game.key_map.items():
                            if value == event.key:
                                self.game.key_map[key] = old_key
                        self.game.key_map[self.selected_text.text] = event.key
                        self.clear_menu()
                        self.list_items()
            if event.type == pg.MOUSEBUTTONDOWN:  # Clears off pictures and stats from previously clicked item when new item is clicked.
                self.last_click = pg.time.get_ticks()
                self.click_event()
                # Lets you move items around and equip them.
                dict = None
                for item in self.clicked_sprites:
                    if item in self.text_sprites:
                        self.click_text_icon(item)
                    if item in self.item_sprites:
                        self.selected_item = item
                        if self.selected_item and ('name' in self.selected_item.item.keys()) and self.previous_selected_item and ('name' in self.previous_selected_item.item.keys()) and (self.previous_selected_item.item['name'] == self.selected_item.item['name']) and not self.moving_item:
                            use_item = True
                        self.display_item_info()
                        if self.selected_item.dict == 'inventory':
                            dict = self.character.inventory
                        elif self.selected_item.dict == 'equipped':
                            dict = self.character.equipped
                        elif self.selected_item.dict == 'magic':
                            dict = self.magic_dict
                        elif self.selected_item.dict == 'crafting':
                            dict = self.crafting_slots
                        elif self.selected_item.dict == 'crafted':
                            dict = [self.crafted_item]
                        elif self.selected_item.dict == 'loot':
                            dict = self.container
                        if self.mouse_click == (1, 0, 0) and not use_item:
                            if self.moving_item and (self.selected_item.dict != 'crafted'):
                                self.swap_item(dict)
                            else:
                                self.check_moving()
                                dict[self.selected_item.slot] = {}
                        elif self.mouse_click == (1, 0, 1):
                            if self.moving_item:
                                if ('number' in self.moving_item.item.keys()) and (self.moving_item.item['number'] > 0):
                                    self.swap_item(dict, 1)
                                else:
                                    self.swap_item(dict)
                            else:
                                self.check_moving()
                                dict[self.selected_item.slot] = {}
                        elif self.mouse_click == (0, 0, 1):
                            if not self.moving_item:
                                if ('number' in self.selected_item.item.keys()) and (self.selected_item.item['number'] > 1):
                                    self.half_stack()
                        self.previous_selected_item = item
                        self.list_items()
                if self.trash in self.clicked_sprites and self.moving_item and (self.selected_heading.text != 'Magic'):
                    self.drop_item(self.moving_item)
                elif self.back_arrow in self.clicked_sprites and not self.moving_item:
                    self.selected_item = None
                    self.selected_text = None
                    if self.selected_heading_list != self.heading_list:
                        self.change_headings(self.heading_list)
                    else:
                        self.clear_menu()
                        self.running = False
            if (event.type == pg.MOUSEBUTTONUP) and self.moving_item:
                self.click_event(False)
                if not self.mouse_click[0]: # Only responds if the left mouse button goes up, not the right or middle
                    # Lets you move items around and equip them.
                    dict = None
                    for item in self.clicked_sprites:
                        if item in self.item_sprites:
                            self.selected_item = item
                            self.display_item_info()
                            if self.selected_item.dict == 'inventory':
                                dict = self.character.inventory
                            elif self.selected_item.dict == 'equipped':
                                dict = self.character.equipped
                            elif self.selected_item.dict == 'magic':
                                dict = self.magic_dict
                            elif self.selected_item.dict == 'crafting':
                                dict = self.crafting_slots
                            elif self.selected_item.dict == 'loot':
                                dict = self.container
                            elif self.selected_item.dict == 'crafted':
                                continue
                            self.swap_item(dict)
                            self.list_items()
        if use_item:
            self.use_item()
    def click_event(self, sound = True):
        self.mouse_click = pg.mouse.get_pressed()
        pos = pg.mouse.get_pos()
        self.clicked_sprites = [s for s in self.menu_sprites if s.rect.collidepoint(pos)]
        if self.clicked_sprites and sound:
            self.game.effects_sounds['click'].play()
        elif self.clicked_sprites:
            self.game.effects_sounds['clickup'].play()
        if sound: # Doesn't delete the list if
            self.printable_stat_list = []

        # get a list of all heading sprites that are under the mouse cursor
        for heading in self.menu_heading_sprites:
            if heading in self.clicked_sprites:
                self.selected_heading = heading
                if self.selected_heading.text == 'Equipment':
                    self.change_headings(self.inventory_heading_list)
                elif self.selected_heading.text == 'Quests':
                    self.change_headings(self.quest_heading_list)
                #elif self.selected_heading.text == 'Game':
                #    self.change_headings(self.game_heading_list)
                self.selected_item = None
                self.selected_text = None
                self.list_items()

    def change_headings(self, new_headings):
        self.clear_menu()
        self.selected_heading_list = new_headings
        self.generate_headings()
        for heading in self.menu_heading_sprites:  # Selects the first heading sprite in the list.
            self.selected_heading = heading
            break
        for heading in self.menu_heading_sprites:  # Selects the heading that fits the menu_type if possible
            if (heading.text == self.menu_type) and (self.menu_type != 'Crafting'):
                self.selected_heading = heading
                break
        self.selected_text = None
        self.list_items()

    def half_stack(self):
        self.moving_item = Item_Icon(self, None, self.selected_item.item.copy(), default_font, 20, WHITE, self.selected_item.x, self.selected_item.y, self.selected_item.slot_text, self.selected_item.dict)
        remainder = self.selected_item.item['number'] % 2
        self.moving_item.item['number'] = int(self.selected_item.item['number'] / 2)
        self.selected_item.item['number'] = self.moving_item.item['number'] + remainder
        self.moving_item.update()
        self.selected_item.update()

    def decrease_stack(self, dict, count): # Used to change number in stack.
        def decrease_num():
            self.moving_item.item['number'] -= count
            self.moving_item.update()
            if self.moving_item.item['number'] == 0:
                self.moving_item = None
        if self.moving_item.item['number'] < count:
            return
        if self.selected_item.item == {}: # If you place one item in an empty slot
            dict[self.selected_item.slot] = self.moving_item.item.copy()
            dict[self.selected_item.slot]['number'] = count
            decrease_num()
        elif self.selected_item.item['name'] == self.moving_item.item['name']:
            if 'max stack' in self.selected_item.item.keys():
                if dict[self.selected_item.slot]['number'] + count > dict[self.selected_item.slot]['max stack']: # Places the max number of items in stack that it can and returns the rest to the moving item.
                    dif = (dict[self.selected_item.slot]['number'] + count) - dict[self.selected_item.slot]['max stack']
                    dict[self.selected_item.slot]['number'] = dict[self.selected_item.slot]['max stack']
                    self.moving_item.item['number'] = dif
                    self.moving_item.update()
                else:
                    dict[self.selected_item.slot]['number'] += count
                    decrease_num()

    def swap_item(self, dict, count = 0):
        if not(((self.selected_item in self.inventory_icons) or (self.selected_item in self.loot_icons)) and (self.moving_item.item in self.character.expanded_inventory['magic'])) and not((self.selected_item in self.magic_icons) and (self.moving_item.item not in self.character.expanded_inventory['magic'])):
            if count:
                if self.selected_item.type:
                    if self.moving_item.type == self.selected_item.slot_text:
                        self.decrease_stack(dict, count)
                    elif dict != self.character.equipped:
                        self.decrease_stack(dict, count)
                    elif self.selected_item in self.variable_equip:
                        self.decrease_stack(dict, count)
                else:
                    self.decrease_stack(dict, count)

            elif ('name' in self.selected_item.item.keys()) and (self.selected_item.item['name'] == self.moving_item.item['name']) and ('number' in self.selected_item.item.keys()):
                self.decrease_stack(dict, self.moving_item.item['number'])

            else:
                if self.selected_item.type:
                    if self.moving_item.type == self.selected_item.slot_text:
                        dict[self.selected_item.slot] = self.moving_item.item
                        self.check_moving()
                    elif dict != self.character.equipped:
                        dict[self.selected_item.slot] = self.moving_item.item
                        self.check_moving()
                    elif self.selected_item in self.variable_equip:
                        dict[self.selected_item.slot] = self.moving_item.item
                        self.check_moving()
                else:
                    dict[self.selected_item.slot] = self.moving_item.item
                    self.check_moving()

    def grab_crafted(self):
         if not self.moving_item and (self.crafted_item != {}):
            self.moving_item = self.crafted_icon
            for i, item in enumerate(self.crafting_slots):
                if 'number' in item:
                    if 'number' in self.crafted_item.keys():
                        item['number'] -= int(self.crafted_item['number'] / self.recipies[self.crafted_item['name']][0])
                    else:
                        item['number'] -= 1
                    if item['number'] == 0:
                        self.crafting_slots[i] = {}
                else:
                    item = {}
            self.list_items()

    def check_moving(self): # Picks up selected item so it moves with mouse unless it is empty.
        if self.selected_item.dict == 'crafted':
            self.grab_crafted()
        elif self.selected_item.item != {}:
            self.moving_item = self.selected_item
            pos = pg.mouse.get_pos()
            if self.moving_item:
                self.icon_offset = (self.selected_item.rect.x - pos[0], self.selected_item.rect.y - pos[1])
            else:
                self.icon_offset = (0, 0)
        else:
            self.moving_item = None

    def clear_menu(self):
        self.draw_map = False
        for item in self.item_sprites:
            if item not in self.game.inventory_hud_icons:
                item.kill()
            else:
                self.item_sprites.remove(item)
                self.menu_sprites.remove(item)
        for item in self.item_tags_sprites:
            item.kill()
        for item in self.text_sprites:
            item.kill()

    def clear_item_info(self):
        self.selected_item = None
        self.selected_text = None
        self.clicked_sprites = []
        self.printable_stat_list = []

    def draw_text(self, text, font_name, size, color, x, y, align="topleft", surface = None):
        font = pg.font.Font(font_name, size)
        text_surface = font.render(text, True, color)
        text_rect = text_surface.get_rect(**{align: (x, y)})
        if surface:
            surface.blit(text_surface, text_rect)
        else:
            self.game.screen.blit(text_surface, text_rect)

    def draw(self):
        self.game.screen.fill(BLACK)
        list_rect = pg.Rect(10, 50, self.game.screen_width / 2 - 10, self.game.screen_height - 74)
        list_rect_fill = pg.Rect(20, 60, self.game.screen_width / 2 - 30, self.game.screen_height - 94)
        description_rect = pg.Rect(self.game.screen_width / 2 + 5, 50, 242, self.game.screen_height - 74)
        description_rect_fill = pg.Rect(self.game.screen_width / 2 + 15, 60, 231, self.game.screen_height - 94)
        preview_rect = pg.Rect(732, 50, 220, 220)
        preview_rect_fill = pg.Rect(self.game.screen_width / 2 + 15, 60, 231, self.game.screen_height - 94)
        stats_rect = pg.Rect(732, 296, 220, 220)
        stats_rect_fill = pg.Rect(self.game.screen_width / 2 + 15, 60, 231, self.game.screen_height - 94)
        pg.draw.rect(self.game.screen, WHITE, list_rect, 2)
        pg.draw.rect(self.game.screen, BLACK, list_rect_fill)
        if self.selected_heading.text not in ['Inventory', 'Magic'] + WORKSTATIONS:
            description_rect = pg.Rect(self.game.screen_width / 2 + 7, 50, self.game.screen_width / 2 - 15, self.game.screen_height - 74)
            description_rect_fill = pg.Rect(self.game.screen_width / 2 + 17, 60, self.game.screen_width / 2 - 35, self.game.screen_height - 94)
            pg.draw.rect(self.game.screen, WHITE, description_rect, 2)
            pg.draw.rect(self.game.screen, BLACK, description_rect_fill)
        else:
            pg.draw.rect(self.game.screen, WHITE, description_rect, 2)
            pg.draw.rect(self.game.screen, BLACK, description_rect_fill)
            pg.draw.rect(self.game.screen, WHITE, preview_rect, 2)
            pg.draw.rect(self.game.screen, BLACK, preview_rect_fill)
            pg.draw.rect(self.game.screen, WHITE, stats_rect, 2)
            pg.draw.rect(self.game.screen, BLACK, stats_rect_fill)

        if self.selected_item:
            selected_rect = pg.Rect(self.selected_item.rect.x - 2, self.selected_item.rect.y - 2, self.selected_item.rect.width + 2, self.selected_item.size + 2)
            pg.draw.rect(self.game.screen, YELLOW, selected_rect, 2)
        if self.selected_text:
            selected_rect = pg.Rect(self.selected_text.rect.x - 2, self.selected_text.rect.y - 2, self.selected_text.rect.width + 2, self.selected_text.size + 2)
            pg.draw.rect(self.game.screen, YELLOW, selected_rect, 2)

        selected_heading_rect = pg.Rect(self.selected_heading.rect.x - 4, self.selected_heading.rect.y, self.selected_heading.rect.width + 8, self.selected_heading.size + 2)
        pg.draw.rect(self.game.screen, YELLOW, selected_heading_rect, 2)
        self.menu_sprites.draw(self.game.screen)
        if self.selected_item:
            for i, item_stat in enumerate(self.printable_stat_list):
                self.draw_text(item_stat, default_font, 18, WHITE, 750, 300 + 20 * i, "topleft")
        if self.selected_text: # Used for printing out quest info
            for i, item_stat in enumerate(self.printable_stat_list):
                self.draw_text(item_stat, default_font, 20, WHITE, self.game.screen_width / 2 + 50, self.game.screen_height / 3 + 30 * i, "topleft")
        if self.selected_heading.text in WORKSTATIONS:
            self.draw_text(self.selected_heading.text, default_font, 30, WHITE, 500, 10, "topleft")
            self.game.screen.blit(self.game.right_arrow_image, (570, 284))
        elif self.selected_heading.text in ['Inventory', 'Magic']:
            self.draw_text('Equipped', default_font, 30, WHITE, 500, 10, "topleft")
        if self.selected_heading.text in ['Inventory', 'Magic'] + WORKSTATIONS:
            self.draw_text('Preview', default_font, 30, WHITE, 750, 10, "topleft")
            self.draw_text('Selected Item Stats', default_font, 18, WHITE, 750, 275, "topleft")
        elif self.selected_heading.text == 'Looting':
            self.draw_text('Loot', default_font, 30, WHITE, 500, 10, "topleft")
        pos = pg.mouse.get_pos()
        if self.moving_item:
            self.game.screen.blit(self.moving_item.image, (pos[0] + self.icon_offset[0], pos[1] + self.icon_offset[1]))
        if self.draw_map:
            self.draw_overmap()

        pg.display.flip()

    def use_item(self):
        if ('type' in self.previous_selected_item.item.keys()) and (self.previous_selected_item.item['type'] in ['book', 'tome', 'letter']):
            self.game.effects_sounds['page turn'].play()
            self.read_book(self.previous_selected_item)
            #self.character.equipped['items'] = self.selected_item.text
            #if self.character == self.game.player:
            #    self.warning_message = self.character.use_item()
            #self.selected_item = None
            self.list_items()

    def read_book(self, item):
        self.letter = False
        if item.item['type'] == 'letter':
            #self.book_image = self.game.open_letter_image
            self.letter = True
        self.book_image = self.game.book_images[0]
        self.page = 0
        self.wrap_factor = int(ceil((self.game.screen_width / 2) / 11))
        self.number_of_lines = int(ceil((self.game.screen_height / 40)))
        self.book_font = eval(item.item['font'])
        if self.book_font == 'KAWTHI_FONT':
            self.heading_font = KAWTHI_FONT
        else:
            self.heading_font = HEADING_FONT
        self.book_heading = item.item['heading']
        self.book_author = item.item['author']
        if 'spell words' in item.item.keys():
            spellwords = item.item['spell words']
        else:
            spellwords = ''
        self.book_spellwords = wrap(spellwords, self.wrap_factor)
        book_file_name = item.item['name']
        with open(path.join(books_folder, book_file_name + '.txt'), 'r') as file:
            self.book_text = file.read()
        book_lines = self.book_text.split('\n')
        wrapped_lines = []
        for line in book_lines:
            wrapped_line = wrap(line, self.wrap_factor, replace_whitespace=False, drop_whitespace=False)
            wrapped_lines.extend(wrapped_line)

        self.book_data = [wrapped_lines[z:z + self.number_of_lines] for z in range(0, len(wrapped_lines), self.number_of_lines)]
        self.display_page()
        waiting = True
        while waiting:
            self.game.clock.tick(30)
            for event in pg.event.get():
                if event.type == pg.QUIT:
                    pg.quit()
                    sys.exit()
                if event.type == pg.MOUSEBUTTONDOWN:
                    self.click_event()
                    if self.back_arrow in self.clicked_sprites:
                        self.game.effects_sounds['close book'].play()
                        waiting = False
                        break
                    if pg.mouse.get_pressed() == (1, 0, 0):
                        pos = pg.mouse.get_pos()
                        if (pos[0] > self.game.screen_width / 2):
                            self.page_turn()
                        else:
                            self.page_turn('back')

                if event.type == pg.KEYDOWN:
                    if event.key == pg.K_ESCAPE:
                        self.game.effects_sounds['close book'].play()
                        waiting = False
                    elif event.key in [pg.K_SPACE, pg.K_RIGHT]:
                        self.page_turn()
                    elif event.key in [pg.K_BACKSPACE, pg.K_LEFT]:
                        self.page_turn('back')

    def page_turn(self, direction = 'forward'):
        if direction == 'forward':
            if self.page == len(self.book_data):
                return
            self.page += 1
        else:
            if self.page == 0:
                return
            self.page -= 3
            if self.page < 0:
                self.page = 0
        animate_speed = 100
        while True:
            now = pg.time.get_ticks()
            if now - self.last_frame > animate_speed:
                if self.frame == 1:
                    self.game.effects_sounds['page turn'].play()
                self.last_frame = now
                self.frame += 1
                if self.frame >= len(self.game.book_images):
                    self.frame = 0
                    break
                if direction == 'forward':
                    self.book_image = self.game.book_images[self.frame]
                else:
                    frame = len(self.game.book_images) - self.frame
                    self.book_image = self.game.book_images[frame]
                self.display_turning_page(direction)
        self.book_image = self.game.book_images[0]
        self.display_page()

    def display_turning_page(self, direction):
        self.clear_menu()
        self.game.screen.fill(BLACK)
        self.game.screen.blit(self.book_image, (0, 0))
        lpage_surface = pg.Surface([self.game.screen_width/2, self.game.screen_height], pg.SRCALPHA).convert_alpha()
        rpage_surface = lpage_surface.copy()
        tlpage_surface = lpage_surface.copy()
        trpage_surface = lpage_surface.copy()

        rpage = 0
        lpage = 0
        trpage = 0
        tlpage = 0
        if direction == 'forward':
            lpage = self.page - 2
            rpage = self.page + 1
            tlpage = self.page
            trpage = self.page - 1
        elif self.page > 0:
            lpage = self.page + 2
            rpage = self.page + 3
            tlpage = self.page
            trpage = self.page + 1
        else:
            lpage = self.page + 1
            rpage = self.page + 2
            tlpage = self.page
            trpage = self.page + 1

        self.render_page('left', lpage_surface, lpage)
        self.render_page('left', rpage_surface, rpage)
        self.render_page('left', tlpage_surface, tlpage)
        self.render_page('left', trpage_surface, trpage)


        reduction = int((self.frame + 1)/len(self.game.book_images) * self.game.screen_width/2)
        reduction2 = int((self.frame)/len(self.game.book_images) * self.game.screen_width/2)

        if direction == 'forward':
            if self.page != 1:
                if self.frame < 4:
                    reduc = 0
                else:
                    reduc = reduction
                mask_surf1 = pg.Surface([self.game.screen_width/2 - reduc, self.game.screen_height], pg.SRCALPHA).convert_alpha()
                mask_surf1.blit(lpage_surface, (0, 0))
                self.game.screen.blit(mask_surf1, (0, 0))
            if self.frame > 2:
                mask_surf1 = pg.Surface([reduction2, self.game.screen_height], pg.SRCALPHA).convert_alpha()
                mask_surf1.blit(rpage_surface, (-self.game.screen_width/2+reduction2, 0))
                self.game.screen.blit(mask_surf1, (self.game.screen_width - reduction2, 0))

            if self.frame > 4:
                mask_surf1 = pg.Surface([reduction2, self.game.screen_height], pg.SRCALPHA).convert_alpha()
                mask_surf1.blit(tlpage_surface, (-self.game.screen_width/2+reduction2, 0))
                self.game.screen.blit(mask_surf1, (self.game.screen_width/2 - reduction2, 0))

            if self.frame < 3:
                mask_surf1 = pg.Surface([self.game.screen_width/2 - reduction, self.game.screen_height], pg.SRCALPHA).convert_alpha()
                mask_surf1.blit(trpage_surface, (0, 0))
                self.game.screen.blit(mask_surf1, (self.game.screen_width/2, 0))
        else:
            mask_surf1 = pg.Surface([self.game.screen_width/2 - reduction, self.game.screen_height], pg.SRCALPHA).convert_alpha()
            mask_surf1.blit(lpage_surface, (-reduction, 0))
            self.game.screen.blit(mask_surf1, (reduction, 0))

            if self.frame > 2:
                mask_surf1 = pg.Surface([self.game.screen_width/2 - reduction, self.game.screen_height], pg.SRCALPHA).convert_alpha()
                mask_surf1.blit(rpage_surface, (-reduction, 0))
                self.game.screen.blit(mask_surf1, (self.game.screen_width/2 + reduction, 0))
            else:
                self.game.screen.blit(rpage_surface, (self.game.screen_width/2, 0))
            if self.page > 0:
                if self.frame < 5:
                    mask_surf1 = pg.Surface([reduction2, self.game.screen_height], pg.SRCALPHA).convert_alpha()
                    mask_surf1.blit(tlpage_surface, (0, 0))
                    self.game.screen.blit(mask_surf1, (0, 0))
                else:
                    self.game.screen.blit(tlpage_surface, (0, 0))
                if self.frame > 3:
                    mask_surf1 = pg.Surface([reduction2, self.game.screen_height], pg.SRCALPHA).convert_alpha()
                    mask_surf1.blit(trpage_surface, (0, 0))
                    self.game.screen.blit(mask_surf1, (self.game.screen_width/2, 0))
        self.read_menu_icons.draw(self.game.screen)

        pg.display.flip()

    def display_page(self):
        self.clear_menu()
        self.game.screen.fill(BLACK)
        self.game.screen.blit(self.book_image, (0, 0))
        yoffset = 0
        byword = 'by'
        if self.book_font == WRITING_FONT:
            font_size = 18
            self.heading_font = WRITING_FONT
        if self.letter:
            byword = 'from'
        if self.page == 0:
            self.draw_text(self.book_heading, self.heading_font, 25, BLACK, self.game.screen_width * (3/4), self.game.screen_height * (1/5) + yoffset, "center")
            self.draw_text(byword, self.book_font, 18, BLACK, self.game.screen_width * (3/4), self.game.screen_height * (2/5) + yoffset, "center")
            self.draw_text(self.book_author, self.book_font, 18, BLACK, self.game.screen_width * (3/4), self.game.screen_height * (3/5) + yoffset, "center")
        else:
            self.render_page('left')
            self.page += 1
            if self.page <= len(self.book_data):
                self.render_page('right')
            else:
                self.page -= 1
        self.read_menu_icons.draw(self.game.screen)
        pg.display.flip()

    def render_page(self, margin, surface = None, page = None):
        if page == None:
            page = self.page
        elif page < 1: # clears surface if the page is out of range
            surface = pg.Surface([self.game.screen_width / 2, self.game.screen_height], pg.SRCALPHA).convert_alpha()
            return
        top_margin = 45
        if margin == 'left':
            left_margin = 55
        else:
            left_margin = self.game.screen_width / 2 + 55
        line_spacing = 32
        font_size = 15
        j = 0
        for i, line in enumerate(self.book_data[page - 1]):
            self.draw_text(line, self.book_font, font_size, BLACK, left_margin, top_margin + (line_spacing * i),
                           "topleft", surface)
            j += 1
        if page == len(self.book_data):
            for line in self.book_spellwords:
                self.draw_text(line, KAWTHI_FONT, font_size, BLACK, left_margin, top_margin + (line_spacing * j),
                               "topleft", surface)
                j += 1

        numberx = int(self.game.screen_width/4)
        if not surface and (page % 2 == 0):
            numberx += self.game.screen_width/2
        self.draw_text(str(page), self.book_font, font_size, BLACK, numberx, self.game.screen_height - 40, "topleft", surface)


    def drop_item(self, moving_item = None):
        if not moving_item:
            dict = None
            if self.selected_item.dict == 'inventory':
                dict = self.character.inventory
            elif self.selected_item.dict == 'loot':
                dict = self.container
            elif self.selected_item.dict == 'equipped':
                dict = self.character.equipped
            dict[self.selected_item.slot] = {}
        else:
            self.moving_item = None
        self.update()

    def list_items(self):
        self.clear_menu()
        #displayed_list = [] # Keeps track of which items have been displayed

        row = 0
        x_row = 50
        max_width = 0
        if self.selected_heading.text in ['Inventory', 'Looting'] + WORKSTATIONS:
            self.trash.un_hide()
            inventory = self.character.inventory
            dict = 'inventory'
        elif self.selected_heading.text == 'Magic':
            self.trash.hide()
            inventory = self.magic_dict
            print(inventory)
            dict = 'magic'
        else: # Used for Game, Control, quest and map menues.
            self.trash.hide()
            if self.selected_heading.text == 'Game':
                menu_list = self.game_heading_list
                font_size = 30
                font_space = 40
                for i, x in enumerate(menu_list):
                    if i < 25:
                        xpos = 50
                        ypos = font_space * i + 75
                    else:
                        xpos = self.game.screen_width / 2 + 50
                        ypos = font_space * (i - 25) + 75
                    item_name = Text(self, x, default_font, font_size, WHITE, xpos, ypos, "topleft")
                    self.text_sprites.add(item_name)
            elif self.selected_heading.text == 'Controls':
                menu_list = self.controls_menu_list
                font_size = 14
                font_space = 16
                for i, x in enumerate(menu_list):
                    if i < 26:
                        xpos = 50
                        ypos = font_space * i + 75
                    else:
                        xpos = self.game.screen_width / 2 + 50
                        ypos = font_space * (i - 25) + 75
                    item_name = Text(self, x, default_font, font_size, WHITE, xpos, ypos, "topleft")
                    self.text_sprites.add(item_name)
                    if menu_list == self.controls_menu_list:
                        item_name = Text(self, pg.key.name(self.game.key_map[x]), default_font, font_size, WHITE,
                                         xpos + 120, ypos, "topleft")
                        self.text_sprites.add(item_name)
            elif self.selected_heading.text == 'Map':
                self.draw_map = True
            elif self.selected_heading.text == 'Stats':
                menu_list = self.game.player.stats.keys()
                font_size = 14
                font_space = 16

                for i, x in enumerate(menu_list):
                    if i < 25:
                        xpos = 50
                        ypos = font_space * i + 75
                    else:
                        xpos = self.game.screen_width / 2 + 50
                        ypos = font_space * (i - 25) + 75
                    item_name = Text(self, x, default_font, font_size, WHITE, xpos, ypos, "topleft")
                    self.text_sprites.add(item_name)
                    item_name = Text(self, str(self.game.player.stats[x]), default_font, font_size, WHITE,
                                     xpos + 200, ypos, "topleft")
                    self.text_sprites.add(item_name)
            elif self.selected_heading.text == 'Save Game':
                self.game.save()
            elif self.selected_heading.text == 'Load Game':
                self.clear_menu()
                for i, filepath in enumerate(sorted(glob(path.join(saves_folder, "*.sav")), reverse=True)):
                    save_name = Text(self, path.basename(filepath), default_font, 20, WHITE, 50, 30 * i + 75, "topleft")
                    if self.selected_item == None:
                        if i == 0:
                            self.selected_item = save_name
                    self.text_sprites.add(save_name)
            elif self.selected_heading.text == 'Active Quests':
                i = 0
                for quest in self.game.quests.keys():
                    if self.game.quests[quest]['accepted']:
                        if not self.game.quests[quest]['completed']:
                            quest_name = Text(self, quest, default_font, 20, WHITE, 50, 30 * i + 75, "topleft")
                            self.text_sprites.add(quest_name)
                            i += 1
            elif self.selected_heading.text == 'Completed Quests':
                i = 0
                for quest in self.game.quests.keys():
                    if self.game.quests[quest]['accepted']:
                        if self.game.quests[quest]['completed']:
                            quest_name = Text(self, quest, default_font, 20, WHITE, 50, 30 * i + 75, "topleft")
                            self.text_sprites.add(quest_name)
                            i += 1
            return
        # Lists inventory slots
        spacing = 5
        xoffset = 18
        yoffset = 58
        padding = 5
        row = -1
        col = 0
        display_area_width = 450
        num_in_row = int(display_area_width / ICON_SIZE)

        for i, item in enumerate(inventory):
            col = i % num_in_row
            if col == 0:
                row += 1
            icon = Item_Icon(self, i, item, default_font, 20, WHITE, xoffset + spacing * col, yoffset + (row * spacing), None, dict)
            spacing = icon.size + padding
            if dict == 'magic':
                self.magic_icons.add(icon)
            elif dict == 'inventory':
                self.inventory_icons.add(icon)

        if self.selected_heading.text != 'Looting':
            # Lists equipped slots
            xoffset = 495
            yoffset = spacing * 4 + 58
            padding = 5
            num_in_row = 3
            row = -1
            col = 0
            i = 0
            self.game.inventory_hud_icons.empty()
            for key in self.character.equipped.keys():
                if key in [0, 1, 2, 3, 4, 5]:
                    item = self.character.equipped[key]
                    col = i % num_in_row
                    if col == 0:
                        row += 1
                    icon = Item_Icon(self, i, item, default_font, 20, WHITE, xoffset + spacing * col, yoffset + (row * spacing), str(i + 1), 'equipped')
                    spacing = icon.size + padding
                    self.variable_equip.add(icon)
                    self.game.inventory_hud_icons.add(icon)
                    i += 1

        if self.selected_heading.text == 'Inventory':
            # lists equipped armor and weapon slots:
            icon = Item_Icon(self, 'head', self.character.equipped['head'], default_font, 20, WHITE, 570, 58, 'head', 'equipped')
            icon = Item_Icon(self, 'torso', self.character.equipped['torso'], default_font, 20, WHITE, 570, spacing + 58, 'torso', 'equipped')
            icon = Item_Icon(self, 'gloves', self.character.equipped['gloves'], default_font, 20, WHITE, 645, spacing + 58, 'gloves', 'equipped')
            icon = Item_Icon(self, 'bottom', self.character.equipped['bottom'], default_font, 20, WHITE, 570, spacing * 2 + 58, 'bottom', 'equipped')
            icon = Item_Icon(self, 'feet', self.character.equipped['feet'], default_font, 20, WHITE, 570, spacing * 3 + 58, 'feet', 'equipped')
        if self.selected_heading.text in ['Inventory', 'Magic']:
            icon = Item_Icon(self, 6, self.character.equipped[6], default_font, 20, WHITE, 495, spacing + 58, 'hand2', 'equipped')
            self.variable_equip.add(icon)

        elif self.selected_heading.text in WORKSTATIONS:
            # Lists crafting slots
            self.check_crafting()
            xoffset = 495
            yoffset = 58
            padding = 5
            num_in_row = 3
            row = -1
            col = 0
            i = 0
            for it, item in enumerate(self.crafting_slots):
                col = i % num_in_row
                if col == 0:
                    row += 1
                icon = Item_Icon(self, i, item, default_font, 20, WHITE, xoffset + spacing * col,
                                 yoffset + (row * spacing), None, 'crafting')
                spacing = icon.size + padding
                self.variable_equip.add(icon)
                i += 1

            self.crafted_icon = Item_Icon(self, 0, self.crafted_item, default_font, 20, WHITE, xoffset + spacing * 2, yoffset + (3 * spacing), 'crafted', 'crafted')

        elif self.selected_heading.text == 'Looting':
            # Lists inventory slots
            spacing = 5
            xoffset = 495
            yoffset = 58
            padding = 5
            row = -1
            col = 0
            display_area_width = 450
            num_in_row = int(display_area_width / ICON_SIZE)

            for i, item in enumerate(self.container):
                col = i % num_in_row
                if col == 0:
                    row += 1
                icon = Item_Icon(self, i, item, default_font, 20, WHITE, xoffset + spacing * col, yoffset + (row * spacing), None, 'loot')
                spacing = icon.size + padding
                self.loot_icons.add(icon)


    def display_item_info(self):
        item_dictionary = self.selected_item.item
        i = 0
        for stat in item_dictionary:
            item_stats = ""
            item_stats += (stat + ":  " + str(item_dictionary[stat]))
            self.printable_stat_list.append(item_stats)
            i += 1

    def display_quest_info(self, item):
        # This part wraps the descriptions of the character races. So they are displayed in paragraph form.
        description = wrap(self.game.quests[item.text]['description'], 45)
        for line in description:
            self.printable_stat_list.append(line)
        self.printable_stat_list.append(" ")

    def update(self):
        self.clear_item_info()
        self.generate_headings()
        self.list_items()
        self.running = True
        while self.running:
            self.game.clock.tick(30)
            self.events()
            self.draw()
        self.update_external_variables()

    def update_external_variables(self):
        if ('name' in self.character.equipped[6]):
            self.character.hand2_item = self.character.equipped[6]
        if ('type' in self.character.equipped[6]) and (self.character.equipped[6]['type'] in WEAPON_TYPES):
            self.character.equipped['weapons2'] = self.character.equipped[6]
        else:
            self.character.equipped['weapons2'] = None
        self.character.hand_item = {}
        self.character.equipped['weapons'] = None
        self.character.human_body.update_animations()  # Updates animations for newly equipped or removed weapons etc.
        self.character.dragon_body.update_animations()
        # Preps the 6 hotkey items for display.
        icony = self.game.screen_height - (HUD_ICON_SIZE + 5)
        iconx = self.game.screen_width/2 - (HUD_ICON_SIZE * 3)
        for i, icon in enumerate(self.game.inventory_hud_icons):
            icon.x = i * HUD_ICON_SIZE + iconx
            icon.y = icony
            icon.resize(HUD_ICON_SIZE)
        self.game.selected_hud_item = None
        self.game.in_menu = False
        self.game.beg = perf_counter() # resets the counter so dt doesn't get messed up.





# Old menues
class Menu():  # used as the parent class for other menus.
    def __init__(self, game, character = 'player'):
        self.game = game
        self.running = True
        self.menu_sprites = pg.sprite.Group()
        self.menu_heading_sprites = pg.sprite.Group()
        self.item_sprites = pg.sprite.Group()
        self.item_pictures = pg.sprite.Group()
        self.item_tags_sprites = pg.sprite.Group()  # Used to show things like if the item is equipped
        self.item_selected = False
        self.selected_item = None
        self.printable_stat_list = []
        # These items are changed for inherrited menus.
        self.exit_keys = [pg.K_e, pg.K_ESCAPE]  # The keys used to enter/exit the menu.
        self.action_keys = [pg.K_b, pg.K_x, pg.K_y]
        self.spacing = 20  # Spacing between headings
        self.heading_list = ['Heading1', 'Heading2']  # This is the list of headings
        self.warning_message = False

    def generate_headings(self):
        previous_rect_right = 0
        for i, heading in enumerate(self.heading_list):
            heading_sprite = Text(self, heading, default_font, 30, WHITE, previous_rect_right + self.spacing, 10, "topleft")
            if i == 0:
                self.selected_heading = heading_sprite
                self.item_type = heading.lower()
            previous_rect_right = heading_sprite.rect.right
            self.menu_heading_sprites.add(heading_sprite)

    def events(self):
        # catch all events here
        for event in pg.event.get():
            if event.type == pg.QUIT:
                self.game.quit()
            if event.type == pg.KEYDOWN:
                if event.key in self.exit_keys:
                    if self.game.in_load_menu:
                        if not self.no_save_selected:
                            self.clear_menu()
                            self.running = False
                    else:
                        self.clear_menu()
                        self.running = False
                if event.key == self.action_keys[0]: # use/buy
                    if self.selected_item:
                        self.use_item()
                if event.key == self.action_keys[1]:  # drop/sell item
                    if self.selected_item:
                        self.drop_item()
                        self.clear_item_info()
                if event.key == self.action_keys[2]:  # place item
                    if self.selected_item:
                        self.drop_item(True)
                        self.clear_item_info()
            if event.type == pg.MOUSEBUTTONDOWN:  # Clears off pictures and stats from previously clicked item when new item is clicked.
                self.warning_message = False
                self.mouse_click = pg.mouse.get_pressed()
                pos = pg.mouse.get_pos()
                if [s for s in self.menu_sprites if s.rect.collidepoint(pos)]:
                    self.game.effects_sounds['click'].play()
                self.printable_stat_list = []
                self.item_selected = False
                for picture in self.item_pictures:
                    picture.kill()
            if event.type == pg.MOUSEBUTTONUP:
                pos = pg.mouse.get_pos()
                # get a list of all heading sprites that are under the mouse cursor
                self.clicked_sprites = [s for s in self.menu_sprites if s.rect.collidepoint(pos)]
                for heading in self.menu_heading_sprites:
                    if heading in self.clicked_sprites:
                        self.item_type = heading.text.lower()
                        self.selected_heading = heading
                        self.item_selected = False
                        self.selected_item = None
                        self.list_items()
                # Equips items
                for item in self.clicked_sprites:
                    if item in self.item_sprites:
                        self.selected_item = item
                        self.item_selected = True
                        self.display_item_info(item)
                        if self.mouse_click == (0, 0, 1):
                            self.right_equip(item)
                        # Equipping weapon in left hand
                        if self.mouse_click == (1, 0, 0):
                            self.left_equip(item)
                        self.list_items()

    def clear_menu(self):
        for item in self.item_sprites:
            item.kill()
        for item in self.item_tags_sprites:
            item.kill()

    def clear_item_info(self):
        for item in self.item_pictures:
            item.kill()
        self.selected_item = None
        self.clicked_sprites = []
        self.printable_stat_list = []

    def clear_pictures(self):
        for item in self.item_pictures:
            item.kill()

    def draw_text(self, text, font_name, size, color, x, y, align="topleft"):
        font = pg.font.Font(font_name, size)
        text_surface = font.render(text, True, color)
        text_rect = text_surface.get_rect(**{align: (x, y)})
        self.game.screen.blit(text_surface, text_rect)

    def draw(self):
        self.game.screen.fill(BLACK)
        list_rect = pg.Rect(10, 50, self.game.screen_width / 2 - 10, self.game.screen_height - 100)
        list_rect_fill = pg.Rect(20, 60, self.game.screen_width / 2 - 30, self.game.screen_height - 120)
        description_rect = pg.Rect(self.game.screen_width / 2 + 10, 50, self.game.screen_width / 2 - 20, self.game.screen_height - 100)
        description_rect_fill = pg.Rect(self.game.screen_width / 2 + 20, 60, self.game.screen_width / 2 - 40, self.game.screen_height - 120)
        pg.draw.rect(self.game.screen, WHITE, list_rect, 2)
        pg.draw.rect(self.game.screen, WHITE, description_rect, 2)
        pg.draw.rect(self.game.screen, BLACK, list_rect_fill)
        pg.draw.rect(self.game.screen, BLACK, description_rect_fill)
        if not self.selected_item == None:
            if self.item_selected:
                selected_rect = pg.Rect(self.selected_item.rect.x - 4, self.selected_item.rect.y, self.selected_item.rect.width + 8, self.selected_item.size + 2)
                pg.draw.rect(self.game.screen, YELLOW, selected_rect, 2)
        selected_heading_rect = pg.Rect(self.selected_heading.rect.x - 4, self.selected_heading.rect.y, self.selected_heading.rect.width + 8, self.selected_heading.size + 2)
        pg.draw.rect(self.game.screen, YELLOW, selected_heading_rect, 2)
        self.menu_sprites.draw(self.game.screen)
        if self.item_selected:
            for i, item_stat in enumerate(self.printable_stat_list):
                self.draw_text(item_stat, default_font, 20, WHITE, self.game.screen_width / 2 + 50, self.game.screen_height / 3 + 30 * i, "topleft")
        self.draw_text("Right Click: Equip/Unequip   Left Click: Equip second weapon/View Item    B: use Items    X: drop selected item    E: Exit Menu", default_font, 20, WHITE, 10, self.game.screen_height - 40, "topleft")
        if self.warning_message != "":
            self.draw_text(self.warning_message, default_font, 30, YELLOW, self.game.screen_width/2, self.game.screen_height/2, "topleft")
        pg.display.flip()

    def update(self):
        self.clear_item_info()
        self.generate_headings()
        self.list_items()
        self.running = True
        while self.running:
            self.game.clock.tick(30)
            self.events()
            self.draw()
        self.update_external_variables()

    def update_external_variables(self):
        self.game.in_menu = False
        self.game.beg = perf_counter() # resets the counter so dt doesn't get messed up.

    def use_item(self):
        pass

    def drop_item(self):
        pass

    def place_item(self):
        pass

    def right_equip(self, item):
        pass

    def left_equip(self, item):
        pass

    def list_items(self):
        pass

    def display_item_info(self, item):
        pass


class Character_Design_Menu(Menu):
    def __init__(self, game, character = 'player'):
        super().__init__(game)
        if character == 'player':
            self.character = self.game.player
        else:
            self.character = character
        self.exit_keys = [pg.K_e, pg.K_ESCAPE]  # The keys used to enter/exit the menu.
        self.heading_list = ['Gender', 'Race', 'Hair']  # This is the list of headings
        self.palette = None

    def events(self):
        # catch all events here
        for event in pg.event.get():
            if event.type == pg.QUIT:
                self.game.quit()
            if event.type == pg.KEYDOWN:
                if event.key in self.exit_keys:
                    self.clear_menu()
                    self.running = False
            if event.type == pg.MOUSEBUTTONDOWN:
                pos = pg.mouse.get_pos()
                if [s for s in self.menu_sprites if s.rect.collidepoint(pos)]:
                    self.game.effects_sounds['click'].play()
                self.mouse_click = pg.mouse.get_pressed()
                self.printable_stat_list = []
                self.printable_stat_vals = []
                self.item_selected = False
                for picture in self.item_pictures:
                    picture.kill()
            if event.type == pg.MOUSEBUTTONUP:
                pos = pg.mouse.get_pos()
                # get a list of all sprites that are under the mouse cursor
                self.clicked_sprites = [s for s in self.menu_sprites if s.rect.collidepoint(pos)]
                if self.palette in self.clicked_sprites:
                    if self.item_type == 'hair':
                        self.character.colors['hair'] = self.game.screen.get_at((pos[0], pos[1]))
                    if self.item_type == 'race':
                        self.character.colors['skin'] = self.game.screen.get_at((pos[0], pos[1]))
                for heading in self.menu_heading_sprites:
                    if heading in self.clicked_sprites:
                        self.item_type = heading.text.lower()
                        self.list_items()
                        self.selected_heading = heading
                        self.clear_pictures()
                for item in self.clicked_sprites:
                    if item in self.item_sprites:
                        self.selected_item = item
                        self.item_selected = True
                        self.display_item_info(item)
                        self.character.equipped[self.item_type] = item.text
                        self.list_items()
                # This if and else block sets up default inventory based on gender
                """
                if self.character == self.game.player:
                    if self.character.equipped['gender'] == 'other':
                        self.character.inventory = copy.deepcopy(DEFAULT_INVENTORIES['female' + ' ' + self.character.equipped['race']])
                    else:
                        self.character.inventory = copy.deepcopy(DEFAULT_INVENTORIES[self.character.equipped['gender'] + ' ' + self.character.equipped['race']])
                    #for kind in ITEM_TYPE_LIST:
                    #    try:
                    #        self.character.equipped[kind] = next(iter(self.character.inventory[kind]))
                    #    except:
                    #        self.character.equipped[kind] = None
                else:
                    if self.character.equipped['race'] in list(RACE.keys()):
                        temp_inventory = None
                        if self.character.equipped['gender'] == 'other':
                            temp_inventory = copy.deepcopy(DEFAULT_INVENTORIES['female' + ' ' + self.character.equipped['race']])
                        else:
                            temp_inventory = copy.deepcopy(DEFAULT_INVENTORIES[self.character.equipped['gender'] + ' ' + self.character.equipped['race']])
                        #for kind in ITEM_TYPE_LIST:
                        #    try:
                        #        self.character.equipped[kind] = next(iter(temp_inventory[kind]))
                        #    except:
                        #        self.character.equipped[kind] = None"""
                # Makes sure you are not wearing hair that does not fit your race.
                if self.character.equipped['hair'] not in RACE_HAIR[self.character.equipped['race']]:
                    self.character.equipped['hair'] = None
                self.character.body.update_animations()  # Updates animations for newly equipped or removed weapons etc.
                character_image = self.character.body.body_surface
                character_preview = Picture(self.game, self, character_image, int(self.game.screen_width * (7 / 8)), int(self.game.screen_height * 0.68))


    def list_items(self):
        self.clear_menu()
        i = 0
        for item in self.character.expanded_inventory[self.item_type]:
            if (self.item_type == 'race') and ('dragon' in item):
                pass
            elif (self.item_type == 'hair') and (item in RACE_HAIR[self.character.equipped['race']]):
                item_name = Text(self, item, default_font, 20, WHITE, 50, 30 * i + 75, "topleft")
                self.item_sprites.add(item_name)
                i += 1
            elif self.item_type != 'hair':
                item_name = Text(self, item, default_font, 20, WHITE, 50, 30 * i + 75, "topleft")
                self.item_sprites.add(item_name)
                i += 1
            else:
                pass

    def display_item_info(self, item):
        if self.item_type != 'hair':
            image_path = "self.game." + self.item_type + "_images[" + self.item_type.upper() + "['" + item.text + "']['image']]"
            item_image = eval(image_path)
            picture = Picture(self.game, self, item_image, int(self.game.screen_width * (3/4)), 150)
        if self.item_type == 'race':
            # This part wraps the descriptions of the character races. So they are displayed in paragraph form.
            description = wrap(RACE[item.text]['description'], 60)
            for line in description:
                self.printable_stat_list.append(line)
                self.printable_stat_vals.append("")
            self.printable_stat_list.append(" ")
            self.printable_stat_vals.append(" ")
            stat_list = ['health', 'stamina', 'magica', 'max weight', 'strength', 'agility','healing', 'stamina regen', 'magica regen']

            for x in stat_list:
                stat = str(RACE[item.text]['start_stats'][x])
                self.printable_stat_list.append(x)
                self.printable_stat_vals.append(stat)
            self.printable_stat_list.append("armor ")
            self.printable_stat_vals.append(str(RACE[item.text]['armor']))


    def draw(self):
        self.game.screen.fill(BLACK)
        list_rect = pg.Rect(10, 50, self.game.screen_width / 2 - 10, self.game.screen_height - 100)
        list_rect_fill = pg.Rect(20, 60, self.game.screen_width / 2 - 30, self.game.screen_height - 120)
        description_rect = pg.Rect(self.game.screen_width / 2 + 10, 50, self.game.screen_width / 2 - 20, self.game.screen_height - 100)
        description_rect_fill = pg.Rect(self.game.screen_width / 2 + 20, 60, self.game.screen_width / 2 - 40, self.game.screen_height - 120)
        pg.draw.rect(self.game.screen, WHITE, list_rect, 2)
        pg.draw.rect(self.game.screen, WHITE, description_rect, 2)
        pg.draw.rect(self.game.screen, BLACK, list_rect_fill)
        pg.draw.rect(self.game.screen, BLACK, description_rect_fill)
        if self.item_type == 'hair':
            self.draw_text("Pick Your Hair Color:", default_font, 24, WHITE, int(self.game.screen_width * 0.27), 90, "topleft")
            if self.palette:
                self.palette.kill()
            try:
                self.palette = Picture(self.game, self, self.game.color_swatch_images[HAIR_PALETE_IMAGES[self.character.equipped['race']]], int(self.game.screen_width * 0.39), int(self.game.screen_height * 0.5))
            except:
                self.palette = Picture(self.game, self, self.game.color_swatch_images[0], int(self.game.screen_width * (1 / 4)), 300)

        elif self.item_type == 'race':
            self.draw_text("Pick Your Skin Tone:", default_font, 24, WHITE, int(self.game.screen_width * 0.27), 90, "topleft")
            if self.palette:
                self.palette.kill()
            try:
                self.palette = Picture(self.game, self, self.game.color_swatch_images[PALETE_IMAGES[self.character.equipped['race']]], int(self.game.screen_width * 0.39), int(self.game.screen_height * 0.5))
            except:
                self.palette = Picture(self.game, self, self.game.color_swatch_images[0], int(self.game.screen_width * (1 / 4) + 100), 300)

        if not self.selected_item == None:
            if self.item_selected:
                selected_rect = pg.Rect(self.selected_item.rect.x - 4, self.selected_item.rect.y, self.selected_item.rect.width + 8, self.selected_item.size + 2)
                pg.draw.rect(self.game.screen, YELLOW, selected_rect, 2)
        selected_heading_rect = pg.Rect(self.selected_heading.rect.x - 4, self.selected_heading.rect.y, self.selected_heading.rect.width + 8, self.selected_heading.size + 2)
        pg.draw.rect(self.game.screen, YELLOW, selected_heading_rect, 2)
        self.menu_sprites.draw(self.game.screen)
        spacing = 15
        initialy = self.game.screen_height * (2/5)
        if self.item_selected:
            for i, item_stat in enumerate(self.printable_stat_list):
                self.draw_text(item_stat, default_font, 15, WHITE, self.game.screen_width / 2 + 50, initialy + spacing * i, "topleft")
                self.draw_text(self.printable_stat_vals[i], default_font, 15, WHITE, self.game.screen_width / 2 + 225, initialy + spacing * i, "topleft")
        self.draw_text("Preview:", default_font, 20, WHITE, int(self.game.screen_width * 0.85), int(self.game.screen_height * 0.55), "topleft")
        self.draw_text("Click to Choose Item. Press E when finished.", default_font, 20, WHITE, 10, self.game.screen_height - 40, "topleft")
        pg.display.flip()

    def update_external_variables(self):
        # This code calculates the player's armor rating
        self.character.expanded_inventory['hair'] = [self.character.equipped['hair']] # Removes all other hairstyles from inventory.
        for item in self.character.equipped:
            if self.character.equipped[item]:
                if '2' in item:
                    temp_item = item.replace('2', '')
                else:
                    temp_item = item
                if 'armor' in eval(temp_item.upper())[self.character.equipped[item]]:
                    self.character.stats['armor'] += eval(item.upper())[self.character.equipped[item]]['armor']
        self.character.last_weapon = self.character.equipped['weapons']  # This string is used to keep track of what the player's last weapon was for equipping and unequipping toggling weapons and keeping track of bullets from old weapons
        self.character.current_weapon = self.character.equipped['weapons']  # weapon you had for autoequipping when your weapon is sheathed.
        self.character.last_weapon2 = self.character.equipped['weapons2']  # This string is used to keep track of what the player's last weapon was for equipping and unequipping toggling weapons and keeping track of bullets from old weapons
        self.character.current_weapon2 = self.character.equipped['weapons2']
        self.character.race = self.character.equipped['race']
        self.game.in_character_menu = False
        self.game.in_menu = False
        check_equip(self.character)
        self.character.human_body.update_animations()  # Updates animations for newly equipped or removed weapons etc.
        self.character.dragon_body.update_animations()
        if self.character.possessing:
            self.character.body.update_animations()
        self.character.pre_reload()
        self.character.stats = RACE[self.character.race]['start_stats'] # Gives player different stats based on selected race.
        if self.character.stats['max hunger'] == 1:
            self.character.hungers = False
        if 'wraith' in self.character.equipped['race'] :
            self.character.immaterial = True
        if self.character.immaterial or 'skeleton' in self.character.equipped['race']:
            self.character.magical_being = True
        if 'mechanima' in self.character.race:
            self.character.brightness = 400
            self.game.lights.add(self.character)
            self.character.light_mask_orig = pg.transform.scale(self.game.light_mask_images[2], (self.character.brightness, self.character.brightness))
            self.character.light_mask = self.character.light_mask_orig.copy()
            self.character.light_mask_rect = self.character.light_mask.get_rect()
        if self.character.equipped['race'] in ['skeleton', 'immortui', 'blackwraith', 'skeleton dragon', 'immortui dragon', 'blackwraith dragon']:
            self.character.aggression = 'awd'
        else:
            self.character.aggression = 'awp'
        self.game.beg = perf_counter()  # resets the counter so dt doesn't get messed up.

class Npc_Design_Menu(Character_Design_Menu):
    def __init__(self, game, character = 'player'):
        super().__init__(game, character)

    def display_item_info(self, item):
        if self.item_type != 'race':
            image_path = "self.game." + self.item_type + "_images[" + self.item_type.upper() + "['" + item.text + "']['image']]"
            itemdict = eval(self.item_type.upper())
            item_image = eval(image_path)
            if 'color' in itemdict[item.text]:
                item_image = color_image(item_image, itemdict[item.text]['color'])
            Picture(self.game, self, item_image, int(self.game.screen_width * (3 / 4)), 150)

    def update_external_variables(self):
        inv_menu = Inventory_Menu(self.game, self.character)
        inv_menu.update()
        self.save()
        self.game.in_npc_menu = False
        self.game.in_menu = False
        self.game.generic_npc.kill()

    def save(self):
        inv_list = ['weapons', 'weapons2', 'tops', 'bottoms', 'hats', 'hair', 'shoes', 'gloves', 'items', 'magic']
        temp_inv = {}
        for kind in inv_list:
            temp_list = []
            temp_list.append(self.character.equipped[kind])
            temp_inv[kind] = temp_list
        self.character.kind['inventory'] = temp_inv
        self.character.kind['inventory']['gold'] = 0
        self.character.kind['gender'] = self.character.equipped['gender']
        self.character.kind['race'] = self.character.equipped['race']
        tkinter_menu = Npc_Info_Designer(self, self.character)
        if self.character.kind['name'] != 'generic': # This makes it so it doesn't write unfinished NPCs
            if self.character.kind['name'] != "":
                file = open("npcs.py", "a")
                file.write("\n")
                file.write("PEOPLE[\'" + self.character.species + "\'] = " + str(self.character.kind))
                file.close()
        if not self.running:
            self.game.quit()
        else:
            self.update()

class Inventory_Menu(Menu): # Inventory Menu, also used as the parent class for other menus.
    def __init__(self, game, character = 'player'):
        super().__init__(game, character)
        if character == 'player':
            self.character = self.game.player
        else:
            self.character = character
        # These items are changed for inherrited menus.
        self.exit_keys = [pg.K_i, pg.K_e, pg.K_ESCAPE] # The keys used to enter/exit the menu.
        self.spacing = 20 # Spacing between headings
        self.heading_list = ['Weapons', 'Hats', 'Tops', 'Bottoms', 'Shoes', 'Gloves', 'Items', 'Blocks', 'Magic'] # This is the list of headings

    def generate_headings(self):
        previous_rect_right = 0
        for i, heading in enumerate(self.heading_list):
            heading_sprite = Text(self, heading, default_font, 30, WHITE, previous_rect_right + self.spacing, 10, "topleft")
            if i == 0:
                self.selected_heading = heading_sprite
                self.item_type = heading.lower()
            previous_rect_right = heading_sprite.rect.right
            self.menu_heading_sprites.add(heading_sprite)

    def use_item(self):
        if self.item_type == 'items':
            for x in ['book', 'tome', 'letter']:
                if x in self.selected_item.text:
                    self.read_book()
            self.character.equipped['items'] = self.selected_item.text
            if self.character == self.game.player:
                self.warning_message = self.character.use_item()
            self.selected_item = None
            self.list_items()

    def read_book(self):
        self.letter = False
        if 'letter' in self.selected_item.text:
            self.book_image = self.game.open_letter_image
            self.letter = True
        else:
            self.book_image = self.game.open_book_image
        self.page = 0
        self.wrap_factor = int(ceil((self.game.screen_width / 2) / 15))
        self.number_of_lines = int(ceil((self.game.screen_height / 42)))
        self.book_font = eval(ITEMS[self.selected_item.text]['font'])
        if self.book_font == 'KAWTHI_FONT':
            self.heading_font = KAWTHI_FONT
        else:
            self.heading_font = HEADING_FONT
        self.book_heading = ITEMS[self.selected_item.text]['heading']
        self.book_author = ITEMS[self.selected_item.text]['author']
        spellwords = ITEMS[self.selected_item.text]['spell words']
        self.book_spellwords = wrap(spellwords, self.wrap_factor)
        if 'book:' in self.selected_item.text:
            book_file_name = self.selected_item.text.replace('book: ', '')
        else:
            book_file_name = self.selected_item.text
        with open(path.join(books_folder, book_file_name + '.txt'), 'r') as file:
            self.book_text = file.read()
        book_lines = self.book_text.split('\n')
        wrapped_lines = []
        for line in book_lines:
            wrapped_line = wrap(line, self.wrap_factor, replace_whitespace=False, drop_whitespace=False)
            wrapped_lines.extend(wrapped_line)

        self.book_data = [wrapped_lines[z:z + self.number_of_lines] for z in range(0, len(wrapped_lines), self.number_of_lines)]
        self.display_page()
        waiting = True
        while waiting:
            self.game.clock.tick(30)
            for event in pg.event.get():
                if event.type == pg.QUIT:
                    pg.quit()
                    sys.exit()
                if event.type == pg.MOUSEBUTTONDOWN:
                    if pg.mouse.get_pressed() == (0, 0, 1):
                        self.page += 1
                        self.display_page()
                    elif pg.mouse.get_pressed() == (1, 0, 0):
                        if self.page == 0:
                            pass
                        elif not self.page <= 0:
                            self.page -= 2
                            self.game.effects_sounds['page turn'].play()
                        else:
                            self.game.effects_sounds['page turn'].play()
                        if self.page < 0:
                            self.page = 0
                        self.display_page()

                if event.type == pg.KEYDOWN:
                    if event.key == pg.K_e:
                        waiting = False
                    elif event.key in [pg.K_SPACE, pg.K_RIGHT]:
                        self.page += 1
                        self.display_page()
                    elif event.key in [pg.K_BACKSPACE, pg.K_LEFT]:
                        if self.page == 0:
                            pass
                        elif not self.page <= 0:
                            self.page -= 2
                            self.game.effects_sounds['page turn'].play()
                        else:
                            self.game.effects_sounds['page turn'].play()
                        if self.page < 0:
                            self.page = 0
                        self.display_page()

    def display_page(self):
        self.game.screen.fill(BLACK)
        self.game.screen.blit(self.book_image, (0, 0))
        self.draw_text("Press SPACE to turn page or RIGHT and LEFT Arrow Keys, E to exit.", default_font, 20, WHITE, self.game.screen_width / 2, self.game.screen_height - 15, "center")
        font_size = 18
        byword = 'by'
        if self.book_font == WRITING_FONT:
            font_size = 18
            self.heading_font = WRITING_FONT
        if self.letter:
            byword = 'from'
        if self.page == 0:
            self.draw_text(self.book_heading, self.heading_font, 25, BLACK, self.game.screen_width * (3/4), self.game.screen_height * (1/5), "center")
            self.draw_text(byword, self.book_font, 18, BLACK, self.game.screen_width * (3/4), self.game.screen_height * (2/5), "center")
            self.draw_text(self.book_author, self.book_font, 18, BLACK, self.game.screen_width * (3/4), self.game.screen_height * (3/5), "center")
        else:
            if self.page > len(self.book_data):
                self.page -= 1
                return
            self.game.effects_sounds['page turn'].play()
            #lines = len(self.book_data[self.page])
            left_margin = 125
            top_margin = 45
            line_spacing = 32
            right_margin = self.game.screen_width/2 + 50
            j = 0
            for i, line in enumerate(self.book_data[self.page - 1]):
                self.draw_text(line, self.book_font, font_size, BLACK, left_margin, top_margin + (line_spacing * i), "topleft")
                j += 1
            if self.page == len(self.book_data):
                for line in self.book_spellwords:
                    self.draw_text(line, KAWTHI_FONT, font_size, BLACK, left_margin, top_margin + (line_spacing * j), "topleft")
                    j += 1
            self.page += 1
            if self.page > len(self.book_data):
                pg.display.flip()
                self.page -= 1
                return
            j = 0
            for i, line in enumerate(self.book_data[self.page - 1]):
                self.draw_text(line, self.book_font, font_size, BLACK, right_margin, top_margin + (line_spacing * i), "topleft")
                j += 1
            if self.page == len(self.book_data):
                for line in self.book_spellwords:
                    self.draw_text(line, KAWTHI_FONT, font_size, BLACK, right_margin, top_margin + (line_spacing * j), "topleft")
                    j += 1
        pg.display.flip()


    def drop_item(self, place = False):
        # Unequips item if you drop one you are equipping and don't have another one.
        if self.character.equipped[self.item_type] == self.selected_item.text:
            self.character.equipped[self.item_type] = None
        elif self.character.equipped['weapons2'] == self.selected_item.text: # Unequips dropped secondary weapon.
            self.character.equipped['weapons2'] = None
        # Removes dropped item from inventory
        if self.character.add_inventory(self.selected_item.text, -1):
            if place:
                dropped_item = Dropped_Item(self.game, self.character.pos + vec(50, 0).rotate(-self.character.rot), self.item_type, self.selected_item.text, self.character.rot - 90)
            else:
                dropped_item = Dropped_Item(self.game, self.character.pos + vec(randrange(-50, 50), randrange(-100, 100)), self.item_type, self.selected_item.text)
            self.selected_item.text = 'None'  # Makes it so it doesn't drop more than one of the same item.
        self.list_items()

    def right_equip(self, item):
        if self.character.equipped[self.item_type] == item.text:  # Unequipping
            if self.item_type == 'weapons':
                self.character.last_weapon = item.text
            self.character.equipped[self.item_type] = None
            if self.item_type == 'blocks':
                self.character.block_gid = None
        else:
            if self.item_type == 'weapons':  # Equipping
                if self.character.equipped['weapons2'] == item.text:
                    if self.character.inventory['weapons'][item.text] > 1:
                        self.character.last_weapon = self.character.equipped['weapons']  # Used to keep track of bullets fired from unequipped weapons
                        self.character.equipped[self.item_type] = item.text
                else:
                    self.character.last_weapon = self.character.equipped['weapons']  # Used to keep track of bullets fired from unequipped weapons
                    self.character.equipped[self.item_type] = item.text
            else:
                self.character.equipped[self.item_type] = item.text
                if self.item_type == 'blocks':
                    self.character.equipped['weapons2'] = None # Makes sure the player doesn't equip a block and a weapon in the same hand
                    self.character.get_equipped_block_gid()
        self.check_dual()

    def left_equip(self, item):
        if self.item_type == 'weapons':
            if self.character.equipped['weapons'] == item.text:
                if self.character.inventory['weapons'][item.text] > 1:
                    if self.character.equipped['weapons2'] == item.text:
                        self.character.last_weapon2 = item.text  # Used to keep track of bullets fired from unequipped weapons
                        self.character.equipped['weapons2'] = None
                    else:
                        self.character.last_weapon2 = self.character.equipped['weapons2']  # Used to keep track of bullets fired from unequipped weapons
                        self.character.equipped['weapons2'] = item.text
            else:
                if self.character.equipped['weapons2'] == item.text:
                    self.character.last_weapon2 = item.text  # Used to keep track of bullets fired from unequipped weapons
                    self.character.equipped['weapons2'] = None
                else:
                    self.character.last_weapon2 = self.character.equipped['weapons2']  # Used to keep track of bullets fired from unequipped weapons
                    self.character.equipped['weapons2'] = item.text
        self.check_dual()

    def check_dual(self):
        # This section prevents dual equipping with two handed weapons.
        dual_list = ['bow', 'rifle', 'shotgun', 'launcher']
        for kind in dual_list:
            if kind in str(self.character.equipped['weapons']):
                self.character.equipped['weapons2'] = None
            if kind in str(self.character.equipped['weapons2']):
                self.character.equipped['weapons'] = None

    def list_items(self):
        self.clear_menu()
        displayed_list = [] # Keeps track of which items have been displayed

        row = 0
        x_row = 50
        max_width = 0
        if self.selected_heading.text == 'Magic':
            inventory = self.character.expanded_inventory
        else:
            inventory = self.character.inventory
        for item in inventory[self.item_type]:
            if item not in displayed_list:
                if 30 * row + 75 > (self.game.screen_height - 195):
                    row = 0
                    x_row += max_width + 10
                item_name = Text(self, item, default_font, 20, WHITE, x_row, 30 * row + 75, "topleft")
                self.item_sprites.add(item_name)
                if self.character.equipped[self.item_type] and self.character.equipped[self.item_type] == item:
                    if self.item_type == 'weapons':
                        equipped_text = Text(self, "(R)", default_font, 20, WHITE, item_name.rect.right + 25, 30 * row + 75, "topleft")
                        self.item_tags_sprites.add(equipped_text)
                    else:
                        equipped_text = Text(self, "(E)", default_font, 20, WHITE, item_name.rect.right + 25, 30 * row + 75, "topleft")
                        self.item_tags_sprites.add(equipped_text)
                if self.character.equipped['weapons2'] and self.character.equipped['weapons2'] == item:
                    left_equipped_text = Text(self, "(L)", default_font, 20, WHITE, item_name.rect.left - 32, 30 * row + 75, "topleft")
                    self.item_tags_sprites.add(left_equipped_text)
                if self.selected_heading.text != 'Magic':
                    item_count = Text(self, str(inventory[self.item_type][item]), default_font, 20, WHITE, item_name.rect.right + 10, 30 * row + 75, "topleft")
                    self.item_tags_sprites.add(item_count)
                if item_name.rect.right > max_width:
                    max_width = item_name.rect.right
                displayed_list.append(item)
                row += 1

        # Calculates the player's armor rating
        if self.character == self.game.player:
            self.character.stats['armor'] = 0
            for item in self.character.equipped:
                if self.character.equipped[item]:
                    if '2' in item:
                        temp_item = item.replace('2', '')
                    else:
                        temp_item = item
                    try:
                        if 'armor' in eval(temp_item.upper())[self.character.equipped[item]]:
                            self.character.stats['armor'] += eval(temp_item.upper())[self.character.equipped[item]]['armor']
                    except:
                        pass

    def display_item_info(self, item):
        item_dictionary = globals()[self.item_type.upper()] #converts the item_type string into the correct dictionary to get the item stats from
        if self.item_type == 'blocks':
            gid = gid_with_property(self.game.map.tmxdata, 'material', item.text)
            item_image = self.game.map.tmxdata.get_tile_image_by_gid(gid)
        else:
            if self.item_type[-1:] == 's':
                image_path = "self.game." + self.item_type[:-1] + "_images[" + self.item_type.upper() + "['" + item.text + "']['image']]"
            else:
                image_path = "self.game." + self.item_type + "_images[" + self.item_type.upper() + "['" + item.text + "']['image']]"
            itemdict = eval(self.item_type.upper())
            item_image = eval(image_path)
            if 'color' in itemdict[item.text]:
                item_image = color_image(item_image, itemdict[item.text]['color'])
        Picture(self.game, self, item_image, int(self.game.screen_width * (3/4)), 150)

        for key in item_dictionary:
            if key == item.text:
                i = 0
                for stat in item_dictionary[key]:
                    if stat in ['image', 'offset', 'walk', 'grip']:
                        continue
                    else:
                        item_stats = ""
                        item_stats += (stat + " " + str(item_dictionary[key][stat]))
                        self.printable_stat_list.append(item_stats)
                        i += 1

    def update_external_variables(self):
        add_light = False
        light_reach = 1
        if self.character.equipped['weapons2'] in LIGHTS_LIST:
            self.character.lamp_hand = 'weapons2'
            self.character.brightness = WEAPONS[self.character.equipped['weapons2']]['brightness']
            self.character.mask_kind = WEAPONS[self.character.equipped['weapons2']]['light mask']
            if 'light reach' in WEAPONS[self.character.equipped['weapons2']]:
                light_reach = WEAPONS[self.character.equipped['weapons2']]['light reach']
            add_light = True
        elif self.character.equipped['weapons'] in LIGHTS_LIST:
            self.character.lamp_hand = 'weapons'
            self.character.brightness = WEAPONS[self.character.equipped['weapons']]['brightness']
            self.character.mask_kind = WEAPONS[self.character.equipped['weapons']]['light mask']
            if 'light reach' in WEAPONS[self.character.equipped['weapons']]:
                light_reach = WEAPONS[self.character.equipped['weapons']]['light reach']
            add_light = True
        if add_light:
            self.game.lights.add(self.character)
            self.character.light_mask_orig = pg.transform.scale(self.game.light_mask_images[self.character.mask_kind], (int(self.character.brightness * light_reach), self.character.brightness))
            self.character.light_mask = self.character.light_mask_orig.copy()
            self.character.light_mask_rect = self.character.light_mask.get_rect()
            if self.character.lamp_hand == 'weapons2':
                self.character.light_mask_rect.center = self.character.body.melee2_rect.center
            else:
                self.character.light_mask_rect.center = self.character.body.melee_rect.center
        else:
            if self.character.race != "mechanima":
                if self.character in self.game.lights:
                    self.game.lights.remove(self.character)
        if self.character.equipped[self.character.lamp_hand]:
            if 'plasma' in self.character.equipped[self.character.lamp_hand] or 'elven' in self.character.equipped[self.character.lamp_hand]:
                self.character.light_on = True
        if 'Zhara Talisman' in self.game.player.inventory['items']: # Only lets you transform into a dragon if you have the Zhara Talisman
            self.game.player.transformable = True
        else:
            self.game.player.transformable = False
        if self.character.in_vehicle:
            if not self.character.vehicle.mountable:
                self.character.vehicle.reequip()
        self.game.player.bow = False
        if self.game.player.equipped['weapons']:
            if 'bow' in self.game.player.equipped['weapons']:
                self.game.player.bow = True
        if self.game.player.equipped['weapons2']:
            if 'bow' in self.game.player.equipped['weapons2']:
                self.game.player.bow = True
        self.game.in_inventory_menu = False
        self.game.in_menu = False
        self.character.current_weapon = self.character.equipped['weapons']
        self.character.current_weapon2 = self.character.equipped['weapons2']
        if self.character.swimming:
            if self.character.in_vehicle:
                if not self.character.vehicle.mountable:
                    self.character.vehicle.reequip()
            else:
                toggle_equip(self.character, True)
        check_equip(self.character)
        self.character.human_body.update_animations()  # Updates animations for newly equipped or removed weapons etc.
        self.character.dragon_body.update_animations()
        if self.character.possessing:
            self.character.body.update_animations()
        if self.character == self.game.player:
            self.character.calculate_fire_power()
            self.character.calculate_perks()
            # Reloads
            self.character.pre_reload()
        if self.character.equipped['race'] in ['skeleton', 'immortui', 'blackwraith', 'skeleton dragon', 'immortui dragon', 'blackwraith dragon']:
            self.character.aggression = 'awd'
        else:
            self.character.aggression = 'awp'
        self.game.beg = perf_counter() # resets the counter so dt doesn't get messed up.


    def draw(self):
        self.game.screen.fill(BLACK)
        list_rect = pg.Rect(10, 50, self.game.screen_width / 2 - 10, self.game.screen_height - 100)
        list_rect_fill = pg.Rect(20, 60, self.game.screen_width / 2 - 30, self.game.screen_height - 120)
        description_rect = pg.Rect(self.game.screen_width / 2 + 10, 50, self.game.screen_width / 2 - 20, self.game.screen_height - 100)
        description_rect_fill = pg.Rect(self.game.screen_width / 2 + 20, 60, self.game.screen_width / 2 - 40, self.game.screen_height - 120)
        pg.draw.rect(self.game.screen, WHITE, list_rect, 2)
        pg.draw.rect(self.game.screen, WHITE, description_rect, 2)
        pg.draw.rect(self.game.screen, BLACK, list_rect_fill)
        pg.draw.rect(self.game.screen, BLACK, description_rect_fill)
        # Used for NPC designing menu
        if self.character != self.game.player:
            self.clear_pictures()
            self.character.body.update_animations()  # Updates animations for newly equipped or removed weapons etc.
            character_image = self.character.body.body_surface
            character_preview = Picture(self.game, self, character_image, int(self.game.screen_width * (3 / 4)), self.game.screen_height - 200)
        if not self.selected_item == None:
            if self.item_selected:
                selected_rect = pg.Rect(self.selected_item.rect.x - 4, self.selected_item.rect.y, self.selected_item.rect.width + 8, self.selected_item.size + 2)
                pg.draw.rect(self.game.screen, YELLOW, selected_rect, 2)
        selected_heading_rect = pg.Rect(self.selected_heading.rect.x - 4, self.selected_heading.rect.y, self.selected_heading.rect.width + 8, self.selected_heading.size + 2)
        pg.draw.rect(self.game.screen, YELLOW, selected_heading_rect, 2)
        self.menu_sprites.draw(self.game.screen)
        if self.item_selected:
            for i, item_stat in enumerate(self.printable_stat_list):
                self.draw_text(item_stat, default_font, 12, WHITE, self.game.screen_width / 2 + 50, self.game.screen_height / 6 + 15 * i, "topleft")
        if self.character == self.game.player:
            self.draw_text("Armor Rating: " + str(self.character.stats['armor']) + "   Carry Weight: " + str(self.character.stats['weight']) + "  Max Carry Weight: " + str(self.character.stats['max weight']), default_font, 12, WHITE, 20, self.game.screen_height - 80, "topleft")
        self.draw_text("Right Click: Equip/Unequip   Left Click: Equip second weapon/View Item   B: use Items   X: drop selected item  Y: place item  E: Exit Menu   ESC: quit game", default_font, 12, WHITE, 10, self.game.screen_height - 40, "topleft")
        if self.warning_message:
            self.draw_text(self.warning_message, default_font, 60, YELLOW, self.game.screen_width/2, self.game.screen_height/2, "center")
        pg.display.flip()


class Loot_Menu(Inventory_Menu):
    def __init__(self, game, container):
        super().__init__(game)
        # These items are changed for inherrited menus.
        self.loot_sprites = pg.sprite.Group()
        self.action_keys = [pg.K_a, pg.K_s]
        self.exit_keys = [pg.K_e, pg.K_ESCAPE]  # The keys used to enter/exit the menu.
        self.heading_list = ['Loot', 'Weapons', 'Hats', 'Tops', 'Bottoms', 'Shoes', 'Gloves', 'Items', 'Blocks']  # This is the list of headings
        self.item_type = None
        self.container = container

    def generate_headings(self):
        previous_rect_right = 0
        for i, heading in enumerate(self.heading_list):
            heading_sprite = Text(self, heading, default_font, 30, WHITE, previous_rect_right + self.spacing, 10, "topleft")
            if i == 0:
                self.selected_heading = heading_sprite
                self.item_type = heading.lower()
            previous_rect_right = heading_sprite.rect.right
            self.menu_heading_sprites.add(heading_sprite)

    def events(self):
        # catch all events here
        for event in pg.event.get():
            if event.type == pg.QUIT:
                self.game.quit()
            if event.type == pg.KEYDOWN:
                if event.key in self.exit_keys:
                    self.clear_menu()
                    self.game.e_down = False
                    self.running = False
                if event.key == self.action_keys[0]: # A key Takes all loot
                    self.game.player.stats['looting'] += self.game.player.add_two_inventories(self.container)
                    for item in ITEM_TYPE_LIST: # Empties the inventory.
                        self.container[item] = {}
                    self.selected_item = None
                    self.list_loot()

                if event.key == self.action_keys[1]: # S key Stores items in containers
                    if self.selected_heading.text != 'Loot':
                        if not self.selected_item == None:
                            # Unequips item if you store one you are equipping and don't have another one.
                            if self.game.player.equipped[self.item_type] == self.selected_item.text:
                                self.game.player.equipped[self.item_type] = None
                            # Stores item in container and removes from inventory
                            add_inventory(self.container, self.selected_item.text, 1)
                            self.game.player.add_inventory(self.selected_item.text, -1)
                            self.selected_item.text = 'None'
                            self.list_items()
                    self.clear_item_info()

            if event.type == pg.MOUSEBUTTONDOWN:
                self.mouse_click = pg.mouse.get_pressed()
                pos = pg.mouse.get_pos()
                if [s for s in self.menu_sprites if s.rect.collidepoint(pos)]:
                    self.game.effects_sounds['click'].play()
                self.printable_stat_list = []
                self.item_selected = False
                for picture in self.item_pictures:
                    picture.kill()
            if event.type == pg.MOUSEBUTTONUP:
                pos = pg.mouse.get_pos()
                # get a list of all sprites that are under the mouse cursor
                self.clicked_sprites = [s for s in self.menu_sprites if s.rect.collidepoint(pos)]
                for heading in self.menu_heading_sprites:
                    if heading in self.clicked_sprites:
                        if heading.text != 'Loot':
                            self.item_type = heading.text.lower()
                            self.list_items()
                        else:
                            self.list_loot()
                        self.selected_heading = heading
                for item in self.clicked_sprites:
                    if item in self.item_sprites:
                        self.selected_item = item
                        self.item_selected = True
                        self.display_item_info(item)
                        if self.mouse_click == (0, 0, 1):
                            self.right_equip(item)
                        if self.mouse_click == (1, 0, 0):
                            self.left_equip(item)
                        self.list_items()
                    elif item in self.loot_sprites:
                        self.selected_item = item
                        self.item_selected = True
                        self.item_type = item.type
                        self.display_item_info(item)
                        if self.mouse_click == (0, 0, 1):
                            counter = Counter(self.container[self.item_type])
                            for x in range(0, counter[item.text]):
                                if self.game.player.add_inventory(item.text, 1):
                                    self.game.player.stats['looting'] += 1
                                    add_inventory(self.container, item.text, -1)
                        self.list_loot()

    def list_loot(self):
        self.clear_menu()
        displayed_list = [] # Keeps track of which items have been displayed
        row = 0
        for item_type in ITEM_TYPE_LIST:
            for item in self.container[item_type]:
                if item not in displayed_list:
                    if item:
                        item_name = Text(self, item, default_font, 20, WHITE, 50, 30 * row + 75, "topleft", item_type)
                        if self.container[item_type][item] > 1:
                            item_count = Text(self, str(self.container[item_type][item]), default_font, 20, WHITE, item_name.rect.right + 10, 30 * row + 75, "topleft")
                            self.item_tags_sprites.add(item_count)
                        row += 1
                        displayed_list.append(item)
                        self.loot_sprites.add(item_name)

    def clear_menu(self):
        super().clear_menu()
        for item in self.loot_sprites:
            item.kill()

    def update(self):
        self.clear_item_info()
        self.generate_headings()
        self.list_loot()
        self.running = True
        while self.running:
            self.game.clock.tick(30)
            self.events()
            self.draw()
        self.update_external_variables()

    def update_external_variables(self):
        if self.game.player.in_vehicle:
            if not self.game.player.vehicle.mountable:
                self.game.player.vehicle.reequip()
        self.game.in_loot_menu = False
        self.game.in_menu = False
        check_equip(self.game.player)
        self.game.player.human_body.update_animations()  # Updates animations for newly equipped or removed weapons etc.
        self.game.player.dragon_body.update_animations()
        self.game.player.current_weapon = self.game.player.equipped['weapons']
        self.game.player.current_weapon2 = self.game.player.equipped['weapons2']
        self.game.player.calculate_fire_power()
        self.game.player.calculate_perks()
        #if self.container in self.game.corpses:
        #    self.container.check_empty()
        self.game.beg = perf_counter() # resets the counter so dt doesn't get messed up.
        del self

    def draw(self):
        self.game.screen.fill(BLACK)
        list_rect = pg.Rect(10, 50, self.game.screen_width / 2 - 10, self.game.screen_height - 100)
        list_rect_fill = pg.Rect(20, 60, self.game.screen_width / 2 - 30, self.game.screen_height - 120)
        description_rect = pg.Rect(self.game.screen_width / 2 + 10, 50, self.game.screen_width / 2 - 20, self.game.screen_height - 100)
        description_rect_fill = pg.Rect(self.game.screen_width / 2 + 20, 60, self.game.screen_width / 2 - 40, self.game.screen_height - 120)
        pg.draw.rect(self.game.screen, WHITE, list_rect, 2)
        pg.draw.rect(self.game.screen, WHITE, description_rect, 2)
        pg.draw.rect(self.game.screen, BLACK, list_rect_fill)
        pg.draw.rect(self.game.screen, BLACK, description_rect_fill)
        if not self.selected_item == None:
            if self.item_selected:
                selected_rect = pg.Rect(self.selected_item.rect.x - 4, self.selected_item.rect.y, self.selected_item.rect.width + 8, self.selected_item.size + 2)
                pg.draw.rect(self.game.screen, YELLOW, selected_rect, 2)
        selected_heading_rect = pg.Rect(self.selected_heading.rect.x - 4, self.selected_heading.rect.y, self.selected_heading.rect.width + 8, self.selected_heading.size + 2)
        pg.draw.rect(self.game.screen, YELLOW, selected_heading_rect, 2)
        self.menu_sprites.draw(self.game.screen)
        if self.item_selected:
            for i, item_stat in enumerate(self.printable_stat_list):
                self.draw_text(item_stat, default_font, 12, WHITE, self.game.screen_width / 2 + 50, self.game.screen_height / 6 + 12 * i, "topleft")
        self.draw_text("Armor Rating: " + str(self.game.player.stats['armor']) + "   Carry Weight: " + str(self.game.player.stats['weight']) + "  Max Carry Weight: " + str(self.game.player.stats['max weight']), default_font, 12, WHITE, 20, self.game.screen_height - 80, "topleft")
        self.draw_text("Right Click to Loot/Equip    A Take all   S: Store selected item   E: Exit menu", default_font, 12, WHITE, 10, self.game.screen_height - 40, "topleft")
        pg.display.flip()


class Lock_Menu():
    def __init__(self, game, lock, kind):
        spacing = 20
        self.game = game
        self.lock = lock
        self.kind = kind
        if self.kind == 'chest':
            self.key_name = self.lock['name'] + ' key'
        self.menu_sprites = pg.sprite.Group()
        self.keyway_sprite = pg.sprite.Group()
        self.running = True
        self.key_unlocked = False
        self.lock_radius = self.game.lock_image.get_width() / 2
        if not self.lock['locked']: # Guards against bugs that might trigger the lock menu for unlocked chests
            self.running = False
        if self.game.player.check_inventory(self.key_name, 1):
            self.key_unlocked = True
            self.lock['locked'] = False
            self.game.effects_sounds['unlock'].play()
            self.game.player.stats['lock picking'] += 2
            self.keyway = Lock_Keyway(self.game, self, True)
            self.keyway.turn = True
            self.label_menu = Text(self, "It looks like you have the right key.", default_font, 15, WHITE, 30, 10, "topleft")
        elif self.game.player.check_inventory('lock pick', 1): # sees if you have a lock pick of any type in your inventory.
            self.keyway = Lock_Keyway(self.game, self)
            self.pick = Lock_Pick(self.game, self)
            self.label_menu = Text(self, "Pick Lock: Use W/S to move lock pick and SPACE to try to open the lock.", default_font, 15, WHITE, 30, 10, "topleft")
        else:
            self.label_menu = Text(self, 'You need a key or lock pick to open this lock!', default_font, 15, WHITE, 30, 100, "topleft")
        self.menu_sprites.add(self.label_menu)
        self.broken = False
        pg.mixer.music.stop() # Music is annoying while picking locks.

    def events(self):
        # catch all events here
        for event in pg.event.get():
            if event.type == pg.QUIT:
                self.game.quit()
            if event.type == pg.KEYDOWN:
                if event.key in [pg.K_e, pg.K_ESCAPE]:
                    self.game.e_down = False
                    self.running = False

    def update(self):
        self.running = True
        while self.running:
            self.game.clock.tick(30)
            try:
                if self.pick.alive():
                    self.pick.update()
            except:
                pass
            try:
                if self.keyway.alive():
                    self.keyway.update()
            except:
                pass
            self.events()
            self.draw()
        self.game.in_lock_menu = self.game.in_menu = False
        if 'inventory' in self.lock: # Enters loot menu after you unlock a chest.
            self.game.in_loot_menu = True
            self.game.loot_menu = Loot_Menu(self.game, self.lock['inventory'])
        pg.mixer.music.play(loops=-1)
        self.game.beg = perf_counter() # resets the counter so dt doesn't get messed up.
        del self

    def draw(self):
        self.game.screen.fill(BLACK)
        self.game.screen.blit(self.game.lock_image, (self.game.screen_width/2 - self.lock_radius, self.game.screen_height/2 - self.lock_radius))
        self.keyway_sprite.draw(self.game.screen)
        self.menu_sprites.draw(self.game.screen)
        if self.key_unlocked:
            self.draw_text("You unlocked the lock with the key.", default_font, 30, WHITE, 120, int(self.game.screen_height * 3/4), "topleft")
        elif not self.lock['locked']:
            self.draw_text("You successfully picked the lock!", default_font, 30, WHITE, 120, int(self.game.screen_height * 3/4), "topleft")
        if self.broken:
            self.draw_text("You broke your lock pick!", default_font, 30, WHITE, 120, int(self.game.screen_height * 3/4), "topleft")
        self.draw_text("E: Exit menu", default_font, 20, WHITE, 10, self.game.screen_height - 40, "topleft")
        pg.display.flip()

    def draw_text(self, text, font_name, size, color, x, y, align="topleft"):
        font = pg.font.Font(font_name, size)
        text_surface = font.render(text, True, color)
        text_rect = text_surface.get_rect(**{align: (x, y)})
        self.game.screen.blit(text_surface, text_rect)

class Lock_Pick(pg.sprite.Sprite):
    def __init__(self, game, mother):
        self.mother = mother
        self.groups = self.mother.menu_sprites
        pg.sprite.Sprite.__init__(self, self.groups)
        self.game = game
        self.surface_width = 30
        self.surface_height = 600
        self.surface = pg.Surface((self.surface_width, self.surface_height)).convert()
        self.surface.fill(TRANSPARENT)
        self.surface.set_colorkey(TRANSPARENT)  # makes transparent
        self.image_orig = self.game.lock_pick_image
        #self.surface.blit(self.image_orig, (5, -100))
        self.image = self.surface
        self.rect = self.image.get_rect()
        self.rect.center = (self.game.screen_width/2 + 5, self.game.screen_height/2 + self.surface_height/2 + 3)
        self.old_center = self.rect.center
        self.pos = vec(0, self.rect.center[1])
        self.rot = 0
        self.rot_speed = 0
        self.combo = self.mother.lock['combo']
        self.difficulty = self.mother.lock['difficulty']
        self.move = False
        self.last_move = 0
        self.hp = 25
        self.toggle = 2
        self.y_offset = 0
        if self.game.player.check_inventory('lock pick', 1):
            self.selected_pick = 'lock pick'

    def get_keys(self):
        self.rot_speed = 0
        self.move = False
        keys = pg.key.get_pressed()
        if keys[pg.K_w]:
            self.rot_speed = -PLAYER_ROT_SPEED
            self.move = True
        if keys[pg.K_s]:
            self.rot_speed = PLAYER_ROT_SPEED
            self.move = True
        if keys[pg.K_SPACE]:
            self.toggle = -self.toggle
            self.mother.keyway.jiggle = True
            self.pick()
        if self.move:
            now = pg.time.get_ticks()
            if now - self.last_move > self.game.effects_sounds['lock click'].get_length() * 1000:
                self.last_move = now
                if abs(self.rot - self.combo) <= self.difficulty:
                    self.game.effects_sounds['lock click'].play()
                else:
                    choice(self.game.lock_picking_sounds).play()

    def pick(self):
        self.pos.x += self.toggle
        self.y_offset += self.toggle
        if self.selected_pick == None:
            self.hp = -1
            self.mother.keyway.rot += self.toggle
            self.mother.broken = True
            choice(self.game.lock_picking_sounds).play()
            self.mother.keyway.kill()
            self.kill()
        #working, self.selected_pick = self.game.player.change_used_item('items', self.selected_pick, True) # Makes it so the lock pick wears out.
        if True:
            if abs(self.rot - self.combo) <= self.difficulty:
                self.mother.keyway.turn = True
            else:
                self.hp -= 1
                self.mother.keyway.rot += self.toggle
                choice(self.game.lock_picking_sounds).play()
                if self.hp < 0:
                    self.game.player.add_inventory(self.selected_pick, -1)
                    self.mother.broken = True
                    choice(self.game.lock_picking_sounds).play()
                    self.mother.keyway.kill()
                    self.kill()
        else:
            self.hp = -1
            self.mother.keyway.rot += self.toggle
            self.mother.broken = True
            choice(self.game.lock_picking_sounds).play()
            self.mother.keyway.kill()
            self.kill()


    def update(self):
        if self.mother.keyway.open:
            self.mother.lock['locked'] = False
            self.game.effects_sounds['unlock'].play()
            self.game.player.stats['lock picking'] += 20 / self.difficulty
            self.kill()
        self.get_keys()
        self.rot = (self.rot + self.rot_speed * self.game.dt) % 360
        y_disp = (abs(self.rot - 180) + 160)/2
        self.pos.y = self.old_center[1] + y_disp + self.y_offset
        self.surface.fill(BLACK)
        self.surface.set_colorkey(BLACK)  # makes transparent
        self.surface.blit(self.image_orig, (5, 70 -y_disp))
        self.image = self.surface
        self.rect = self.image.get_rect()
        pos =  (self.old_center) + vec(self.pos.x, 0)
        self.rect.center = pos


class Lock_Keyway(pg.sprite.Sprite):
    def __init__(self, game, mother, key = False):
        self.mother = mother
        self.groups = self.mother.keyway_sprite
        pg.sprite.Sprite.__init__(self, self.groups)
        self.game = game
        self.keyway_radius = self.game.lock_keyway_image.get_width() / 2
        if key:
            self.image_orig = self.game.keyed_keyway_image
        else:
            self.image_orig = self.game.lock_keyway_image
        self.image = self.image_orig.copy()
        self.rect = self.image.get_rect()
        self.rect.center = (self.game.screen_width/2 - 1, self.game.screen_height/2 + 8)
        self.rot = 0
        self.last_frame = 0
        self.turn = False
        self.jiggle = False
        self.jiggle_down = True
        self.open = False

    def false_set(self):
        if self.jiggle_down:
            if self.rot > -8:
                self.rot -= 1
            else:
                self.jiggle_down = False
        else:
            if self.rot < 0:
                self.rot += 1
            else:
                self.jiggle_down = True
                self.jiggle = False

    def animate(self):
        if self.rot > -90:
            self.rot -= 5
            if self.rot < -91:
                self.rot = -91
        else:
            self.open = True

    def update(self):
        now = pg.time.get_ticks()
        if self.turn:
            if now - self.last_frame > 1:
                self.last_fram = now
                self.animate()
        elif self.jiggle:
            if now - self.last_frame > 20:
                self.last_fram = now
                self.false_set()
        self.image = pg.transform.rotate(self.game.lock_pick_image, self.rot)
        new_image = pg.transform.rotate(self.image_orig, self.rot)
        old_center = self.rect.center
        self.image = new_image
        self.rect = self.image.get_rect()
        self.rect.center = old_center


class Load_Menu(Menu):
    def __init__(self, game):
        super().__init__(game)
        self.exit_keys = [pg.K_l, pg.K_e, pg.K_ESCAPE] # The keys used to enter/exit the menu.
        self.spacing = 40 # Spacing between headings
        self.heading_list = ['Saves'] # This is the list of headings
        self.previous_item = None
        self.no_save_selected = True

    def use_item(self):
        if self.selected_item:
            pass

    def drop_item(self):
        if not self.game.in_character_menu:
            if self.selected_item:
                pass

    def right_equip(self, item):
        keys = pg.key.get_pressed()
        if keys[pg.K_r]:
            self.game.update_old_save(path.join(saves_folder, item.text))
            print('save updated: quests/chests/npcs reset')
        else:
            self.game.load_save(path.join(saves_folder, item.text))
        self.running = False
        self.no_save_selected = False

    def left_equip(self, item):
        if self.previous_item:
            if item.text == self.previous_item.text:
                self.game.load_save(path.join(saves_folder, item.text))
                self.running = False
        self.previous_item = item

    def list_items(self):
        self.clear_menu()
        for i, filepath in enumerate(sorted(glob(path.join(saves_folder, "*.sav")), reverse = True)):
            save_name = Text(self, path.basename(filepath), default_font, 20, WHITE, 50, 30 * i + 75, "topleft")
            if self.selected_item == None:
                if i == 0:
                    self.selected_item = save_name
            self.item_sprites.add(save_name)

    def display_item_info(self, item):
        pass

    def update_external_variables(self):
        self.game.in_load_menu = False
        self.game.in_menu = False
        self.game.beg = perf_counter() # resets the counter so dt doesn't get messed up.

    def draw(self):
        self.game.screen.fill(BLACK)
        list_rect = pg.Rect(10, 50, self.game.screen_width / 2 - 10, self.game.screen_height - 100)
        list_rect_fill = pg.Rect(20, 60, self.game.screen_width / 2 - 30, self.game.screen_height - 120)
        description_rect = pg.Rect(self.game.screen_width / 2 + 10, 50, self.game.screen_width / 2 - 20, self.game.screen_height - 100)
        description_rect_fill = pg.Rect(self.game.screen_width / 2 + 20, 60, self.game.screen_width / 2 - 40, self.game.screen_height - 120)
        pg.draw.rect(self.game.screen, WHITE, list_rect, 2)
        pg.draw.rect(self.game.screen, WHITE, description_rect, 2)
        pg.draw.rect(self.game.screen, BLACK, list_rect_fill)
        pg.draw.rect(self.game.screen, BLACK, description_rect_fill)
        if not self.selected_item == None:
            if self.item_selected:
                selected_rect = pg.Rect(self.selected_item.rect.x - 4, self.selected_item.rect.y, self.selected_item.rect.width + 8, self.selected_item.size + 2)
                pg.draw.rect(self.game.screen, YELLOW, selected_rect, 2)
        selected_heading_rect = pg.Rect(self.selected_heading.rect.x - 4, self.selected_heading.rect.y, self.selected_heading.rect.width + 8, self.selected_heading.size + 2)
        pg.draw.rect(self.game.screen, YELLOW, selected_heading_rect, 2)
        self.menu_sprites.draw(self.game.screen)
        if self.item_selected:
            for i, item_stat in enumerate(self.printable_stat_list):
                self.draw_text(item_stat, default_font, 20, WHITE, self.game.screen_width / 2 + 50, self.game.screen_height / 3 + 30 * i, "topleft")
        self.draw_text("Left Click: Select Save    Right or Double Click: Load Save", default_font, 20, WHITE, 10, self.game.screen_height - 40, "topleft")
        pg.display.flip()

class Stats_Menu(Draw_Text):
    def __init__(self, game):
        spacing = 20
        self.game = game
        self.menu_sprites = pg.sprite.Group()
        self.menu_heading_sprites = pg.sprite.Group()
        self.item_sprites = pg.sprite.Group()
        self.weapons_menu = Text(self, "Stats:", default_font, 30, WHITE, 30, 10, "topleft")
        self.menu_heading_sprites.add(self.weapons_menu)
        self.running = True

    def events(self):
        # catch all events here
        for event in pg.event.get():
            if event.type == pg.QUIT:
                self.game.quit()
            if event.type == pg.KEYDOWN:
                if event.key in [pg.K_e, pg.K_k, pg.K_ESCAPE]:
                    self.running = False

    def update(self):
        self.running = True
        while self.running:
            self.game.clock.tick(30)
            self.events()
            self.draw()
        self.game.in_stats_menu = self.game.in_menu = False
        self.game.beg = perf_counter() # resets the counter so dt doesn't get messed up.

    def draw(self):
        self.game.screen.fill(BLACK)
        list_rect = pg.Rect(10, 50, self.game.screen_width / 2 - 10, self.game.screen_height - 100)
        list_rect_fill = pg.Rect(20, 60, self.game.screen_width / 2 - 30, self.game.screen_height - 120)
        description_rect = pg.Rect(self.game.screen_width / 2 + 10, 50, self.game.screen_width / 2 - 20, self.game.screen_height - 100)
        description_rect_fill = pg.Rect(self.game.screen_width / 2 + 20, 60, self.game.screen_width / 2 - 40, self.game.screen_height - 120)
        pg.draw.rect(self.game.screen, WHITE, list_rect, 2)
        pg.draw.rect(self.game.screen, WHITE, description_rect, 2)
        pg.draw.rect(self.game.screen, BLACK, list_rect_fill)
        pg.draw.rect(self.game.screen, BLACK, description_rect_fill)
        self.menu_sprites.draw(self.game.screen)

        # Prints out player's stats
        for i, item in enumerate(self.game.player.stats):
            self.draw_text(item + ": " + str(round(self.game.player.stats[item], 2)), default_font, 20, WHITE, 20, 60 + (25 * i), "topleft")
        self.draw_text("Right Click to Select Menu  E or K to exit menu", default_font, 20, WHITE, 10, self.game.screen_height - 40, "topleft")
        pg.display.flip()

class Work_Station_Menu(Menu): # Used for upgrading weapons
    def __init__(self, game, kind):
        super().__init__(game)
        # These items are changed for inherrited menus.
        self.exit_keys = [pg.K_i, pg.K_e, pg.K_ESCAPE]  # The keys used to enter/exit the menu.
        self.action_keys = [pg.K_f]
        self.spacing = 20  # Spacing between headings
        self.kind = kind
        if self.kind == 'anvil':
            self.heading_list = ['Weapons', 'Hats', 'Tops', 'Bottoms', 'Shoes', 'Gloves', 'Items']  # This is the list of headings
        elif self.kind == 'smelter':
            self.heading_list = ['Items']  # This is the list of headings
        elif self.kind == 'tanning rack':
            self.heading_list = ['Items']  # This is the list of headings
        elif self.kind == 'work bench':
            self.heading_list = ['Hats', 'Tops', 'Bottoms', 'Shoes', 'Gloves']  # This is the list of headings
        elif self.kind == 'grinder':
            self.heading_list = ['Weapons']  # This is the list of headings
        elif self.kind == 'cooking fire':
            self.heading_list = ['Items']
        elif self.kind == 'alchemy lab':
            self.heading_list = ['Items']
        elif self.kind == 'enchanter':
            self.heading_list = ['Enchantments', 'Weapons', 'Hats', 'Tops', 'Bottoms', 'Shoes', 'Gloves']  # This is the list of headings
        elif self.kind == 'crafting':
            self.heading_list = ['Weapons', 'Hats', 'Tops', 'Bottoms', 'Shoes', 'Gloves', 'Items', 'Blocks']
        self.clicked_sprites = []
        self.not_enough_text = False
        self.materials_list = {}
        self.item_type = self.heading_list[0].lower()
        self.selected_item = None
        self.selected_enchantment = None
        self.task_acomplished = False
        self.list_items()

    def generate_headings(self):
        previous_rect_right = 0
        for i, heading in enumerate(self.heading_list):
            heading_sprite = Text(self, heading, default_font, 30, WHITE, previous_rect_right + self.spacing, 10, "topleft")
            if i == 0:
                self.selected_heading = heading_sprite
                self.item_type = heading.lower()
            previous_rect_right = heading_sprite.rect.right
            self.menu_heading_sprites.add(heading_sprite)

    def forge_item(self):
        if self.item_type != 'enchantments':
            self.task_accomplished = False
            if self.kind == 'tanning rack':
                sound = 'scrape'
                if not self.task_accomplished:
                    skins = [s for s in list(self.game.player.inventory['items'].keys()) if "skin" in s]
                    if skins:
                        if self.game.player.add_inventory(self.selected_item.text, 1):
                            self.game.player.add_inventory(skins[0], -1)
                            self.game.player.stats['smithing'] += 1
                            self.task_accomplished = True
                    elif not self.task_accomplished:
                        self.not_enough_text = True

            elif self.kind == 'grinder':
                sound = 'grindstone'
                enough = self.check_materials(self.selected_item.text, True)
                if enough:
                    # Subtracts used materials from inventory
                    self.remove_materials()
                    # Upgrades item and adds it to the WEAPONS dictionary
                    upgraded_item = WEAPONS[self.selected_item.text].copy()
                    upgraded_item['melee damage'] += 1 + self.game.player.stats['smithing'] / 10
                    upgraded_item['damage'] += 1 + self.game.player.stats['smithing'] / 10
                    if 'value' in upgraded_item.keys():
                        upgraded_item['value'] += 1 + int(self.game.player.stats['smithing'] / UPGRADE_FACTOR)
                    new_item_name = self.rename_item()
                    UPGRADED_WEAPONS[new_item_name] = upgraded_item
                    WEAPONS[new_item_name] = upgraded_item
                    self.game.player.add_inventory(self.selected_item.text, -1) # removes old item from inventory
                    self.game.player.add_inventory(new_item_name, 1) # adds upgraded item to inventory
                    # Unequips old item and equips upgraded one if you were equipping it.
                    if self.game.player.equipped['weapons'] == self.selected_item.text:
                        self.game.player.equipped['weapons'] = new_item_name
                    if self.game.player.equipped['weapons2'] == self.selected_item.text:
                        self.game.player.equipped['weapons2'] = new_item_name
                    self.selected_item = None
                    self.game.player.stats['smithing'] += 1
                    self.task_accomplished = True
                else:
                    self.not_enough_text = True

            elif self.kind == 'anvil':
                sound = 'anvil'
                enough = self.check_materials(self.selected_item.text)

                if enough:
                    # Subtracts used materials from inventory
                    self.remove_materials()
                    self.game.player.add_inventory(self.selected_item.text, 1) # adds forged item to inventory
                    self.game.player.stats['smithing'] += 1
                    self.task_accomplished = True
                else:
                    self.not_enough_text = True

            elif self.kind == 'smelter':
                sound = 'fire blast'
                enough = self.check_materials(self.selected_item.text)

                if enough:
                    # Subtracts used materials from inventory
                    self.remove_materials()
                    self.game.player.add_inventory(self.selected_item.text, 1) # adds forged item to inventory
                    self.game.player.stats['smithing'] += 1
                    self.task_accomplished = True
                else:
                    self.not_enough_text = True

            elif self.kind == 'work bench':
                sound = 'hammering'
                enough = self.check_materials(self.selected_item.text, True)
                if enough:
                    # Subtracts used materials from inventory
                    self.remove_materials()
                    # Upgrades item and adds it to the armor dictionary
                    upgraded_item = eval(self.item_type.upper())[self.selected_item.text].copy()
                    upgraded_item['armor'] += 1 + self.game.player.stats['smithing'] / 10
                    if 'value' in upgraded_item.keys():
                        upgraded_item['value'] += 1 + int(self.game.player.stats['smithing'] / UPGRADE_FACTOR)
                    new_item_name = self.rename_item()
                    if self.item_type == 'hats':
                        UPGRADED_HATS[new_item_name] = upgraded_item
                        HATS[new_item_name] = upgraded_item
                    elif self.item_type == 'tops':
                        UPGRADED_TOPS[new_item_name] = upgraded_item
                        TOPS[new_item_name] = upgraded_item
                    elif self.item_type == 'gloves':
                        UPGRADED_GLOVES[new_item_name] = upgraded_item
                        GLOVES[new_item_name] = upgraded_item
                    elif self.item_type == 'bottoms':
                        UPGRADED_BOTTOMS[new_item_name] = upgraded_item
                        BOTTOMS[new_item_name] = upgraded_item
                    elif self.item_type == 'shoes':
                        UPGRADED_SHOES[new_item_name] = upgraded_item
                        SHOES[new_item_name] = upgraded_item
                    self.game.player.add_inventory(self.selected_item.text, -1) # removes non-upgraded item
                    self.game.player.add_inventory(new_item_name, 1)  # adds upgraded item to inventory
                    # Unequips old item and equips upgraded one if you were equipping it.
                    if self.game.player.equipped[self.item_type] == self.selected_item.text:
                        self.game.player.equipped[self.item_type] = new_item_name
                    self.game.player.stats['smithing'] += 1
                    self.task_accomplished = True
                else:
                    self.not_enough_text = True

            elif self.kind == 'enchanter':
                enchanted_offset = ENCHANTED_OFFSET
                casting_factor = int(self.game.player.stats['casting'] / 10) # This is how much your casting experience influences enchantment's potency
                sound = 'enchant'
                enough = self.check_materials(self.selected_enchantment)
                if enough:
                    # Subtracts used materials from inventory
                    self.remove_materials()
                    # Upgrades item and adds it to the armor dictionary
                    upgraded_item = eval(self.item_type.upper())[self.selected_item.text].copy()
                    if self.selected_enchantment == 'fire spark':
                        if upgraded_item['gun']:
                            upgraded_item['damage'] += casting_factor
                            if 'value' in upgraded_item.keys():
                                upgraded_item['value'] += 1 + int(self.game.player.stats['casting'] / UPGRADE_FACTOR)
                            bullet = upgraded_item['bullet_size'][-1:]
                            size = upgraded_item['bullet_size'][:2]
                            if bullet == '1':
                                upgraded_item['bullet_size'] = size + '6'
                            elif bullet == '2':
                                upgraded_item['bullet_size'] = size + '9'
                            elif bullet == '3':
                                upgraded_item['bullet_count'] += 1
                            elif bullet == '4':
                                upgraded_item['bullet_size'] = size + '5'
                            else:
                                upgraded_item['bullet_size'] = 'md3'
                        else:
                            upgraded_item['bullet_speed'] = 200 + casting_factor
                            if upgraded_item['bullet_speed'] > 700:
                                upgraded_item['bullet_speed'] = 700
                            upgraded_item['bullet_lifetime'] = 400 + casting_factor * 5
                            if upgraded_item['bullet_lifetime'] > 2000:
                                upgraded_item['bullet_lifetime'] = 2000
                            upgraded_item['magazine size'] = 10 + casting_factor
                            upgraded_item['kickback'] = 0
                            upgraded_item['spread'] = 4
                            upgraded_item['damage'] = 1 + casting_factor
                            upgraded_item['bullet_size'] = 'lg3'
                            upgraded_item['bullet_count'] = 1
                            upgraded_item['offset'] = enchanted_offset

                    elif self.selected_enchantment == 'electric spark':
                        if upgraded_item['gun']:
                            upgraded_item['damage'] += casting_factor
                            bullet = upgraded_item['bullet_size'][-1:]
                            size = upgraded_item['bullet_size'][:2]
                            if bullet == '1':
                                upgraded_item['bullet_size'] = size + '7'
                            elif bullet == '2':
                                upgraded_item['bullet_count'] += 1
                            elif bullet == '3':
                                upgraded_item['bullet_size'] = size + '9'
                            elif bullet == '4':
                                upgraded_item['bullet_size'] = size + '8'
                            else:
                                upgraded_item['bullet_size'] = 'lg2'

                        else:
                            upgraded_item['bullet_speed'] = 225 + casting_factor
                            if upgraded_item['bullet_speed'] > 700:
                                upgraded_item['bullet_speed'] = 700
                            upgraded_item['bullet_lifetime'] = 300 + casting_factor*5
                            if upgraded_item['bullet_lifetime'] > 2000:
                                upgraded_item['bullet_lifetime'] = 2000
                            upgraded_item['magazine size'] = 20 + casting_factor
                            upgraded_item['kickback'] = 0
                            upgraded_item['spread'] = 30
                            upgraded_item['damage'] = 1 + casting_factor
                            upgraded_item['bullet_size'] = 'lg2'
                            upgraded_item['bullet_count'] = 2 + int(casting_factor/10)
                            upgraded_item['offset'] = enchanted_offset

                    elif self.selected_enchantment == 'explosive':
                        if upgraded_item['gun']:
                            upgraded_item['damage'] += casting_factor
                            bullet = upgraded_item['bullet_size'][-1:]
                            size = upgraded_item['bullet_size'][:2]
                            if bullet == '1':
                                upgraded_item['bullet_size'] = size + '10'
                            elif bullet == '2':
                                upgraded_item['bullet_size'] = size + 8
                            elif bullet == '3':
                                upgraded_item['bullet_size'] = size + '5'
                            elif bullet == '4':
                                upgraded_item['bullet_size'] = size + '10'
                                upgraded_item['bullet_count'] += 1
                            else:
                                upgraded_item['bullet_size'] = size + '10'
                        else:
                            upgraded_item['bullet_speed'] = 300 + casting_factor
                            if upgraded_item['bullet_speed'] > 700:
                                upgraded_item['bullet_speed'] = 700
                            upgraded_item['bullet_lifetime'] = 200 + casting_factor
                            if upgraded_item['bullet_lifetime'] > 2000:
                                upgraded_item['bullet_lifetime'] = 2000
                            upgraded_item['magazine size'] = 20 + casting_factor
                            upgraded_item['kickback'] = 0
                            upgraded_item['spread'] = 15
                            upgraded_item['damage'] = 1 + casting_factor
                            upgraded_item['bullet_size'] = 'md10'
                            upgraded_item['bullet_count'] = 1 + int(casting_factor / 10)
                            upgraded_item['offset'] = enchanted_offset

                    elif self.selected_enchantment == 'dragon breath':
                        if 'fire enhance' not in upgraded_item.keys():
                            added_damage = 10 + casting_factor
                            if added_damage > 100:
                                added_damage = 100
                            reduced_rate = 100 + casting_factor
                            upgraded_item['fire enhance'] = {'after effect': 'fire', 'damage': added_damage, 'life time': 1000, 'speed': 50, 'rate reduction': reduced_rate}
                        else:
                            upgraded_item['fire enhance']['damage'] += added_damage

                    elif 'reinforced' in self.selected_enchantment:
                        reinforce_kind = self.selected_enchantment.replace('d', '')
                        if reinforce_kind not in upgraded_item.keys():
                            upgraded_item[reinforce_kind] = 10 + casting_factor
                        else:
                            upgraded_item[reinforce_kind] += 20

                    new_item_name = self.rename_item()
                    if self.item_type == 'weapons':
                        UPGRADED_WEAPONS[new_item_name] = upgraded_item
                        WEAPONS[new_item_name] = upgraded_item
                    if self.item_type == 'hats':
                        UPGRADED_HATS[new_item_name] = upgraded_item
                        HATS[new_item_name] = upgraded_item
                    elif self.item_type == 'tops':
                        UPGRADED_TOPS[new_item_name] = upgraded_item
                        TOPS[new_item_name] = upgraded_item
                    elif self.item_type == 'gloves':
                        UPGRADED_GLOVES[new_item_name] = upgraded_item
                        GLOVES[new_item_name] = upgraded_item
                    elif self.item_type == 'bottoms':
                        UPGRADED_BOTTOMS[new_item_name] = upgraded_item
                        BOTTOMS[new_item_name] = upgraded_item
                    elif self.item_type == 'shoes':
                        UPGRADED_SHOES[new_item_name] = upgraded_item
                        SHOES[new_item_name] = upgraded_item
                    self.game.player.add_inventory(self.selected_item.text, -1) # removes non-upgraded item
                    self.game.player.add_inventory(new_item_name, 1) # adds upgraded item to inventory
                    # Unequips old item and equips upgraded one if you were equipping it.
                    if self.item_type == 'weapons':
                        if self.game.player.equipped['weapons'] == self.selected_item.text:
                            self.game.player.equipped['weapons'] = new_item_name
                        if self.game.player.equipped['weapons2'] == self.selected_item.text:
                            self.game.player.equipped['weapons2'] = new_item_name
                    elif self.game.player.equipped[self.item_type] == self.selected_item.text:
                        self.game.player.equipped[self.item_type] = new_item_name
                    self.game.player.stats['casting'] += 1
                    self.task_accomplished = True
                else:
                    self.not_enough_text = True

            elif self.kind == 'cooking fire':
                sound = 'fire blast'
                self.add_forged_item()

            elif self.kind == 'alchemy lab':
                sound = 'alchemy'
                self.add_forged_item()

            elif self.kind == 'crafting':
                sound = 'anvil'
                self.add_forged_item()
            else:
                sound = 'anvil'
            if self.task_accomplished:
                self.game.effects_sounds[sound].play()
                self.list_items()
        self.selected_enchantment = None
        self.selected_item = None

    def add_forged_item(self):
        enough = self.check_materials(self.selected_item.text)
        if enough:
            # Subtracts used materials from inventory
            self.remove_materials()
            self.game.player.add_inventory(self.selected_item.text, 1)  # adds forged item to inventory
            self.task_accomplished = True
        else:
            self.not_enough_text = True

    def rename_item(self):
        new_item_name = self.selected_item.text
        if self.kind == 'enchanter':
            new_item_name = self.selected_enchantment + ' enchanted ' + self.selected_item.text + ' ELV' + str(self.game.player.stats['casting'])
        else:
            times_upgraded = 0
            if 'LV' in self.selected_item.text:
                times_upgraded = int(self.selected_item.text[-1:])
                new_item_name = self.selected_item.text.replace(' SLV', '')
                new_item_name = new_item_name.replace(' UP', '')
                new_item_name = re.sub(r'\d+', '', new_item_name)  # Removes numbers from the string
            times_upgraded += 1
            new_item_name = new_item_name + ' SLV' + str(self.game.player.stats['smithing']) + ' UP' + str(times_upgraded)
        return new_item_name

    def remove_materials(self):
        for material, count in self.materials_list.items():
            self.game.player.add_inventory(material, -count)

    def check_materials(self, chosen_item, upgrade = False):
        if not upgrade:
            makeorupgrade = 'materials'
        else:
            makeorupgrade = 'upgrade'
        if 'aetherial' in chosen_item: # Only lets wraiths craft aetherial armor
            if 'wraith' not in self.game.player.equipped['race']:
                return False
        if 'elven' in chosen_item: # Only lets elves craft elven things
            if 'elf' not in self.game.player.equipped['race']:
                return False
        if 'mech' in chosen_item: # Only lets elves craft elven things
            if 'mechanima' not in self.game.player.equipped['race']:
                return False
        if 'dragon' in chosen_item: # Only lets dragons craft dragon things
            if 'dragon' not in self.game.player.equipped['race']:
                return False
        if self.kind == 'enchanter':
            self.materials_list = ENCHANTMENTS[chosen_item][makeorupgrade]
        else:
            self.materials_list = eval(self.item_type.upper())[chosen_item][makeorupgrade]
        return self.game.player.check_materials_list(self.materials_list)


    def events(self):
        # catch all events here
        for event in pg.event.get():
            if event.type == pg.QUIT:
                self.game.quit()
            if event.type == pg.KEYDOWN:
                if event.key in self.exit_keys:
                    self.clear_menu()
                    self.running = False
                if event.key == self.action_keys[0]: # use/buy
                    if self.kind != 'enchanter':
                        if self.selected_item:
                            self.forge_item()
                    else:
                        if self.selected_item and self.selected_enchantment:
                            self.forge_item()

            if event.type == pg.MOUSEBUTTONDOWN:  # Clears off pictures and stats from previously clicked item when new item is clicked.
                self.not_enough_text = False # Clears of the warning text with next click
                self.mouse_click = pg.mouse.get_pressed()
                self.printable_stat_list = []
                self.item_selected = False
                for picture in self.item_pictures:
                    picture.kill()
            if event.type == pg.MOUSEBUTTONUP:
                pos = pg.mouse.get_pos()
                # get a list of all sprites that are under the mouse cursor
                self.clicked_sprites = [s for s in self.menu_sprites if s.rect.collidepoint(pos)]
                for heading in self.menu_heading_sprites:
                    if heading in self.clicked_sprites:
                        self.item_type = heading.text.lower()
                        self.list_items()
                        self.selected_heading = heading

            for item in self.clicked_sprites:
                if item in self.item_sprites:
                    if self.item_type != 'enchantments':
                        self.selected_item = item
                    else:
                        self.selected_enchantment = item.text
                        self.selected_item = item
                    self.item_selected = True
                    self.display_item_info(item)
                    self.list_items()

    def list_items(self):
        self.clear_menu()
        if self.kind == 'anvil':
            row = 0
            item_dict = eval(self.item_type.upper())
            for item in item_dict:
                if item:
                    if ('LV' not in item) and ('HP' not in item):    # no upgraded/damaged items show in forge
                        if ' M' in item:
                            if self.game.player.equipped['gender'] not in ['male']:
                                continue
                        elif ' F' in item:
                            if self.game.player.equipped['gender'] not in ['female', 'other']:
                                continue
                        if 'materials' in item_dict[item]:
                            if self.check_materials(item):
                                if self.item_type == 'items':
                                    if 'forgeable' in item_dict[item]:
                                        item_name = Text(self, item, default_font, 20, WHITE, 50, 30 * row + 75, "topleft")
                                        self.item_sprites.add(item_name)
                                        row += 1
                                else:
                                    item_name = Text(self, item, default_font, 20, WHITE, 50, 30 * row + 75, "topleft")
                                    self.item_sprites.add(item_name)
                                    row += 1

        elif self.kind == 'cooking fire':
            row = 0
            item_dict = eval(self.item_type.upper())
            for item in item_dict:
                if 'food' in item_dict[item]:
                    if item:
                        if 'materials' in item_dict[item]:
                            if self.check_materials(item):
                                item_name = Text(self, item, default_font, 20, WHITE, 50, 30 * row + 75, "topleft")
                                self.item_sprites.add(item_name)
                                row += 1

        elif self.kind == 'alchemy lab':
            row = 0
            item_dict = eval(self.item_type.upper())
            for item in item_dict:
                if 'alchemy' in ITEMS[item].keys():
                    if item:
                        if 'materials' in item_dict[item]:
                            if self.check_materials(item):
                                item_name = Text(self, item, default_font, 20, WHITE, 50, 30 * row + 75, "topleft")
                                self.item_sprites.add(item_name)
                                row += 1

        elif self.kind == 'crafting':
            row = 0
            item_dict = eval(self.item_type.upper())
            for item in item_dict:
                if item:
                    if 'LV' not in item:    # no upgraded items show in crafting
                        if 'materials' in item_dict[item]:
                            if self.check_materials(item):
                                if 'craftable' in item_dict[item]:
                                    item_name = Text(self, item, default_font, 20, WHITE, 50, 30 * row + 75, "topleft")
                                    self.item_sprites.add(item_name)
                                    row += 1

        elif self.kind == 'smelter':
            row = 0
            item_dict = eval(self.item_type.upper())
            for item in item_dict:
                if 'ingot' in item:
                    if item:
                        if 'materials' in item_dict[item]:
                            if self.check_materials(item):
                                item_name = Text(self, item, default_font, 20, WHITE, 50, 30 * row + 75, "topleft")
                                self.item_sprites.add(item_name)
                                row += 1

        elif self.kind == 'tanning rack':
            tan_list = ['leather', 'leather strips']
            row = 0
            for item in tan_list:
                item_name = Text(self, item, default_font, 20, WHITE, 50, 30 * row + 75, "topleft")
                self.item_sprites.add(item_name)
                row += 1

        elif self.kind == 'enchanter':
            row = 0
            for item in eval(self.item_type.upper()):
                if item:
                    if self.item_type == 'enchantments':  # Only lists enchantments you have materials to perform.
                        if 'materials' in ENCHANTMENTS[item]:
                            if self.check_materials(item):
                                item_name = Text(self, item, default_font, 20, WHITE, 50, 30 * row + 75, "topleft")
                                self.item_sprites.add(item_name)
                                row += 1
                    # Only shows items that you can enchant with selected enchantment
                    else:
                        self.clear_menu()
                        self.counter = Counter(self.game.player.inventory[self.item_type])
                        displayed_list = []  # Keeps track of which items have been displayed

                        row = 0
                        for item in self.game.player.inventory[self.item_type]:
                            if item not in displayed_list:
                                if item and self.selected_enchantment:
                                    if self.item_type in ENCHANTMENTS[self.selected_enchantment]['equip kind']:
                                        if 'enchanted' not in item:  # Only shows items that are not enchanted already
                                            item_name = Text(self, item, default_font, 20, WHITE, 50, 30 * row + 75, "topleft")
                                            self.item_sprites.add(item_name)
                                            if self.game.player.equipped[self.item_type] and self.game.player.equipped[self.item_type] == item:
                                                equipped_text = Text(self, "(Equipped)", default_font, 20, WHITE, item_name.rect.right + 25, 30 * row + 75, "topleft")
                                                self.item_tags_sprites.add(equipped_text)
                                            elif self.game.player.equipped['weapons2'] and self.game.player.equipped['weapons2'] == item:
                                                equipped_text = Text(self, "(Equipped Left)", default_font, 20, WHITE, item_name.rect.right + 25, 30 * row + 75, "topleft")
                                                self.item_tags_sprites.add(equipped_text)
                                            if self.counter[item] > 1:
                                                item_count = Text(self, str(self.counter[item]), default_font, 20, WHITE, item_name.rect.right + 10, 30 * row + 75, "topleft")
                                                self.item_tags_sprites.add(item_count)
                                            displayed_list.append(item)
                                            row += 1

        else:
            self.counter = Counter(self.game.player.inventory[self.item_type])
            displayed_list = []  # Keeps track of which items have been displayed

            row = 0
            for item in self.game.player.inventory[self.item_type]:
                if item not in displayed_list:
                    if item:
                        if item[-1:] != '4':
                            if 'upgrade' in eval(self.item_type.upper())[item]:
                                if self.check_materials(item, True):
                                    item_name = Text(self, item, default_font, 20, WHITE, 50, 30 * row + 75, "topleft")
                                    self.item_sprites.add(item_name)
                                    if self.game.player.equipped[self.item_type] and self.game.player.equipped[self.item_type] == item:
                                        equipped_text = Text(self, "(Equipped)", default_font, 20, WHITE, item_name.rect.right + 25, 30 * row + 75, "topleft")
                                        self.item_tags_sprites.add(equipped_text)
                                    elif self.game.player.equipped['weapons2'] and self.game.player.equipped['weapons2'] == item:
                                        equipped_text = Text(self, "(Equipped Left)", default_font, 20, WHITE, item_name.rect.right + 25, 30 * row + 75, "topleft")
                                        self.item_tags_sprites.add(equipped_text)
                                    if self.counter[item] > 1:
                                        item_count = Text(self, str(self.counter[item]), default_font, 20, WHITE, item_name.rect.right + 10, 30 * row + 75, "topleft")
                                        self.item_tags_sprites.add(item_count)
                                    displayed_list.append(item)
                                    row += 1

        # Calculates the player's armor rating
        self.game.player.stats['armor'] = 0
        for item in self.game.player.equipped:
            if self.game.player.equipped[item]:
                if '2' in item:
                    temp_item = item.replace('2', '')
                else:
                    temp_item = item
                if 'armor' in eval(temp_item.upper())[self.game.player.equipped[item]]:
                    self.game.player.stats['armor'] += eval(temp_item.upper())[self.game.player.equipped[item]]['armor']

    def display_item_info(self, item):
        item_dictionary = globals()[self.item_type.upper()]  # converts the item_type string into the correct dictionary to get the item stats from
        if self.item_type == 'blocks':
            gid = gid_with_property(self.game.map.tmxdata, 'material', item.text)
            item_image = self.game.map.tmxdata.get_tile_image_by_gid(gid)
        else:
            if self.item_type[-1:] == 's':
                image_path = "self.game." + self.item_type[:-1] + "_images[" + self.item_type.upper() + "['" + item.text + "']['image']]"
            else:
                image_path = "self.game." + self.item_type + "_images[" + self.item_type.upper() + "['" + item.text + "']['image']]"
            itemdict = eval(self.item_type.upper())
            item_image = eval(image_path)
            if 'color' in itemdict[item.text]:
                item_image = color_image(item_image, itemdict[item.text]['color'])
        Picture(self.game, self, item_image, int(self.game.screen_width * (3 / 4)), 150)

        for key in item_dictionary:
            if key == item.text:
                i = 0
                for stat in item_dictionary[key]:
                    if stat in ['image', 'offset', 'walk', 'grip']:
                        continue
                    else:
                        item_stats = ""
                        item_stats += (stat + " " + str(item_dictionary[key][stat]))
                        self.printable_stat_list.append(item_stats)
                        i += 1

    def update_external_variables(self):
        self.game.in_station_menu = False
        self.game.in_menu = False
        self.game.player.current_weapon = self.game.player.equipped['weapons']
        self.game.player.current_weapon2 = self.game.player.equipped['weapons2']
        if self.game.player.swimming:
            toggle_equip(self.game.player, True)
        check_equip(self.game.player)
        self.game.player.human_body.update_animations()  # Updates animations for newly equipped or removed weapons etc.
        self.game.player.dragon_body.update_animations()
        if self.game.player.possessing:
            self.game.player.body.update_animations()
        self.game.player.calculate_fire_power()
        self.game.player.calculate_perks()
        # Reloads
        self.game.player.pre_reload()
        self.game.beg = perf_counter() # resets the counter so dt doesn't get messed up.

    def draw(self):
        self.game.screen.fill(BLACK)
        list_rect = pg.Rect(10, 50, self.game.screen_width / 2 - 10, self.game.screen_height - 100)
        list_rect_fill = pg.Rect(20, 60, self.game.screen_width / 2 - 30, self.game.screen_height - 120)
        description_rect = pg.Rect(self.game.screen_width / 2 + 10, 50, self.game.screen_width / 2 - 20, self.game.screen_height - 100)
        description_rect_fill = pg.Rect(self.game.screen_width / 2 + 20, 60, self.game.screen_width / 2 - 40, self.game.screen_height - 120)
        pg.draw.rect(self.game.screen, WHITE, list_rect, 2)
        pg.draw.rect(self.game.screen, WHITE, description_rect, 2)
        pg.draw.rect(self.game.screen, BLACK, list_rect_fill)
        pg.draw.rect(self.game.screen, BLACK, description_rect_fill)
        if not self.selected_item == None:
            if self.item_selected:
                selected_rect = pg.Rect(self.selected_item.rect.x - 4, self.selected_item.rect.y, self.selected_item.rect.width + 8, self.selected_item.size + 2)
                pg.draw.rect(self.game.screen, YELLOW, selected_rect, 2)

        selected_heading_rect = pg.Rect(self.selected_heading.rect.x - 4, self.selected_heading.rect.y, self.selected_heading.rect.width + 8, self.selected_heading.size + 2)
        pg.draw.rect(self.game.screen, YELLOW, selected_heading_rect, 2)
        self.menu_sprites.draw(self.game.screen)
        if self.item_selected:
            for i, item_stat in enumerate(self.printable_stat_list):
                self.draw_text(item_stat, default_font, 12, WHITE, self.game.screen_width / 2 + 50, self.game.screen_height / 3 + 15 * i, "topleft")

        previous_line_location = 0
        for x in FORGEITEMS:
            if x in self.game.player.inventory['items']:
                self.draw_text(x + " " + str(self.game.player.inventory['items'][x]), default_font, 12, WHITE, 15 + previous_line_location, self.game.screen_height - 120, "topleft")
                previous_line_location += (len(x) * 10)

        if self.kind == 'enchanter' and self.selected_enchantment:
            self.draw_text(self.selected_enchantment.capitalize() + ' enchantment selected.', default_font, 30, WHITE, 50, self.game.screen_height - 170, "topleft")
        self.draw_text("Left Click: Select Item    F: create item    E: Exit Menu", default_font, 12, WHITE, 10, self.game.screen_height - 40, "topleft")
        if self.not_enough_text:
            self.draw_text("Insufficient resources!", default_font, 20, YELLOW, self.game.screen_width/4, self.game.screen_height/2, "topleft")
        pg.display.flip()

class Dialogue_Menu():
    def __init__(self, game, hit):
        self.game = game
        self.menu_sprites = pg.sprite.Group()
        # These next two numbers keep the text in the display window. They may need some tweeking for different resolutions.
        self.wrap_factor = int(ceil((self.game.screen_width * 2/5)/ 13))
        self.number_of_lines = int(ceil((self.game.screen_height * 1/7) / 35))
        self.item_selected = False
        self.selected_item = None
        self.exit_keys = [pg.K_e, pg.K_i, pg.K_ESCAPE]  # The keys used to enter/exit the menu.
        self.game.in_dialogue_menu = True
        self.game.in_menu = True
        self.hit = hit
        self.text_data = []
        self.response_text = []
        self.text_screen = 0
        self.YN = False
        self.inventory_check = False
        self.needed_item = None
        self.needed_item_count = 1
        self.player_has_item = False
        self.gifted = False
        self.name = self.hit.kind['name']
        self.do_action = False # Used so the NPC does the after quest action at the right time.
        self.previous_quest = None
        if self.game.player.race in self.hit.kind.keys(): # Checks for race specific dialogue and quests
            self.quest = self.hit.kind[self.game.player.race]['quest']
            self.hit.kind['dialogue'] = self.hit.kind[self.game.player.race]['dialogue']
            self.assign_quest_info()

        elif 'quest' in self.hit.kind.keys():
            self.quest = self.hit.kind['quest']
            self.assign_quest_info()
        else:
            self.quest = None
            self.format_text()
        self.store = self.hit.kind['store']

        self.lines = 0

    def assign_quest_info(self):
        if self.quest:
            # This is used for quests that involve giving the NPC an item.
            if self.game.quests[self.quest]['inventory check']:
                self.inventory_check = True
                if '&' in self.game.quests[self.quest]['needed item']:
                    self.needed_item, needed_item_count = self.game.quests[self.quest]['needed item'].split('&')
                    try:
                        self.needed_item_count = int(needed_item_count)
                    except:
                        pass
                else:
                    self.needed_item = self.game.quests[self.quest]['needed item']
            if self.game.quests[self.quest]['completed']:
                if (self.game.quests[self.quest]['next quest']) and (self.hit.talk_counter == 1):
                    self.hit.kind['dialogue'] = self.game.quests[self.quest]['next dialogue']
                    self.quest = self.hit.kind['quest'] = self.game.quests[self.quest]['next quest']
                    self.hit.talk_counter = 0
                    self.format_text()
                elif not self.game.quests[self.quest]['rewarded']:
                    self.game.quests[self.quest]['rewarded'] = True
                    self.game.effects_sounds['fanfare'].play()
                    self.format_response(self.game.quests[self.quest]['reward text'])
                    self.add_reward(self.game.quests[self.quest]['reward'])
                else:
                    self.format_response(self.game.quests[self.quest]['completed text'])
                    self.hit.talk_counter += 1
            elif self.game.quests[self.quest]['accepted']:
                if self.inventory_check:
                    if self.check_inventory():
                        self.format_response(self.game.quests[self.quest]['has item text'])
                    else:
                        self.format_response(self.game.quests[self.quest]['waiting text'])
                else:
                    self.format_response(self.game.quests[self.quest]['waiting text'])
            else:
                self.format_text()
        else:
            self.format_text()

    def events(self):
        # catch all events here
        for event in pg.event.get():
            if event.type == pg.QUIT:
                self.game.quit()
            if event.type == pg.KEYDOWN:
                if event.key in self.exit_keys:
                    self.clear_menu()
                    self.running = False
                if event.key == pg.K_SPACE:
                    self.YN = False
                    self.text_screen += 1
                if event.key == pg.K_y:
                    if self.YN:
                        self.accept_quest()
                if event.key == pg.K_n:
                    if self.YN:
                        self.deny_quest()
                if event.key in [pg.K_b, pg.K_ESCAPE]:
                    if self.store:
                        self.game.in_dialogue_menu = False
                        self.running = False
                        self.game.store_menu = Store_Menu(self.game, self.store)
            if event.type == pg.MOUSEBUTTONDOWN:  # Clears off pictures and stats from previously clicked item when new item is clicked.
                self.mouse_click = pg.mouse.get_pressed()
                self.item_selected = False
            if event.type == pg.MOUSEBUTTONUP:
                pos = pg.mouse.get_pos()
                # get a list of all sprites that are under the mouse cursor
                self.clicked_sprites = [s for s in self.menu_sprites if s.rect.collidepoint(pos)]
                for choice in self.menu_sprites:
                    if choice in self.clicked_sprites:
                        if self.YN:
                            self.game.effects_sounds['click'].play()
                            if choice.text == 'Yes':
                                self.accept_quest()
                            if choice.text == 'No':
                                self.deny_quest()

    def add_reward(self, reward):
        for item in reward:
            for kind in ITEM_TYPE_LIST:
                if item in eval(kind.upper()):
                    self.game.player.add_inventory(item, 1)

    def accept_quest(self):
        if self.quest:
            if self.game.quests[self.quest]['accepted'] == True: #This block of code is used for a second quesiton in the 'accept text' section. For NPCs who don't want to go through the bother of asking you to give them the item later
                if not self.player_has_item:
                    self.check_inventory()
                if not self.player_has_item:
                    self.response_text = self.game.quests[self.quest]['lie text']
                    self.format_response()
                    self.clear_menu()
                    self.YN = False

            if self.player_has_item:
                self.take_item()
                self.game.quests[self.quest]['rewarded'] = True
                self.game.effects_sounds['fanfare'].play()
                self.response_text = self.game.quests[self.quest]['reward text']
                self.response_text.append(self.game.quests[self.quest]['completed text'][0])
                self.format_response()
                self.add_reward(self.game.quests[self.quest]['reward'])
                self.clear_menu()
                self.YN = False
                self.inventory_check = False
                self.needed_item = None
                self.player_has_item = False
                self.hit.kind['dialogue'] = self.game.quests[self.quest]['next dialogue']
                self.quest = self.hit.kind['quest'] = self.game.quests[self.quest]['next quest']
                if self.quest:
                    if 'autoaccept' in self.game.quests[self.quest]:
                        if self.game.quests[self.quest]['autoaccept']:
                            self.game.quests[self.quest]['accepted'] = True
            elif self.game.quests[self.quest]['accepted'] != True:
                self.game.quests[self.quest]['accepted'] = True
                self.response_text = self.game.quests[self.quest]['accept text']
                self.format_response()
                self.clear_menu()
                self.YN = False
                if self.quest:
                    if 'autocomplete' in self.game.quests[self.quest]:
                        if self.game.quests[self.quest]['autocomplete']:
                            self.game.quests[self.quest]['completed'] = True
                            self.do_action = True
                            self.previous_quest = self.quest

    def deny_quest(self):
        if self.quest:
            if self.player_has_item:
                self.response_text = self.game.quests[self.quest]['refuse to give text']
                self.format_response()
                self.clear_menu()
                self.YN = False
            else:
                self.game.quests[self.quest]['accepted'] = False
                self.response_text = self.game.quests[self.quest]['deny text']
                self.format_response()
                self.clear_menu()
                self.YN = False

    def take_item(self):
        self.player_has_item = False
        self.inventory_check = False
        count = 0
        self.game.player.add_inventory(self.needed_item, -self.needed_item_count)
        self.hit.add_inventory(self.needed_item, self.needed_item_count)
        change_clothing(self.hit, True)
        self.hit.body.update_animations()

        self.game.quests[self.quest]['completed'] = True
        if 'action' in self.game.quests[self.quest]:
            self.do_action = True
            self.previous_quest = self.quest


    def check_inventory(self):
        if self.game.player.check_inventory(self.needed_item, self.needed_item_count):
            self.player_has_item = True
            return True

    def action(self):
        if 'summon' in self.game.quests[self.previous_quest]['action']:
            _, creature = self.game.quests[self.previous_quest]['action'].split(':')
            if creature in PEOPLE:
                self.game.effects_sounds['enchant'].play()
                summoned = Npc(self.game, self.hit.pos.x + 128, self.hit.pos.y, self.game.map, creature)
                summoned.make_companion()
            elif creature in ANIMALS:
                self.game.effects_sounds['enchant'].play()
                Animal(self.game, pos.x, pos.y, self.game.map, creature)
        if self.game.quests[self.previous_quest]['action'] == 'companion':
            self.hit.make_companion()

        if self.game.quests[self.previous_quest]['action'] == 'unfollow':
            self.hit.remove(self.game.companions)
            try:
                self.hit.body.remove(self.game.companion_bodies)
            except:
                pass
            self.hit.default_detect_radius = self.hit.detect_radius = 250
            self.hit.guard = False
            self.hit.speed = self.hit.walk_speed = 80
            self.hit.run_speed = 100


    def clear_menu(self):
        for item in self.menu_sprites:
            item.kill()

    def format_response(self, text = None): # Used for formatting quest responses.
        if text:
            self.response_text = text
        self.text_data = []
        self.text_screen = 0
        for x in self.response_text:
            if 'SAMERACE' in x:
                if self.game.player.race == self.hit.kind['race']:
                    x = x.replace('SAMERACE', '')
                    self.divide_lines(x)
            elif 'DIFFRACE' in x:
                if self.game.player.race != self.hit.kind['race']:
                    x = x.replace('DIFFRACE', '')
                    self.divide_lines(x)
            else:
                self.divide_lines(x)

    def format_text(self): # Used for formatting dialogue.
        # This part wraps text, so it is displayed in paragraph form.
        if 'random' not in self.hit.kind['dialogue']:
            for x in eval(self.hit.kind['dialogue']):
                if 'SAMERACE' in x:
                    if self.game.player.race == self.hit.kind['race']:
                        x = x.replace('SAMERACE', '')
                        self.divide_lines(x)
                elif 'DIFFRACE' in x:
                    if self.game.player.race != self.hit.kind['race']:
                        x = x.replace('DIFFRACE', '')
                        self.divide_lines(x)
                else:
                    self.divide_lines(x)

        else: # This part is used for characters with a randomized dialogue.
            dialogue = self.hit.kind['dialogue'].replace('random ', '')
            randomized_list = copy.copy(eval(dialogue))
            shuffle(randomized_list)
            for x in randomized_list:
                if 'SAMERACE' in x:
                    if self.game.player.race == self.hit.kind['race']:
                        x = x.replace('SAMERACE', '')
                        self.divide_lines(x)
                elif 'DIFFRACE' in x:
                    if self.game.player.race != self.hit.kind['race']:
                        x = x.replace('DIFFRACE', '')
                        self.divide_lines(x)
                else:
                    self.divide_lines(x)

    def divide_lines(self, x): # This is used to split long dialogue into separate screens.
        description = wrap(x, self.wrap_factor)
        chunks = [description[z:z + self.number_of_lines] for z in range(0, len(description), self.number_of_lines)]
        for y in chunks:
            self.text_data.append(y)

    def draw_text(self, text, font_name, size, color, x, y, align="topleft"):
        font = pg.font.Font(font_name, size)
        text_surface = font.render(text, True, color)
        text_rect = text_surface.get_rect(**{align: (x, y)})
        self.game.screen.blit(text_surface, text_rect)

    def list_choices(self):
        if self.YN:
            yes_text = Text(self, 'Yes', default_font, 40, YELLOW, self.game.screen_width/5 + 15, self.game.screen_height * 4/7 + 60 + (45 * self.lines), "topleft")
            self.menu_sprites.add(yes_text)
            no_text = Text(self, 'No', default_font, 40, YELLOW, self.game.screen_width/5 + 15,  self.game.screen_height * 4/7 + 60 + (45 * (self.lines + 1)), "topleft")
            self.menu_sprites.add(no_text)

    def draw(self):
        list_rect = pg.Rect(self.game.screen_width/5, int(self.game.screen_height * 4/7), self.game.screen_width * 3/5, self.game.screen_height * 3/7 - 50)
        list_rect_fill = pg.Rect(self.game.screen_width/5 + 2, self.game.screen_height * 4/7 + 2, self.game.screen_width * 3/5 - 2, self.game.screen_height)
        pg.draw.rect(self.game.screen, BLACK, list_rect_fill)
        pg.draw.rect(self.game.screen, WHITE, list_rect, 2)
        if self.text_screen > len(self.text_data) - 1:
            self.text_screen = 0
            self.running = False
            return
        self.lines = len(self.text_data[self.text_screen])
        for i, text_screens in enumerate(self.text_data[self.text_screen]):
            if 'YN' in text_screens:
                text_screens = text_screens.replace('YN', '')
                self.YN = True
            if 'GIFTS' in text_screens:
                text_screens = text_screens.replace('GIFTS', '')
                if not self.gifted:
                    self.game.effects_sounds['gun_pickup'].play()
                    self.add_reward(self.game.quests[self.quest]['gifts'])
                    self.gifted = True
            self.draw_text(text_screens, default_font, 40, WHITE, self.game.screen_width/5 + 15, self.game.screen_height * 4/7 + 60 + (45 * i), "topleft")
        if self.YN:
            self.list_choices()

        self.draw_text(self.name + ':', default_font, 40, BLUE, self.game.screen_width / 5 + 15, self.game.screen_height * 4 / 7 + 15, "topleft")
        self.draw_text("E: Exit Dialogue Menu   SPACE: Advance Dialogue", HUD_FONT, 30, WHITE, self.game.screen_width/5 + 50, self.game.screen_height - 40, "topleft")
        if self.store:
            self.draw_text("B: Buy/Sell", HUD_FONT, 30, WHITE, self.game.screen_width / 5 + 700, self.game.screen_height - 40, "topleft")
        self.menu_sprites.draw(self.game.screen)
        pg.display.flip()

    def update(self):
        self.running = True
        while self.running:
            self.game.clock.tick(30)
            self.events()
            self.draw()
        self.update_external_variables()

    def update_external_variables(self):
        if self.do_action:  # Only does the after quest action after you finish talking to them.
            self.action()
        self.game.in_dialogue_menu = False
        self.game.dialogue_menu_npc = None
        self.game.in_menu = False
        self.game.last_dialogue = pg.time.get_ticks() # Gets the time you exited the menu. This is used so that the menu doesn't keep popping up.
        self.game.beg = perf_counter()  # Resets the counter so the dt doesn't get messed up.
        del self


class Store_Menu(Inventory_Menu): # Inventory Menu, also used as the parent class for other menus.
    def __init__(self, game, store):
        super().__init__(game)
        # These items are changed for inherrited menus.
        self.game.in_store_menu = True
        self.game.in_menu = True
        self.store = store
        self.exit_keys = [pg.K_e, pg.K_ESCAPE] # The keys used to enter/exit the menu.
        self.spacing = 20 # Spacing between headings
        self.heading_list = ['Weapons', 'Hats', 'Hair', 'Tops', 'Bottoms', 'Shoes', 'Gloves', 'Items', 'Blocks'] # This is the list of headings
        self.store_inventory = self.store['inventory'].copy()
        self.markup = self.store['markup']
        self.pvalue = self.store['pvalue'] # percent of item value store buys at
        self.display_inventory = 'store'
        self.item_type = 'weapons'
        self.cost = 0
        self.worth = 0

    def events(self):
        # catch all events here
        for event in pg.event.get():
            if event.type == pg.QUIT:
                self.game.quit()
            if event.type == pg.KEYDOWN:
                if event.key in self.exit_keys:
                    self.clear_menu()
                    self.running = False
                if event.key == pg.K_TAB:
                    if self.display_inventory == 'store':
                        self.display_inventory = 'player'
                        self.list_items()
                    else:
                        self.display_inventory = 'store'
                        self.list_store_items()
                    self.cost = 0
                    self.worth = 0
                if event.key == pg.K_b: # buy
                    if self.selected_item:
                        if self.display_inventory == 'store':
                            self.buy_item()
                if event.key == pg.K_s:  # drop/sell item
                    if self.selected_item:
                        if self.display_inventory == 'player':
                            self.sell_item()
            if event.type == pg.MOUSEBUTTONDOWN:  # Clears off pictures and stats from previously clicked item when new item is clicked.
                self.mouse_click = pg.mouse.get_pressed()
                pos = pg.mouse.get_pos()
                if [s for s in self.menu_sprites if s.rect.collidepoint(pos)]:
                    self.game.effects_sounds['click'].play()
                self.printable_stat_list = []
                self.item_selected = False
                for picture in self.item_pictures:
                    picture.kill()
            if event.type == pg.MOUSEBUTTONUP:
                pos = pg.mouse.get_pos()
                # get a list of all sprites that are under the mouse cursor
                self.clicked_sprites = [s for s in self.menu_sprites if s.rect.collidepoint(pos)]
                for heading in self.menu_heading_sprites:
                    if heading in self.clicked_sprites:
                        self.item_type = heading.text.lower()
                        if self.display_inventory == 'store':
                            self.list_store_items()
                        else:
                            self.list_items()
                        self.selected_heading = heading
                # Equips items
                for item in self.clicked_sprites:
                    if item in self.item_sprites:
                        self.selected_item = item
                        self.item_selected = True
                        self.calculate_cost()
                        self.calculate_worth()
                        self.display_item_info(item)
                        if self.mouse_click == (0, 0, 1):
                            pass
                        # Equipping weapon in left hand
                        if self.mouse_click == (1, 0, 0):
                            pass
                        if self.display_inventory == 'store':
                            self.list_store_items()
                        else:
                            self.list_items()

    def calculate_cost(self):
        if 'value' in eval(self.item_type.upper())[self.selected_item.text]:
            self.cost = int(eval(self.item_type.upper())[self.selected_item.text]['value'] * self.markup)
        else:
            self.cost = 0

    def calculate_worth(self):
        if 'value' in eval(self.item_type.upper())[self.selected_item.text]:
            self.worth = int(eval(self.item_type.upper())[self.selected_item.text]['value'] * self.pvalue)
        else:
            self.worth = 0

    def buy_item(self):
        if self.cost != 0:
            if self.game.player.add_inventory('gold', -self.cost):
                self.game.player.add_inventory(self.selected_item.text, 1)
                self.game.effects_sounds['cashregister'].play()
                add_inventory(self.store_inventory, self.selected_item.text, -1)

    def sell_item(self):
        if self.worth != 0:
            # Unequips item if you drop one you are equipping and don't have another one.
            if self.game.player.equipped[self.item_type] == self.selected_item.text:
                self.game.player.equipped[self.item_type] = None
            elif self.game.player.equipped['weapons2'] == self.selected_item.text: # Unequips dropped secondary weapon.
                self.game.player.equipped['weapons2'] = None
            # Removes sold item from inventory
            self.game.player.add_inventory(self.selected_item.text, -1)
            add_inventory(self.store_inventory, self.selected_item.text, 1) #Adds item to store inventory
            self.selected_item.text = 'None'  # Makes it so it doesn't drop more than one of the same item.
            self.game.player.add_inventory('gold', self.worth) # Gives you gold for item
            self.game.effects_sounds['cashregister'].play()
            self.selected_item = None
            self.cost = 0
            self.worth = 0
            self.list_items()

    def list_store_items(self):
        self.clear_menu()
        displayed_list = [] # Keeps track of which items have been displayed

        row = 0
        for item in self.store_inventory[self.item_type]:
            if item:
                if ' M' in item:
                    if self.game.player.equipped['gender'] not in ['male']:
                        continue
                elif ' F' in item:
                    if self.game.player.equipped['gender'] not in ['female', 'other']:
                        continue
                if item not in displayed_list:
                    item_name = Text(self, item, default_font, 20, WHITE, 50, 30 * row + 75, "topleft")
                    self.item_sprites.add(item_name)
                    displayed_list.append(item)
                    row += 1

    def display_item_info(self, item):
        item_dictionary = globals()[self.item_type.upper()] #converts the item_type string into the correct dictionary to get the item stats from
        if self.item_type == 'blocks':
            gid = gid_with_property(self.game.map.tmxdata, 'material', item.text)
            item_image = self.game.map.tmxdata.get_tile_image_by_gid(gid)
        else:
            if self.item_type[-1:] == 's':
                image_path = "self.game." + self.item_type[:-1] + "_images[" + self.item_type.upper() + "['" + item.text + "']['image']]"
            else:
                image_path = "self.game." + self.item_type + "_images[" + self.item_type.upper() + "['" + item.text + "']['image']]"
            itemdict = eval(self.item_type.upper())
            item_image = eval(image_path)
            if 'color' in itemdict[item.text]:
                item_image = color_image(item_image, itemdict[item.text]['color'])
        Picture(self.game, self, item_image, int(self.game.screen_width * (3 / 4)), 150)

        for key in item_dictionary:
            if key == item.text:
                i = 0
                for stat in item_dictionary[key]:
                    if stat in ['image', 'offset', 'walk', 'grip']:
                        continue
                    else:
                        item_stats = ""
                        item_stats += (stat + " " + str(item_dictionary[key][stat]))
                        self.printable_stat_list.append(item_stats)
                        i += 1

    def update(self):
        self.generate_headings()
        self.list_store_items()
        self.running = True
        while self.running:
            self.game.clock.tick(30)
            self.events()
            self.draw()
        self.update_external_variables()

    def update_external_variables(self):
        self.game.in_store_menu = False
        self.game.in_menu = False
        self.game.player.current_weapon = self.game.player.equipped['weapons']
        self.game.player.current_weapon2 = self.game.player.equipped['weapons2']
        if self.game.player.swimming:
            toggle_equip(self.game.player, True)
        check_equip(self.game.player)
        self.game.player.human_body.update_animations()  # Updates animations for newly equipped or removed weapons etc.
        self.game.player.dragon_body.update_animations()
        if self.game.player.possessing:
            self.game.player.body.update_animations()
        self.game.player.calculate_fire_power()
        self.game.player.calculate_perks()
        # Reloads
        self.game.player.pre_reload()
        self.game.beg = perf_counter() # resets the counter so dt doesn't get messed up.

    def draw(self):
        self.game.screen.fill(BLACK)
        list_rect = pg.Rect(10, 50, self.game.screen_width / 2 - 10, self.game.screen_height - 100)
        list_rect_fill = pg.Rect(20, 60, self.game.screen_width / 2 - 30, self.game.screen_height - 120)
        description_rect = pg.Rect(self.game.screen_width / 2 + 10, 50, self.game.screen_width / 2 - 20, self.game.screen_height - 100)
        description_rect_fill = pg.Rect(self.game.screen_width / 2 + 20, 60, self.game.screen_width / 2 - 40, self.game.screen_height - 120)
        pg.draw.rect(self.game.screen, WHITE, list_rect, 2)
        pg.draw.rect(self.game.screen, WHITE, description_rect, 2)
        pg.draw.rect(self.game.screen, BLACK, list_rect_fill)
        pg.draw.rect(self.game.screen, BLACK, description_rect_fill)
        if not self.selected_item == None:
            if self.item_selected:
                selected_rect = pg.Rect(self.selected_item.rect.x - 4, self.selected_item.rect.y, self.selected_item.rect.width + 8, self.selected_item.size + 2)
                pg.draw.rect(self.game.screen, YELLOW, selected_rect, 2)
        selected_heading_rect = pg.Rect(self.selected_heading.rect.x - 4, self.selected_heading.rect.y, self.selected_heading.rect.width + 8, self.selected_heading.size + 2)
        pg.draw.rect(self.game.screen, YELLOW, selected_heading_rect, 2)
        self.menu_sprites.draw(self.game.screen)
        if self.item_selected:
            for i, item_stat in enumerate(self.printable_stat_list):
                self.draw_text(item_stat, default_font, 20, WHITE, self.game.screen_width / 2 + 50, self.game.screen_height / 3 + 30 * i, "topleft")
        if self.display_inventory == 'store':
            disp_text = 'Buy From Store'
            cost_text = 'This item costs ' + str(self.cost) + ' gold.'
        else:
            disp_text = 'Sell to Store'
            cost_text = 'This item is worth ' + str(self.worth) + ' gold.'
        self.draw_text(disp_text, default_font, 35, YELLOW, self.game.screen_width - 300, 10, "topright")
        self.draw_text(cost_text, default_font, 35, YELLOW, self.game.screen_width - 300, 50, "topright")
        self.draw_text("Carry Weight: " + str(self.game.player.stats['weight']) + "  Max Carry Weight: " + str(self.game.player.stats['max weight']), default_font, 25, WHITE, 20, self.game.screen_height - 80, "topleft")
        self.draw_text("Click: Select Item    B: Buy Item    S: Sell item    TAB: Toggle Store & Player inventory   E: Exit Menu", default_font, 20, WHITE, 10, self.game.screen_height - 40, "topleft")
        pg.display.flip()

class Quest_Menu(Menu):
    def __init__(self, game):
        super().__init__(game)
        self.exit_keys = [pg.K_j, pg.K_e, pg.K_ESCAPE] # The keys used to enter/exit the menu.
        self.spacing = 40 # Spacing between headings
        self.heading_list = ['Active Quests', 'Completed Quests'] # This is the list of headings
        self.previous_item = None
        self.selected_heading = 'Active Quests'

    def use_item(self):
        if self.selected_item:
            pass

    def drop_item(self):
        pass

    def right_equip(self, item):
        pass

    def left_equip(self, item):
        pass

    def list_items(self):
        self.clear_menu()
        i = 0
        if self.selected_heading.text == 'Active Quests':
            for quest in self.game.quests.keys():
                if self.game.quests[quest]['accepted']:
                    if not self.game.quests[quest]['completed']:
                        quest_name = Text(self, quest, default_font, 20, WHITE, 50, 30 * i + 75, "topleft")
                        self.item_sprites.add(quest_name)
                        i += 1
        elif self.selected_heading.text == 'Completed Quests':
            for quest in self.game.quests.keys():
                if self.game.quests[quest]['accepted']:
                    if self.game.quests[quest]['completed']:
                        quest_name = Text(self, quest, default_font, 20, WHITE, 50, 30 * i + 75, "topleft")
                        self.item_sprites.add(quest_name)
                        i += 1

    def display_item_info(self, item):
        # This part wraps the descriptions of the character races. So they are displayed in paragraph form.
        description = wrap(self.game.quests[item.text]['description'], 80)
        for line in description:
            self.printable_stat_list.append(line)
        self.printable_stat_list.append(" ")

    def update_external_variables(self):
        self.game.in_quest_menu = False
        self.game.in_menu = False
        self.game.beg = perf_counter() # resets the counter so dt doesn't get messed up.
        del self

    def draw(self):
        self.game.screen.fill(BLACK)
        list_rect = pg.Rect(10, 50, self.game.screen_width / 2 - 10, self.game.screen_height - 100)
        list_rect_fill = pg.Rect(20, 60, self.game.screen_width / 2 - 30, self.game.screen_height - 120)
        description_rect = pg.Rect(self.game.screen_width / 2 + 10, 50, self.game.screen_width / 2 - 20, self.game.screen_height - 100)
        description_rect_fill = pg.Rect(self.game.screen_width / 2 + 20, 60, self.game.screen_width / 2 - 40, self.game.screen_height - 120)
        pg.draw.rect(self.game.screen, WHITE, list_rect, 2)
        pg.draw.rect(self.game.screen, WHITE, description_rect, 2)
        pg.draw.rect(self.game.screen, BLACK, list_rect_fill)
        pg.draw.rect(self.game.screen, BLACK, description_rect_fill)
        if not self.selected_item == None:
            if self.item_selected:
                selected_rect = pg.Rect(self.selected_item.rect.x - 4, self.selected_item.rect.y, self.selected_item.rect.width + 8, self.selected_item.size + 2)
                pg.draw.rect(self.game.screen, YELLOW, selected_rect, 2)
        selected_heading_rect = pg.Rect(self.selected_heading.rect.x - 4, self.selected_heading.rect.y, self.selected_heading.rect.width + 8, self.selected_heading.size + 2)
        pg.draw.rect(self.game.screen, YELLOW, selected_heading_rect, 2)
        self.menu_sprites.draw(self.game.screen)
        if self.item_selected:
            for i, item_stat in enumerate(self.printable_stat_list):
                self.draw_text(item_stat, default_font, 20, WHITE, self.game.screen_width / 2 + 50, self.game.screen_height / 3 + 30 * i, "topleft")
        self.draw_text("Left Click: Select Quest    Right Click: Select Quest    E: Exit Menu", default_font, 20, WHITE, 10, self.game.screen_height - 40, "topleft")
        pg.display.flip()

class Fly_Menu(Draw_Text):
    def __init__(self, game):
        self.game = game
        self.cell_width = self.game.screen_width / len(self.game.map_data_list[0])
        self.cell_height = self.game.screen_height / len(self.game.map_data_list)
        self.offsetx = int(self.game.world_location.x * self.cell_width)
        self.offsety = int(self.game.world_location.y * self.cell_height)
        self.currentmap_rect = pg.Rect(0, 0, self.cell_width, self.cell_height)
        self.currentmap_rect.topleft = (self.offsetx, self.offsety)
        self.update()

    def update(self):
        self.running = True
        while self.running:
            self.game.clock.tick(30)
            self.events()
            self.draw()
        self.update_external_variables()

    def update_external_variables(self):
        self.game.in_fly_menu = False
        self.game.in_menu = False
        self.game.beg = perf_counter() # resets the counter so dt doesn't get messed up.
        map = str(self.game.map_data_list[int(self.game.world_location.y)][int(self.game.world_location.x)]) + '.tmx'
        # Puts player in map center
        self.game.player.pos = vec(self.game.map.width/2, self.game.map.height/2)
        self.game.player.rect.center = self.game.player.pos
        self.game.load_map(map)
        del self

    def events(self):
        for event in pg.event.get():
            if event.type == pg.QUIT:
                self.game.quit()
            if event.type == pg.KEYDOWN:
                if event.key in [pg.K_e, pg.K_u, pg.K_ESCAPE]:
                    self.running = False

        keys = pg.key.get_pressed()
        # WASD keys for moving ship to new maps
        if self.game.player.vehicle.fuel > 0:
            if keys[pg.K_w]:
                self.game.world_location.y -= 1
                if self.game.world_location.y < 0:
                    self.game.world_location.y = self.game.world_height
                self.set_position()
            if keys[pg.K_s]:
                self.game.world_location.y += 1
                if self.game.world_location.y > self.game.world_height:
                    self.game.world_location.y = 0
                self.set_position()
            if keys[pg.K_a]:
                self.game.world_location.x -= 1
                if self.game.world_location.x < 0:
                    self.game.world_location.x = self.game.world_width
                self.set_position()
            if keys[pg.K_d]:
                self.game.world_location.x += 1
                if self.game.world_location.x > self.game.world_width:
                    self.game.world_location.x = 0
                self.set_position()

    def set_position(self):
        self.game.player.vehicle.fuel -= 1
        if self.game.player.vehicle.fuel < 0:
            self.game.player.vehicle.fuel = 0
        self.offsetx = int(self.game.world_location.x * self.cell_width)
        self.offsety = int(self.game.world_location.y * self.cell_height)
        self.currentmap_rect.topleft = (self.offsetx, self.offsety)

    def draw(self):
        self.game.screen.blit(self.game.over_minimap_image, (0, 0))
        pg.draw.rect(self.game.screen, YELLOW, self.currentmap_rect, 4)
        self.draw_text("Use WASD to move ship", default_font, 20, WHITE, 10, self.game.screen_height - 40, "topleft")
        self.draw_text("Fuel: " + str(self.game.player.vehicle.fuel), default_font, 40, WHITE, 10, 40, "topleft")
        pg.display.flip()


class Settings_Menu(Menu):
    def __init__(self, game):
        super().__init__(game)
        self.exit_keys = [pg.K_ESCAPE] # The keys used to enter/exit the menu.
        self.spacing = 40 # Spacing between headings
        self.heading_list = ['Game', 'Inventory', 'Map', 'Crafting', 'Quests', 'Controls'] # This is the list of headings
        self.game_menu_list = ['Save Game', 'Load Game', 'Quit Game']
        self.controls_menu_list = self.game.key_map.keys()
        self.previous_item = None

    def events(self):
        # catch all events here
        for event in pg.event.get():
            if event.type == pg.QUIT:
                self.game.quit()
            if event.type == pg.KEYDOWN:
                if event.key in self.exit_keys:
                    if self.game.in_load_menu:
                        if not self.no_save_selected:
                            self.clear_menu()
                            self.running = False
                    else:
                        self.clear_menu()
                        self.running = False
                if self.selected_item and (self.selected_item.text in self.controls_menu_list) and event.key: # This part is used for remapping player controls.
                    if event.key != pg.K_ESCAPE:
                        old_key = self.game.key_map[self.selected_item.text]
                        for key, value in self.game.key_map.items():
                            if value == event.key:
                                self.game.key_map[key] = old_key
                        self.game.key_map[self.selected_item.text] = event.key
                        self.clear_menu()
                        self.list_items()

            if event.type == pg.MOUSEBUTTONDOWN:  # Clears off pictures and stats from previously clicked item when new item is clicked.
                self.warning_message = False
                self.mouse_click = pg.mouse.get_pressed()
                pos = pg.mouse.get_pos()
                if [s for s in self.menu_sprites if s.rect.collidepoint(pos)]:
                    self.game.effects_sounds['click'].play()
                self.printable_stat_list = []
                self.item_selected = False
                for picture in self.item_pictures:
                    picture.kill()
            if event.type == pg.MOUSEBUTTONUP:
                pos = pg.mouse.get_pos()
                # get a list of all heading sprites that are under the mouse cursor
                self.clicked_sprites = [s for s in self.menu_sprites if s.rect.collidepoint(pos)]
                for heading in self.menu_heading_sprites:
                    if heading in self.clicked_sprites:
                        self.item_type = heading.text.lower()
                        self.selected_heading = heading
                        self.item_selected = False
                        self.selected_item = None
                        # Switches to other menus.
                        if self.selected_heading.text == 'Inventory':
                            self.game.in_inventory_menu = True
                            self.running = False
                        elif self.selected_heading.text == 'Map':
                            self.game.hud_overmap = True
                            self.running = False
                        elif self.selected_heading.text == 'Crafting':
                            self.running = False
                            self.game.in_station_menu = True
                            self.game.station_menu = Work_Station_Menu(self.game, 'crafting')
                        elif self.selected_heading.text == 'Quests':
                            self.running = False
                            self.game.in_quest_menu = True
                            self.game.quest_menu = Quest_Menu(self.game)
                        self.list_items()
                # Equips items
                for item in self.clicked_sprites:
                    if item in self.item_sprites:
                        self.selected_item = item
                        self.item_selected = True
                        self.display_item_info(item)
                        if self.mouse_click == (0, 0, 1):
                            self.right_equip(item)
                        # Equipping weapon in left hand
                        if self.mouse_click == (1, 0, 0):
                            self.left_equip(item)
                        self.list_items()


    def use_item(self):
        pass

    def drop_item(self):
        if not self.game.in_character_menu:
            if self.selected_item:
                pass

    def right_equip(self, item):
        pass

    def left_equip(self, item):
        global WIDTH
        global HEIGHT
        if item.text == 'Quit Game':
            self.game.quit()
        elif item.text == 'Save Game':
            self.game.save()
        elif item.text == 'Load Game':
            self.game.in_load_menu = True
            self.running = False

    def list_items(self):
        self.clear_menu()
        if self.selected_heading.text in ['Game', 'Controls']:
            if self.selected_heading.text == 'Controls':
                menu_list = self.controls_menu_list
                font_size = 14
                font_space = 16
            else:
                menu_list = self.game_menu_list
                font_size = 30
                font_space = 40

            for i, x in enumerate(menu_list):
                if i < 25:
                    xpos = 50
                    ypos = font_space * i + 75
                else:
                    xpos = self.game.screen_width/2 + 50
                    ypos = font_space * (i - 25) + 75
                item_name = Text(self, x, default_font, font_size, WHITE, xpos, ypos, "topleft")
                self.item_sprites.add(item_name)
                if menu_list == self.controls_menu_list:
                    item_name = Text(self, pg.key.name(self.game.key_map[x]), default_font, font_size, WHITE, xpos + 120, ypos, "topleft")
                    self.item_sprites.add(item_name)

    def display_item_info(self, item):
        pass

    def update_external_variables(self):
        self.game.in_settings_menu = False
        self.game.in_menu = False
        self.game.beg = perf_counter() # resets the counter so dt doesn't get messed up.

    def draw(self):
        self.game.screen.fill(BLACK)
        list_rect = pg.Rect(10, 50, self.game.screen_width / 2 - 10, self.game.screen_height - 100)
        list_rect_fill = pg.Rect(20, 60, self.game.screen_width / 2 - 30, self.game.screen_height - 120)
        description_rect = pg.Rect(self.game.screen_width / 2 + 10, 50, self.game.screen_width / 2 - 20, self.game.screen_height - 100)
        description_rect_fill = pg.Rect(self.game.screen_width / 2 + 20, 60, self.game.screen_width / 2 - 40, self.game.screen_height - 120)
        pg.draw.rect(self.game.screen, WHITE, list_rect, 2)
        pg.draw.rect(self.game.screen, WHITE, description_rect, 2)
        pg.draw.rect(self.game.screen, BLACK, list_rect_fill)
        pg.draw.rect(self.game.screen, BLACK, description_rect_fill)
        if not self.selected_item == None:
            if self.item_selected:
                selected_rect = pg.Rect(self.selected_item.rect.x - 4, self.selected_item.rect.y, self.selected_item.rect.width + 8, self.selected_item.size + 2)
                pg.draw.rect(self.game.screen, YELLOW, selected_rect, 2)
        selected_heading_rect = pg.Rect(self.selected_heading.rect.x - 4, self.selected_heading.rect.y, self.selected_heading.rect.width + 8, self.selected_heading.size + 2)
        pg.draw.rect(self.game.screen, YELLOW, selected_heading_rect, 2)
        self.menu_sprites.draw(self.game.screen)
        if self.item_selected:
            for i, item_stat in enumerate(self.printable_stat_list):
                self.draw_text(item_stat, default_font, 20, WHITE, self.game.screen_width / 2 + 50, self.game.screen_height / 3 + 30 * i, "topleft")
        self.draw_text("Left Click to select option, ESCAPE: Exit Menu", default_font, 20, WHITE, 10, self.game.screen_height - 40, "topleft")
        pg.display.flip()
