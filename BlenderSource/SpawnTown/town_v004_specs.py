"""TownLayout v004: StreetProps11 dressing on the v003 west street (world metres, Blender axes).
Read by build_town_layout_v004.py. v003 is the base; the west street walking surface stays clear.
"""
SOURCE = 'Models/TownLayout/v003/TownLayout_v003.blend'
PROPS_DIR = 'Models'                 # Models/<Prop>/v001/<Prop>_v001.blend
WALK_Z = .24

# New paved pads beside the street (x0, x1, y0, y1), top at WALK_Z.
PAVING = {
    'Well_Pad': (-9.0, -6.2, -8.8, -5.4),       # south of the west lane, east of the street
    'Notice_Pad': (-9.0, -8.25, -2.02, .2),     # north of the lane mouth, clear of the pine roots (x > -8.0)
}

# (prop, (x, y, base_z), rotation_z_degrees, note). Front of every prop is -Y before rotation.
PROPS = [
    ('StoneWell', (-7.6, -7.1, WALK_Z), 0, 'well on its own pad, crank side away from the street'),
    ('WellBucket', (-6.6, -5.85, WALK_Z), 0, 'spare bucket beside the well'),
    ('NoticeBoard', (-8.62, -.9, WALK_Z), -90, 'board faces the street (west)'),
    ('WoodenCrate', (-7.05, 7.6, WALK_Z), 0, 'crates behind the herbal stall bench'),
    ('WoodenCrate', (-7.05, 7.6, WALK_Z + .5), 12, 'stacked on the first crate'),
    ('WoodenCrate', (-7.0, 8.1, WALK_Z), 0, ''),
    ('BambooBasket', (-7.4, 6.45, WALK_Z), 0, 'between the stall and the bench'),
    ('BambooBasket', (-13.6, .7, .54), 90, 'on the eatery veranda (veranda paving at 0.54)'),
    ('FirewoodStack', (-22.07, -3.3, 0.0), -90, 'against the eatery rear wall, south of the back door, on the ground'),
]

LANE_SAMPLES = [(x, y) for x in (-4.3, -5.5, -6.7, -7.9, -8.7) for y in (-3.9, -3.2, -2.5)]
STREET_SAMPLES = [(x, y) for x in (-11.4, -10.5, -9.6) for y in (-10, -6, -3.2, 0, 4.5, 8, 12)]
