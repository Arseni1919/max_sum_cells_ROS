from CONSTANTS import *
# from cell_sprite import *
# from robot_sprite import *
# from target_sprite import *
# from title_sprite import *
from cell_functions import *
from robot import *
from target_functions import *
from variable_node import *
from function_node import *


# def init_pygame():
#     clock = pygame.time.Clock()
#     pygame.mixer.init()
#     pygame.init()
#     screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
#     finish_sound = pygame.mixer.Sound("sounds/Bell_2.ogg")
#     return clock, screen, finish_sound


def update_statistics(results_dict, graphs, all_agents, collisions, alg_name, iteration, problem):
    results_dict[alg_name]['col'].append(collisions)
    graphs[alg_name][iteration][problem] = calculate_convergence(all_agents)


def calculate_convergence(all_agents):
    robots, targets, cells, robots_dict, cells_dict = separate_all_agents(all_agents)
    convergence = 0
    for target in targets:
        curr_conv = REQ
        for robot in robots:
            if distance(target.get_pos(), robot.get_pos()) <= SR:
                curr_conv = max(0, curr_conv - CRED)
        convergence += curr_conv
    return convergence


# def create_results_dict():
#     # graphs[algorithm][iteration][problem] = convergence
#     results_dict = {}
#     graphs = {}
#     for alg_name, params in ALGORITHMS_TO_CHECK:
#         results_dict[alg_name] = {'col': []}
#         graphs[alg_name] = np.zeros((ITERATIONS_IN_BIG_LOOPS, NUMBER_OF_PROBLEMS))
#     return results_dict, graphs


def reset_delay(all_agents):
    for agent in all_agents:
        if 'robot' in agent.name:
            agent.delay = 0


# def reset_agents(all_sprites, all_agents, screen):
#     go_back_to_initial_positions(all_sprites, all_agents, screen)
#     reset_delay(all_agents)


# def go_back_to_initial_positions(all_sprites, all_agents, screen):
#     for sprite in all_sprites:
#         for agent in all_agents:
#             if sprite.name == agent.name:
#                 sprite.set_pos(agent.initial_pos)
#                 agent.pos = agent.initial_pos
#                 agent.prev_pos = agent.initial_pos
#
#     first_screen_blit(screen, all_sprites)


# def first_screen_blit(screen, all_sprites):
#     # Draw all sprites
#     for entity in all_sprites:
#         screen.blit(entity.surf, entity.rect)
#
#     # Update the display
#     pygame.display.flip()
#     time.sleep(1)


# def close_pygame(finish_sound):
#     finish_sound.play()
#     time.sleep(2)
#     # All done! Stop and quit the mixer.
#     pygame.mixer.music.stop()
#     pygame.mixer.quit()
#
#     # time.sleep(2)
#     # Done! Time to quit.
#     pygame.quit()


def pickle_results_if(graphs, results_dict):
    if NEED_TO_SAVE_RESULTS:
        suffix_str = time.strftime("%d.%m.%Y-%H:%M:%S")
        algorithms = graphs.keys()
        for alg in algorithms:
            suffix_str = suffix_str + '__%s' % alg
        suffix_str = suffix_str + '__%s' % ADDING_TO_FILE_NAME
        os.mkdir('data/%s' % suffix_str)
        suffix_str = "data/%s/file" % suffix_str
        file_name = "%s.graf" % suffix_str
        # open the file for writing
        with open(file_name, 'wb') as fileObject:
            pickle.dump(graphs, fileObject)

        # file_name = "data/%s_%s_file.resu" % (suffix_str, adding_to_file_name)
        file_name = "%s.resu" % suffix_str
        with open(file_name, 'wb') as fileObject:
            pickle.dump(results_dict, fileObject)

        collisions = {}
        for alg_name, inner_dict in results_dict.items():
            collisions[alg_name] = sum(inner_dict["col"])/2

        # file_name = "data/%s_%s_file.info" % (suffix_str, adding_to_file_name)
        file_name = "%s.info" % suffix_str
        # open the file for writing
        with open(file_name, 'wb') as fileObject:
            info = {'graphs': list(graphs.keys()),
                    'collisions': collisions,
                    'EXECUTE_DELAY': EXECUTE_DELAY,
                    'DELAY_OF_COLLISION': DELAY_OF_COLLISION,
                    'grid_size': (rows, columns),
                    'num_of_targets': len(TARGETS),
                    'num_of_agents': len(ROBOTS),
                    'target_range': REQ,
                    'MR': MR,
                    'SR': SR,
                    'cred': CRED,
                    'MAX_ITERATIONS': ITERATIONS_IN_BIG_LOOPS}
            pickle.dump(info, fileObject)


def plot_results_if(graphs):
    if NEED_TO_PLOT_RESULTS:
        # print_t_test_table(graphs)
        # plt.style.use('fivethirtyeight')
        plt.style.use('bmh')
        lines = ['-', '--', '-.', ':', ]
        lines.reverse()
        markers = [',', '+', '_', '.', 'o', '*']
        markers.reverse()
        marker_index, line_index = 0, 0
        # num_of_iterations, num_of_problems = graphs[algorithms[0]].shape
        # t_value = t.ppf(1 - alpha, df=(NUMBER_OF_PROBLEMS - 1))
        l = len(graphs[list(graphs.keys())[0]])
        iterations = [i+1 for i in range(len(graphs[list(graphs.keys())[0]]))]
        # avr = np.average(a, 1)
        # std = np.std(a, 1)

        fig, ax = plt.subplots()

        for alg_name in graphs.keys():

            line_index = 0 if line_index == len(lines) else line_index
            marker_index = 0 if marker_index == len(markers) else marker_index

            matrix = graphs[alg_name]
            avr = np.average(matrix, 1)
            print('%s last iteration: %s' % (alg_name, avr[-1]))
            std = np.std(matrix, 1)

            line = lines[line_index]
            marker = markers[marker_index]

            ax.plot(iterations, avr, '%s%s' % (marker, line), label=alg_name)

            line_index += 1
            marker_index += 1

            # if need_to_plot_variance:
            #     # confidence interval
            #     ax.fill_between(iterations, avr - t_value * std, avr + t_value * std,
            #                     alpha=0.2, antialiased=True)

            if NEED_TO_PLOT_MIN_MAX:
                # confidence interval
                ax.fill_between(iterations, np.min(matrix, 1), np.max(matrix, 1),
                                alpha=0.2, antialiased=True)

        ax.legend(loc='upper right')
        ax.set_title('Results')
        ax.set_ylabel('Coverage')
        ax.set_xlabel('Iterations')
        ax.set_xticks(iterations)
        # ax.set_xlim(xmin=iterations[0], xmax=iterations[-1])
        fig.tight_layout()
        plt.show()


def plot_collisions(results_dict):
    # results_dict[alg_name] = {'col': []}
    alg_names = list(results_dict.keys())
    iterations = range(len(results_dict[alg_names[0]]['col']))
    fig, ax = plt.subplots()

    for alg_name in alg_names:
        curr_col_list = results_dict[alg_name]['col']
        cumsum_list = np.cumsum(curr_col_list)
        ax.plot(iterations, cumsum_list, label=alg_name)

    ax.legend(loc='upper right')
    ax.set_title('Collisions')
    ax.set_ylabel('Accumulated Collisions')
    ax.set_xlabel('Accumulated Iterations')
    # ax.set_xticks(iterations)
    # ax.set_xlim(xmin=iterations[0], xmax=iterations[-1])
    fig.tight_layout()
    plt.show()


# def print_results(results_dict):
#     print()
#     for alg_name, inner_dict in results_dict.items():
#         print(colored(f'Collisions in {alg_name}: {sum(inner_dict["col"])/2} <- the set: {inner_dict["col"]}', 'yellow'))


def print_main(description, order, pred=''):
    logging.info("%s: %s --- %s " % (description, order, pred))
    # print(f' --- {description}: {order} --- ')


def check_targets_apart(all_agents):
    robots, targets, cells, robots_dict, cells_dict = separate_all_agents(all_agents=all_agents)
    for target1 in targets:
        for target2 in targets:
            if target1.name != target2.name:
                if distance(target1.get_pos(), target2.get_pos()) < 2*SR:
                    return False
    return True


# def create_problem():
#     good = False
#     all_sprites, all_agents = init_problem()
#     if TARGETS_APART:
#         while not good:
#             good = check_targets_apart(all_agents)
#             if not good:
#                 all_sprites, all_agents = init_problem()
#     return all_sprites, all_agents


# def init_problem(all_sprites):
#     # all_sprites = create_all_sprites()
#     all_agents = create_all_agents(all_sprites)
#     # reset_all(all_sprites, all_agents)
#     return all_sprites, all_agents


def reset_all(all_sprites, all_agents):
    if LOAD_PREVIOUS_POSITIONS:
        for sprite in all_sprites:
            sprite.pos = load_weight_of(sprite.name, FILE_NAME)['pos']
        for agent in all_agents:
            # agent.rund = load_weight_of(agent.name, file_name)['rund']
            agent.pos = load_weight_of(agent.name, FILE_NAME)['pos']
            agent.prev_pos = load_weight_of(agent.name, FILE_NAME)['pos']
            agent.initial_pos = load_weight_of(agent.name, FILE_NAME)['pos']

# Create Field
# def create_field(all_sprites, cells):
#     num = 1
#     for i in range(int(SCREEN_HEIGHT / (cell_size + PADDING))):
#         for j in range(int(SCREEN_HEIGHT / (cell_size + PADDING))):
#             surf_center = (
#                 PADDING + i * (cell_size + PADDING) + (cell_size / 2),
#                 PADDING + j * (cell_size + PADDING) + (cell_size / 2)
#             )
#             new_cell = CellSprite(cell_size, order=num, surf_center=surf_center)
#             num += 1
#             cells.add(new_cell)
#             all_sprites.add(new_cell)


# Create targets
# def create_targets(cell_size, all_sprites, targets, cells,
#                    ratio=0.3,
#                    req=-1,
#                    use_rate=True,
#                    num_of_targets=-1):
#     order = 1
#     if use_rate:
#         for cell in cells.sprites():
#             if random.random() < ratio:
#                 new_target = TargetSprite(
#                     cell_size,
#                     order=order,
#                     req=req,
#                     surf_center=cell.get_pos()
#                 )
#                 cell.prop = new_target
#                 targets.add(new_target)
#                 all_sprites.add(new_target)
#                 order += 1
#     else:
#         if num_of_targets == -1:
#             print('[ERROR]: bad')
#             raise RuntimeError('BADDDD')
#         while True:
#             cell = random.choice(cells.sprites())
#             if not cell.prop:
#                 new_target = TargetSprite(
#                     cell_size,
#                     order=order,
#                     req=req,
#                     surf_center=cell.get_pos()
#                 )
#                 cell.prop = new_target
#                 targets.add(new_target)
#                 all_sprites.add(new_target)
#                 order += 1
#                 if num_of_targets == len(targets.sprites()):
#                     break


# def create_robots(cell_size, all_sprites, agents, cells,
#                   num_of_agents=4,
#                   ratio=0.05,
#                   MR=round(3.5 * CELL_SIZE['BIG']),
#                   SR=int(2.5 * CELL_SIZE['BIG']),
#                   cred=5,
#                   show_ranges=False,
#                   speed=10):
#     for agent in range(1, num_of_agents + 1):
#         assigned = False
#         while not assigned:
#             indexes = [i for i in range(len(cells.sprites()))]
#             random.shuffle(indexes)
#             for index in indexes:
#                 cell = cells.sprites()[index]
#                 if random.random() < ratio and cell.prop is None:
#                     new_agent = RobotSprite(cell_size=cell_size,
#                                             number_of_robot=agent,
#                                             surf_center=cell.get_pos(),
#                                             MR=MR,
#                                             SR=SR,
#                                             cred=cred,
#                                             show_ranges=show_ranges,
#                                             speed=speed)
#                     cell.prop = new_agent
#                     agents.add(new_agent)
#                     all_sprites.add(new_agent)
#                     assigned = True
#                     break


# def create_dictionary(agents, targets):
#     for agent in agents.sprites():
#         OBJECTS[agent.get_name()] = agent
#     for target in targets.sprites():
#         OBJECTS[target.get_name()] = target


# def create_all_sprites():
#     # Create groups to hold all kinds of sprites
#     # - all_sprites is used for rendering
#     agents = pygame.sprite.Group()
#     targets = pygame.sprite.Group()
#     cells = pygame.sprite.Group()
#     # titles = pygame.sprite.Group()
#     all_sprites = pygame.sprite.Group()
#
#     # Create Field
#     create_field(all_sprites, cells)
#     print('height/weight: ', math.sqrt(len(cells.sprites())), end='')
#
#     # Create targets on field
#     create_targets(cell_size, all_sprites, targets, cells, target_rate, REQ, use_rate, NUM_OF_TARGETS)
#
#     # Create agents on field
#     create_robots(cell_size, all_sprites, agents, cells,
#                   num_of_agents=NUM_OF_AGENTS,
#                   MR=MR,
#                   SR=SR,
#                   cred=CRED,
#                   show_ranges=SHOW_RANGES,
#                   speed=speed)
#     # add_cell_and_target_tuples(agents, cells, targets)
#     create_dictionary(agents, targets)
#     return all_sprites


def create_all_agents(all_sprites):
    all_agents = []
    for sprite in all_sprites:
        if 'robot' in sprite.name:
            all_agents.append(VariableNode(name=sprite.name, num=sprite.num, domain=[], pos=sprite.pos))
        elif 'target' in sprite.name:
            all_agents.append(FunctionNode(name=sprite.name, num=sprite.num, func=None, pos=sprite.pos))
        elif 'cell' in sprite.name:
            all_agents.append(FunctionNode(name=sprite.name, num=sprite.num,
                                           func=func_cell, pos=sprite.pos))
        else:
            raise RuntimeError('[ERROR]: unknown sprite')
    return all_agents
