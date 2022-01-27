from race_info import RACE_TYPE_LIST

HAIR = {}
HAIR['long pony'] = {'name': 'long pony', 'races': ['osidine', 'shaktele', 'elf'], 'gender': 'female'}
HAIR['long straight'] = {'name': 'long straight', 'races': ['osidine', 'shaktele', 'immortui'], 'gender': 'female'}
HAIR['long curly'] = {'name': 'long curly', 'races': ['osidine', 'shaktele'], 'gender': 'female'}
HAIR['medium messy'] = {'name': 'medium messy', 'races': ['osidine', 'shaktele', 'immortui'], 'gender': 'female'}
HAIR['long side pony'] = {'name': 'long side pony', 'races': ['osidine', 'shaktele', 'elf'], 'gender': 'female'}
HAIR['short messy'] = {'name': 'short messy', 'races': ['osidine', 'shaktele', 'immortui'], 'gender': 'female'}
HAIR['short'] = {'name': 'short', 'races': ['osidine', 'shaktele', 'elf', 'immortui'], 'gender': 'male'}
HAIR['short combed'] = {'name': 'short combed', 'races': ['osidine', 'shaktele', 'elf', 'immortui'], 'gender': 'male'}
HAIR['dreadlocks'] = {'name': 'dreadlocks', 'races': ['osidine', 'shaktele', 'immortui'], 'gender': 'other'}
HAIR['elf braids'] = {'name': 'elf braids', 'races': ['elf'], 'image': 9, 'gender': 'other'}
HAIR['lizard horns'] = {'name': 'lizard horns', 'races': ['lacertolian'], 'gender': 'other'}
HAIR['lizard spikes'] = {'name': 'lizard spikes', 'races': ['lacertolian', 'demon'], 'gender': 'other'}
HAIR['cat tufts'] = {'name': 'cat tufts', 'races': ['miewdra'], 'gender': 'other'}
HAIR['frizzy cat'] = {'name': 'frizzy cat', 'races': ['miewdra'], 'gender': 'other'}
HAIR['fluffy cat'] = {'name': 'fluffy cat', 'races': ['miewdra'], 'gender': 'other'}
HAIR['long straight cat'] = {'name': 'long straight cat', 'races': ['miewdra'], 'gender': 'female'}
HAIR['bald'] = {'name': 'bald', 'races': ['osidine', 'shaktele', 'elf', 'lacertolian', 'miewdra', 'immortui', 'wraith', 'spirit', 'skeleton', 'demon', 'vadashay'], 'gender': 'other'}
HAIR['ram horns'] = {'name': 'ram horns', 'races': ['skeleton', 'demon'], 'gender': 'other'}
HAIR['demon horns'] = {'name': 'demon horns', 'races': ['skeleton', 'demon'], 'gender': 'other'}
HAIR['short horns'] = {'name': 'short horns', 'races': ['skeleton', 'demon'], 'gender': 'other'}
HAIR['long wraith'] = {'name': 'long wraith', 'races': ['wraith', 'spirit'], 'gender': 'female'}
HAIR['back strip lights'] = {'name': 'back strip lights', 'races': ['mechanima'], 'gender': 'other'}
HAIR['two strip lights'] = {'name': 'two strip lights', 'races': ['mechanima'], 'gender': 'other'}
HAIR['bug lights'] = {'name': 'bug lights', 'races': ['mechanima'], 'gender': 'other'}
HAIR['basic lights'] = {'name': 'basic lights', 'races': ['mechanima'], 'gender': 'other'}
HAIR['LED skin'] = {'name': 'LED skin', 'races': ['mechanima'], 'gender': 'other'}
HAIR['light strips'] = {'name': 'light strips', 'races': ['mechanima'], 'gender': 'other'}
HAIR['LED stripes'] = {'name': 'LED stripes', 'races': ['mechanima'], 'gender': 'other'}
HAIR['beard'] = {'name': 'beard', 'races': ['osidine', 'shaktele', 'elf', 'immortui'], 'gender': 'male'}

# Makes a dictionary containing the hairstyles appropriate for each race.
#temp_race_list = ['demon', 'osidine', 'shaktele', 'elf', 'lacertolian', 'miewdra', 'immortui', 'mechanima', 'wraith', 'spirit', 'skeleton']
RACE_HAIR = {}
for race in RACE_TYPE_LIST:
    RACE_HAIR[race] = []
for item, value in HAIR.items():
    for race in RACE_TYPE_LIST:
        if race in HAIR[item]['races']:
            RACE_HAIR[race].append(value)

# Separates long and short hair styles into lists
SHORT_HAIR_LIST = []
MEDIUM_HAIR_LIST = []
LONG_HAIR_LIST = []
for item in HAIR:
    if ('osidine' in HAIR[item]['races']) or ('shaktele' in HAIR[item]['races']):
        if 'short' in item:
            SHORT_HAIR_LIST.append(item)
        if 'medium' in item:
            MEDIUM_HAIR_LIST.append(item)
        if 'long' in item:
            LONG_HAIR_LIST.append(item)