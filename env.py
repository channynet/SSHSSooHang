from geo import Point
from base import Entity


class Env:
    def __init__(self):
        self.entity_loc: dict["Entity", Point] = {}

    def update(self, dt: float): ...
