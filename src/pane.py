from .gamestate import GameState
from .utils import config

# (TODO): choose a better class name later
class Wrapper:

    def __init__(self, cls, screen, coords):
        super().__init__()
        self.cls = cls
        self.screen = screen
        self.coords = coords

    def translateCoordinateX(self, x):
        if isinstance(x, float): # percentage
            return self.coords[0] + self.coords[2] * x
        else: # raw coordinate
            return self.coords[0] + x

    def translateCoordinateY(self, y):
        if isinstance(y, float):
            return self.coords[1] + self.coords[3] * y
        else:
            return self.coords[1] + y

    def scaleLengthX(self, x):
        if isinstance(x, float):
            return self.coords[2] * x
        else:
            return x

    def scaleLengthY(self, y):
        if isinstance(y, float):
            return self.coords[3] * y
        else:
            return y

    def transformCoordinates(self, coords):
        if isinstance(coords[0], tuple):
            return list(map(
                lambda cc: (self.translateCoordinateX(cc[0]), self.translateCoordinateY(cc[1])),
                coords
            ))
        else:
            return self.translateCoordinateX(coords[0]), self.translateCoordinateY(coords[1])

    def rect(self, colour, coords):
        pos, dim = coords
        true_coords = (
            (self.translateCoordinateX(pos[0]), self.translateCoordinateY(pos[1])),
            (self.scaleLengthX(dim[0]), self.scaleLengthY(dim[1]))
        )
        rect = self.cls.Rect(true_coords)
        self.cls.draw.rect(self.screen, colour, rect)

    def line(self, colour, coords):
        st, ed = coords
        true_coords = self.transformCoordinates(coords)
        self.cls.draw.line(self.screen, colour, true_coords[0], true_coords[1])

    def polygon(self, colour, coords, width=None):
        true_coords = self.transformCoordinates(coords)
        if width is None:
            self.cls.draw.polygon(self.screen, colour, true_coords)
        else:
            self.cls.draw.polygon(self.screen, colour, true_coords, width=width)


class Pane:

    # (TODO): -allow state to be initialized to opponent's board
    #         -allow passing in game mode
    def __init__(self, cls, coordinates, screen, subpanes=[]):
        self.cls = cls
        self.coordinates = coordinates
        self.screen = screen
        self.panes = subpanes
        self.state = GameState(
            cls,
            Wrapper(cls, screen, coordinates)
        )

    def render(self, events=[]):
        # render its own state and then its children
        self.screen.fill(config.black)
        self.state.render(events)
        for pane in self.panes:
            pane.render(events)

