"""Shared values for FreshIngredients13 (meters, front = -Y, origin = bottom centre).
Some items reuse StreetProps11 containers appended from Models/<Container>/v001 under a scalable Container empty.
Read by draw_fresh_sheets.py (design sheets) and build_fresh13.py (Blender models).
"""

NAMES = {'RiceSack': '米袋', 'CuredMeatRack': '臘肉吊架', 'RadishCrate': '蘿蔔木箱', 'VegetableBasket': '蔬菜籃',
         'EggBasket': '蛋籃', 'FishTub': '鮮魚木盆'}

DETAILS = {
    'RiceSack': 'Hemp rice sack with wrinkled sides, rolled-down cuff, visible rice and a wooden scoop.',
    'CuredMeatRack': 'Small timber drying rack hung with cured pork belly strips and sausage links.',
    'RadishCrate': 'StreetProps11 crate without its lid, filled with white radishes and a few carrots.',
    'VegetableBasket': 'StreetProps11 bamboo basket cut down to a shallow basket (no straps) holding napa cabbage, carrots and scallions.',
    'EggBasket': 'Small shallow bamboo basket with a straw lining and a heap of eggs.',
    'FishTub': 'StreetProps11 stave bucket widened into a shallow tub (no bail) with water and three live fish.',
}

# Container per item: (asset, scale (x, y, z), object-name prefixes to skip). None = no container.
CONTAINERS = {
    'RiceSack': None, 'CuredMeatRack': None,
    'RadishCrate': ('WoodenCrate', (1, 1, 1), ('Lid_',)),
    'VegetableBasket': ('BambooBasket', (1.05, 1.05, .40), ('Shoulder_Strap',)),
    'EggBasket': ('BambooBasket', (.62, .62, .30), ('Shoulder_Strap',)),
    'FishTub': ('WellBucket', (1.7, 1.7, .65), ('Bucket_Rope_Bail',)),
}

# Unscaled container interiors (from StreetProps11 street_specs): floor height, inner radius / size at the rim.
BASKET = {'floor_z': .042, 'bottom_r': .138, 'top_r': .198, 'h': .55}
BUCKET = {'floor_z': .03, 'bottom_r': .111, 'top_r': .145, 'h': .30}
CRATE = {'floor_z': .024, 'inner': (.52, .37), 'h': .45}

SPECS = {
    'RiceSack': {'base_r': .19, 'belly_r': .22, 'neck_r': .17, 'h': .55, 'cuff_r': .185, 'rice_top': .60},
    'CuredMeatRack': {'width': .9, 'depth': .40, 'h': .95, 'bar_z': .85, 'strips': 4, 'sausage_strings': 3},
    'RadishCrate': {'radishes': 10, 'radish_len': .32, 'radish_r': .035, 'carrots': 3},
    'VegetableBasket': {'cabbages': 2, 'carrots': 4, 'scallion_bundle': 1},
    'EggBasket': {'eggs': 14, 'egg': (.021, .029)},
    'FishTub': {'water_z': .145, 'fish': 3, 'fish_len': .17},
}
