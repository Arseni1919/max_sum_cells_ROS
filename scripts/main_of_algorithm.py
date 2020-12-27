#!/usr/bin/env python3
from CONSTANTS import *
from pure_functions import *
from algorithms import *
from main_of_algorithm_help_functions import *


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
    print('[WAIT] - finished')


def calc(curr_iteration, all_agents):
    message_of_new_positions = {'iteration': curr_iteration}
    # update new pos with alg
    new_positions, collisions = algorithm(params={}, all_agents=all_agents)
    message_of_new_positions['positions'] = new_positions
    message = json.dumps(message_of_new_positions)
    pub_CALC_READY_topic.publish(message)
    print(message)
    print('[CALC] - finished')


def finish():
    # save results
    if NEED_TO_SAVE_RESULTS:
        print('[FIN] - finished saving results')
    else:
        print('[FIN] - finished without saving results')


if __name__ == '__main__':
    # ------------------------ INPUT ------------------------ #
    print('######################### ALGORITHM #########################')

    CALC_READY_dict = create_empty_by_iteration_dict()
    READY_dict = create_empty_by_iteration_dict()
    # ------------------------------------------------------- #
    rospy.init_node('ALGORITHM_topic')
    # pub_READY_topic = rospy.Publisher('READY_topic', String, latch=True, queue_size=10)
    sub_READY_topic = rospy.Subscriber('READY_topic', String, callback_READY_topic)
    pub_CALC_READY_topic = rospy.Publisher('CALC_READY_topic', String, latch=True, queue_size=50)
    sub_CALC_READY_topic = rospy.Subscriber('CALC_READY_topic', String, callback_CALC_READY_topic)
    rate = rospy.Rate(1)  # 1 second
    algorithm = get_the_algorithm(CURRENT_ALGORITHM)
    all_agents = create_all_agents(all_sprites=SPRITES)

    for iteration in range(ITERATIONS_IN_BIG_LOOPS):
        print('# --------------------- iteration: %s --------------------- #' % iteration)
        wait(iteration)
        calc(iteration, all_agents)
    finish()
