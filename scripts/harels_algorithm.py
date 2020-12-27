from CONSTANTS import *
from pure_functions import *
from target_functions import *


def harels_algorithm(params, all_agents):
    robots, targets, cells, robots_dict, cells_dict = separate_all_agents(all_agents)
    clear_domains_and_neighbours_update_runds_update_cells(all_agents, robots, targets, cells)
    set_FMR_for_targets(targets, robots)
    set_targets_funcs(targets, cells)
    set_targets_vs_robots_neighbours(targets, robots)

    set_robots_domains(robots, cells)
    init_message_boxes(all_agents)

    for iteration in range(ITERATIONS_IN_SMALL_LOOPS):
        # print_iteration_in_smaller_loop(iteration)
        send_message(all_agents, iteration)

    assignments = get_choices(all_agents, ITERATIONS_IN_SMALL_LOOPS - 1)
    new_positions = get_new_positions(assignments, robots_dict, cells_dict)
    new_positions = analyze_and_correct_new_positions(new_positions, robots_dict)
    collisions = calc_collisions(new_positions)
    return new_positions, collisions


def get_new_positions(assignments, robots_dict, cells_dict):
    new_positions = {}
    for robot_name, list_of_cells in assignments.items():
        robot = robots_dict[robot_name]
        robot.prev_pos = robot.pos
        robot.pos = cells_dict[random.choice(list_of_cells)].pos
        new_positions[robot.name] = robot.pos
    return new_positions


def get_choices(all_agents, iteration):
    assignments = {}
    text_to_print = ''
    for a in all_agents:
        if 'robot' in a.name:
            counter_dict = {}
            for d in a.domain:
                counter_dict[d] = 0
            for b in all_agents:
                if b.name in a.message_box[iteration]:
                    for k, v in a.message_box[iteration][b.name].items():
                        counter_dict[k] += v

            max_value = max(counter_dict.values())
            cells_with_highest_value = [k for k, v in counter_dict.items() if v == max_value]
            text_to_print += colored(a.name, 'green')
            choose_str = 'chooses one of' if len(cells_with_highest_value) > 1 else 'chooses'
            # text_to_print += f'{choose_str}: {cells_with_highest_value}'
            # text_to_print += f'with the highest value: {max_value:.2f}\n'
            assignments[a.name] = cells_with_highest_value
    text_to_print += colored('---', 'blue')
    # print(text_to_print)
    return assignments


def send_message(agents, iteration):
    # logging.info(" ---------- Small iteration: %s ---------- " % (iteration + 1))
    for agent in agents:
        # print(agent.name)
        for nei in agent.neighbours:
            agent.send_message_to(nei, iteration)


def init_message_boxes(agents):
    for agent in agents:
        for itr in range(ITERATIONS_IN_SMALL_LOOPS):
            agent.message_box[itr] = {}
            for nei in agent.neighbours:
                agent.message_box[itr][nei.name] = 0


def set_robots_domains(robots, cells):
    # mark_occupied_cells_by_robots(robots, cells)
    for robot in robots:
        for cell in cells:
            dist = distance(robot.get_pos(), cell.get_pos())
            if dist <= DISTANCE_BETWEEN_CELLS:
                if dist == 0 or not cell.occupied:
                    robot.domain.append(cell.num)


def set_targets_vs_robots_neighbours(targets, robots):
    for target in targets:
        for robot in robots:
            dist = distance(target.get_pos(), robot.get_pos())
            if dist < (SR + MR):
                if robot in target.fmr_set:
                    target.neighbours.append(robot)
                    robot.neighbours.append(target)


def set_targets_funcs(targets, cells):
    for target in targets:
        for cell in cells:
            dist = distance(target.get_pos(), cell.get_pos())
            if dist < SR:
                target.cells_in_range.append(cell.num)
            if dist == 0:
                cell.occupied = True
        target.func = create_func_target(cells_near_me=target.cells_in_range)