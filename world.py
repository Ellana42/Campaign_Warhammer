from random import choice, randrange


class World:
    def __init__(self, player_list=['Raphael', 'Sam', 'Marius']):

        self.player_list = player_list
        self.width, self.height = 30, 20
        self.number_armies = 5
        self.terrain_types = ['p', 'm', 'd', 'f', 'h']
        self.vision_range = 2
        self.players = {name: Player(name, self)
                        for name in self.player_list}
        self.tiles = {}
        self.armies = []
        self.generate_world()
        self.generate_armies()

    def generate_world(self):
        w, h = self.width, self.height
        self.tiles = {(x, y): Tile(x, y, choice(self.terrain_types))
                      for x in range(w) for y in range(h)}

    def generate_armies(self):
        for owner in self.players.values():
            for _ in range(self.number_armies):
                tile = self.random_tile()
                x, y = tile.get_coordinates()
                army = Army(owner, x, y)
                self.armies.append(army)
                owner.armies.append(army)
                tile.armies.append(army)

    def random_tile(self):
        return self.tiles[randrange(self.width), randrange(self.height)]

    def is_inside(self, x, y):
        return x in range(self.width) and y in range(self.height)

    def get_dimensions(self):
        return self.width, self.height

    def get_map(self):
        return self.tiles

    def get_players(self):
        return self.players

    def get_player(self, name):
        return self.players.get(name)

    def get_armies(self):
        return self.armies

    def nearby(self, x, y):
        if y % 2 == 1:
            theoretical_nearby = [(x, y), (x + 1, y), (x - 1, y),
                                  (x, y - 1), (x + 1, y - 1), (x, y + 1), (x + 1, y + 1)]
        else:
            theoretical_nearby = [(x, y), (x + 1, y), (x - 1, y),
                                  (x - 1, y - 1), (x, y - 1), (x - 1, y + 1), (x, y + 1)]
        nearby = set(
            slot for slot in theoretical_nearby if self.is_inside(slot[0], slot[1]))
        return nearby


class Tile:
    def __init__(self, x, y, terrain, armies=[]):
        self.x, self.y = x, y
        self.terrain = terrain
        self.armies = armies

    def get_terrain(self):
        return self.terrain

    def get_armies(self):
        return self.armies

    def move_out(self, army):
        self.armies.remove(army)

    def move_in(self, army):
        self.armies.append(army)

    def get_coordinates(self):
        return self.x, self.y


# --------------------------------------------------------------------------------------------


class Player:
    def __init__(self, name, world):
        self.name = name
        self.armies = []
        self.discovered_land = set()
        self.field_of_view = set()
        self.world = world

    def belongs(self, army):
        return army in self.armies

    def can_view(self, x, y):
        return (x, y) in self.field_of_view

    def has_discovered(self, x, y):
        return (x, y) in self.discovered_land

    def discover(self):
        self.field_of_view.clear()
        for army in self.armies:
            self.discovered_land |= self.world.nearby(army.x, army.y)
            self.field_of_view |= self.world.nearby(army.x, army.y)


class Army:
    def __init__(self, owner, x, y):
        self.owner = owner
        self.moves_left = 2
        self.x, self.y = x, y

    def move_to(self, x, y):
        distance = self.distance(self.x, self.y, x, y)
        if distance <= self.moves_left:
            self.moves_left -= distance
            self.x, self.y = x, y

    @classmethod
    def distance(cls, x, y, a, b):
        x = x if y % 2 == 0 else x + 0.5
        a = a if b % 2 == 0 else a + 0.5
        return int(abs(x - a)) + abs(y - b)

    def __str__(self):
        return ', '.join(str(self.x), str(self.y), str(self.moves_left))