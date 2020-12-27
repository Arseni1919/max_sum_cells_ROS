from CONSTANTS import *
from pure_functions import *


class VariableNode:
    def __init__(self, name, num, domain, pos):
        self.name = name
        self.num = num
        # print(f'{self.name}: {self.num}')
        self.domain = domain
        self.initial_pos = pos
        self.prev_pos = pos
        self.pos = pos
        self.future_pos = pos
        self.delay = 0
        self.neighbours = []
        self.targets_nearby = []
        self.message_box = {}
        if LOAD_PREVIOUS_POSITIONS:
            # self.rund = load_weight_of(self.name, file_name)['rund']
            self.pos = load_weight_of(self.name, FILE_NAME)['pos']
        else:
            self.rund = get_random_num()

    def get_pos(self):
        return self.pos

    def get_neighbour(self, n):
        for nei in self.neighbours:
            if nei.num == n:
                return nei

    def _create_message(self):
        message = {}
        for d in self.domain:
            message[d] = 0
        return message

    def send_message_to(self, func_node, iteration):
        message = self._create_message()

        if iteration > 0:
            for nei in self.neighbours:
                if nei.name != func_node.name:
                    past_message = self.message_box[iteration - 1][nei.name]
                    for d in self.domain:
                        message[d] += past_message[d]
        if FLATTEN:
            flatten_message(message)
        func_node.message_box[iteration][self.name] = message

    def update_rund(self):
        self.rund = get_random_num()

    def update_delay(self):
        if self.delay == 0:
            self.delay = DELAY_OF_COLLISION
        else:
            self.delay -= 1