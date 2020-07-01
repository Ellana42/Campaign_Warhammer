from pygame import *

class Displayer:
    def __init__(self, world, pointer, game):
        self.game = game
        self.world = world
        self.pointer = pointer
        self.terrain_skins = {}

        self.tilew, self.tileh = image.load(
            'graphics/selector.png').get_rect().size

        init()
        self.screen = Screen(self)
        self.window = self.screen.get_window()

        self.graphics = {}
        self.army_icons = {}
        self.load_graphics()

        self.board = Board(self.world, self)
        self.board_surf = self.board.get_surface()

        self.world_tiles = [(x, y) for x in range(self.world.width)
                            for y in range(self.world.height)]

    def load_graphics(self):
        self.graphics = {'cursor': image.load('graphics/selector.png').convert_alpha(),
                         'highlight': image.load('graphics/selected.png').convert_alpha(),
                         'fog': image.load('graphics/fog.png').convert_alpha(),
                         'hide': image.load('graphics/hide.png').convert_alpha(),
                         'menu': image.load('graphics/menu.png').convert_alpha(),
                         'parchment': transform.scale(image.load('graphics/parchment.png').convert_alpha(), (500, 500)),
                         'select_arrow': transform.scale(image.load('graphics/select_arrow.png').convert_alpha(), (80, 55))}

        self.army_icons = {'Marius': image.load('graphics/Tyrion.png').convert_alpha(),
                           'Raphael': image.load('graphics/Orion.png').convert_alpha(),
                           'Sam': image.load('graphics/Archaon.png').convert_alpha()}
                           
        self.text = {'start_game': transform.scale(image.load('graphics/text/start_game.png').convert_alpha(), (180, 55)),
                     'Marius': transform.scale(image.load('graphics/text/Marius.png').convert_alpha(), (180, 55)),
                     'Sam': transform.scale(image.load('graphics/text/Sam.png').convert_alpha(), (100, 55)),
                     'Raphael': transform.scale(image.load('graphics/text/Raphael.png').convert_alpha(), (180, 55)),
                     'quit': transform.scale(image.load('graphics/text/quit.png').convert_alpha(), (150, 55)),
                     'save': transform.scale(image.load('graphics/text/save.png').convert_alpha(), (150, 55))}

    def display(self):
        self.window.fill((0, 0, 0))
        self.move_camera()
        self.window.blit(self.board_surf, self.simple_conv(
            self.board.x, self.board.y))

        if self.pointer.selection is not None:
            self.board.display_on_board(
                self.graphics['highlight'],
                self.pointer.selection[0], 
                self.pointer.selection[1])

        self.display_armies()
        # self.hide_out_of_view()
        # self.hide_undiscovered()
        self.board.display_on_board(
            self.graphics['cursor'],
            self.pointer.x, 
            self.pointer.y)
        display.update()

    def display_menu(self):
        self.window.blit(self.graphics['menu'], (0, 0))
        self.window.blit(self.graphics['parchment'], (self.world.width/2, self.world.height/2))   

        spacing = 60
        selector_align = 50
        text_align = 150

        initial_spacing = 40
        choices = self.game.selection_menu.choices
        selection = self.game.selection_menu.current_selection
        for i, choice in enumerate(choices):
            self.window.blit(self.text[choice], 
                (text_align, initial_spacing + i * spacing))
        self.window.blit(self.graphics['select_arrow'], 
            (selector_align, initial_spacing + selection * spacing))

        display.update()

    def move_camera(self):
        if self.pointer.x + self.board.x < 1 and self.board.x < 0:
            self.board.x += 1
        if self.pointer.x + self.board.x > 6:
            self.board.x -= 1
        if self.pointer.y + self.board.y < 1 and self.board.y < 0:
            self.board.y += 1
        if self.pointer.y + self.board.y > 4:
            self.board.y -= 1

    def display_armies(self):
        for army in self.world.get_armies():
            if self.game.current_player.can_view(army.x, army.y):
                army_icon = self.army_icons[army.owner.name]
                self.board.display_on_board(army_icon, army.x, army.y, centered=True, size=army_icon.get_rect().size)

    def hide_undiscovered(self):
        for (x, y) in self.world_tiles:
            if not self.game.current_player.has_discovered(x, y):
                self.window.blit(self.graphics['fog'], self.conv(x, y))

    def hide_out_of_view(self):
        for (x, y) in self.world_tiles:
            if self.game.current_player.has_discovered(x, y):
                if not self.game.current_player.can_view(x, y):
                    self.window.blit(self.graphics['hide'], self.conv(x, y))

    # Conversion tools ======================================================

    def simple_conv(self, x, y):
        return (x if y % 2 == 0 else x + 0.5) * self.tilew, 0.75 * y * self.tileh

    # def conv(self, x, y):
    #     x += self.board.x
    #     y += self.board.y
    #     return (x if y % 2 == 0 else x + 0.5) * self.tilew, 0.75 * y * self.tileh

    def conv_center(self, size, x, y):
        convx, convy = self.conv(x, y)
        imw, imh = size
        convx += int(0.5 * self.tilew - 0.5 * imw)
        convy += int(0.5 * self.tileh - 0.5 * imh)
        return convx, convy

    def conv(self, x, y, centered=False, size=None):
        x, y = (x if y % 2 == 0 else x + 0.5) * self.tilew, 0.75 * y * self.tileh
        if not centered:
            return x, y
        else:
            width, height = size
            x += int(0.5 * self.tilew - 0.5 * width)
            y += int(0.5 * self.tileh - 0.5 * height)
            return x, y


class Screen:
    def __init__(self, displayer, width=1440, height=810):
        self.displayer = displayer

        self.tilew, self.tileh = self.displayer.tilew, self.displayer.tileh
        self.width, self.height = width, height

        self.window = display.set_mode((self.width, self.height))

        game_icon = image.load('graphics/game_icon.png')
        display.set_icon(game_icon)
        display.set_caption('Warhammer Campaign Manager')

    def get_window(self):
        return self.window


class Board:
    def __init__(self, world, displayer):
        self.world = world
        self.displayer = displayer
        self.ncol, self.nline = self.world.get_dimensions()

        self.simple_conv = self.displayer.simple_conv
        self.conv = self.displayer.conv

        self.x, self.y = 0,0
        self.buffer_size = 1

        self.surface = self.make_empty_surface()
        self.tile_up()

    def tile_up(self):
        terrains = {
            'p': image.load('graphics/plain.png').convert_alpha(),
            'm': image.load('graphics/mountain.png').convert_alpha(),
            'd': image.load('graphics/desert.png').convert_alpha(),
            'f': image.load('graphics/forest.png').convert_alpha(),
            'h': image.load('graphics/hills.png').convert_alpha()
        }
        for x in range(self.ncol):
            for y in range(self.nline):
                terrain = self.world.get_map()[x, y].get_terrain()
                self.surface.blit(
                    terrains[terrain], self.simple_conv(x, y))

    def make_empty_surface(self):
        tilew, tileh = self.displayer.tilew, self.displayer.tileh
        surface = Surface((self.ncol * tilew, self.nline * tileh))
        return surface

    def get_surface(self):
        return self.surface

    def display_on_board(self, image, x, y, centered=False, size=None):
        self.surface.blit(
            image, self.conv(x, y, centered, size))



