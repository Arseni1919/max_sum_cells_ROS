from CONSTANTS import *


def calc_weight(cell, robot):
    # return order_of_nei[i].rund / 10 * (self.num + 1)
    # return order_of_nei[i].rund / 10 * (self.num + 2)
    # return order_of_nei[i].num / 10 * (self.num + 1)
    # return order_of_nei[i].num / 10 * (self.num + order_of_nei[i].rund)
    # aaa = order_of_nei[i].rund / 10 * (self.num+100)
    # aaa = order_of_nei[i].rund * (self.num/order_of_nei[i].num + self.rund) / 10
    # val = round(order_of_nei[i].rund * (self.rund) * 10, 2)  # --> works
    val = round(cell.rund * robot.rund * 10, 3)
    # return round(cell.rund * robot.rund * 1, 3)
    return round(cell.rund * robot.rund * 10, 3)


def func_cell_zero(self, combination, order_of_nei):
    return 0


def func_cell(self, combination, order_of_nei):

    # if there are neighbours to the cell
    # if len(order_of_nei) <= 1:
    #     return 0
    counter = 0
    # if the cell itself chosen by more than one robot
    for item_and_how_many_of_it in collections.Counter(combination).items():
        # looking only on one item and it th cell itself
        if item_and_how_many_of_it[0] == self.num:
            counter = max(counter, item_and_how_many_of_it[1])
    if counter > 1:
        # return -30 * counter  # + (0.5 - random.random())
        return MINUS_INF

    # if the cell is even inside the combination
    if self.num in combination:
        i = combination.index(self.num)
        val = calc_weight(self, order_of_nei[i])
        return val
    return 0