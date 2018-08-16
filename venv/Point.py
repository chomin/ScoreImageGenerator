import sys


class Point:

    def __init__(self, x_init: int, y_init: int):

        self.x: int = x_init
        self.y: int = y_init

    @property
    def x1(self) -> int:
        return self.x

    @x1.setter
    def x1(self, value):
        self.x: int = value

    @property
    def y1(self) -> int:
        return self.y

    @y1.setter
    def y1(self, value):
        self.y: int = value

    @classmethod
    def sum(cls, a, b):

        return Point(a.x + b.x, a.y + b.y)
