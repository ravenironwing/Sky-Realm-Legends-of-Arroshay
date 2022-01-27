from color_palettes import MATERIALS

lg = 'logs'
p = 'wood plank'
b = 'brick'
ls = 'leather strips'
l = 'leather'
st = 'stick'
f = 'flint'
CRAFTING_RECIPIES = {}
CRAFTING_RECIPIES['log wall'] = [2, lg, lg, 0,
                                         lg, lg, 0,
                                         lg, lg]

CRAFTING_RECIPIES['brick wall'] = [1, b, b, 0,
                                         b, b, 0,
                                         b, b]
CRAFTING_RECIPIES['flint axe'] = [1, f, 0,
                                  0, ls, 0,
                                  0, st]


WORKBENCH_RECIPIES = {}
WORKBENCH_RECIPIES['wood plank'] = [4, lg]
WORKBENCH_RECIPIES['wood floor'] = [2, p, p, p,
                                      p, p, p,
                                      p, p, p]
WORKBENCH_RECIPIES['chest'] = [1, p, p, p,
                                      p, 0, p,
                                      p, p, p]
WORKBENCH_RECIPIES['wooden armor'] = [1, p, 0, p,
                                      ls, p, ls,
                                      0, p, 0]

FORGING_RECIPIES = {}
for material in MATERIALS:
    x = material + ' ingot'
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

ENCHANTING_RECIPIES = {}
SMELTING_RECIPIES = {}
TANNING_RECIPIES = {}
GRINDER_RECIPIES = {}
COOKING_RECIPIES = {}
ALCHEMY_RECIPIES = {}

# Simply change out the recipie dictionary for different workstations.
RECIPIES = {'Crafting': CRAFTING_RECIPIES, 'Work Bench': WORKBENCH_RECIPIES, 'Anvil': FORGING_RECIPIES, 'Enchanter': ENCHANTING_RECIPIES, 'Smelter': SMELTING_RECIPIES, 'Tanning Rack': TANNING_RECIPIES, 'Grinder': GRINDER_RECIPIES, 'Cooking Fire': COOKING_RECIPIES, 'Alchemy Lab': ALCHEMY_RECIPIES}
