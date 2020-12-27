from CONSTANTS import *
from pure_functions import *


def random_walk(params, all_agents):
    robots, targets, cells, robots_dict, cells_dict = separate_all_agents(all_agents)
    clear_domains_and_neighbours_update_runds_update_cells(all_agents, robots, targets, cells)
    set_robots_domains_and_neighbours_for_robots_and_cells(robots, cells)

    new_random_positions = get_new_random_positions(robots_dict, cells_dict)
    new_positions = analyze_and_correct_new_positions(new_random_positions, robots_dict)
    collisions = calc_collisions(new_random_positions)
    return new_positions, collisions


def clear_domains_and_neighbours_update_runds_update_cells(all_agents, robots, targets, cells):
    for agent in all_agents:
        agent.neighbours = []
        if LOAD_PREVIOUS_WEIGHTS:
            agent.rund = load_weight_of(agent.name, FILE_NAME)['rund']
        else:
            agent.update_rund()
    for robot in robots:
        robot.domain = []
        # robot.prev_pos = robot.pos
    for cell in cells:
        cell.occupied = False
    for target in targets:
        target.cells_in_range = []


def get_new_random_positions(robots_dict, cells_dict):
    new_positions = {}
    for robot_name, robot in robots_dict.items():
        robot.prev_pos = robot.pos
        robot.pos = cells_dict[random.choice(robot.domain)].pos
        new_positions[robot.name] = robot.pos
    return new_positions