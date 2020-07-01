from pygame import *

class Inputer:
    def __init__(self, world):
        self.world = world

    def main_input(self):
        events = event.get()
        for evt in events:
            if evt.type == QUIT:
                return QUIT
            if evt.type == KEYDOWN:
                return evt.key

    def get_input(self):
        inp = self.main_input()
        input_dict = {K_UP: (0, -1), K_LEFT: (-1, 0),
                      K_DOWN: (0, 1), K_RIGHT: (1, 0), QUIT: 'quit',
                      K_RETURN: 'select', K_ESCAPE: 'log_out', K_n: 'next turn'}
        return input_dict.get(inp)


    def get_menu_input(self):
        inp = self.main_input()
        if inp == QUIT:
            return 'quit'
        input_dict = {K_UP: 'up', K_LEFT: 'up',
                      K_DOWN: 'down', K_RIGHT: 'down', QUIT: 'quit',
                      K_RETURN: 'select'}
        return input_dict.get(inp)


    def get_confirmation(self):
        inp = self.main_input()
        if inp == K_RETURN:
            return True
        else:
            return False

class SelectionMenu:
    def __init__(self, choices):
        self.choices = choices
        self.current_selection = 0

    def select_previous(self):
        self.current_selection = (self.current_selection - 1) % len(self.choices)

    def select_next(self):
        self.current_selection = (self.current_selection + 1) % len(self.choices)

    def select(self):
        return self.choices[self.current_selection]