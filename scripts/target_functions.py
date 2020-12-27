from CONSTANTS import *


def create_func_target(cells_near_me):
    def func_target(self, combination, order_of_nei):
        self.cells_near_me = cells_near_me
        count = 0
        domain_choice_of_var = combination[0]
        others = combination
        for i in others:
            if i in cells_near_me:
                count += 1
        if count == 0:
            return 0
        return max(0, min(REQ, CRED * count))

    return func_target