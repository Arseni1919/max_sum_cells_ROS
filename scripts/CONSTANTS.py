#!/usr/bin/env python

from __future__ import print_function
import os
from decimal import Decimal
import sys
print(sys.executable)
print('---')
for i in sys.path:
    print(i)

# import pygame
from prettytable import PrettyTable
import os
import random
import logging
import threading
import time
# import concurrent.futures
import matplotlib
# matplotlib.use('TkAgg')
import matplotlib.pyplot as plt
import math
import numpy as np
import pickle
import json
import copy
#from scipy.stats import t
#from scipy import stats
import itertools
# from tqdm import tqdm
from pprint import pprint
# import statistics
from collections import namedtuple
import collections
import operator
# from termcolor import colored

CellTuple = namedtuple('CellTuple', ['pos', 'name', 'num' ])
TargetTuple = namedtuple('TargetTuple', ['pos', 'req', 'name', 'num'])
RobotTuple = namedtuple('AgentTuple',
                        ['pos', 'num_of_robot_nei', 'num_of_target_nei', 'name', 'num', 'cred', 'SR', 'MR'])
# for logging
_format = "%(asctime)s: %(message)s"
logging.basicConfig(format=_format, level=logging.INFO, datefmt="%H:%M:%S")


# -------------------------------------------------------- FOR EXPERIMENT
ITERATIONS_IN_BIG_LOOPS = 5
ITERATIONS_IN_SMALL_LOOPS = 10
# MOVE_REAL_ROBOTS = True
MOVE_REAL_ROBOTS = False
# ONE_BY_ONE = True
ONE_BY_ONE = False
POS_POLICY = 'random_furthest'
REQ = 100
CRED = 30
SR = 1.0
MR = 2.5
# EXECUTE_DELAY = True
EXECUTE_DELAY = False
DELAY_OF_COLLISION = 70
CURRENT_ALGORITHM = 'random_walk'
ALGORITHMS_TO_CHECK = [
    ('random_walk', {}),
    ('harels_algorithm', {}),
    ('max_sum_cells', {}),
]
MINUS_INF = -50000
# -------------------------------------------------- #
# FLATTEN = False
FLATTEN = True
SHOW_RANGES = True
# SHOW_RANGES = False
# NEED_TO_SAVE_RESULTS = False
NEED_TO_SAVE_RESULTS = True
ADDING_TO_FILE_NAME = ''
NEED_TO_PLOT_RESULTS = True
# NEED_TO_PLOT_RESULTS = False
NEED_TO_PLOT_VARIANCE, NEED_TO_PLOT_MIN_MAX = False, True
# NEED_TO_PLOT_VARIANCE, NEED_TO_PLOT_MIN_MAX = True, False
# -------------------------------------------------- #
FILE_NAME = "last_weights.txt"
# LOAD_PREVIOUS_POSITIONS = True
LOAD_PREVIOUS_POSITIONS = False
# LOAD_PREVIOUS_WEIGHTS = True
LOAD_PREVIOUS_WEIGHTS = False
SAVE_WEIGHTS = True
# SAVE_WEIGHTS = False

TARGETS = [
    TargetTuple(pos=(0.60,2.00), req=REQ, name='target1', num=1),
    TargetTuple(pos=(2.10,2.00), req=REQ, name='target2', num=2),
    # TargetTuple(pos=(0, -2), req=req, name='target3', num=3),
    # TargetTuple(pos=(4, -2), req=req, name='target4', num=4),
]

ROBOTS = [
    RobotTuple(pos=(2.18,0.07), num_of_robot_nei=None, num_of_target_nei=None, name='robot1', num=1, cred=CRED,
               SR=SR, MR=MR),
    # RobotTuple(pos=(2.1, 3), num_of_robot_nei=None, num_of_target_nei=None, name='robot2', num=2, cred=CRED,
    #            SR=SR, MR=MR),
    RobotTuple(pos=( 0.52,0.08), num_of_robot_nei=None, num_of_target_nei=None, name='robot3', num=3, cred=CRED,
               SR=SR, MR=MR),
    # RobotTuple(pos=(1.2, 1), num_of_robot_nei=None, num_of_target_nei=None, name='robot4', num=4, cred=CRED,
    #            SR=SR, MR=MR),
    # RobotTuple(pos=(2.18,0.07), num_of_robot_nei=None, num_of_target_nei=None, name='robot5', num=5, cred=CRED,
    #            SR=SR, MR=MR)
]

CELLS = []
DISTANCE_BETWEEN_CELLS = 1.6
start_pose_to_go = (0.52, 0.08)
#################
# p_2 . . . p_3 #
# .         .   #
# .         .   #
# .         .   #
# p_1 . . . p_4 #
#################
p_1 = (0.52, 0.08)
p_2 = (0.65, 2.03)
p_3 = (2.13, 2.04)
p_4 = (2.18, 0.07)
rows = round(min(abs(p_2[1] - p_1[1]), abs(p_3[1] - p_4[1])) / 0.7)
columns = round(min(abs(p_2[0] - p_3[0]), abs(p_1[0] - p_4[0])) / 0.7)
print('rows: %s, columns: %s' % (rows, columns))
row_divisions = []
for i in range(rows):
    row_divisions.append(i/float(rows-1))
column_divisions = []
for i in range(columns):
    column_divisions.append(i/float(columns-1))

field = PrettyTable()
field.field_names = [i+1 for i in range(columns)]
counter_cells = 0
for r in range(rows-1, -1, -1):

    def get_xy(p1, p2, p3, p4, row_division, column_division):
        ax_left = p1[0] + row_division * (p2[0] - p1[0])
        ax_right = p4[0] + row_division * (p3[0] - p4[0])
        x = ax_left + column_division * (ax_right - ax_left)
        ax_top = p2[1] + column_division * (p3[1] - p2[1])
        ax_bottom = p1[1] + column_division * (p4[1] - p1[1])
        y = ax_bottom + row_division * (ax_top - ax_bottom)
        return x, y

    raw = []
    for c in range(columns):
        counter_cells += 1
        curr_x, curr_y = get_xy(p_1, p_2, p_3, p_4, row_divisions[r], column_divisions[c])
        v = np.array([curr_x, curr_y])
        raw.append('%s,%s (%s)' % (round(v[0], 2), round(v[1], 2), counter_cells))

        CELLS.append(CellTuple(pos=(v[0], v[1]), name='cell%s' % counter_cells, num=counter_cells))
    field.add_row(raw)

print('field: \n%s' % field)

SPRITES = []
SPRITES.extend(TARGETS)
SPRITES.extend(ROBOTS)
SPRITES.extend(CELLS)
# -----------------------------------------------------------------------


# MessageType = namedtuple('MessageType', ['from_var_to_func',
#                                          'from_var_to_func_only_pos',
#                                          'from_var_to_func_dir',
#                                          'from_func_pos_collisions_to_var',
#                                          'from_func_dir_collisions_to_var',
#                                          'from_func_target_to_var'])
# message_types = MessageType(from_var_to_func='from_var_to_func',
#                             from_var_to_func_only_pos='from_var_to_func_only_pos',
#                             from_var_to_func_dir='from_var_to_func_dir',
#                             from_func_pos_collisions_to_var='from_func_pos_collisions_to_var',
#                             from_func_dir_collisions_to_var='from_func_dir_collisions_to_var',
#                             from_func_target_to_var='from_func_target_to_var')
# from_func_to_var_types = (message_types.from_func_pos_collisions_to_var, message_types.from_func_target_to_var,
#                           message_types.from_func_dir_collisions_to_var)
# dictionary_message_types = (message_types.from_func_pos_collisions_to_var, message_types.from_func_target_to_var,
#                             message_types.from_func_dir_collisions_to_var, message_types.from_var_to_func,
#                             message_types.from_var_to_func_dir)
# TypesOfRequirement = namedtuple('TypesOfRequirement', ['copy', 'copy_var_dicts', 'copy_func_dicts'])
# copy_types = TypesOfRequirement('copy', 'copy_var_dicts', 'copy_func_dicts')