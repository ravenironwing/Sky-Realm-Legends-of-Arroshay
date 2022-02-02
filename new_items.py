import pygame as pg
from color_palettes import *
from chests import *
vec = pg.math.Vector2

ITEMS = {}

WEAPON_TYPES = ['axe', 'sword', 'dagger', 'pickaxe']
EQUIP_TYPES = WEAPON_TYPES + ['head', 'torso', 'gloves', 'feet', 'bottom']
WEAPON_GRIPS = {'axe': 'CP_SWORD_GRIP', 'sword': 'CP_SWORD_GRIP', 'dagger': 'CP_SWORD_GRIP', 'pickaxe': 'CP_SWORD_GRIP'}
WEAPON_WALKS = {'axe': 'WALK', 'sword': 'WALK', 'dagger': 'WALK', 'pickaxe': 'WALK'}
WEAPON_MELEE_ANIM = {'axe': 'SWIPE', 'sword': 'PUNCH', 'dagger': 'PUNCH', 'pickaxe': 'SWIPE'}
GUN_LIST = ['hand gun', 'shotgun', 'rifle', 'laser']
ITEM_SIZE = 20 # Size items are displayed in world.

for material in MATERIALS:
    # Weapons
    """
    ITEMS[material + ' dagger'] = {'name': material + ' dagger', 'type': 'sword',
                                       'damage': 18 * MATERIALS[material]['hardness'],
                                       'weight': 1 * MATERIALS[material]['weight'],
                                       'hp': 1000 * MATERIALS[material]['hardness'],
                                       'max hp': 1000 * MATERIALS[material]['hardness'],
                                       'color': MATERIALS[material]['color']}
    ITEMS[material + ' longsword'] = {'name': material + ' longsword', 'type': 'sword',
                                       'damage': 45 * MATERIALS[material]['hardness'],
                                      'weight': 5 * MATERIALS[material]['weight'],
                                       'hp': 1000 * MATERIALS[material]['hardness'],
                                       'max hp': 1000 * MATERIALS[material]['hardness'],
                                       'color': MATERIALS[material]['color']}"""
    ITEMS[material + ' broadsword'] = {'name': material + ' broadsword', 'type': 'sword',
                                       'damage': 25 * MATERIALS[material]['hardness'],
                                       'weight': 4 * MATERIALS[material]['weight'],
                                       'hp': 1000 * MATERIALS[material]['hardness'],
                                       'max hp': 1000 * MATERIALS[material]['hardness'],
                                       'color': MATERIALS[material]['color']}
    ITEMS[material + ' axe'] = {'name': material + ' axe', 'type': 'axe',
                                'damage': 15 * MATERIALS[material]['hardness'],
                                'weight': 7 * MATERIALS[material]['weight'],
                                'hp': 1000 * MATERIALS[material]['hardness'],
                                'max hp': 1000 * MATERIALS[material]['hardness'],
                                'color': MATERIALS[material]['color']}
    ITEMS[material + ' pickaxe'] = {'name': material + ' pickaxe', 'type': 'pickaxe',
                                'damage': 15 * MATERIALS[material]['hardness'],
                                'weight': 8 * MATERIALS[material]['weight'],
                                'hp': 1000 * MATERIALS[material]['hardness'],
                                'max hp': 1000 * MATERIALS[material]['hardness'],
                                    'color': MATERIALS[material]['color']}
    # Armor
    ITEMS[material + ' helmet'] = {'name': material + ' helmet', 'type': 'head',
                                   'armor': 25 * MATERIALS[material]['hardness'],
                                   'hp': 1000 * MATERIALS[material]['hardness'],
                                   'max hp': 1000 * MATERIALS[material]['hardness'],
                                   'color': MATERIALS[material]['color']}
    ITEMS[material + ' armor'] = {'name': material + ' armor', 'type': 'torso',
                                  'armor': 25 * MATERIALS[material]['hardness'],
                                  'hp': 1000 * MATERIALS[material]['hardness'],
                                  'max hp': 1000 * MATERIALS[material]['hardness'],
                                  'color': MATERIALS[material]['color']}
    ITEMS[material + ' gauntlets'] = {'name': material + ' gauntlets', 'type': 'gloves',
                                      'armor': 25 * MATERIALS[material]['hardness'],
                                      'hp': 1000 * MATERIALS[material]['hardness'],
                                      'max hp': 1000 * MATERIALS[material]['hardness'],
                                      'color': MATERIALS[material]['color']}
    ITEMS[material + ' leg armor'] = {'name': material + ' leg armor', 'type': 'bottom',
                                      'armor': 25 * MATERIALS[material]['hardness'],
                                      'hp': 1000 * MATERIALS[material]['hardness'],
                                      'max hp': 1000 * MATERIALS[material]['hardness'],
                                      'color': MATERIALS[material]['color']}
    ITEMS[material + ' plated boots'] = {'name': material + ' plated boots', 'type': 'feet',
                                  'armor': 25 * MATERIALS[material]['hardness'],
                                  'hp': 1000 * MATERIALS[material]['hardness'],
                                  'max hp': 1000 * MATERIALS[material]['hardness'],
                                  'color': MATERIALS[material]['color']}
    # Ores and Ingots
    ITEMS[material + ' ingot'] = {'name': material + ' ingot', 'type': 'ingot', 'number': 1, 'max stack': 32, 'color': MATERIALS[material]['color']}
    ITEMS[material + ' cast block'] = {'name': material + ' cast block', 'type': 'ingot', 'number': 1, 'max stack': 10, 'color': MATERIALS[material]['color']}
    ITEMS[material + ' cube wall'] = {'name': material + ' cube wall', 'type': 'ingot', 'number': 1, 'max stack': 4, 'color': MATERIALS[material]['color']}
    ITEMS[material + ' ore'] = {'name': material + ' ore', 'type': 'ore', 'number': 1, 'max stack': 16, 'color': MATERIALS[material]['color']}

ITEMS['wooden armor'] = {'name': 'wooden armor', 'type': 'torso', 'armor': 15, 'hp': 150, 'max hp': 150}
ITEMS['flint axe'] = {'name': 'flint axe', 'type': 'axe',
                            'damage': 10,
                            'weight': 4,
                            'hp': 80,
                            'max hp': 80}

for color in CLOTHING_COLORS:
    ITEMS[color + ' pants'] = {'name': color + ' pants', 'type': 'bottom', 'armor': 3, 'hp': 100, 'max hp': 100, 'color': CLOTHING_COLORS[color]}
    ITEMS[color + ' tshirt'] = {'name': color + ' tshirt', 'type': 'torso','armor': 1, 'hp': 100, 'max hp': 100, 'color': CLOTHING_COLORS[color]}
    ITEMS[color + ' burlap shirt'] = {'name': color + ' burlap shirt', 'type': 'torso','armor': 0.5, 'hp': 50, 'max hp': 50, 'color': CLOTHING_COLORS[color]}

for color in BOOT_COLORS:
    ITEMS[color + ' boots'] = {'name': color + ' boots', 'type': 'feet','armor': 2, 'hp': 100, 'max hp': 100, 'color': CLOTHING_COLORS[color]}

for color in CRYSTAL_COLORS:
    ITEMS[color + ' crystal'] = {'name': color + ' crystal', 'type': 'crystals', 'color': color, 'number': 1, 'max stack': 32, 'leather': 10}

POTIONS = {}
POTIONS['potion of minor healing'] = {'health': 20, 'color': PINK}
POTIONS['potion of moderate healing'] = {'health': 40, 'color': MAGENTA}
POTIONS['potion of major healing'] = {'health': 75, 'color': RED}
POTIONS['potion of minor magica'] = {'magica': 20, 'color': LIGHT_BLUE}
POTIONS['potion of moderate magica'] = {'magica': 40, 'color': BABY_BLUE}
POTIONS['potion of major magica'] = {'magica': 75, 'color': DARK_BLUE}
POTIONS['potion of minor stamina'] = {'stamina': 20, 'color': CYAN}
POTIONS['potion of moderate stamina'] = {'stamina': 40, 'color': GREEN}
POTIONS['potion of major stamina'] = {'stamina': 75, 'color': DARK_GREEN}
for potion in POTIONS:
    temp_dict = {'name': potion, 'number': 1, 'max stack': 16, 'type': 'potion'}
    ITEMS[potion] = POTIONS[potion]
    ITEMS[potion].update(temp_dict)

ITEMS['empty bottle'] = {'name': 'empty bottle', 'type': 'item', 'number': 1, 'max stack': 16}

ITEMS['leather'] = {'name': 'leather', 'type': 'item', 'number': 1, 'max stack': 16}
ITEMS['leather strips'] = {'name': 'leather strips', 'type': 'item', 'number': 1, 'max stack': 32}
ITEMS['stick'] = {'name': 'stick', 'type': 'item', 'number': 1, 'max stack': 32}
ITEMS['wood plank'] = {'name': 'wood plank', 'type': 'item', 'number': 1, 'max stack': 32}
ITEMS['brick'] = {'name': 'brick', 'type': 'item', 'number': 1, 'max stack': 32}

# Books
ITEMS['Guide to Arroshay'] = {'name': 'Guide to Arroshay', 'type': 'book', 'author': 'King Prefect', 'heading': "Guide to Arroshay", 'font': 'SCRIPT_FONT', 'number': 1, 'max stack': 16, 'color': BROWN}
ITEMS['War of the Worlds'] = {'name': 'War of the Worlds', 'type': 'book', 'author': 'H. G. Wells', 'heading': 'War of the Worlds', 'font': 'SCRIPT_FONT', 'number': 1, 'max stack': 16, 'color': ORANGE}

# Blocks
ITEMS['chest'] = {'name': 'chest', 'type': 'block', 'layer': 'self.game.map.river_layer', 'number': 1, 'max stack': 32}
ITEMS['brick wall'] = {'name': 'brick wall', 'type': 'block',  'layer': 'self.game.map.base_layer', 'number': 1, 'max stack': 32}
ITEMS['log wall'] = {'name': 'log wall', 'type': 'block',  'layer': 'self.game.map.base_layer', 'number': 1, 'max stack': 32}
ITEMS['log corner post'] = {'name': 'log corner post', 'type': 'block', 'layer': 'self.game.map.base_layer', 'number': 1, 'max stack': 32}
ITEMS['wood floor'] = {'name': 'wood floor', 'type': 'block', 'layer': 'self.game.map.base_layer', 'number': 1, 'max stack': 32}
ITEMS['wood counter'] = {'name': 'wood counter', 'type': 'block', 'layer': 'self.game.map.ocean_plants_layer', 'number': 1, 'max stack': 32}
ITEMS['work bench'] = {'name': 'work bench', 'type': 'block', 'layer': 'self.game.map.ocean_plants_layer', 'number': 1, 'max stack': 32}
ITEMS['anvil'] = {'name': 'anvil', 'type': 'block', 'layer':  'self.game.map.ocean_plants_layer', 'number': 1, 'max stack': 32}
ITEMS['fire pit'] = {'name': 'fire pit', 'type': 'block', 'layer':'self.game.map.river_layer', 'number': 1, 'max stack': 32}
#ITEMS['thatch roof'] = {'name': 'thatch roof', 'type': 'block', 'layer': 'self.game.map.trees_layer', 'number': 1, 'max stack': 32}
ITEMS['logs'] = {'name': 'logs', 'type': 'block', 'layer': 'self.game.map.river_layer', 'number': 1, 'max stack': 32}

# Harvestables
# rose is in colored items
for color in FLOWER_COLORS:
    ITEMS[color + ' rose'] = {'name': color + ' rose', 'type': 'harvestable', 'color': color, 'number': 1, 'max stack': 32}
ITEMS['cactus'] = {'name': 'cactus', 'type': 'harvestable', 'number': 1, 'max stack': 32}
ITEMS['seaweed'] = {'name': 'seaweed', 'type': 'harvestable', 'number': 1, 'max stack': 32}
ITEMS['zhe buds'] = {'name': 'zhe buds', 'type': 'harvestable', 'number': 1, 'max stack': 32}
ITEMS['marra leaf'] = {'name': 'marra leaf', 'type': 'harvestable', 'number': 1, 'max stack': 32}
ITEMS['dry brush'] = {'name': 'stick', 'type': 'item', 'number': 2, 'max stack': 32} # There is not actually a dry brush item. But harvesting it gives you sticks.
ITEMS['dry grass'] ={'name': 'dry grass', 'type': 'harvestable', 'number': 1, 'max stack': 32}
ITEMS['cattails'] = {'name': 'cattails', 'type': 'harvestable', 'number': 1, 'max stack': 32}
ITEMS['blueberries'] = {'name': 'blueberries', 'type': 'harvestable', 'number': 1, 'max stack': 32}
ITEMS['sage'] = {'name': 'sage', 'type': 'harvestable', 'number': 1, 'max stack': 32}

ITEMS['flint'] = {'name': 'flint', 'type': 'item', 'number': 1, 'max stack': 32}

# Generates keys for all chests
for chest in CHESTS:
    key_name = CHESTS[chest]['name'] + " key"
    ITEMS[key_name] = {'name': key_name}

# Generates keys for all doors
for door in DOORS:
    key_name = DOORS[door]['name'] + " key"
    ITEMS[key_name] = {'name': key_name}

ITEMS['lock pick'] = {'name': 'lock pick', 'type': 'item', 'hp': 10, 'max hp': 10}
