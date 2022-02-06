import pygame as pg
import os
from os import path
from hair import *
from magic import *
from interactables import *
from new_items import *
from chests import *
from race_info import *
from color_palettes import *
#from weapons import *
#from armor import *

vec = pg.math.Vector2
vec3 = pg.math.Vector3

# define game folders
game_folder = path.dirname(__file__)
img_folder = path.join(game_folder, 'img')
books_folder = path.join(game_folder, 'books')
saves_folder = path.join(game_folder, 'saves')
fonts_folder = path.join(game_folder, 'fonts')
snd_folder = path.join(game_folder, 'snd')
music_folder = path.join(game_folder, 'music')
map_folder = path.join(game_folder, 'maps')
# image folder and subfolders
male_mech_suit_parts_folder = female_mech_suit_parts_folder = path.join(img_folder, 'mech_suit')
male_golem_parts_folder = female_golem_parts_folder = path.join(img_folder, 'golem_parts')
male_icegolem_parts_folder = female_icegolem_parts_folder = path.join(img_folder, 'icegolem_parts')
male_wraith_parts_folder = female_wraith_parts_folder = path.join(img_folder, 'wraith_parts')
male_spirit_parts_folder = female_spirit_parts_folder = path.join(img_folder, 'spirit_parts')
male_wraithdragon_parts_folder = female_wraithdragon_parts_folder = path.join(img_folder, 'wraithdragon_parts')
male_spiritdragon_parts_folder = female_spiritdragon_parts_folder = path.join(img_folder, 'spiritdragon_parts')
male_skeleton_parts_folder = female_skeleton_parts_folder = path.join(img_folder, 'skeleton_parts')
male_skeletondragon_parts_folder = female_skeletondragon_parts_folder = path.join(img_folder, 'skeletondragon_parts')
female_shaktele_parts_folder = female_osidine_parts_folder = path.join(img_folder, 'female_osidine_parts')
male_shaktele_parts_folder = male_osidine_parts_folder = path.join(img_folder, 'male_osidine_parts')
female_shakteledragon_parts_folder = female_osidinedragon_parts_folder = path.join(img_folder, 'female_osidinedragon_parts')
male_shakteledragon_parts_folder = male_osidinedragon_parts_folder = path.join(img_folder, 'male_osidinedragon_parts')
female_elfdragon_parts_folder = path.join(img_folder, 'female_elfdragon_parts')
male_elfdragon_parts_folder = path.join(img_folder, 'male_elfdragon_parts')
female_miewdradragon_parts_folder = path.join(img_folder, 'female_miewdradragon_parts')
male_miewdradragon_parts_folder = path.join(img_folder, 'male_miewdradragon_parts')
female_lacertoliandragon_parts_folder = path.join(img_folder, 'female_lacertoliandragon_parts')
male_lacertoliandragon_parts_folder = path.join(img_folder, 'male_lacertoliandragon_parts')
male_mechanimadragon_parts_folder = path.join(img_folder, 'male_mechanimadragon_parts')
female_mechanimadragon_parts_folder = path.join(img_folder, 'female_mechanimadragon_parts')
male_immortuidragon_parts_folder = path.join(img_folder, 'male_immortuidragon_parts')
female_immortuidragon_parts_folder = path.join(img_folder, 'female_immortuidragon_parts')
female_miewdra_parts_folder = path.join(img_folder, 'female_miewdra_parts')
male_miewdra_parts_folder = path.join(img_folder, 'male_miewdra_parts')
female_immortui_parts_folder = path.join(img_folder, 'female_immortui_parts')
male_immortui_parts_folder = path.join(img_folder, 'male_immortui_parts')
male_elf_parts_folder = path.join(img_folder, 'male_elf_parts')
female_elf_parts_folder = path.join(img_folder, 'female_elf_parts')
male_lacertolian_parts_folder = path.join(img_folder, 'male_lacertolian_parts')
female_lacertolian_parts_folder = path.join(img_folder, 'female_lacertolian_parts')
male_mechanima_parts_folder = path.join(img_folder, 'male_mechanima_parts')
female_mechanima_parts_folder = path.join(img_folder, 'female_mechanima_parts')
male_vadashay_parts_folder = path.join(img_folder, 'male_vadashay_parts')
female_vadashay_parts_folder = path.join(img_folder, 'female_vadashay_parts')
male_demon_parts_folder = path.join(img_folder, 'male_demon_parts')
female_demon_parts_folder = path.join(img_folder, 'female_demon_parts')
male_goblin_parts_folder = path.join(img_folder, 'male_goblin_parts')
female_goblin_parts_folder = path.join(img_folder, 'female_goblin_parts')
animals_folder = path.join(img_folder, 'animals')
book_animation_folder = path.join(img_folder, 'book_animation')
new_items_folder = path.join(img_folder, 'new_items')
doors_folder = path.join(img_folder, 'doors')
door_break_folder = path.join(img_folder, 'door_break_animation')
bullets_folder = path.join(img_folder, 'bullets')
fire_folder = path.join(img_folder, 'fire_animation')
breakable_folder = path.join(img_folder, 'breakable')
tree_folder = path.join(img_folder, 'trees')
shock_folder = path.join(img_folder, 'shock_animation')
electric_door_folder = path.join(img_folder, 'electric_door_animation')
fireball_folder = path.join(img_folder, 'fireball')
explosion_folder = path.join(img_folder, 'explosion')
workstations_folder = path.join(img_folder, 'workstations')
#items_folder = path.join(img_folder, 'items')
#weapons_folder = path.join(img_folder, 'weapons')
#hats_folder = path.join(img_folder, 'hats')
#tops_folder = path.join(img_folder, 'tops')
#bottoms_folder = path.join(img_folder, 'bottoms')
#shoes_folder = path.join(img_folder, 'shoes')
#gloves_folder = path.join(img_folder, 'gloves')
hair_folder = path.join(img_folder, 'hair')
magic_folder = path.join(img_folder, 'magic')
gender_folder = path.join(img_folder, 'gender')
race_folder = path.join(img_folder, 'race')
enchantments_folder = path.join(img_folder, 'enchantments')
corpse_folder = path.join(img_folder, 'corpses')
loading_screen_folder = path.join(img_folder, 'loading_screens')
vehicles_folder = path.join(img_folder, 'vehicles')
color_swatches_folder = path.join(img_folder, 'color_swatches')
light_masks_folder = path.join(img_folder, 'light_masks')

# Font settings:
HEADING_FONT = path.join(fonts_folder, 'UncialAntiqua-Regular.ttf')
SCRIPT_FONT = path.join(fonts_folder, 'EagleLake-Regular.ttf')
HUD_FONT = path.join(fonts_folder, 'Aegean.ttf')
MENU_FONT = path.join(fonts_folder, 'LinBiolinum_Rah.ttf')
WRITING_FONT = path.join(fonts_folder, 'DancingScript-Regular.ttf')
KAWTHI_FONT = path.join(fonts_folder, 'Kawthi.ttf')

# Menu Related stuff
ICON_SIZE = 71
HUD_ICON_SIZE = 40
DOUBLE_CLICK_TIME = 200

#ITEM_TYPE_LIST = ['weapons', 'tops', 'bottoms', 'hats', 'shoes', 'gloves', 'items', 'blocks']
EQUIP_DRAW_LIST = ['feet', 'feet', 'bottom', 'gloves', 'gloves', None, None, 'torso']
#EQUIP_IMG_LIST = ['shoe', 'shoe', 'bottom', 'glove', 'glove', None, None, 'top']

#print(len([name for name in os.listdir(body_parts_folder) if os.path.isfile(os.path.join(body_parts_folder, name))]))

# game settings
pg.mixer.pre_init(44100, -16, 4, 2048)
pg.init()
pg.mixer.init()
os.environ['SDL_VIDEO_CENTERED'] = '1'
#infoObject = pg.display.Info() #creates an info object to detect native screen resolution.
# Sets maximum screen resolution to 1920 by 1080
MODES = pg.display.list_modes()
#WIDTH = int(infoObject.current_w / 2)
#HEIGHT = int(infoObject.current_h / 2)
#if (WIDTH < 960) and (infoObject.current_w > 960):
WIDTH = 960
HEIGHT = 540
SOUND_SOURCE_DISTANCE = int(WIDTH/2) + 100
#elif WIDTH > 1920:
#    WIDTH = 1920
#    HEIGHT = 1080
#if WIDTH > 1600: # Allowing for 1080 slows down performance by about 10+ fps and really doesn't improve the experience much.
#WIDTH = 1600
#HEIGHT = 900
#WIDTH = 1024
#HEIGHT = 768
#if WIDTH > 1920: # Allowing for 1080p slows down performance by about 10+ fps and really doesn't improve the experience much.
#    WIDTH = 1920
#    HEIGHT = 1080
#MAPWIDTH = 8192 # Number of tiles wide times pixel width of tile or 65 * 128
#MAPHEIGHT = 8192 # Number of tiles high times pixel height of tile or 65 * 128
FPS = 60
TITLE = "Sky Realm"
BGCOLOR = BROWN
TITLE_IMAGE = 'skyrealm.png'
LOGO_IMAGE = 'a two headed snick.png'
MPY_WORDS = 'mpy_words.png'
ICON_IMG = 'zhara_icon.png'
OVERWORLD_MAP_IMAGE = 'worldmap.png'
#MAP_TILE_WIDTH = 64 # 64 tiles by 64 tiles per map
#GRIDWIDTH = WIDTH / MAP_TILE_WIDTH
#GRIDHEIGHT = HEIGHT / MAP_TILE_WIDTH
TILESIZE = 32
START_WORLD = 'worldmap.tmx'
UPGRADE_FACTOR = 1.2 # This number determines how much item value increases when upgrading armor and weapons. The higher the number the lower the value.

KEY_MAP = {'jump': pg.K_SPACE, 'sprint': pg.K_LSHIFT, 'forward': pg.K_w, 'back': pg.K_s, 'rot left': pg.K_a, 'rot right': pg.K_d, 'strafe left': pg.K_z, 'strafe right': pg.K_c, 'dismount': pg.K_x, 'interact': pg.K_e, 'reload': pg.K_r, 'fire': pg.K_f, 'climb': pg.K_q, 'lamp': pg.K_n, 'transform': pg.K_t, 'grenade': pg.K_g, 'place': pg.K_y, 'minimap': pg.K_m, 'pause': pg.K_p, 'up': pg.K_u, 'hitbox': pg.K_h, 'inventory': pg.K_i, 'melee': pg.K_TAB, 'block': pg.K_LALT}

# Day/Night
DAY_LENGTH = 15 * 60 * 1000
NIGHT_LENGTH = 9 * 60 * 1000
DAY_PERIOD = DAY_LENGTH + NIGHT_LENGTH
NIGHTFALL_SPEED = 100 # The higher the slower. In ms.
GAME_HOUR = DAY_PERIOD/24


WORKSTATIONS = ['Crafting', 'Work Bench', 'Anvil', 'Enchanter', 'Smelter', 'Tanning Rack', 'Grinder', 'Cooking Fire', 'Alchemy Lab']
WORK_STATION_LIST = []
for item in WORKSTATIONS:
    WORK_STATION_LIST.append(item.lower())
WORK_STATION_DICT = {'crafting': 'Crafting', 'work bench': 'Work Bench', 'anvil': 'Anvil', 'enchanter': 'Enchanter', 'smelter': 'Smelter', 'tanning rack': 'Tanning Rack', 'grinder': 'Grinder', 'cooking fire': 'Cooking Fire', 'alchemy lab': 'Alchemy Lab', 'looting': 'Looting'}

# Player settings
#PLAYER_HEALTH = 100
#PLAYER_STAMINA = 100
#PLAYER_STRENGTH = 1
#PLAYER_ACC = 38
RUN_INCREASE = 12
#PLAYER_CLIMB = 14
MAX_RUN = 80
CLIMB_TIME = 1000
PLAYER_FRIC = -0.17
PLAYER_ROT_SPEED = 200
PLAYER_TUR = 'turret.png'
PLAYER_TANK = 'tank.png'
TALK_RADIUS =  int(TILESIZE*0.66)
TANK_IN_WATER = 'tank_underwater.png'
SUNKEN_TANK = 'sunken_tank.png'
PLAYER_IMG = 'player1.png'
PLAYER_HIT_RECT = pg.Rect(0, 0, int(TILESIZE*0.7), int(TILESIZE*0.7))
MELEE_SIZE = 5
#WALL_DETECT_DIST = 80

#Misc Sprite Settings/Stuffs
TREE_SIZES = {'small': 110, 'medium': 183, 'large': 256}
TREES = {}
TREES['dead tree'] = {}
TREES['green tree'] = {}
TREES['palm tree'] = {}
TREES['pine tree'] = {}
BREAKABLES = {}
BREAKABLES['empty turtle shell'] = {'break type': 'gradual', 'wobble': False, 'weapon required': ['mace', 'pickaxe', 'axe'], 'animate speed': 50, 'right weapon hit sound': 'rock_hit', 'hit sound': 'rock_hit', 'break sound': 'rocks', 'health': 2, 'damage': 0, 'knockback': 0, 'protected': False, 'random drop number': True, 'items': {'turtle shell plate':12}, 'min drop': 4, 'rare items': ['bluefish']}

# Used for mapping portal firepot combos with map locations
# 1234-Goblin Island, 4132: Demon's Lair, 3421-Dewcastle Graveyard, 2143-Norwald the Miewdra Village, 1342-Mechanima Village, 1243-Lacertolia, 2413-Zombieland, 4321-Elf Town, 3124-South Pole
PORTAL_CODES = {'1234': [107, 34, 32, 26], '4132': [53, 75, 31, 5], '3421': [27, 40, 5, 33], '2143': [89, 49, 32, 32], '1342': [126, 22, 32, 32], '1243': [146, 43, 32, 32], '2413': [65, 20, 32, 32],  '4321': [38, 27, 32, 42], '3124': [85, 96, 32, 32]}

AIPATHS = ['UD', 'RL']

# Sets up randomizable map files by type:
MOUNTAIN_MAPS = []
FOREST_MAPS = []
GRASSLAND_MAPS = []
TUNDRA_MAPS = []
DESERT_MAPS = []
SWAMP_MAPS = []
for file in os.listdir(map_folder):
    name = file.replace('.tmx', '')
    if file.startswith("MOUNTAIN"):
        MOUNTAIN_MAPS.append(name)
    elif file.startswith("FOREST"):
        FOREST_MAPS.append(name)
    elif file.startswith("GRASSLAND"):
        GRASSLAND_MAPS.append(name)
    elif file.startswith("TUNDRA"):
        TUNDRA_MAPS.append(name)
    elif file.startswith("DESERT"):
        DESERT_MAPS.append(name)
    elif file.startswith("SWAMP"):
        SWAMP_MAPS.append(name)
RANDOM_MAP_TILES = {'53': 'MOUNTAIN_MAPS', '27': 'FOREST_MAPS', '11': 'GRASSLAND_MAPS', '48': 'SWAMP_MAPS'}

# Player body image settings
gender_list = ['male', 'female']
HUMANOID_IMAGES = {}
for kind in RACE_TYPE_LIST:
    for gender in gender_list:
        temp_images = []
        number_of_files = len([name for name in os.listdir(eval(gender + '_' + kind + '_parts_folder')) if os.path.isfile(os.path.join(eval(gender + '_' + kind + '_parts_folder'), name))])
        for i in range(1, number_of_files + 1):
            filename = 'player_layer{}.png'.format(i)
            temp_images.append(filename)
        HUMANOID_IMAGES[gender + '_' + kind + '_images'] = temp_images


PORTAL_SHEET = path.join(img_folder, 'portal.png')

BULLET_IMAGES = []
number_of_files = len([name for name in os.listdir(bullets_folder) if os.path.isfile(os.path.join(bullets_folder, name))])
for i in range(0, number_of_files):
    filename = 'bullet{}.png'.format(i)
    BULLET_IMAGES.append(filename)

FIRE_IMAGES = []
number_of_files = len([name for name in os.listdir(fire_folder) if os.path.isfile(os.path.join(fire_folder, name))])
for i in range(1, number_of_files + 1):
    filename = 'fire_1b_40_{}.png'.format(i)
    FIRE_IMAGES.append(filename)

BREAKABLE_IMAGES = {}
for breakable in BREAKABLES:
    temp_list = []
    number_of_files = len([name for name in os.listdir(breakable_folder) if breakable in name if os.path.isfile(os.path.join(breakable_folder, name))])
    for i in range(0, number_of_files):
        filename = breakable + '{}.png'.format(i)
        temp_list.append(filename)
    BREAKABLE_IMAGES[breakable] = temp_list

TREE_IMAGES = {}
for tree in TREES:
    temp_list = []
    number_of_files = len([name for name in os.listdir(tree_folder) if tree in name if os.path.isfile(os.path.join(tree_folder, name))])
    for i in range(0, number_of_files):
        filename = tree + '{}.png'.format(i)
        temp_list.append(filename)
    TREE_IMAGES[tree] = temp_list

SHOCK_IMAGES = []
number_of_files = len([name for name in os.listdir(shock_folder) if os.path.isfile(os.path.join(shock_folder, name))])
for i in range(1, number_of_files + 1):
    filename = 'shock{}.png'.format(i)
    SHOCK_IMAGES.append(filename)

ELECTRIC_DOOR_IMAGES = []
number_of_files = len([name for name in os.listdir(electric_door_folder) if os.path.isfile(os.path.join(electric_door_folder, name))])
for i in range(1, number_of_files + 1):
    filename = 'electric{}.png'.format(i)
    ELECTRIC_DOOR_IMAGES.append(filename)

FIREBALL_IMAGES = []
number_of_files = len([name for name in os.listdir(fireball_folder) if os.path.isfile(os.path.join(fireball_folder, name))])
for i in range(1, number_of_files + 1):
    filename = 'f{}.png'.format(i)
    FIREBALL_IMAGES.append(filename)

EXPLOSION_IMAGES = []
number_of_files = len([name for name in os.listdir(explosion_folder) if os.path.isfile(os.path.join(explosion_folder, name))])
for i in range(1, number_of_files + 1):
    filename = 'E000{}.png'.format(i)
    EXPLOSION_IMAGES.append(filename)

HAIR_IMAGES = {} # Loads all item filepaths
for name in os.listdir(hair_folder):
    if os.path.isfile(os.path.join(hair_folder, name)):
        item_name = name.replace('.png', '')
        HAIR_IMAGES[item_name] = name

RACE_IMAGES = {} # Loads all item filepaths
for name in os.listdir(race_folder):
    if os.path.isfile(os.path.join(race_folder, name)):
        item_name = name.replace('.png', '')
        RACE_IMAGES[item_name] = name

NEW_ITEM_IMAGES = {} # Loads all item filepaths
for name in os.listdir(new_items_folder):
    if os.path.isfile(os.path.join(new_items_folder, name)):
        item_name = name.replace('.png', '')
        NEW_ITEM_IMAGES[item_name] = name

WORKSTATION_IMAGES = {} # Loads all item filepaths
for name in os.listdir(workstations_folder):
    if os.path.isfile(os.path.join(workstations_folder, name)):
        item_name = name.replace('.png', '')
        WORKSTATION_IMAGES[item_name] = name

MAGIC_IMAGES = {} # Loads all magic filepaths
for name in os.listdir(magic_folder):
    if os.path.isfile(os.path.join(magic_folder, name)):
        item_name = name.replace('.png', '')
        MAGIC_IMAGES[item_name] = name

ENCHANTMENT_IMAGES = []
number_of_files = len([name for name in os.listdir(enchantments_folder) if os.path.isfile(os.path.join(enchantments_folder, name))])
for i in range(0, number_of_files):
    filename = 'enchantment{}.png'.format(i)
    ENCHANTMENT_IMAGES.append(filename)

GENDER_IMAGES = []
number_of_files = len([name for name in os.listdir(gender_folder) if os.path.isfile(os.path.join(gender_folder, name))])
for i in range(0, number_of_files):
    filename = 'gender{}.png'.format(i)
    GENDER_IMAGES.append(filename)

CORPSE_IMAGES = []
number_of_files = len([name for name in os.listdir(corpse_folder) if os.path.isfile(os.path.join(corpse_folder, name))])
for i in range(0, number_of_files):
    filename = 'corpse{}.png'.format(i)
    CORPSE_IMAGES.append(filename)

LOADING_SCREEN_IMAGES = []
number_of_files = len([name for name in os.listdir(loading_screen_folder) if os.path.isfile(os.path.join(loading_screen_folder, name))])
for i in range(0, number_of_files):
    filename = 'screen{}.png'.format(i)
    LOADING_SCREEN_IMAGES.append(filename)

VEHICLES_IMAGES = []
number_of_files = len([name for name in os.listdir(vehicles_folder) if os.path.isfile(os.path.join(vehicles_folder, name))])
for i in range(0, number_of_files):
    filename = 'vehicle{}.png'.format(i)
    VEHICLES_IMAGES.append(filename)

COLOR_SWATCH_IMAGES = []
number_of_files = len([name for name in os.listdir(color_swatches_folder) if os.path.isfile(os.path.join(color_swatches_folder, name))])
for i in range(0, number_of_files):
    filename = 'swatch{}.png'.format(i)
    COLOR_SWATCH_IMAGES.append(filename)

LIGHT_MASK_IMAGES = []
number_of_files = len([name for name in os.listdir(light_masks_folder) if os.path.isfile(os.path.join(light_masks_folder, name))])
for i in range(0, number_of_files):
    filename = 'light{}.png'.format(i)
    LIGHT_MASK_IMAGES.append(filename)

# Bullet Images
BULLET_IMG = path.join(img_folder, 'bullet.png')
BLUELASER_IMG = path.join(img_folder, 'laserBlue.png')

# Hit Rects
EXPLOSION_HIT_RECT = pg.Rect(0, 0,  int(TILESIZE*1), int(TILESIZE*1))
FIREBALL_HIT_RECT = pg.Rect(0, 0,  int(TILESIZE*0.3), int(TILESIZE*0.3))
SMALL_HIT_RECT = pg.Rect(0, 0,  int(TILESIZE*0.5), int(TILESIZE*0.5))
MEDIUM_HIT_RECT = pg.Rect(0, 0,  int(TILESIZE*0.75), int(TILESIZE*0.75))
LARGE_HIT_RECT = pg.Rect(0, 0,  int(TILESIZE*1), int(TILESIZE*1))
XLARGE_HIT_RECT = pg.Rect(0, 0,  int(TILESIZE*1.3), int(TILESIZE*1.3))

# Mob settings
MOB_SPEEDS = [150, 100, 75, 125]
MOB_ROT_SPEED = 200
MOB_HIT_RECT = pg.Rect(0, 0,  int(TILESIZE*0.8), int(TILESIZE*0.8))
MOB_HEALTH = 100
MOB_DAMAGE = 10
MOB_KNOCKBACK = 20
MOB_HEALTH_BAR_LENGTH = 80
MOB_HEALTH_SHOW_TIME = 1000
AVOID_RADIUS = 50
DETECT_RADIUS = 400

DAMAGE_RATE = 100

# Effects
MUZZLE_FLASHES = ['whitePuff15.png', 'whitePuff16.png', 'whitePuff17.png',
                  'whitePuff18.png']
FLASH_DURATION = 50
DAMAGE_ALPHA = [i for i in range(0, 255, 55)]
NIGHT_COLOR = (20, 20, 20)
LIGHT_RADIUS = (200, 200)
EXPLODE_LIGHT_RADIUS = (250, 250)
FIRE_LIGHT_RADIUS = (500, 500)
FIREBALL_LIGHT_RADIUS = (150, 150)
LIGHT_MASK = "light_350_med.png"
SQUARE_LIGHT_MASK = 'light_square.png'
MAX_DARKNESS = 180
DIRECTIONAL_LIGHTS = [3, 5]
# This is a list of items and weapons that are light sources:
#LIGHTS_LIST = []
#for x in ITEMS:
#    if 'brightness' in ITEMS[x]:
#        LIGHTS_LIST.append(x)

# Layers
BASE_LAYER = 0
CORNERS_LAYER = 1
WATER_LAYER = 2
ITEMS_LAYER = 2
PLAYER_LAYER = 3
TREE_LAYER = 4
#WALL_LAYER = 4
#MOB_LAYER = 6
#VEHICLE_LAYER = 8
#BULLET_LAYER = 9
#ROOF_LAYER = 10
#EFFECTS_LAYER = 11
#SKY_LAYER = 12

# Music
TITLE_MUSIC = 'WendaleAbbey.ogg'
BG_MUSIC = 'Cloudforest_Awakening.ogg'
OCEAN_MUSIC = 'Eternal Renewal.ogg'
BEACH_MUSIC = 'Emerald Paradise.ogg'
ICEBEACH_MUSIC = 'Emerald Paradise.ogg'
ANT_TUNNEL_MUSIC = 'The Road Ahead.ogg'
CAVE_MUSIC = 'The Road Ahead.ogg'
MINE_MUSIC = 'The Road Ahead.ogg'
FOREST_MUSIC = 'Light from the Shadows.ogg'
GRASSLAND_MUSIC = 'The Forgotten Age.ogg'
TOWN_MUSIC = 'Last Haven.ogg'
ZOMBIELAND_MUSIC = 'DarkWinds.ogg'
TUNDRA_MUSIC = 'Tales and Tidings.ogg'
MOUNTAIN_MUSIC = 'Cloudforest_Awakening.ogg'
DESERT_MUSIC = 'Eternal Renewal.ogg'
SWAMP_MUSIC = 'Light from the Shadows.ogg'

# Sounds
LOCK_PICKING_SOUNDS = ['pick_lock1.ogg', 'pick_lock2.ogg', 'pick_lock3.ogg', 'pick_lock4.ogg']
MALE_PLAYER_HIT_SOUNDS = ['pain/8.ogg', 'pain/9.ogg', 'pain/10.ogg', 'pain/11.ogg', 'pain/12.ogg', 'pain/13.ogg']
FEMALE_PLAYER_HIT_SOUNDS = ['pain/f8.ogg', 'pain/f9.ogg', 'pain/f10.ogg', 'pain/f11.ogg', 'pain/f12.ogg', 'pain/f13.ogg']
ZOMBIE_MOAN_SOUNDS = ['brains2.ogg', 'brains3.ogg', 'zombie-roar-1.ogg', 'zombie-roar-2.ogg',
                      'zombie-roar-3.ogg', 'zombie-roar-5.ogg', 'zombie-roar-6.ogg', 'zombie-roar-7.ogg']
ZOMBIE_HIT_SOUNDS = ['splat-15.ogg']
WRAITH_SOUNDS = ['wraith1.ogg', 'wraith2.ogg', 'wraith3.ogg', 'wraith4.ogg']
EFFECTS_SOUNDS = {'tree fall': 'tree_fall.ogg', 'chopping wood': 'chopping_wood.ogg', 'eat': 'eat.ogg', 'door close': 'door_close.ogg', 'door open': 'door_open.ogg', 'charge': 'charge.ogg', 'bow reload': 'bow reload.ogg', 'level_start': 'Day_1_v2_mod.ogg', 'click': 'click.ogg', 'clickup': 'clickup.ogg', 'fanfare': 'fanfare.ogg', 'rustle': 'rustle.ogg', 'pickaxe': 'pickaxe.ogg', 'rocks': 'rocks.ogg', 'rock_hit': 'rock_hit.ogg', 'fart': 'fart.ogg', 'pee': 'pee.ogg', 'toilet': 'toilet.ogg',
                  'health_up': 'health_pack.ogg', 'casting healing': 'casting_healing.ogg', 'page turn': 'page_turn.ogg', 'close book': 'close_book.ogg',
                  'gun_pickup': 'gun_pickup.ogg', 'jump': 'jump.ogg', 'tank': 'tank.ogg', 'tank engine': 'tank_engine.ogg','splash': 'splash.ogg', 'grass': 'grass.ogg', 'swim': 'swim.ogg', 'shallows': 'shallows.ogg', 'climb': 'climb.ogg', 'unlock': 'unlock.ogg', 'lock click': 'lock_click.ogg', 'fire blast': 'fire_blast.ogg', 'knock':
                  'knock.ogg', 'metal hit': 'metal_hit.ogg', 'anvil': 'anvil.ogg', 'scrape': 'scrape.ogg', 'grindstone': 'grindstone.ogg', 'hammering': 'hammering.ogg', 'snore': 'snore.ogg', 'cashregister': 'cashregister.ogg', 'alchemy': 'alchemy.ogg', 'enchant': 'enchant.ogg', 'fire crackle': 'fire_crackling.ogg'}

PUNCH_SOUNDS = []
for i in range(0, 10):
    PUNCH_SOUNDS.append('punch'+ str(i+1) + '.ogg')

# Body mods/characteristics are stored in the players inventory like items. This just makes it way easier to customize them and give them attributes
GENDER = {}
GENDER['female'] = {'armor': 1,
                              'image': 1}
GENDER['male'] = {'armor': 1,
                              'image': 0}
GENDER['other'] = {'armor': 1,
                              'image': 2}
RACE = {}
RACE['osidine'] = {'name': 'osidine', 'start map': (1, 2), 'start pos': (570, 655),
                   'perks': {'strength': -0.2, 'agility': 0.2, 'magica': 5},
                   'description': 'The Osidine are descendants of the ancients who fought along side the dragons of Zhara for the liberation of Arroshay during the great war. They specialize in the construction of armor and melee weapons.'}
RACE['shaktele'] = {'name': 'shaktele', 'start map': (1, 2), 'start pos': (570, 655),
                    'perks': {'strength': 0.2, 'agility': -0.2},
                    'description': 'The Shaktele are a technologically advanced race that live in a modernized post-apocalyptic land created by biological warfare gone wrong. They specialize in the usage and construction of firearms and advanced weaponry.'}
RACE['elf'] = {'name': 'elf', 'armor': 1, 'start map': (1, 2), 'start pos': (570, 655),
               'perks': {'health': -10, 'stamina': 20, 'magica': 20, 'hunger': 20, 'strength': -0.5, 'agility': 1, 'stamina regen': 0.2, 'magica regen': 0.2},
                'description': 'The elves of Arroshay live in harmony with the forces of nature. Animals are less fearful of elves and usually only attack them if provoked.'}
RACE['immortui'] = {'name': 'immortui', 'start map': (1, 2), 'start pos': (570, 655),
                    'perks': {'health': 100, 'stamina': -40, 'hunger': 10, 'strength': -1, 'agility': -0.5},
                    'description': 'The Immortui are the undead either raised from the grave by dark magic or created in biological warfare gone wrong. They are slow but hard to kill and have the advantage of not attracting the attention of other Immortui.'}
RACE['lacertolian'] = {'name': 'lacertolian', 'start map': (1, 2), 'start pos': (570, 655),
                       'perks': {'health': 20, 'magica': -10, 'hunger': 100, 'strength': 1, 'agility': 1, 'healing': 0.5, 'stamina regen': 2, 'armor': 20},
                        'description': 'The Lacertolians are a peaceful people who are expert mariners. They can go for long periods without eating, have naturally armored skin and are immune to venom.'}
RACE['miewdra'] = {'name': 'miewdra', 'start map': (1, 2), 'start pos': (570, 655),
                   'perks': {'health': -5, 'stamina': 50, 'magica': 10, 'agility': 1.5, 'armor': 4, 'stamina regen': 1},
                    'description': 'The Miewdra live near Arroshay\'s north pole. They are resistant to cold, have high stamina, and can run quickly.'}
RACE['mechanima'] = {'name': 'mechanima', 'start map': (1, 2), 'start pos': (570, 655),
                     'perks': {'health': 10, 'magica': -30, 'hunger': 0, 'strength': 2.5, 'agility': 0.2, 'stamina regen': 0.2, 'armor': 35},
                    'description': 'The Mechanima are the remnants of an advanced race who were driven into extinction who were able to preserve their souls in robot bodies. They are strong, naturally armored, immune to poison, and recharged by energy attacks. They do not need to eat, but can.'}
RACE['wraith'] = {'name': 'wraith', 'start map': (1, 2), 'start pos': (570, 655),
                       'perks': {'health': 200, 'stamina': 50, 'magica': 50, 'hunger': 0, 'strength': -0.8, 'healing': 2, 'magica regen': 2},
                        'description': 'Black wraiths are disembodied practitioners of dark magic. They are immune to unenchanted melee weapons, bullets, cannot eat, and can walk through walls when not carrying any weight.'}
RACE['spirit'] = {'name': 'spirit', 'start map': (1, 2), 'start pos': (570, 655),
                       'perks': {'health': 100, 'stamina': 60, 'magica': 120, 'hunger': 0, 'strength': -0.9, 'healing': 2, 'magica regen': 2.5},
                        'description': 'White wraiths are disembodied practitioners of white magic. They are immune to unenchanted melee weapons, bullets, cannot eat, and can walk through walls when not carrying any weight.'}
RACE['skeleton'] = {'name': 'skeleton', 'armor': 12, 'start map': (1, 2), 'start pos': (570, 655),
                    'perks': {'health': -50, 'stamina': -50, 'magica': 200, 'hunger': 0, 'strength': 1, 'healing': 4, 'stamina regen': 4, 'magica regen': 4},
                    'description': 'Skeletons are undead beings who are reanimated by magic. They cannot eat, and are immune to poison and magic attacks'}
RACE['osidinedragon'] = {'name': 'osidinedragon', 'armor': 20}
RACE['shakteledragon'] = {'name': 'shakteledragon', 'armor': 20}
RACE['elfdragon'] = {'name': 'elfdragon', 'armor': 20}
RACE['immortuidragon'] = {'name': 'immortuidragon', 'armor': 30}
RACE['lacertoliandragon'] = {'name': 'lacertoliandragon', 'armor': 40}
RACE['miewdradragon'] = {'name': 'miewdradragon', 'armor': 22}
RACE['mechanimadragon'] = {'name': 'mechanimadragon', 'armor': 40}
RACE['wraithdragon'] = {'name': 'wraithdragon', 'armor': 40}
RACE['spiritdragon'] = {'name': 'spiritdragon', 'armor': 40}
RACE['skeletondragon'] = {'name': 'skeletondragon', 'armor': 40}

BASIC_RACES = []
for race, value in RACE.items():
    if 'dragon' not in race:
        BASIC_RACES.append(value)

#TEST_INVENTORY = {'weapons': {}, 'hats': {}, 'tops': {}, 'bottoms': {}, 'gloves': {}, 'shoes': {}, 'items': {}, 'blocks': {}}
#slot = {'item type': 'weapons', 'name': 'sword', 'hp': 100, 'stack': 1, 'enchanted'}

EMPTY_INVENTORY = {'weapons': {}, 'hats': {}, 'tops': {}, 'bottoms': {}, 'gloves': {}, 'shoes': {}, 'items': {}, 'blocks': {}}
EMPTY_EQUIP = {'gender': 'female', 'race': 'osidine', 'hair': None, 'weapons': None, 'weapons2': None, 'head': {}, 'torso': {}, 'bottom': {}, 'feet': {}, 'gloves': {}, 0: {}, 1: {}, 2: {}, 3: {}, 4: {}, 5: {}, 6: {}}
DEFAULT_INVENTORIES = {}
DEFAULT_INVENTORIES['osidine'] = {'orange burlap shirt': 1, 'brown pants': 1, 'Guide to Arroshay':1, "Grandpa's house key":1}
DEFAULT_INVENTORIES['shaktele'] = {'blue burlap shirt': 1, 'brown pants': 1, 'Guide to Arroshay':1}
DEFAULT_INVENTORIES['elf'] = {'green burlap shirt': 1, 'brown pants': 1, 'Guide to Arroshay':1}
DEFAULT_INVENTORIES['lacertolian'] = {'red burlap shirt': 1, 'brown pants': 1, 'Guide to Arroshay':1}
DEFAULT_INVENTORIES['immortui'] = {'grey burlap shirt': 1, 'brown pants': 1, 'Guide to Arroshay':1}
DEFAULT_INVENTORIES['miewdra'] = {'light blue burlap shirt': 1, 'blue pants': 1, 'Guide to Arroshay':1}
DEFAULT_INVENTORIES['mechanima'] = {'Guide to Arroshay':1}
DEFAULT_INVENTORIES['spirit'] = {'Guide to Arroshay':1}
DEFAULT_INVENTORIES['skeleton'] = {'Guide to Arroshay':1}
DEFAULT_INVENTORIES['wraith'] = {'Guide to Arroshay':1}

ENCHANTMENTS = {}
ENCHANTMENTS['explosive'] = {'materials':{'gun powder':1, 'black crystal':1}, 'equip kind': ['weapons'], 'image': 3}
ENCHANTMENTS['fire spark'] = {'materials':{'flint':1, 'steel ingot':1, 'red crystal':1}, 'equip kind': ['weapons'], 'image': 0}
ENCHANTMENTS['electric spark'] = {'materials':{'dead rabbit':1, 'blue crystal':1, 'white crystal':1}, 'equip kind': ['weapons'], 'image': 1}
ENCHANTMENTS['dragon breath'] = {'materials':{'gun powder':1, 'red crystal':1, 'dragon spit':1}, 'equip kind': ['hats'], 'image': 7}
ENCHANTMENTS['reinforced health'] = {'materials':{'potion of major healing':1, 'red crystal':1}, 'equip kind': ['hats', 'tops', 'bottoms', 'gloves', 'shoes'], 'image': 4}
ENCHANTMENTS['reinforced stamina'] = {'materials':{'potion of major stamina':1, 'blue crystal':1}, 'equip kind': ['hats', 'tops', 'bottoms', 'gloves', 'shoes'], 'image': 5}
ENCHANTMENTS['reinforced magica'] = {'materials':{'potion of major magica':1, 'white crystal':1}, 'equip kind': ['hats', 'tops', 'bottoms', 'gloves', 'shoes'], 'image': 6}

#ENCHANTMENTS['dragon fire '] = {'materials':{'red crystal':10}, 'equip kind': ['weapons'], 'image': 2}

# Defs used throughout all the files
def fix_inventory(container, kind = 'player'):
    if kind == 'player':
        slots = 36
    elif kind == 'chest':
        slots = 36
    else:
        slots = 9
    new_inventory = []
    for i in range(0, slots):
        new_inventory.append({})

    if kind == 'chest':
        inventory = container['inventory']
    else:
        inventory = container

    i = 0
    for key, value in inventory.items():
        new_inventory[i] = ITEMS[key].copy()
        if 'number' in ITEMS[key]:
            new_inventory[i]['number'] = value
        i += 1

    if kind != 'chest':
        return new_inventory

    else:
        new_container = container.copy()
        new_container['inventory'] = new_inventory
        return new_container
