from CONSTANTS import *
from cell_functions import *
from robot import *
from target_functions import *
from variable_node import *
from function_node import *


def max_sum_cells_alg(params, all_agents):
    robots_dict, cells_dict = update_domains_and_neighbours_and_runds(all_agents)
    init_message_boxes(all_agents)
    choice_list = create_choice_list(all_agents)

    for iteration in range(ITERATIONS_IN_SMALL_LOOPS):
        # print_iteration_in_smaller_loop(iteration)
        send_message(all_agents, iteration)
        extend_choice_list(all_agents, iteration, choice_list)

    assignments = get_choices(all_agents, ITERATIONS_IN_SMALL_LOOPS - 1)
    new_positions = get_new_positions(assignments, robots_dict, cells_dict)
    new_positions = analyze_and_correct_new_positions(new_positions, robots_dict, cells_dict, choice_list)
    collisions = calc_collisions(new_positions)
    return new_positions, collisions


def get_new_positions(assignments, robots_dict, cells_dict):
    new_positions = {}
    for robot_name, list_of_cells in assignments.items():
        robot = robots_dict[robot_name]
        robot.prev_pos = robot.pos
        robot.pos = cells_dict[list_of_cells[0]].pos
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
            # text_to_print += colored(a.name, 'green')
            # choose_str = 'chooses one of' if len(cells_with_highest_value) > 1 else 'chooses'
            # text_to_print += f'{choose_str}: {cells_with_highest_value}'
            # text_to_print += f'with the highest value: {max_value:.2f}\n'
            assignments[a.name] = cells_with_highest_value
    # text_to_print += colored('---', 'blue')
    # print(text_to_print)
    return assignments


def init_message_boxes(agents):
    for agent in agents:
        for itr in range(ITERATIONS_IN_SMALL_LOOPS):
            agent.message_box[itr] = {}
            for nei in agent.neighbours:
                agent.message_box[itr][nei.name] = 0


def send_message(agents, iteration):
    # logging.info(" ---------- Small iteration: %s ---------- " % (iteration + 1))
    for agent in agents:
        # print(agent.name)
        for nei in agent.neighbours:
            agent.send_message_to(nei, iteration)


def update_domains_and_neighbours_and_runds(all_agents):
    # update, domains of robots, functions of targets and neighbours of everybody
    robots, targets, cells, robots_dict, cells_dict = separate_all_agents(all_agents)
    clear_domains_and_neighbours_update_runds_update_cells(all_agents, robots, targets, cells)
    set_targets_funcs(targets, cells)
    set_FMR_for_targets(targets, robots)
    set_targets_vs_robots_neighbours(targets, robots)
    set_robots_domains_and_neighbours_for_robots_and_cells(robots, cells)
    save_weights(all_agents, FILE_NAME)
    return robots_dict, cells_dict


def set_targets_vs_robots_neighbours(targets, robots):
    for target in targets:
        for robot in robots:
            dist = distance(target.get_pos(), robot.get_pos())
            if dist < (SR + MR):
                # target.neighbours.append(robot)
                # robot.neighbours.append(target)
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


def print_runds(robots_dict, cells_dict):
    # for r_name, robot in robots_dict.items():
        # print(f'{r_name}: {robot.rund}')
        # for nei in robot.neighbours:
        #     print(f'\t{nei.name}: {nei.rund}')
    print('---')
    # for c_name, cell in cells_dict.items():
    #     print(f'{c_name}: {cell.rund}')


def save_weights(all_agents, file_name):
    if SAVE_WEIGHTS:
        # open the file for writing
        curr_dict = {}
        for agent in all_agents:
            to_save = {'rund': agent.rund, 'pos': agent.pos}
            curr_dict[agent.name] = to_save
        with open(file_name, 'wb') as fileObject:
            pickle.dump(curr_dict, fileObject)


def get_dict_of_weights(file_name: str):
    with open(file_name, 'rb') as handle:
        return pickle.load(handle)


def create_choice_list(all_agents):
    choice_list = {}
    for a in all_agents:
        if 'robot' in a.name:
            choice_list[a.name] = {'choice': [], 'weight': []}
    return choice_list


def extend_choice_list(all_agents, iteration, choice_list):

    for a in all_agents:
        if 'robot' in a.name:
            counter_dict = {}
            for d in a.domain:
                counter_dict[d] = 0
            for b in all_agents:
                if b.name in a.message_box[iteration]:
                    for k, v in a.message_box[iteration][b.name].items():
                        counter_dict[k] += v
            choice, weight = max(counter_dict.items(), key=operator.itemgetter(1))

            choice = choice - 100 if choice > 100 else choice
            choice_list[a.name]['choice'].append(choice)
            choice_list[a.name]['weight'].append(weight)


def graph_choice_list(choice_list):
    fig, axs = plt.subplots(2, 1)
    # ax.scatter(z, y)
    for robot_name, choices_dict in choice_list.items():
        axs[0].plot(choices_dict['choice'], label=robot_name, ls='dashdot', alpha=0.5)
        axs[1].plot(choices_dict['weight'][:], label=robot_name, ls='dashdot', alpha=0.5)
        for i, txt in enumerate(choices_dict['weight']):
            if i % 5 == 0:
                axs[0].annotate(round(txt, 2), (i, choices_dict['choice'][i]), fontsize=5)
    axs[0].set_xticks(range(1, ITERATIONS_IN_SMALL_LOOPS+1))
    axs[0].set_xticklabels(range(1, ITERATIONS_IN_SMALL_LOOPS+1), fontsize=5)
    axs[1].set_xticks(range(3, ITERATIONS_IN_SMALL_LOOPS + 1))
    axs[1].set_xticklabels(range(3, ITERATIONS_IN_SMALL_LOOPS + 1), fontsize=5)
    # plt.axhline(y=0, color='black')
    axs[0].legend()
    axs[1].legend()

    plt.title('Choices of Robots (y - choices, x - time)')
    plt.show()