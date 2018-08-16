from enum import Enum, auto


class NoteType(Enum):
    TAP = auto()
    FLICK = auto()
    START = auto()
    MIDDLE = auto()
    TAP_END = auto()
    FLICK_END = auto()
    START2 = auto()
    MIDDLE2 = auto()
    TAP_END2 = auto()
    FLICK_END2 = auto()


class Note:

    def __init__(self, note_type: NoteType, pos: float, lane_num: int):

        self.note_type = note_type
        self.pos = pos
        self.lane_num = lane_num

    # def __lt__(self, other):
    #     return self.pos < other.pos
    def __repr__(self):
        return repr((self.note_type, self.pos, self.lane_num))

    @property
    def note_type1(self):
        return self.note_type

    @note_type1.setter
    def note_type1(self, value):
        self.note_type = value

    @property
    def pos1(self):
        return self.pos

    @pos1.setter
    def pos1(self, value):
        self.pos = value

    @property
    def lane_num1(self):
        return self.lane_num

    @lane_num1.setter
    def lane_num1(self, value):
        self.lane_num = value
