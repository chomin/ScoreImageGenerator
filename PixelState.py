import enum


class StateType(enum.Enum):
    """
    個々のノーツを識別するために必要になる、現時点でのピクセルの状態を表す。
    """
    NONE = enum.auto()
    IN_TAP = enum.auto()  # NONE → IN_TAP → NONE
    IN_GREEN = enum.auto()  # start,tapend,middleのいずれかわからない状態。NONE　→ IN_GREEN →　？？
    IN_START = enum.auto()  # IN_GREEN → IN_START → NONE
    IN_TAP_END = enum.auto()
    IN_PINK = enum.auto()  # flick,flickendのいずれかわからない状態
    IN_FLICK = enum.auto()
    IN_FLICK_END = enum.auto()
    IN_MIDDLE = enum.auto()  # NONE → MIDDLE → NONE
    IN_YELLOW = enum.auto()  # tap, startのいずれか分からない状態


class SubStateType(enum.Enum):
    """
    左右の線上における、長押し緑の追跡状態を表す
    """
    NONE = enum.auto()
    FOLLOWING_LONG = enum.auto()


class FollowableDirection(enum.Enum):
    """
    （両手押しの急な横スライドのときに必要）
    """
    BOTH = enum.auto()
    TO_RIGHT = enum.auto()
    TO_LEFT = enum.auto()


class PixelState:

    def __init__(self, state: StateType, from_pixel_index: int):
        self.state = state
        self.left_state = SubStateType.NONE
        self.right_state = SubStateType.NONE
        self.from_pixel_index = from_pixel_index
        self.following_long_num = 0
        self.will_stop_following = False
        self.followable_direction = FollowableDirection.BOTH

    @property
    def state1(self):
        return self.state

    @state1.setter
    def state1(self, value):
        self.state = value

    @property
    def left_state1(self):
        return self.left_state

    @left_state1.setter
    def left_state1(self, value):
        self.left_state = value

    @property
    def right_state1(self):
        return self.right_state

    @right_state1.setter
    def right_state1(self, value):
        self.right_state = value

    @property
    def from_pixel_index1(self):
        return self.from_pixel_index

    @from_pixel_index1.setter
    def from_pixel_index1(self, value):
        self.from_pixel_index = value

    @property
    def following_long_num1(self):
        return self.following_long_num

    @following_long_num1.setter
    def following_long_num1(self, value):
        self.following_long_num = value

    @property
    def will_stop_following1(self):
        return self.will_stop_following

    @will_stop_following1.setter
    def will_stop_following1(self, value):
        self.will_stop_following = value

    @property
    def followable_direction1(self):
        return self.followable_direction

    @followable_direction1.setter
    def followable_direction1(self, value):
        self.followable_direction = value
