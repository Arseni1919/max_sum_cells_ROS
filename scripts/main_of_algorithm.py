#!/usr/bin/env python3
from CONSTANTS import *
from pure_functions import *
from algorithms import *
from main_of_algorithm_help_functions import *
from ROS_CONSTANTS import *

def callback_READY_topic(msg):
    message = json.loads(msg.data)
    READY_dict[message['iteration']][message['name']] = message['ready']
    # print(message['name'], ' arrived')


def callback_CALC_READY_topic(msg):
    message = json.loads(msg.data)
    CALC_READY_dict[message['iteration']]['positions'] = message['positions']


def wait(curr_iteration):

    everybody_ready = False
    while not everybody_ready:
        everybody_ready = True

        for robot in ROBOTS:
            if robot.name not in READY_dict[curr_iteration] or not READY_dict[curr_iteration][robot.name]:
                everybody_ready = False
                break
        rate.sleep()
    time_list.append(int(time.time()-start_time))
    print('[WAIT] - finished')


def calc(curr_iteration):
    message_of_new_positions = {'iteration': curr_iteration}
    # update new pos with alg
    new_positions, collisions = ALGORITHM(params={}, all_agents=ALL_AGENTS)
    message_of_new_positions['positions'] = new_positions
    message = json.dumps(message_of_new_positions)
    pub_CALC_READY_topic.publish(message)
    print_check(message, ALL_AGENTS, new_positions)
    convergence_list.append(calculate_convergence(ALL_AGENTS))
    collisions_list.append(collisions)
    print('[CALC] - finished')


def print_check(message, all_agents, new_positions):
    print(message)
    for agent1 in all_agents:
        if 'robot' in agent1.name:
            print('%s domain: %s' % (agent1.name, agent1.domain))

            for agent2 in all_agents:
                if 'cell' in agent2.name:
                    if new_positions[agent1.name] == agent2.pos:
                        print('%s -> %s' % (agent1.name, agent2.name))

    for agent1 in all_agents:
        if 'target' in agent1.name:
            print('%s domain: %s' % (agent1.name, agent1.cells_in_range))

        # print('%s neighbours: %s' % (agent.name, [a.name for a in agent.neighbours]))


def finish():
    print('algorithm: %s' % CURRENT_ALGORITHM)
    print('coverage list: %s' % convergence_list)
    print('times list: %s' % time_list)
    print('collisions list: %s' % collisions_list)

    # save results
    if NEED_TO_SAVE_RESULTS:
        print('[FIN] - finished saving results')
    else:
        print('[FIN] - finished without saving results')


if __name__ == '__main__':
    # ------------------------ INPUT ------------------------ #
    print('######################### %s #########################' % CURRENT_ALGORITHM)
    start_time = time.time()
    time_list = [0,]
    convergence_list = []
    collisions_list = []
    CALC_READY_dict = create_empty_by_iteration_dict()
    READY_dict = create_empty_by_iteration_dict()
    # ------------------------------------------------------- #
    rospy.init_node('ALGORITHM_topic')
    # pub_READY_topic = rospy.Publisher('READY_topic', String, latch=True, queue_size=10)
    sub_READY_topic = rospy.Subscriber('READY_topic', String, callback_READY_topic)
    pub_CALC_READY_topic = rospy.Publisher('CALC_READY_topic', String, latch=True, queue_size=50)
    sub_CALC_READY_topic = rospy.Subscriber('CALC_READY_topic', String, callback_CALC_READY_topic)
    rate = rospy.Rate(1)  # 1 second
    ALGORITHM = get_the_algorithm(CURRENT_ALGORITHM)
    ALL_AGENTS = create_all_agents(all_sprites=SPRITES)

    for iteration in range(ITERATIONS_IN_BIG_LOOPS):
        print('# --------------------- iteration: %s --------------------- #' % iteration)
        wait(iteration)
        calc(iteration)
    finish()

#