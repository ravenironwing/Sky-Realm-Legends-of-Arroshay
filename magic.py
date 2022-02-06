MAGIC = {}
MAGIC['healing'] = {'name': 'healing', 'type': 'magic', 'healing': 5, 'cost': 20, 'sound': 'casting healing'}
MAGIC['fireball'] = {'name': 'fireball', 'type': 'magic', 'fireballs': 1, 'damage': 30, 'cost': 20, 'sound': 'fire blast'}
MAGIC['fire spray'] = {'name': 'fire spray', 'type': 'magic', 'fireballs': 10, 'damage': 50, 'cost': 75, 'sound': 'fire blast'}
MAGIC['summon golem'] = {'name': 'summon golem', 'type': 'magic', 'summon': 'clay golem guard', 'cost': 25, 'materials': {'clay':4}, 'sound': 'fire blast'}
MAGIC['summon rabbit'] = {'name': 'summon rabbit', 'type': 'magic', 'summon': 'rabbit', 'cost': 5, 'sound': 'fire blast'}
MAGIC['demonic possession'] = {'name': 'demonic possesion', 'type': 'magic', 'possession': True, 'cost': 100, 'sound': 'fire blast'}