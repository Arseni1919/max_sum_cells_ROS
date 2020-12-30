from pure_functions import *

# +---------------+---------------+
# |       1       |       2       |
# +---------------+---------------+
# | 0.65,2.03 (1) | 2.13,2.04 (2) |
# | 0.58,1.06 (3) | 2.16,1.06 (4) |
# | 0.52,0.08 (5) | 2.18,0.07 (6) |
# +---------------+---------------+
def get_cell(num):
    for c in CELLS:
        if  c.num == num:
            return c
    return -1


cell1 = get_cell(num=14)
cell2 = get_cell(num=13)

print(distance(pos1=cell1.pos, pos2=cell2.pos))