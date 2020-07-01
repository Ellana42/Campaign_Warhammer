from inputer import Inputer, SelectionMenu
from displayer import Displayer
from world import World


class Game:
    def __init__(self):

        self.world = World()
        self.pointer = Pointer(self, self.world)
        self.displayer = Displayer(self.world, self.pointer, self)
        self.inputer = Inputer(self.world)
        self.selection_menu = SelectionMenu(['Marius', 'Sam', 'Raphael', 'quit'])

        self.current_player = None
        self.current_loop = self.log_menu
        self.running = True

        self.view_range = 1

    def play(self):
        while self.running:
            self.current_loop()

    def log_menu(self):
        self.displayer.display_menu()
        event = self.inputer.get_menu_input()
        if event is not None:
            if event == 'quit':
                self.running = False
            elif event == 'up':
                self.selection_menu.select_previous()
            elif event == 'down':
                self.selection_menu.select_next()
            elif event == 'select':
                choice = self.selection_menu.select()
                if choice == 'quit':
                    self.running = False
                else:
                    player = self.world.get_player(choice)
                    self.current_player = player
                    self.switch_screen(self.mvt_menu)

    def mvt_menu(self):
        self.current_player.discover()
        self.displayer.display()
        event = self.inputer.get_input()
        if event is not None:
            if event == 'quit':
                self.running = False
            elif event == 'select':
                self.pointer.click()
            elif event == 'log_out':
                self.switch_screen(self.log_menu)
            elif event == 'next turn':
                self.switch_screen(self.next_turn)
            else:
                self.pointer.move(event)

    def switch_screen(self, new_loop):
        self.last_loop = self.current_loop
        self.current_loop = new_loop

    def next_turn(self):
        confirmation = self.inputer.get_confirmation()
        if confirmation:
            self.reset_turn()
            self.switch_screen(self.log_menu)
        else:
            self.switch_screen(self.mvt_menu)

    def reset_turn(self):
        for army in self.world.armies.values():
            army.moves_left = 2
        print('Armies reset')

    def get_current_player(self):
        return self.current_player


# --------------------------------------------------------------------------------------------


class Pointer:
    def __init__(self, game, world):
        self.world = world
        self.game = game

        self.x, self.y = 0, 0
        self.selection = None

    def move(self, direction):
        if self.world.is_inside(self.x + direction[0], self.y + direction[1]):
            self.x += direction[0]
            self.y += direction[1]

    def click(self):
        if self.selection is None:
            self.selection = self.x, self.y
        else:
            for army in self.game.current_player.armies:
                if (army.x, army.y) == self.selection:
                    army.move_to(self.x, self.y)
            self.selection = None

    def is_pointer(self, x, y):
        return self.x == x and self.y == y


Game().play()
