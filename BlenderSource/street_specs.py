"""Shared dimensions for StreetProps11 (meters, front = -Y, origin = bottom centre).
Read by draw_street_sheets.py (design sheets) and build_street_props11.py (Blender models).
"""

NAMES = {'StoneWell': '石井', 'WellBucket': '木水桶', 'NoticeBoard': '公告板', 'WoodenCrate': '木箱',
         'BambooBasket': '竹簍', 'FirewoodStack': '柴堆'}

DETAILS = {
    'StoneWell': 'Round dry-stone well with coping, stone apron, timber windlass with crank, small tiled gable roof, rope and hanging bucket.',
    'WellBucket': 'Wooden stave bucket with two iron hoops and a rope bail; same bucket hangs in the well.',
    'NoticeBoard': 'Village notice board: two posts on stone feet, framed plank board with blank paper notices, small tiled cap roof.',
    'WoodenCrate': 'Planked storage crate with corner battens and a separate lid.',
    'BambooBasket': 'Woven bamboo back basket (竹簍) with ribs, rings, foot frame and two shoulder straps on the back.',
    'FirewoodStack': 'Split firewood stacked between end posts on two base rails, with a small plank rain cap.',
}

SPECS = {
    'StoneWell': {'outer_r': .60, 'inner_r': .42, 'wall_h': .75, 'apron_r': .90, 'apron_h': .08, 'post_x': .78, 'post_h': 2.05,
                  'roller_z': 1.55, 'roof': {'ridge_z': 2.45, 'eave_z': 2.12, 'half_x': .98, 'half_y': .66}, 'water_z': .18},
    'WellBucket': {'top_r': .16, 'bottom_r': .135, 'h': .30, 'wall': .015, 'staves': 14},
    'NoticeBoard': {'post_x': .85, 'post_h': 2.3, 'post': .12, 'board': (1.5, .06, 1.0), 'board_z': .95, 'roof_w': 1.95, 'roof_d': .62, 'roof_rise': .2},
    'WoodenCrate': {'size': (.60, .45, .45), 'plank_gap': .012, 'lid_t': .03},
    'BambooBasket': {'top_r': .21, 'bottom_r': .15, 'h': .55, 'wall': .012, 'ribs': 18},
    'FirewoodStack': {'length': 1.5, 'depth': .55, 'rows': 7, 'log_r': (.055, .075), 'post_h': 1.12, 'cap_z': (1.14, 1.26)},
}
