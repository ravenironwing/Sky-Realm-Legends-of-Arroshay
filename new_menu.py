import copy
import sys
import pygame as pg
from color_palettes import *
from settings import EFFECTS_SOUNDS, snd_folder, img_folder, new_items_folder, magic_folder, KEY_MAP, OVERWORLD_MAP_IMAGE, saves_folder, map_folder, START_WORLD, book_animation_folder, EQUIP_DRAW_LIST
from character_positions import CP_STANDING_ARMS_OUT0
from quests import *
from tilemap import *
from os import path
from new_items import *
from glob import glob
from textwrap import wrap
from math import ceil
from time import perf_counter
vec = pg.math.Vector2

pg.mixer.pre_init(44100, -16, 4, 2048)
pg.init()
pg.mixer.init()
WIDTH = 960
HEIGHT = 540
ICON_SIZE = 71
DOUBLE_CLICK_TIME = 200
default_font = pg.font.match_font('arial') #python looks for closest match to arial on whatever computer

NEW_ITEM_IMAGES = {} # Loads all item filepaths
for name in os.listdir(new_items_folder):
    if os.path.isfile(os.path.join(new_items_folder, name)):
        item_name = name.replace('.png', '')
        NEW_ITEM_IMAGES[item_name] = name

MAGIC_IMAGES = {} # Loads all magic filepaths
for name in os.listdir(magic_folder):
    if os.path.isfile(os.path.join(magic_folder, name)):
        item_name = name.replace('.png', '')
        MAGIC_IMAGES[item_name] = name

#ITEMS = {}
#ITEMS['wood'] = {'name': 'wood', 'type': 'item', 'number': 1, 'max stack': 64}
#ITEMS['wood block'] = {'name': 'wood block', 'type': 'item', 'number': 1, 'max stack': 64}
#ITEMS['rock'] = {'name': 'rock', 'type': 'item', 'number': 1, 'max stack': 40}
#ITEMS['flint and steel'] = {'name': 'flint and steel', 'type': 'item', 'hp': 5, 'max hp': 20}
CRAFTING_RECIPIES = {}
#CRAFTING_RECIPIES['wood block'] = [1, 'wood', 'wood', 0, 'wood', 'wood']
FORGING_RECIPIES = {}
for material in MATERIALS:
    x = material + ' ingot'
    l = 'leather'
    ls = 'leather strips'
    st = 'stick'
    FORGING_RECIPIES[material + ' armor'] = [1, x, 0, x,
                                                x, x, x,
                                                x, x, x]
    FORGING_RECIPIES[material + ' leg armor'] = [1, x, x, x,
                                                x, 0, x,
                                                x, 0, x]
    FORGING_RECIPIES[material + ' boots'] = [1, ls, 0, ls,
                                                x, 0, x,
                                                l, 0, l]
    FORGING_RECIPIES[material + ' gauntlets'] = [1, l, 0, l,
                                                x, 0, x]
    FORGING_RECIPIES[material + ' helmet'] = [1, x, x, x,
                                                x, 0, x]
    FORGING_RECIPIES[material + ' axe'] = [1, 0, x, x,
                                                0, st, x,
                                                0, st, 0]
    FORGING_RECIPIES[material + ' broadsword'] = [1, x, 0,
                                                0, x, 0,
                                                0, st]
    FORGING_RECIPIES[material + ' pickaxe'] = [1, x, x, x,
                                                0, st, 0,
                                                0, st, 0]
    #FORGING_RECIPIES[material + ' longsword'] = [1, 0, 0, x,
    #                                            0, x, x,
    #                                            st, x, 0]
    #FORGING_RECIPIES[material + ' dagger'] = [1, x, 0,
    #                                            0, st]

WORKBENCH_RECIPIES = {}
ENCHANTING_RECIPIES = {}
SMELTING_RECIPIES = {}
TANNING_RECIPIES = {}
GRINDER_RECIPIES = {}
COOKING_RECIPIES = {}
ALCHEMY_RECIPIES = {}

# Simply change out the recipie dictionary for different workstations.
WORKSTATIONS = ['Crafting', 'Work Bench', 'Anvil', 'Enchanter', 'Smelter', 'Tanning Rack', 'Grinder', 'Cooking Fire', 'Alchemy Lab']
RECIPIES = {'Crafting': CRAFTING_RECIPIES, 'Work Bench': WORKBENCH_RECIPIES, 'Anvil': FORGING_RECIPIES, 'Enchanter': ENCHANTING_RECIPIES, 'Smelter': SMELTING_RECIPIES, 'Tanning Rack': TANNING_RECIPIES, 'Grinder': GRINDER_RECIPIES, 'Cooking Fire': COOKING_RECIPIES, 'Alchemy Lab': ALCHEMY_RECIPIES}

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
    if ('type' in item.keys()) and (item['type'] == 'book'):
        filename = 'generic book'
    return filename

def color_image(image, color):
    temp_image = image.copy()
    color_image = pg.Surface(temp_image.get_size()).convert_alpha()
    color_image.fill(color)
    temp_image.blit(color_image, (0, 0), special_flags=pg.BLEND_RGBA_MULT)
    return temp_image

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


class Game:
    def __init__(self):
        self.screen_width = WIDTH
        self.screen_height = HEIGHT
        self.key_map = KEY_MAP
        self.quests = QUESTS
        self.flags = pg.SCALED # | pg.FULLSCREEN
        self.screen = pg.display.set_mode((self.screen_width, self.screen_height), self.flags)
        self.effects_sounds = {}
        for key in EFFECTS_SOUNDS:
            self.effects_sounds[key] = pg.mixer.Sound(path.join(snd_folder, EFFECTS_SOUNDS[key]))
        self.black_box_image = pg.image.load(path.join(img_folder, 'black_box.png')).convert()
        self.start_icon_image = pg.image.load(path.join(img_folder, 'start_icon.png')).convert()
        self.dark_grey_box_image = pg.image.load(path.join(img_folder, 'dark_grey_box.png')).convert()
        self.grey_box_image = pg.image.load(path.join(img_folder, 'grey_box.png')).convert()
        self.right_arrow_image = pg.transform.scale(pg.image.load(path.join(img_folder, 'right_arrow.png')).convert(), (ICON_SIZE, ICON_SIZE))
        self.back_arrow_image = pg.transform.scale(pg.image.load(path.join(img_folder, 'back_arrow.png')).convert(), (ICON_SIZE, ICON_SIZE))
        self.trash_image = pg.image.load(path.join(img_folder, 'trash.png')).convert()
        self.book_images = []
        for i in range(0, 6):
            image = pg.image.load(path.join(book_animation_folder, 'book{}.png'.format(i))).convert()
            image = pg.transform.scale(image, (self.screen_width, self.screen_height))
            self.book_images.append(image)
        self.over_minimap_image = pg.image.load(path.join(map_folder, OVERWORLD_MAP_IMAGE)).convert()
        self.map_sprite_data_list = []
        self.overworld_map = START_WORLD
        self.load_over_map(self.overworld_map)
        self.world_location = vec(1, 2)
        map = self.map_data_list[int(self.world_location.y)][int(self.world_location.x)]
        self.minimap_image = pg.image.load(path.join(map_folder, str(map - 1) + '.png')).convert()
        self.clock = pg.time.Clock()
        self.player = Character()
        self.item_images = {}
        for item in NEW_ITEM_IMAGES:
            img = pg.image.load(path.join(new_items_folder, NEW_ITEM_IMAGES[item])).convert_alpha()
            self.item_images[item] = img
        self.magic_images = {}
        for item in MAGIC_IMAGES:
            img = pg.image.load(path.join(magic_folder, MAGIC_IMAGES[item])).convert_alpha()
            self.magic_images[item] = img
        self.hair_images = {}
        for item in HAIR_IMAGES:
            img = pg.image.load(path.join(hair_folder, HAIR_IMAGES[item])).convert_alpha()
            self.hair_images[item] = img
        self.race_images = {}
        for item in RACE_IMAGES:
            img = pg.image.load(path.join(race_folder, RACE_IMAGES[item])).convert_alpha()
            self.race_images[item] = img
        self.color_swatch_images = []
        for i, x in enumerate(COLOR_SWATCH_IMAGES):
            img = pg.image.load(path.join(color_swatches_folder, COLOR_SWATCH_IMAGES[i])).convert()
            self.color_swatch_images.append(img)
        self.humanoid_images = {}
        for kind in HUMANOID_IMAGES:
            temp_list = []
            for i, picture in enumerate(HUMANOID_IMAGES[kind]):
                temp_folder = kind.replace('images', 'parts_folder')
                img = pg.image.load(path.join(eval(temp_folder), HUMANOID_IMAGES[kind][i])).convert_alpha()
                temp_list.append(img)
            self.humanoid_images[kind] = temp_list
        self.mech_back_image = pg.image.load(path.join(img_folder, 'mech_back_lights.png')).convert_alpha()
        self.menu = MainMenu(self, self.player)


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
                    map_data_store = MapData(x, y)
                    row.append(map_data_store)
                self.map_sprite_data_list.append(row)

    def quit(self):
        pg.quit()
        sys.exit()

    def save(self):
        print('Game Saved') # Replace with real code here

    def load_save(self, file):
        print(file)

    def run(self):
        pass

class Character():
    def __init__(self):
        self.inventory = []
        for i in range(0, 36):
            self.inventory.append({})
        self.inventory[0] = ITEMS['steel broadsword'].copy()
        self.inventory[1] = ITEMS['steel helmet'].copy()
        self.inventory[2] = ITEMS['red burlap shirt'].copy()
        self.inventory[3] = ITEMS['steel gauntlets'].copy()
        self.inventory[4] = ITEMS['brown boots'].copy()
        self.inventory[5] = ITEMS['steel plated boots'].copy()
        self.inventory[6] = ITEMS['potion of major healing'].copy()
        self.inventory[7] = ITEMS['potion of minor healing'].copy()
        self.inventory[8] = ITEMS['potion of major magica'].copy()
        self.inventory[9] = ITEMS['potion of major stamina'].copy()
        self.inventory[10] = ITEMS['platinum ingot'].copy()
        self.inventory[10]['number'] = self.inventory[10]['max stack']
        self.inventory[11] = ITEMS['steel ingot'].copy()
        self.inventory[11]['number'] = self.inventory[11]['max stack']
        self.inventory[12] = ITEMS['leather'].copy()
        self.inventory[12]['number'] = self.inventory[12]['max stack']
        self.inventory[13] = ITEMS['leather strips'].copy()
        self.inventory[13]['number'] = self.inventory[13]['max stack']
        self.inventory[14] = ITEMS['stick'].copy()
        self.inventory[14]['number'] = self.inventory[14]['max stack']
        self.inventory[15] = ITEMS['War of the Worlds'].copy()
        self.inventory[16] = ITEMS['Guide to Arroshay'].copy()
        self.inventory[17] = ITEMS['black crystal'].copy()
        self.inventory[18] = ITEMS['green crystal'].copy()

        self.expanded_inventory = {'magic': [{'name' : 'healing'}, {'name': 'fireball'}, {'name': 'fire spray'}, {'name': 'summon golem'}, {'name': 'summon rabbit'}, {'name': 'demonic possession'}]}
        self.equipped = {'gender': 'female', 'race': 'osidine', 6: {}, 'hair': None, 'weapons': None, 'weapons2': None, 'head': {}, 'torso': ITEMS['orange burlap shirt'].copy(), 'bottom': ITEMS['brown pants'].copy(), 'feet': {}, 'gloves': {}, 'items': {}, 0: {}, 1: {}, 2: {}, 3: {}, 4: {}, 5: {}}
        self.colors = {'hair': DEFAULT_HAIR_COLOR, 'skin': DEFAULT_SKIN_COLOR}
        self.hand_item = self.equipped[0]
        self.hand2_item = self.equipped[6]
        self.stats = {'health': 100, 'max health': 100, 'stamina': 100, 'max stamina': 100, 'magica': 100, 'max magica': 100,
              'hunger': 100, 'max hunger': 100, 'weight': 0, 'max weight': 100, 'strength': 1, 'agility': 1, 'armor': 0,
              'kills': 0, 'marksmanship hits': 0, 'marksmanship shots fired': 0, 'marksmanship accuracy': 0, 'melee': 0,
              'hits taken': 0, 'exercise': 0, 'healing': 0, 'stamina regen': 0, 'magica regen': 0, 'looting': 0,
              'casting': 0, 'lock picking': 0, 'touch damage': 0, 'touch knockback': 0, 'acceleration': 38, 'level': 0}

class Item_Icon(pg.sprite.Sprite):
    def __init__(self, mother, slot, item, font_name, size, color, x, y, slot_text = None, dict = 'inventory'):
        self.font = pg.font.Font(font_name, size)
        self.font_name = font_name
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
        self.text = ''
        pg.sprite.Sprite.__init__(self, self.groups)
        self.x = x
        self.y = y
        self.update()

    def update(self):
        if 'type' in self.item.keys():
            self.type = self.item['type']
        elif self.item in self.mother.character.expanded_inventory['magic']:
            self.type = 'magic'
        elif self.item in HAIR.values():
            self.type = 'hair'
        elif self.item in BASIC_RACES:
            self.type = 'race'
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
            elif self.type == 'hair':
                self.item_image = pg.transform.scale(self.game.black_box_image, (ICON_SIZE - 2, ICON_SIZE - 2))
                temp_img = pg.transform.scale(self.game.hair_images[self.item['name']], (ICON_SIZE - 2, ICON_SIZE - 2))
                self.item_image.blit(temp_img, (0, 0))
                self.item_image = color_image(self.item_image, self.mother.character.colors['hair'])
            elif self.type == 'race':
                self.item_image = pg.transform.scale(self.game.black_box_image, (ICON_SIZE - 2, ICON_SIZE - 2))
                temp_img = pg.transform.scale(self.game.race_images[self.item['name']], (ICON_SIZE - 2, ICON_SIZE - 2))
                self.item_image.blit(temp_img, (0, 5))
                self.font = pg.font.Font(self.font_name, 13)
                self.text = self.item['name']
                self.text_image = self.font.render(self.text, True, self.color)
                self.item_image.blit(self.text_image, (1, 0))
            elif ('type' in self.item) and (self.item['type'] == 'block'):
                try:
                    gid = gid_with_property(self.game.map.tmxdata, 'material', self.item['name'])
                    self.item_image = self.game.map.tmxdata.get_tile_image_by_gid(gid)
                except:
                    self.item_image = self.box_image
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
        if ('hp' in self.item.keys()) and ('max hp' in self.item.keys()):
            if self.item['hp'] != self.item['max hp']:
                self.draw_hp_bar(self.image, 2, ICON_SIZE - 8, self.item['hp']/self.item['max hp'])


        self.rect = self.image.get_rect()
        self.rect.x = self.x
        self.rect.y = self.y
        self.size = self.rect.width

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

class Picture(pg.sprite.Sprite):
    def __init__(self, game, mother, item_image, x, y, width = None, height = None):
        self.game = game
        self.mother = mother
        self.groups = self.mother.menu_sprites
        pg.sprite.Sprite.__init__(self, self.groups)
        if not width:
            self.image = item_image
        else:
            self.image = pg.transform.scale(item_image, (width, height))
        self.image.set_colorkey(BLACK)
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y

class MainMenu():  # used as the parent class for other menus.
    def __init__(self, game, character = 'player', menu_type = 'Crafting', container = [{}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}]):
        self.game = game
        self.over_minimap_image = pg.transform.scale(self.game.over_minimap_image, (self.game.screen_height - 80, self.game.screen_height - 80))
        if menu_type != 'Character':
            self.minimap_image = pg.transform.scale(self.game.minimap_image, (self.game.screen_height - 80, self.game.screen_height - 80))
        if character == 'player':
            self.character = self.game.player
        else:
            self.character = character
        self.menu_type = menu_type
        if self.menu_type in ['Game', 'Character']:
            self.menu_type = 'Crafting'
        self.container = container
        if self.menu_type not in  ['Looting']:
            self.recipies = RECIPIES[self.menu_type]
        else:
            self.recipies = {}
        self.surface_width = self.surface_height = 128
        self.body_surface = pg.Surface((self.surface_width, self.surface_height)).convert_alpha()
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
        self.palette = None
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
        self.character_heading_list = ['Gender', 'Race', 'Hair']
        self.game_heading_list = ['Settings', 'Save/Load Game', 'Exit Menu', 'Quit Game']
        self.quest_heading_list = ['Active Quests', 'Completed Quests']
        self.settings_heading_list = ['Controls']
        self.save_heading_list = ['Save Game', 'Load Game']
        self.controls_menu_list = self.game.key_map.keys()
        if menu_type == 'Game':
            self.selected_heading_list = self.heading_list
        elif menu_type == 'Character':
            self.selected_heading_list = self.character_heading_list
        else:
            self.selected_heading_list = self.inventory_heading_list
        self.moving_item = None
        self.draw_map = False
        self.trash = Picture_Icon(self, self.game.trash_image, 932, 25, 40)
        if menu_type == 'Character':
            self.back_arrow = Picture_Icon(self, self.game.start_icon_image, 25, 25, 40)
        else:
            self.back_arrow = Picture_Icon(self, self.game.back_arrow_image, 25, 25, 40)
        self.read_menu_icons.add(self.back_arrow)
        self.generate_headings(True)
        self.icon_offset = (0, 0) # Used for telling where you clicked on an icon to make the motion fluid.
        self.crafting_slots = []
        for i in range (0, 9): # generates list of slots to be used in the crafting menu to craft items.
            self.crafting_slots.append({})
        self.run()

    def draw_character_preview(self):
        self.body_surface = pg.Surface((self.surface_width, self.surface_height)).convert_alpha()
        if self.character.equipped['race'] == 'wraith':
            temp_surface = pg.Surface((90, 90)).convert()
            temp_surface.fill(WHITE)
            self.body_surface.blit(temp_surface, (26, 18))
        part_placement = CP_STANDING_ARMS_OUT0
        rect = self.body_surface.get_rect()
        if self.character.equipped['gender'] == 'other':
            body_part_images_list = 'male' + '_' + self.character.equipped['race']+ '_' + 'images'  # Used male images by default for 'other'
        else:
            body_part_images_list = self.character.equipped['gender'] + '_' + self.character.equipped['race']+ '_' + 'images'
        part_image_dict = {0: 0, 1: 0, 2: 1, 3: 2, 4: 2, 5: 3, 6: 3, 7: 4, 8: 5, 9: 6, 10: 6}
        reverse_list = [1, 4, 6, 10]
        for i, part in enumerate(part_placement):
            if i in range(0, 9):
                temp_img = self.game.humanoid_images[body_part_images_list][part_image_dict[i]]
                if i in reverse_list:
                    temp_img = pg.transform.flip(temp_img, False, True)
                colored_img = color_image(temp_img, self.character.colors['skin'])
                image = pg.transform.rotate(colored_img, part[2])
                temp_rect = image.get_rect()
                self.body_surface.blit(image, (rect.centerx - (temp_rect.centerx - part[0]), rect.centery - (temp_rect.centery - part[1])))
                if i == 7 and 'mechanima' in self.character.equipped['race']:  # draws back lights on mechs.
                    temp_img = self.game.mech_back_image
                    colored_img = color_image(temp_img, self.character.colors['hair'])
                    temp_rect = colored_img.get_rect()
                    self.body_surface.blit(colored_img, (
                    rect.centerx - (temp_rect.centerx - part[0]), rect.centery - (temp_rect.centery - part[1])))

            if i in [0, 1, 2, 3, 4, 7]:  # Adds all clothing except weapons and hats.
                if not ((self.selected_heading_list == self.character_heading_list) and (self.character.equipped['race'] in NO_CLOTHES_RACES)):
                    if self.character.equipped[EQUIP_DRAW_LIST[i]] != {}:
                        # imgpath = self.mother.equipped[EQUIP_DRAW_LIST[i]
                        try:
                            temp_img = self.game.item_images[correct_filename(self.character.equipped[EQUIP_DRAW_LIST[i]])]
                        except:  # Finds image for appropriate gendered clothing item if it is a gendered item (only tops and bottoms are ever gendered).
                            filename = correct_filename(self.character.equipped[EQUIP_DRAW_LIST[i]]) + gender_tag(self.character)
                            temp_img = self.game.item_images[filename]
                        if 'color' in self.character.equipped[EQUIP_DRAW_LIST[i]]:
                            temp_img = color_image(temp_img, self.character.equipped[EQUIP_DRAW_LIST[i]]['color'])
                        if i in reverse_list:  # Flips gloves and shoes
                            temp_img = pg.transform.flip(temp_img, False, True)
                        image = pg.transform.rotate(temp_img, part[2])
                        temp_rect = image.get_rect()
                        self.body_surface.blit(image, (rect.centerx - (temp_rect.centerx - part[0]), rect.centery - (temp_rect.centery - part[1])))
                    if i == 7:  # Adds shirt/top
                        torso_pos = part  # used to place the wings on at the correct location/angle
            elif i == 10:
                if self.character.equipped['hair']:
                    temp_img = self.game.hair_images[self.character.equipped['hair']]
                    colored_img = color_image(temp_img, self.character.colors['hair'])
                    image = pg.transform.rotate(colored_img, part_placement[8][2])
                    temp_rect = image.get_rect()
                    self.body_surface.blit(image, (rect.centerx - (temp_rect.centerx - part_placement[8][0]),
                                              rect.centery - (temp_rect.centery - part_placement[8][1])))
                if self.character.equipped['head'] != {}:
                    temp_img = self.game.item_images[correct_filename(self.character.equipped['head'])]
                    if 'color' in self.character.equipped['head']:
                        temp_img = color_image(temp_img, self.character.equipped['head']['color'])
                    image = pg.transform.rotate(temp_img, part_placement[8][2])
                    temp_rect = image.get_rect()
                    self.body_surface.blit(image, (rect.centerx - (temp_rect.centerx - part_placement[8][0]),
                                              rect.centery - (temp_rect.centery - part_placement[8][1])))

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
        elif self.selected_text.text == 'Male':
            self.character.equipped['gender'] = 'male'
            self.draw_character_preview()
        elif self.selected_text.text == 'Female':
            self.character.equipped['gender'] ='female'
            self.draw_character_preview()
        elif self.selected_text.text == 'Other':
            self.character.equipped['gender'] = 'other'
            self.draw_character_preview()
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
                for item in self.clicked_sprites:
                    if item in self.text_sprites:
                        self.click_text_icon(item)
                    elif item in self.item_sprites:
                        self.selected_item = item
                        if self.selected_heading.text in ['Hair', 'Race', 'Gender']:
                            if self.selected_item.text in RACE.keys():
                                self.character.equipped['race'] = self.selected_item.text
                                self.character.equipped['hair'] = 'bald'
                                self.character.colors = DEFAULT_RACE_COLORS[self.selected_item.text]
                            self.display_item_info()
                            if self.selected_item.dict == 'hair':
                                self.character.equipped['hair'] = self.selected_item.item['name']
                            self.list_items()
                    if self.palette in self.clicked_sprites:
                        pos = pg.mouse.get_pos()
                        if self.selected_heading.text == 'Hair':
                            self.character.colors['hair'] = self.game.screen.get_at((pos[0], pos[1]))
                            for icon in self.inventory_icons:
                                self.inventory_icons.update()
                            self.list_items()
                        if self.selected_heading.text == 'Race':
                            self.character.colors['skin'] = self.game.screen.get_at((pos[0], pos[1]))
                            self.list_items()
                    if self.selected_item and (self.selected_heading.text not in self.character_heading_list):
                        # Lets you move items around and equip them.
                        dict = None
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
                    if self.selected_heading_list == self.character_heading_list:
                        self.create_character()
                        self.clear_menu()
                        self.running = False
                    elif self.selected_heading_list != self.heading_list:
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
            item.kill()
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
        if self.selected_heading.text in ['Inventory', 'Magic'] + WORKSTATIONS + self.character_heading_list: # Draws character preview
            self.game.screen.blit(pg.transform.rotate(pg.transform.scale(self.body_surface, (300, 300)), -90), (692, -7))
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
        if self.selected_heading.text not in ['Inventory', 'Magic'] + WORKSTATIONS + self.character_heading_list:
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
        if self.selected_heading.text in ['Inventory', 'Magic'] + WORKSTATIONS + self.character_heading_list:
            self.draw_text('Preview', default_font, 30, WHITE, 750, 10, "topleft")
            self.draw_text('Selected Item Stats', default_font, 18, WHITE, 750, 275, "topleft")
        elif self.selected_heading.text == 'Looting':
            self.draw_text('Loot', default_font, 30, WHITE, 500, 10, "topleft")
        pos = pg.mouse.get_pos()
        if self.moving_item:
            self.game.screen.blit(self.moving_item.image, (pos[0] + self.icon_offset[0], pos[1] + self.icon_offset[1]))
        if self.draw_map:
            self.draw_overmap()
        if self.palette:
            self.palette.kill()
        swatch_image = None
        if self.selected_heading.text == 'Hair':
            try:
                swatch_image = self.game.color_swatch_images[HAIR_PALETE_IMAGES[self.character.equipped['race']]]
            except:
                swatch_image = self.game.color_swatch_images[0]

        elif self.selected_heading.text == 'Race':
            race_text = wrap(RACE[self.character.equipped['race']]['description'], 45)
            for i, line in enumerate(race_text):
                self.draw_text(line, default_font, 20, WHITE, 40, self.game.screen_height / 2 + 30 * i, "topleft")
            try:
                swatch_image = self.game.color_swatch_images[PALETE_IMAGES[self.character.equipped['race']]]
            except:
                swatch_image = self.game.color_swatch_images[0]
        if self.selected_heading.text in ['Hair', 'Race']:
            self.draw_text('Color', default_font, 30, WHITE, 500, 10, "topleft")
            self.palette = Picture(self.game, self, swatch_image, 493, 57, 227, 453)

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
        self.draw_character_preview()
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
            dict = 'magic'
        elif self.selected_heading.text == 'Hair':
            self.trash.hide()
            inventory = RACE_HAIR[self.character.equipped['race']]
            dict = 'hair'
        elif self.selected_heading.text == 'Race':
            self.trash.hide()
            inventory = BASIC_RACES
            dict = 'race'
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
            elif self.selected_heading.text == 'Gender':
                self.trash.hide()
                menu_list = ['Male', 'Female', 'Other']
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

        if self.selected_heading.text not in ['Looting', 'Race', 'Hair']:
            # Lists equipped slots
            xoffset = 495
            yoffset = spacing * 4 + 58
            padding = 5
            num_in_row = 3
            row = -1
            col = 0
            i = 0
            for key in self.character.equipped.keys():
                if key in [0, 1, 2, 3, 4, 5]:
                    item = self.character.equipped[key]
                    col = i % num_in_row
                    if col == 0:
                        row += 1
                    icon = Item_Icon(self, i, item, default_font, 20, WHITE, xoffset + spacing * col, yoffset + (row * spacing), str(i + 1), 'equipped')
                    spacing = icon.size + padding
                    self.variable_equip.add(icon)
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
        if self.selected_item:
            if self.selected_heading.text == 'Race':
                item_dictionary = {'Name': self.selected_item.item['name']}
                i = 0
                for stat in item_dictionary:
                    item_stats = ""
                    item_stats += (stat + ":  " + str(item_dictionary[stat]))
                    self.printable_stat_list.append(item_stats)
                    i += 1

            else:
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
        if ('type' in self.character.equipped[6]):
            self.character.hand2_item = self.character.equipped[6]
        if ('type' in self.character.equipped[6]) and (self.character.equipped[6]['type'] in WEAPON_TYPES):
            self.character.equipped['weapons2'] = self.character.equipped[6]
        else:
            self.character.equipped['weapons2'] = None
        self.game.in_menu = False
        self.game.beg = perf_counter() # resets the counter so dt doesn't get messed up.

    def create_character(self):
        self.game.quit

g = Game()
while True:
    g.run()