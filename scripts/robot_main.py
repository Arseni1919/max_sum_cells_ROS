#!/usr/bin/env python3
# !/home/hamster/anaconda3/bin/python
# ------------------------------------ for PyCharm / for ROS
# from scripts.Max_sum_FMR_TAC import *
from CONSTANTS import *
from robot import Robot
from pure_functions import *
from ROS_CONSTANTS import *
# ------------------------------------
# ------------------------------------


# ------------------------------------ LOCAL VARS
# READY = False
# ------------------------------------


def callback_READY_topic(msg):
    # print(msg.data)
    message = json.loads(msg.data)
    READY_dict[message['iteration']][message['name']] = message['ready']


def callback_CALC_READY_topic(msg):
    message = json.loads(msg.data)
    # CALC_READY_dict[message['iteration']][message['name']] = message['ready']
    CALC_READY_dict[message['iteration']]['positions'] = message['positions']


def calc(curr_iteration):
    new_position_arrived = False
    while not new_position_arrived:
        new_position_arrived = True
        if 'positions' not in CALC_READY_dict[curr_iteration]:
            new_position_arrived = False
        rate.sleep()
    print('[CALC WAIT] - finished')

    next_position = CALC_READY_dict[curr_iteration]['positions'][named_tuple_of_this_robot.name]
    print('[CALC] - finished calc of %s prev_pos: %s -> next_pos: %s' % (
    robot_object.name, robot_object.pos, next_position))
    return next_position


def callback_MOVE_topic(msg):
    message = json.loads(msg.data)
    MOVE_dict[message['iteration']][message['name']] = message['ready']
    print('In iteration %s %s arrived to its position' % (message['iteration'], message['name']))


def callback_amcl(msg):
    print('---')
    print('x_pose_amcl: %s' % msg.pose.pose.position.x)
    print('y_pose_amcl: %s' % msg.pose.pose.position.y)
    print('---')
    robot_object.pos = (msg.pose.pose.position.x, msg.pose.pose.position.y)
    rate.sleep()


def wait(curr_iteration):
    message = json.dumps({'name': robot_object.name, 'iteration': curr_iteration, 'ready': True})
    # print(message)
    everybody_ready = False
    while not everybody_ready:
        # print(READY_dict)
        pub_READY_topic.publish(message)
        everybody_ready = True
        # for target in TARGETS:
        #     if target.name not in READY_dict[curr_iteration] or not READY_dict[curr_iteration][target.name]:
        #         everybody_ready = False
        #         break
        for robot in ROBOTS:
            if robot.name not in READY_dict[curr_iteration] or not READY_dict[curr_iteration][robot.name]:
                everybody_ready = False
                break
        rate.sleep()
    print('[WAIT] - finished')


def move_wait(curr_iteration):
    # print(message)
    everybody_ready = False
    while not everybody_ready:
        everybody_ready = True
        for robot in ROBOTS:
            if robot.num < robot_object.num:
                if robot.name not in MOVE_dict[curr_iteration]:
                    everybody_ready = False
                    break
        rate.sleep()
    print('[MOVE WAIT] - finished')


def move(curr_iteration, to_next_pos):
    if MOVE_REAL_ROBOTS:
        client.send_goal(goal_pose(to_next_pos))
        client.wait_for_result()

    robot_object.pos = tuple(to_next_pos)
    message = json.dumps({'name': robot_object.name, 'iteration': curr_iteration, 'ready': True})
    pub_MOVE_topic.publish(message)
    print('[MOVE] - finished move')
    # print(robot_object.pos)


def finish():
    # save results
    if NEED_TO_SAVE_RESULTS:
        print('[FIN] - finished saving results')
    else:
        print('[FIN] - finished without saving results')


def get_named_tuple_of_robot(curr_num_of_robot):
    for robot in ROBOTS:
        # print(type(target.num))
        # print(type(curr_num_of_target))
        if robot.num == curr_num_of_robot:
            return robot
    print('[ERROR]! no named_tuple_of_target')





def goal_pose(pose):
    # print("in goal_pose %s" % (datetime.datetime.now()))
    goal_pose = MoveBaseGoal()
    goal_pose.target_pose.header.frame_id = 'map'
    goal_pose.target_pose.pose.position.x = float(pose[0])
    goal_pose.target_pose.pose.position.y = float(pose[1])
    goal_pose.target_pose.pose.position.z = 0.0
    goal_pose.target_pose.pose.orientation.x = 0.0
    goal_pose.target_pose.pose.orientation.y = 0.0
    goal_pose.target_pose.pose.orientation.z = 0.0
    goal_pose.target_pose.pose.orientation.w = 1.0

    return goal_pose


if __name__ == '__main__':
    # ------------------------ INPUT ------------------------ #
    num_of_robot = sys.argv[1]
    print('######################### robot%s #########################' % num_of_robot)
    named_tuple_of_this_robot = get_named_tuple_of_robot(int(num_of_robot))

    robot_object = Robot(number_of_robot=named_tuple_of_this_robot.num,
                         cell_size=1, surf_center=named_tuple_of_this_robot.pos,
                         MR=named_tuple_of_this_robot.MR, SR=named_tuple_of_this_robot.SR,
                         cred=named_tuple_of_this_robot.cred, name=named_tuple_of_this_robot.name, cells=CELLS)
    # print('[SR] - %s' % robot_object.SR)
    READY_dict = create_empty_by_iteration_dict()
    CALC_READY_dict = create_empty_by_iteration_dict()
    MOVE_dict = create_empty_by_iteration_dict()
    # ------------------------------------------------------- #
    rospy.init_node('robot%s' % sys.argv[1])
    pub_READY_topic = rospy.Publisher('READY_topic', String, latch=True, queue_size=10)
    sub_READY_topic = rospy.Subscriber('READY_topic', String, callback_READY_topic)
    sub_CALC_READY_topic = rospy.Subscriber('CALC_READY_topic', String, callback_CALC_READY_topic)
    pub_MOVE_topic = rospy.Publisher('MOVE_topic', String, latch=True, queue_size=50)
    sub_MOVE_topic = rospy.Subscriber('MOVE_topic', String, callback_MOVE_topic)
    # sub_amcl = rospy.Subscriber('/agent%s/amcl_pose' % sys.argv[1], PoseWithCovarianceStamped, callback_amcl)
    rate = rospy.Rate(1)  # 1 second
    if MOVE_REAL_ROBOTS:
        print('[INFO] - before initializing SimpleActionClient')
        client = actionlib.SimpleActionClient('agent%s/move_base' % sys.argv[1], MoveBaseAction)
        client.wait_for_server()
        print('[INFO] - after initializing SimpleActionClient')

        print('[INFO] - before going to start_pose_to_go -> (%s, %s)' % (start_pose_to_go[0], start_pose_to_go[1]))
        client.send_goal(goal_pose(start_pose_to_go))
        client.wait_for_result()
        print('[INFO] - after going to start_pose_to_go')

        client.send_goal(goal_pose(named_tuple_of_this_robot.pos))
        client.wait_for_result()
        print('[INITIAL] - came to initial position')
    # move(0, named_tuple_of_this_robot.pos)

    # start(READY)
    for iteration in range(ITERATIONS_IN_BIG_LOOPS):
        print('# --------------------- iteration: %s (robot %s) --------------------- #' % (iteration, num_of_robot))
        wait(iteration)
        # prep(iteration)
        # calc_wait(iteration)
        next_pos = calc(iteration)
        if ONE_BY_ONE:
            move_wait(iteration)
        move(iteration, next_pos)
    finish()
