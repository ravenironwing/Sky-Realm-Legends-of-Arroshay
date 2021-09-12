# The larger the difficulty the easier the lock is to pick. It's just how far off you can be from the actual value.
# The combo is just an angle from 0 to 360.

# Chest contents
EMPTY_CHEST = {'name': 'chest', 'map': '0.tmx', 'locked': False, 'combo': None, 'difficulty': 0, 'inventory': {'weapons': {}, 'hats': {}, 'tops': {}, 'bottoms': {}, 'gloves': {}, 'shoes': {}, 'items': {}, 'blocks': {}}}
CHESTS = {}
CHESTS[(568, 648)] = {'name': "Grandpa's chest", 'map': '15', 'locked': False, 'combo': None, 'difficulty': 0, 'inventory': {'weapons': {}, 'hats': {}, 'tops': {}, 'bottoms': {}, 'gloves': {}, 'shoes': {}, 'items': {'lock pick': 5, 'gold': 100}, 'blocks': {}}}
CHESTS[(574, 671)] = {'name': "abandoned chest", 'map': '15', 'locked': True, 'combo': 90, 'difficulty': 5, 'inventory': {'weapons': {}, 'hats': {}, 'tops': {}, 'bottoms': {}, 'gloves': {}, 'shoes': {}, 'items': {'iron ingot': 40, 'steel ingot': 40, 'aluminum ingot': 40, 'brass ingot': 40, 'lead ingot': 20, 'gold ingot': 40}, 'blocks': {'anvil':1}}}
