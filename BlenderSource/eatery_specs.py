"""Eatery10 layout (meters). Front = -Y, origin = bottom centre of the stone plinth footprint.
Shared by draw_eatery_sheets.py (design drawings) and build_eatery10.py (Blender model).
"""

NAME = 'Eatery'
NAME_ZH = '食肆客棧'

W, D = 10.0, 7.0                 # main body, x in [-5, 5], y in [-3.5, 3.5]
VERANDA = 1.5                    # front veranda / balcony depth, y in [-5, -3.5]
PLINTH = .45                     # stone plinth; ground floor level
F1 = 3.2                         # ground storey clear height to slab underside
SLAB = .20
F2 = 2.8                         # upper storey wall height
WALL_T = .22
EAVE = .8                        # roof overhang front/back
GABLE_OVER = .5                  # roof overhang at gable ends
RISE = 2.2                       # ridge height above wall top

Z_UP = PLINTH + F1 + SLAB        # upper floor level (3.85)
Z_TOP = Z_UP + F2                # upper wall top (6.65)
Z_RIDGE = Z_TOP + RISE           # ridge (8.85)

COLUMNS_X = [-5.0, -2.5, 0.0, 2.5, 5.0]
OPEN_BAYS = [(-2.5, 0.0), (0.0, 2.5)]             # ground front bays with folding doors fully open
DOOR_H = 2.6                                       # clear opening height above floor

STAIR = {'x0': -4.76, 'x1': -3.76,  # inside the west wall's inner face (-4.78)
         'y0': -1.2, 'risers': 17, 'riser': .20, 'tread': .22}
STAIR_TOP_Y = STAIR['y0'] + STAIR['risers'] * STAIR['tread']     # 2.54
# Hole in the upper slab (x0, x1, y0, y1). Starts above tread 6 so every tread under the slab keeps >= 2.0 m headroom.
STAIRWELL = (-4.78, -3.7, STAIR['y0'] + 6 * STAIR['tread'] - .02, STAIR_TOP_Y + .02)

COUNTER = {'x0': -2.8, 'x1': -.6, 'y': 1.2, 'depth': .6, 'h': 1.05}
KITCHEN = {'x0': 1.2, 'y0': .5, 'door': (2.0, 3.0), 'hatch': (3.6, 4.6)}   # walls at x=1.2 and y=0.5
HEARTH_AT = (3.6, 2.6)           # CookingHearth centre (rear face against chimney)
CHIMNEY = {'x': 3.6, 'y0': 3.0, 'y1': 3.6, 'w': .7, 'top': Z_RIDGE - .6}
BACK_DOOR_X = 2.2

TABLES = [(-2.4, -2.1), (.9, -2.1), (3.6, -2.1), (-.8, -.2)]
STOOL_OFFSET = .7

ROOM_WALLS_X = [-1.6, 1.6]       # upper floor partitions between three guest rooms
CORRIDOR_Y = .1                  # upper corridor wall line (rooms to the south), on the stairwell's south edge

LANTERNS_X = [-1.6, 1.6]
SIGN = {'w': 2.2, 'h': .55, 'z': 3.05}
