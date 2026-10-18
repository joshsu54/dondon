"""Shared dimensions for KitchenWare09 (meters, front = -Y, origin = bottom centre).
Both the design-sheet script and the Blender build script read these values,
so the drawings and the models stay in step.
"""

NAMES = {
    'CookingHearth': '柴火爐灶', 'IronWok': '雙耳鐵鍋', 'BambooSteamer': '竹蒸籠', 'PrepBoard': '料理砧板',
    'CeramicBowl': '粗陶碗', 'CeramicPlate': '粗陶盤', 'DiningTable': '食肆方桌', 'RoundStool': '木圓凳',
}

DETAILS = {
    'CookingHearth': 'Plastered brick stove on a stone plinth. One wok opening sized for IronWok, front arched fire mouth with firewood, rear smoke vent.',
    'IronWok': 'Spherical-cap iron wok with 6 mm wall, rolled rim and two loop ears. Rests in the CookingHearth opening.',
    'BambooSteamer': 'Two stacking bamboo tiers with slatted floors and a woven domed lid; tiers and lid are separate objects.',
    'PrepBoard': 'Thick end-grain chopping board with rounded corners and a hanging hole.',
    'CeramicBowl': 'Coarse stoneware bowl with separate inner and outer walls and a foot ring. Empty base for food variants.',
    'CeramicPlate': 'Coarse stoneware plate with a shallow well and foot ring.',
    'DiningTable': 'Square eatery table: four-plank top, aprons, legs and low stretchers.',
    'RoundStool': 'Round wooden stool with four splayed legs and a ring stretcher.',
}

# Lathe profiles: (radius, height) pairs running outer wall -> rim -> inner wall.
BOWL_PROFILE = [(0, .006), (.030, .006), (.031, 0), (.038, 0), (.040, .010), (.052, .022), (.066, .040), (.076, .058),
                (.080, .070), (.0795, .0725), (.0765, .0715), (.073, .060), (.064, .044), (.050, .028), (.032, .016), (0, .013)]
PLATE_PROFILE = [(0, .004), (.050, .004), (.052, 0), (.060, 0), (.062, .007), (.100, .018), (.120, .028),
                 (.1200, .0305), (.117, .030), (.098, .022), (.062, .012), (0, .010)]

SPECS = {
    'CookingHearth': {'size': (1.2, .8, .8), 'plinth_h': .10, 'top_h': .06, 'wok_hole_r': .25, 'wok_hole_x': -.18,
                      'fire_mouth': {'w': .34, 'h': .28, 'z': .14}, 'vent': {'w': .16, 'h': .12, 'z': .52}},
    'IronWok': {'mouth_d': .55, 'depth': .16, 'wall': .006, 'ear_r': .045},
    'BambooSteamer': {'d': .40, 'tier_h': .09, 'tiers': 2, 'lid_ring_h': .03, 'lid_dome_h': .045},
    'PrepBoard': {'size': (.45, .30, .04), 'corner_r': .03, 'hole_r': .014, 'hole_x': .185},
    'CeramicBowl': {'mouth_d': .16, 'h': .0725, 'foot_d': .076},
    'CeramicPlate': {'d': .24, 'h': .0305, 'foot_d': .12},
    'DiningTable': {'size': (1.0, 1.0, .75), 'top_t': .05, 'leg': .07, 'leg_inset': .06, 'apron_h': .08, 'stretcher_z': .15},
    'RoundStool': {'h': .45, 'seat_d': .32, 'seat_t': .04, 'leg_r': .018, 'leg_top': .10, 'leg_foot': .145, 'ring_z': .14},
}
