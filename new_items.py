import pygame as pg
from color_palettes import *
from chests import *
vec = pg.math.Vector2

# Weapon settings
BULLET_SIZES = ['sm', 'md', 'lg', 'xl', 'ar']
ENCHANTED_BULLETS = ['2', '3', '5', '6', '7', '8', '9', '12']
ROB_HEALTH_BULLETS = ['12']
FIRE_BULLETS = ['3', '5', '6', '9']
SHOCK_BULLETS = ['2', '7', '8', '9']
EXPLOSIVE_BULLETS = ['4', '5', '8', '10', '0']
ENCHANTED_OFFSET = vec(19, 0)

WEAPON_SOUNDS = {'shovel': ['mace_swipe.ogg'], 'pistol': ['pistol.ogg'], 'laser': ['laser.ogg'], 'grenades': ['shotgun.ogg'], 'pickaxe': ['mace_swipe.ogg'], 'axe': ['mace_swipe.ogg'], 'plasma': ['plasma_swipe.ogg', 'plasma_swipe2.ogg'],
                 'shotgun': ['shotgun.ogg'], 'rifle': ['assault rifle.ogg'], 'turret': ['turret.ogg'], 'sword': ['sword_swipe.ogg'], 'mace': ['mace_swipe.ogg'], 'dagger': ['sword_swipe.ogg'], 'shield': ['mace_swipe.ogg'], 'bow': ['arrow.ogg']}
WEAPON_HIT_SOUNDS = {'pistol': ['gun_hit1.ogg'], 'laser': ['gun_hit1.ogg'], 'grenades': ['shotgun.ogg'], 'pickaxe': ['pickaxe.ogg'], 'axe': ['axe.ogg'], 'shovel': ['rock_hit.ogg'],
                 'shotgun': ['gun_hit1.ogg'], 'rifle': ['gun_hit1.ogg'], 'turret': ['turret_hit1.ogg'], 'sword': ['sword_hit1.ogg'], 'mace': ['mace_hit1.ogg', 'mace_hit2.ogg'], 'dagger': ['sword_hit1.ogg'], 'shield': ['punch1.ogg', 'punch2.ogg'], 'bow': ['punch1.ogg', 'punch2.ogg'], 'plasma': ['plasma_hit.ogg', 'plasma_hit2.ogg']}
WEAPON_RELOAD_SOUNDS = {'axe': 'mace_swipe.ogg', 'sword': 'sword_draw.ogg', 'dagger': 'sword_swipe.ogg', 'pickaxe': 'mace_swipe.ogg', 'shotgun': 'gun_pickup.ogg', 'pistol': 'gun_pickup.ogg', 'rifle': 'gun_pickup.ogg', 'laser': 'gun_pickup.ogg', 'bow': 'sword_swipe.ogg'}
WEAPON_TYPES = ['axe', 'sword', 'dagger', 'pickaxe', 'shotgun', 'pistol', 'rifle', 'laser', 'bow']


SHARP_WEAPON_TYPES = ['axe', 'sword', 'dagger', 'pickaxe']
EQUIP_TYPES = WEAPON_TYPES + ['head', 'torso', 'gloves', 'feet', 'bottom']
WEAPON_GRIPS = {'axe': 'CP_SWORD_GRIP', 'sword': 'CP_SWORD_GRIP', 'dagger': 'CP_SWORD_GRIP', 'pickaxe': 'CP_SWORD_GRIP', 'shotgun': 'CP_SHOTGUN0', 'rifle': 'CP_SHOTGUN0', 'pistol': 'CP_PISTOL0', 'bow': 'BOWWALK0', 'laser': 'CP_PISTOL0'}
WEAPON_WALKS = {'axe': 'WALK', 'sword': 'WALK', 'dagger': 'WALK', 'pickaxe': 'WALK', 'shotgun': 'SHOTGUN_WALK', 'rifle': 'SHOTGUN_WALK', 'pistol': 'PISTOL_WALK', 'bow': 'BOW_WALK', 'laser': 'PISTOL_WALK'}
WEAPON_MELEE_ANIM = {'axe': 'SWIPE', 'sword': 'PUNCH', 'dagger': 'PUNCH', 'pickaxe': 'SWIPE', 'shotgun': 'SWIPE', 'rifle': 'SWIPE', 'pistol': 'PUNCH', 'bow': 'SWIPE', 'laser': 'SWIPE'}
GUN_LIST = ['pistol', 'shotgun', 'rifle', 'laser']

#ITEMS, weapons, armor, etc.
ITEMS = {}

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

# Guns
# Optional parameters: bullet_lifetime
ITEMS['double barrel shotgun'] = {'name': 'double barrel shotgun', 'type': 'shotgun',
                      'hp': 1000, 'max hp': 1000,
                      'bullet_speed': 200,
                      'magazine size': 2,
                      'reload speed': 150,
                      'rate': 100,
                      'auto': False,
                      'kickback': 50,
                      'knockback': 0.5,
                      'spread': 20,
                      'shot damage': 25,
                      'damage': 3,
                      'bullet_size': 'sm1',
                      'bullet_count': 12,
                      'offset': vec(29, 0),
                      'weight': 2.7}

ITEMS['Barlita M92'] = {'name': 'Barlita M92', 'type': 'pistol',
                     'bullet_speed': 250,
                     'magazine size': 6,
                     'reload speed': 100,
                     'rate': 250,
                     'auto': False,
                     'kickback': 5,
                     'knockback': 0.2,
                     'spread': 5,
                     'shot damage': 10,
                     'damage': 2,
                     'bullet_size': 'md1',
                     'bullet_count': 1,
                     'offset': vec(14, 0),
                     'weight': 1.4}

ITEMS['HJ416'] = {'name': 'HJ416', 'type': 'rifle',
                      'bullet_speed': 350,
                      'bullet_lifetime': 700,
                      'magazine size': 30,
                      'reload speed': 160,
                      'rate': 100,
                      'auto': True,
                      'kickback': 0.4,
                      'knockback': 5,
                      'spread': 7,
                      'shot damage': 12,
                      'damage': 3,
                      'bullet_size': 'sm1',
                      'bullet_count': 1,
                      'offset': vec(29, 0),
                      'weight': 2.9}

for color in CLOTHING_COLORS:
    ITEMS[color + ' pants'] = {'name': color + ' pants', 'type': 'bottom', 'armor': 3, 'hp': 100, 'max hp': 100, 'color': CLOTHING_COLORS[color]}
    ITEMS[color + ' tshirt'] = {'name': color + ' tshirt', 'type': 'torso','armor': 1, 'hp': 100, 'max hp': 100, 'color': CLOTHING_COLORS[color]}
    ITEMS[color + ' burlap shirt'] = {'name': color + ' burlap shirt', 'type': 'torso','armor': 0.5, 'hp': 50, 'max hp': 50, 'color': CLOTHING_COLORS[color]}

for color in BOOT_COLORS:
    ITEMS[color + ' boots'] = {'name': color + ' boots', 'type': 'feet','armor': 2, 'hp': 100, 'max hp': 100, 'color': CLOTHING_COLORS[color]}

for color in CRYSTAL_COLORS:
    ITEMS[color + ' crystal'] = {'name': color + ' crystal', 'type': 'crystals', 'color': color, 'number': 1, 'max stack': 32}

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
ITEMS['palm branch'] ={'name': 'palm branch', 'type': 'item', 'number': 1, 'max stack': 32}
ITEMS['wood plank'] = {'name': 'wood plank', 'type': 'item', 'number': 1, 'max stack': 32}
ITEMS['brick'] = {'name': 'brick', 'type': 'item', 'number': 1, 'max stack': 32}

# Books
ITEMS['Guide to Arroshay'] = {'name': 'Guide to Arroshay', 'type': 'book', 'author': 'King Prefect', 'heading': "Guide to Arroshay", 'font': 'SCRIPT_FONT', 'number': 1, 'max stack': 16, 'color': BROWN}
ITEMS['War of the Worlds'] = {'name': 'War of the Worlds', 'type': 'book', 'author': 'H. G. Wells', 'heading': 'War of the Worlds', 'font': 'SCRIPT_FONT', 'number': 1, 'max stack': 16, 'color': ORANGE}

# Blocks
ITEMS['chest'] = {'name': 'chest', 'type': 'block', 'layer': 'river', 'number': 1, 'max stack': 32}
ITEMS['brick wall'] = {'name': 'brick wall', 'type': 'block',  'layer': 'base', 'number': 1, 'max stack': 32}
ITEMS['log wall'] = {'name': 'log wall', 'type': 'block',  'layer': 'base', 'number': 1, 'max stack': 32}
ITEMS['log corner post'] = {'name': 'log corner post', 'type': 'block', 'layer': 'base', 'number': 1, 'max stack': 32}
ITEMS['wood floor'] = {'name': 'wood floor', 'type': 'block', 'layer': 'base', 'number': 1, 'max stack': 32}
ITEMS['wood counter'] = {'name': 'wood counter', 'type': 'block', 'layer': 'ocean_plants', 'number': 1, 'max stack': 32}
ITEMS['work bench'] = {'name': 'work bench', 'type': 'block', 'layer': 'ocean_plants', 'number': 1, 'max stack': 32}
ITEMS['anvil'] = {'name': 'anvil', 'type': 'block', 'layer':  'ocean_plants', 'number': 1, 'max stack': 32}
ITEMS['fire pit'] = {'name': 'fire pit', 'type': 'block', 'layer':'river', 'number': 1, 'max stack': 32}
ITEMS['thatch roof'] = {'name': 'thatch roof', 'type': 'block', 'layer': 'trees', 'number': 1, 'max stack': 32}
ITEMS['logs'] = {'name': 'logs', 'type': 'block', 'layer': 'river', 'number': 1, 'max stack': 32}
ITEMS['closed wood door'] = {'name': 'closed wood door', 'type': 'block', 'layer': 'ocean_plants', 'number': 1, 'max stack': 32} #Ocean plants is the rounded corners layer as well.

# Harvestables
# rose is in colored items
for color in FLOWER_COLORS:
    ITEMS[color + ' rose'] = {'name': color + ' rose', 'type': 'harvestable', 'color': color, 'number': 1, 'max stack': 32}
ITEMS['cactus'] = {'name': 'cactus', 'type': 'harvestable', 'number': 1, 'max stack': 32}
ITEMS['seaweed'] = {'name': 'seaweed', 'type': 'harvestable', 'number': 1, 'max stack': 32}
ITEMS['zhe buds'] = {'name': 'zhe buds', 'type': 'harvestable', 'number': 1, 'max stack': 32}
ITEMS['marra leaf'] = {'name': 'marra leaf', 'type': 'harvestable', 'number': 1, 'max stack': 32}
ITEMS['dry brush'] = {'name': 'stick', 'type': 'item', 'number': 2, 'max stack': 32} # There is not actually a dry brush item. But harvesting it gives you sticks.
ITEMS['branches'] = {'name': 'stick', 'type': 'item', 'number': 3, 'max stack': 32} # There is not actually a dry brush item. But harvesting it gives you sticks.
ITEMS['palm branches'] = {'name': 'palm branch', 'type': 'item', 'number': 3, 'max stack': 32} # There is not actually a dry brush item. But harvesting it gives you sticks.
ITEMS['dry grass'] ={'name': 'dry grass', 'type': 'harvestable', 'number': 1, 'max stack': 32}
ITEMS['cattails'] = {'name': 'cattails', 'type': 'harvestable', 'number': 1, 'max stack': 32}
ITEMS['blueberries'] = {'name': 'blueberries', 'type': 'harvestable', 'number': 1, 'max stack': 32}
ITEMS['sage'] = {'name': 'sage', 'type': 'harvestable', 'number': 1, 'max stack': 32}

ITEMS['flint'] = {'name': 'flint', 'type': 'item', 'number': 1, 'max stack': 32}

# Generates keys for all chests
for chest in CHESTS:
    key_name = CHESTS[chest]['name'] + " key"
    ITEMS[key_name] = {'name': key_name, 'type': 'key'}

# Generates keys for all doors
for door in DOORS:
    key_name = DOORS[door]['name'] + " key"
    ITEMS[key_name] = {'name': key_name, 'type': 'key'}

ITEMS['lock pick'] = {'name': 'lock pick', 'type': 'item', 'hp': 10, 'max hp': 10}

ITEMS['live rabbit'] = {'name': 'live rabbit', 'type': 'animal'}
ITEMS['dead rabbit'] = {'name': 'dead rabbit', 'type': 'item', 'number': 1, 'max stack': 16}
ITEMS['roasted rabbit'] = {'name': 'roasted rabbit', 'type': 'food', 'number': 1, 'max stack': 16, 'health': 18, 'stamina': 25, 'hunger': 20}

# Lights
ITEMS['candle'] = {'name': 'candle', 'type': 'item', 'brightness': 150, 'light mask': 1, 'hp': 100, 'max hp': 100, 'side view': False}
ITEMS['lantern'] = {'name': 'lantern', 'type': 'item', 'brightness': 200, 'light mask': 2, 'hp': 100, 'max hp': 100, 'side view': False}

LIGHTS_LIST = []
for x in ITEMS:
    if 'brightness' in ITEMS[x]:
        LIGHTS_LIST.append(x)

FLOAT_LIST = []
for x in ITEMS:
    if 'floats' in ITEMS[x]:
        FLOAT_LIST.append(x)
