"""Shared values for FoodDishes12 (meters, front = -Y, origin = bottom centre).
Dishes sit in KitchenWare09 containers, appended from Models/<Container>/v001; the container may be scaled per dish.
Read by draw_food_sheets.py (design sheets) and build_food_dishes12.py (Blender models).
"""

NAMES = {'RiceBowl': '白米飯', 'NoodleSoup': '湯麵', 'SteamedBuns': '蒸籠包子', 'SteamedFish': '清蒸魚',
         'StirFryGreens': '炒青菜', 'BraisedPork': '紅燒肉'}

DETAILS = {
    'RiceBowl': 'Domed mound of white rice in the KitchenWare09 stoneware bowl.',
    'NoodleSoup': 'Large noodle bowl (bowl scaled 1.35x): broth, swirled noodles, two pork slices, half egg, greens, scallion rings and resting chopsticks.',
    'SteamedBuns': 'Bottom tier of the KitchenWare09 bamboo steamer holding seven pleated steamed buns.',
    'SteamedFish': 'Whole steamed fish on an oval plate (plate scaled 1.6 x 1.05) in light soy sauce with scallion and ginger shreds.',
    'StirFryGreens': 'Heap of stir-fried bok choy leaves and stems with garlic on the stoneware plate.',
    'BraisedPork': 'Glossy braised pork belly cubes in sauce, stacked in the stoneware bowl, with scallion.',
}

# Container per dish: (asset, scale (x, y, z), object-name prefixes to skip when appending)
CONTAINERS = {
    'RiceBowl': ('CeramicBowl', (1, 1, 1), ()),
    'NoodleSoup': ('CeramicBowl', (1.35, 1.35, 1.25), ()),
    'SteamedBuns': ('BambooSteamer', (1, 1, 1), ('Tier_2', 'Lid')),
    'SteamedFish': ('CeramicPlate', (1.6, 1.05, 1), ()),
    'StirFryGreens': ('CeramicPlate', (1, 1, 1), ()),
    'BraisedPork': ('CeramicBowl', (1, 1, 1), ()),
}

# Inner surfaces of the unscaled containers (radius, height), rim to centre; from KitchenWare09 kitchen_specs.
BOWL_INNER = [(.0765, .0715), (.073, .060), (.064, .044), (.050, .028), (.032, .016), (0, .013)]
PLATE_INNER = [(.117, .030), (.098, .022), (.062, .012), (0, .010)]
STEAMER_FLOOR_Z, STEAMER_INNER_R = .025, .188

SPECS = {
    'RiceBowl': {'mound_top': .098, 'mound_base_z': .060},
    'NoodleSoup': {'broth_z': .052, 'noodle_r': .0028, 'egg_r': .022, 'chopstick_len': .24},
    'SteamedBuns': {'bun_r': .046, 'bun_h': .045, 'ring_r': .112, 'count': 7},
    'SteamedFish': {'length': .30, 'height': .055, 'width': .085, 'sauce_r': (.15, .095)},
    'StirFryGreens': {'leaves': 14, 'heap_h': .06},
    'BraisedPork': {'cube': .03, 'count': 9, 'sauce_z': .046},
}

# Table preview: the KitchenWare09 dining table set with one of each dish.
TABLE_SETTING = [('SteamedBuns', (-.27, .27)), ('NoodleSoup', (.30, .28)), ('RiceBowl', (.10, .30)), ('SteamedFish', (.05, -.08)),
                 ('StirFryGreens', (.34, -.33)), ('BraisedPork', (-.30, -.30)), ('RiceBowl', (-.38, -.02))]
