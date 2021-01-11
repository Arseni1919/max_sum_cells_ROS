#!/usr/bin/env python
# ------------------------------------ for PyCharm / for ROS
# from scripts.CONSTANTS import *
from CONSTANTS import *


# ------------------------------------

def create_empty_by_iteration_dict():
    curr_dict = {}
    for i in range(ITERATIONS_IN_BIG_LOOPS):
        curr_dict[i] = {}
    return curr_dict


def distance(pos1, pos2):
    """
    input:
    output:
    """
    return math.sqrt(math.pow(pos1[0] - pos2[0], 2) + math.pow(pos1[1] - pos2[1], 2))


def in_area(pos_1, pos_2, SR):
    """
    input:
    output:
    """
    px, py = pos_1
    tx, ty = pos_2
    return math.sqrt(math.pow(px - tx, 2) + math.pow(py - ty, 2)) < SR


def foo():
    print('here')
    logging.info("Thread %s : starting foo", threading.get_ident())
    time.sleep(0.1)
    logging.info("Thread %s : finishing foo", threading.get_ident())


def getAngle(a, b, c):
    ang = math.degrees(math.atan2(c[1] - b[1], c[0] - b[0]) - math.atan2(a[1] - b[1], a[0] - b[0]))
    curr_ang = ang + 360 if ang < 0 else ang
    small_ang = 360 - curr_ang if curr_ang > 180 else curr_ang
    return small_ang


def load_weight_of(agent_name: str, file_to_load_name: str):
    with open(file_to_load_name, 'rb') as handle:
        return pickle.load(handle)[agent_name]


def flatten_message(message):
    min_value = 99999
    for v in message.values():
        min_value = min(min_value, v)

    for k in message.keys():
        message[k] = message[k] - min_value


def get_random_num():
    return random.choice(range(1000)) / 1000


def calc_collisions(new_positions):
    col = 0
    for robot_name_1, pos_1 in new_positions.items():
        for robot_name_2, pos_2 in new_positions.items():
            if robot_name_1 != robot_name_2 and distance(pos_1, pos_2) == 0:
                col += 1
    return col


def separate_all_agents(all_agents):
    robots = []
    targets = []
    cells = []
    robots_dict = {}
    cells_dict = {}
    for agent in all_agents:
        if 'robot' in agent.name:
            robots.append(agent)
            robots_dict[agent.name] = agent
        elif 'target' in agent.name:
            targets.append(agent)
        elif 'cell' in agent.name:
            cells.append(agent)
            cells_dict[agent.num] = agent
        else:
            raise RuntimeError('[ERROR]: unknown agent')
    return robots, targets, cells, robots_dict, cells_dict


def clear_domains_and_neighbours_update_runds_update_cells(all_agents, robots, targets, cells):
    for agent in all_agents:
        agent.neighbours = []
        if LOAD_PREVIOUS_WEIGHTS:
            agent.rund = load_weight_of(agent.name, FILE_NAME)['rund']
        else:
            agent.update_rund()
    for robot in robots:
        robot.domain = []
        robot.targets_nearby = []
        # robot.prev_pos = robot.pos
    for cell in cells:
        cell.occupied = False
    for target in targets:
        target.cells_in_range = []
        target.fmr_set = []


# def print_iteration_in_smaller_loop(iteration):
#     # print(f'\rIteration in a smaller loop: {iteration + 1}', end='')
#     tracker.curr_smaller_iteration = iteration
#     tracker.print_progress()
#     # if iteration == ITERATIONS_IN_SMALL_LOOPS-1:
#     #     print()

def set_targets_vs_robots_neighbours(targets, robots):
    for target in targets:
        for robot in robots:
            dist = distance(target.get_pos(), robot.get_pos())
            if dist < (SR + MR):
                if robot in target.fmr_set:
                    target.neighbours.append(robot)
                    robot.neighbours.append(target)


def set_FMR_for_targets(targets, robots):
    create_target_neighbours_for_robots(targets, robots)
    for target in targets:
        target.fmr_set = select_FMR_nei(target, robots)
        # target.neighbours = target.fmr_set


def create_target_neighbours_for_robots(targets, robots):
    for robot in robots:
        for target in targets:
            dist = distance(robot.get_pos(), target.get_pos())
            if dist <= SR + MR:
                robot.targets_nearby.append(target)


def select_FMR_nei(target, robots):
    '''
    Assumptions: homogeneous agents and targets, in Fsum mode
    '''
    r_value = int(REQ/CRED)

    total_set = []
    SR_set = []
    rest_set = []

    for robot in robots:
        dist = distance(robot.get_pos(), target.get_pos())

        if dist <= SR + MR:
            total_set.append(robot)
            if dist <= SR:
                SR_set.append(robot)
            else:
                rest_set.append(robot)

    while len(total_set) > r_value:
        max_degree, min_degree = 0, 0
        for nei in total_set:
            degree = len(nei.targets_nearby)
            if nei in rest_set:
                max_degree = degree if max_degree < degree else max_degree
            if nei in SR_set:
                min_degree = degree if min_degree > degree else min_degree

        if len(rest_set) > 0:
            selected_to_remove = rest_set[0]
            for nei in rest_set:
                if len(nei.targets_nearby) == max_degree:
                    selected_to_remove = nei
                    break
            total_set.remove(selected_to_remove)
            rest_set.remove(selected_to_remove)
        else:
            selected_to_remove = SR_set[0]
            for nei in SR_set:
                if len(nei.targets_nearby) == min_degree:
                    selected_to_remove = nei
                    break
            total_set.remove(selected_to_remove)
            SR_set.remove(selected_to_remove)
    return total_set


def set_robots_domains_and_neighbours_for_robots_and_cells(robots, cells):
    mark_occupied_cells_by_robots(robots, cells)
    for robot in robots:
        for cell in cells:
            dist = distance(robot.get_pos(), cell.get_pos())
            if dist <= DISTANCE_BETWEEN_CELLS:
                if dist == 0 or not cell.occupied:
                    robot.domain.append(cell.num)
                    robot.neighbours.append(cell)
                    cell.neighbours.append(robot)


def mark_occupied_cells_by_robots(robots, cells):
    for robot in robots:
        for cell in cells:
            dist = distance(robot.get_pos(), cell.get_pos())
            if dist == 0:
                cell.occupied = True
                break


def return_to_prev_pos(robots_dict):
    new_positions = {}
    for robot_name, robot in robots_dict.items():
        robot.pos = robot.prev_pos
        new_positions[robot.name] = robot.pos
    return new_positions


def analyze_and_correct_new_positions(new_positions: dict, robots_dict, cells_dict=None, choice_list=None):
    if EXECUTE_DELAY:
        # print()
        for robot_name, robot in robots_dict.items():
            if robot.delay > 0:
                robot.pos = robot.prev_pos
                new_positions[robot.name] = robot.pos

        for robot_name_1, pos_1 in new_positions.items():
            for robot_name_2, pos_2 in new_positions.items():
                if robot_name_1 != robot_name_2 and distance(pos_1, pos_2) == 0:
                    dict_to_print = {robot_name_1: robots_dict[robot_name_1],
                                     robot_name_2: robots_dict[robot_name_2]}
                    # print_runds(dict_to_print, cells_dict)
                    # graph_choice_list(choice_list)
                    d_robot = robots_dict[robot_name_1]
                    d_robot.update_delay()
                    # print(colored('\r[ERROR]: Robot %s delaying on the same pos!' % d_robot.num, 'yellow'), end='')

    return new_positions
