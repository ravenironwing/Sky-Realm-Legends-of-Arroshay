# The larger the difficulty the easier the lock is to pick. It's just how far off you can be from the actual value.
# The combo is just an angle from 0 to 360.

# Chest contents
EMPTY_CHEST = {'name': 'chest', 'map': '0.tmx', 'locked': False, 'combo': None, 'difficulty': 0, 'inventory': {}}
CHESTS = {}
#CHESTS[(568, 648)] = {'name': "Grandpa's chest", 'map': '15', 'locked': False, 'combo': None, 'difficulty': 0, 'inventory': {'weapons': {'pistol':1, 'shotgun':1, 'assault rifle':1, 'mini gun':1, 'lantern':1}, 'hats': {}, 'tops': {}, 'bottoms': {}, 'gloves': {}, 'shoes': {}, 'items': {'lock pick':5, 'gold':100, 'fireball tome':1, 'summon rabbit tome':1, 'elementary healing tome':1}, 'blocks': {}}}
#CHESTS[(574, 671)] = {'name': "abandoned chest", 'map': '15', 'locked': True, 'combo': 90, 'difficulty': 5, 'inventory': {'weapons': {}, 'hats': {}, 'tops': {}, 'bottoms': {}, 'gloves': {}, 'shoes': {}, 'items': {'iron ingot': 40, 'steel ingot': 40, 'aluminum ingot': 40, 'brass ingot': 40, 'lead ingot': 20, 'gold ingot': 40, 'red crystal':6, 'white crystal': 6, 'blue crystal':7, 'flint and steel':2, 'gun powder':3, 'black crystal':3, 'flint':5, 'dead rabbit':1, 'dragon spit':5, 'potion of major healing':5, 'potion of major stamina':5, 'potion of major magica':5, 'potion of feminization': 1, 'potion of masculinization':1, 'garlic':10, 'yarrow':10, 'empty bottle':10}, 'blocks': {'anvil':1}}}
CHESTS[(568, 648)] = {'name': "Grandpa's chest", 'map': '15', 'locked': False, 'combo': None, 'difficulty': 0, 'inventory': {'copper ingot': 10, 'leather strips': 10, 'flint': 2}}
