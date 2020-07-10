from pygame import *
import math

class Displayer:
    def __init__(self, world, pointer, game):
        self.game = game
        self.world = world
        self.pointer = pointer

        self.tilew, self.tileh = image.load(
            'graphics/selector.png').get_rect().size

        init()
        self.screen = Screen(self)
        self.window = self.screen.get_window()

        self.menu_graphics = {}
        self.load_graphics()

        self.board = Board(self.world, self, self.game)


    def load_graphics(self):
        self.menu_graphics = {
            'menu': image.load('graphics/menu.png').convert_alpha(),
            'parchment': transform.scale(image.load('graphics/parchment.png').convert_alpha(), (500, 500)),
            'select_arrow': transform.scale(image.load('graphics/select_arrow.png').convert_alpha(), (80, 55))
            }
                           
        self.text = {'start_game': transform.scale(image.load('graphics/text/start_game.png').convert_alpha(), (180, 55)),
                     'Marius': transform.scale(image.load('graphics/text/Marius.png').convert_alpha(), (180, 55)),
                     'Sam': transform.scale(image.load('graphics/text/Sam.png').convert_alpha(), (100, 55)),
                     'Raphael': transform.scale(image.load('graphics/text/Raphael.png').convert_alpha(), (180, 55)),
                     'quit': transform.scale(image.load('graphics/text/quit.png').convert_alpha(), (150, 55)),
                     'save': transform.scale(image.load('graphics/text/save.png').convert_alpha(), (150, 55))}


    def display(self):
        self.window.fill((0, 0, 0))
        self.board.update()
        self.move_camera()
        self.window.blit(self.board.get_surface(), self.simple_conv(self.board.x, self.board.y))
        display.update()


    def display_menu(self):
        self.window.blit(self.menu_graphics['menu'], (0, 0))
        self.window.blit(self.menu_graphics['parchment'], (self.world.width/2, self.world.height/2))   

        spacing = 60
        selector_align = 50
        text_align = 150

        initial_spacing = 40
        choices = self.game.selection_menu.choices
        selection = self.game.selection_menu.current_selection
        for i, choice in enumerate(choices):
            self.window.blit(self.text[choice], 
                (text_align, initial_spacing + i * spacing))
        self.window.blit(self.menu_graphics['select_arrow'], 
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

    def simple_conv(self, x, y):
        return (x if y % 2 == 0 else x + 0.5) * self.tilew, 0.75 * y * self.tileh


class Screen:
    def __init__(self, displayer, width=1440, height=810):
        self.displayer = displayer
        self.width, self.height = width, height
        self.window = display.set_mode((self.width, self.height))

        game_icon = image.load('graphics/game_icon.png')
        display.set_icon(game_icon)
        display.set_caption('Warhammer Campaign Manager')

    def get_window(self):
        return self.window


class DisplayLayer:
    def __init__(self, world, displayer):
        self.world = world
        self.displayer = displayer
        self.ncol, self.nline = self.world.get_dimensions()

        self.tilew, self.tileh = image.load(
            'graphics/selector.png').get_rect().size

        self.surface = None

    def simple_conv(self, x, y):
        return (x if y % 2 == 0 else x + 0.5) * self.tilew, 0.75 * y * self.tileh

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

    def load_graphics(self):
        pass

    def make_empty_surface(self):
        tilew, tileh = self.displayer.tilew, self.displayer.tileh
        surface = Surface((self.ncol * tilew, self.nline * tileh))
        return surface

    def get_surface(self):
        return self.surface


class TerrainLayer(DisplayLayer):
    def __init__(self, world, displayer):
        super().__init__(world, displayer)

        self.surface = self.tile_up()
        self.tile_up()

    def tile_up(self):
        surface = self.make_empty_surface()
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
                surface.blit(
                    terrains[terrain], self.simple_conv(x, y))
        return surface


class CloudLayer(DisplayLayer):
    def __init__(self, world, displayer):
        super().__init__(world, displayer)

        self.fog = image.load('graphics/fog.png').convert_alpha()
        self.surface = self.tile_up().convert_alpha()
        # self.uncover()

    def tile_up(self):
        surface = self.make_empty_surface()

        for x in range(self.ncol):
            for y in range(self.nline):
                surface.blit(
                    self.fog, self.simple_conv(x, y))
        return surface

    def uncover(self, x=0, y=0):
        draw.circle(self.surface, (255, 255, 255, 0), (x, y), 200)

    def drawRegularPolygon(self, color, x, y, radius):
      pts = []
      for i in range(6):
        x = x + radius * math.cos(math.pi * 2/3 + math.pi * 2 * i / 6)
        y = y + radius * math.sin(math.pi * 2/3 + math.pi * 2 * i / 6)
        pts.append([int(x), int(y)])
      pygame.draw.polygon(self.surface, color, pts)



class Board(DisplayLayer):
    def __init__(self, world, displayer, game):
        super().__init__(world, displayer)
        self.game = game
        self.pointer = self.displayer.pointer

        self.world_tiles = [(x, y) for x in range(self.world.width)
                            for y in range(self.world.height)]

        self.terrain_layer = TerrainLayer(self.world, self.displayer).surface
        self.cloud_layer = CloudLayer(self.world, self.displayer)
        self.surface = self.make_empty_surface()

        self.x, self.y = 0, 0

        self.board_graphics = {}
        self.army_icons = {}
        self.load_graphics()

    def load_graphics(self):
        self.graphics = {'cursor': image.load('graphics/selector.png').convert_alpha(),
                         'highlight': image.load('graphics/selected.png').convert_alpha(),
                         'fog': image.load('graphics/fog.png').convert_alpha(),
                         'hide': image.load('graphics/hide.png').convert_alpha(),
                         }

        self.army_icons = {'Marius': image.load('graphics/Tyrion.png').convert_alpha(),
                           'Raphael': image.load('graphics/Orion.png').convert_alpha(),
                           'Sam': image.load('graphics/Archaon.png').convert_alpha()}

    def light_update(self):
        pass

    def update(self):
        self.surface.blit(self.terrain_layer, (0, 0))
        self.display_armies()
        # self.cloud_layer.uncover()
        # self.surface.blit(self.cloud_layer.surface, (0, 0))
        # self.hide_undiscovered()
        self.display_selector()

    def display_armies(self):
        for army in self.world.get_armies():
            if self.game.current_player.can_view(army.x, army.y):
                army_icon = self.army_icons[army.owner.name]
                self.surface.blit(army_icon, self.conv(army.x, army.y, centered=True, size=army_icon.get_rect().size))

    def display_selector(self):
        self.surface.blit(
                    self.graphics['cursor'],
                    self.conv(self.pointer.x, self.pointer.y))
        if self.pointer.selection is not None:
            self.surface.blit(
                self.graphics['highlight'],
                self.conv(self.pointer.selection[0], self.pointer.selection[1]))

    def hide_undiscovered(self):
        for (x, y) in self.world_tiles:
            if not self.game.current_player.has_discovered(x, y):
                self.surface.blit(self.graphics['fog'], self.conv(x, y))
            else :
                if not self.game.current_player.can_view(x, y):
                    self.surface.blit(self.graphics['hide'], self.conv(x, y))