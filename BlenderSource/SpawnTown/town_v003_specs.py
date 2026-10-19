"""TownLayout v003: west street with the eatery, materials shop and herbal stall (world metres, Blender axes).
Shared by draw_town_v003_plan.py (layout drawing) and build_town_layout_v003.py (Blender scene).
v002 coordinates are kept: plaza around (0, -3), house east at x 12, smithy north-east, gateway north.
"""

SOURCE = 'Models/TownLayout/v002/TownLayout_v002.blend'
WALK_Z = .24                     # paving top used by every street in v002

TERRAIN_WEST_FROM = -11.0        # v002 island edge
TERRAIN_WEST_TO = -25.0          # extended edge
CURBS_REMOVED = ['Plaza_Edge_-1_2', 'Plaza_Edge_-1_3', 'Plaza_Edge_-1_4']   # opens y -4.39 .. -2.02

# Paved areas: name -> (x0, x1, y0, y1), top at WALK_Z.
PAVING = {
    'West_Lane': (-9.0, -4.59, -4.39, -2.02),      # plaza west edge to the street; south of the pine roots
    'West_Street': (-12.0, -9.0, -10.5, 12.5),
    'Stall_Pad': (-9.0, -6.6, 2.4, 8.4),
    'Shop_Apron': (-20.4, -12.0, 3.3, 12.9),
}

# Buildings: (source blend, collections prefix filter, placement (x, y, z), rotation_z_degrees, note)
# Front of every source asset is -Y; +90 deg turns it to face +X (east), -90 to face -X (west).
PLACEMENTS = {
    'Eatery': ('Models/Eatery/v001/Eatery_v001.blend', (-17.1, -3.2, .09), 90,
               'front steps end on the street edge; lower step top flush with the street (0.24)'),
    'MaterialShop': ('Models/MaterialShop/v001/MaterialShop_v001.blend', (-16.72, 8.0, WALK_Z), 90,
                     'porch steps start at the street edge'),
    'HerbalStall': ('Models/HerbalStall/v001/HerbalStall_v001.blend', (-7.9, 4.5, WALK_Z), -90,
                    'counter faces the street (west)'),
}
EATERY_PLOT_BASE = (-21.65, -12.0, -8.5, 2.1, 0, .09)   # x0, x1, y0, y1, z0, z1 under the raised eatery plinth

BENCH_MOVE = {'from_centre': (-3.65, -3.1), 'to_centre': (-8.4, 7.4)}   # v002 west plaza bench, was blocking the lane

MARKERS = {
    'Eatery_Entry_Feet': (-12.3, -3.2, .39),
    'MaterialShop_Entry_Feet': (-12.3, 8.0, WALK_Z),
    'HerbalStall_Customer_Feet': (-9.6, 4.5, WALK_Z),
    'West_Street_South_End': (-10.5, -10.5, WALK_Z),
    'West_Street_North_End': (-10.5, 12.5, WALK_Z),
}

# Walk samples (x, y): must hit paving at WALK_Z with nothing in the way between 0.3 m and 2.2 m.
LANE_SAMPLES = [(x, y) for x in (-4.3, -5.5, -6.7, -7.9, -8.7) for y in (-3.9, -3.2, -2.5)]
STREET_SAMPLES = [(x, y) for x in (-11.4, -10.5, -9.6) for y in (-10, -6, -3.2, 0, 4.5, 8, 12)]
