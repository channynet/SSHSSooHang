class Vector:
    def __init__(self, x, y):
        self.x = x
        self.y = y


class Point:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __sub__(self, other: "Point") -> "Vector":
        return Vector(self.x - other.x, self.y - other.y)
