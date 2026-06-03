import math


class Vector:
    def __init__(self, x: float, y: float):
        self.x = x
        self.y = y

    def __add__(self, other: "Vector") -> "Vector":
        return Vector(self.x + other.x, self.y + other.y)

    def __sub__(self, other: "Vector") -> "Vector":
        return Vector(self.x - other.x, self.y - other.y)

    def __mul__(self, scalar: float) -> "Vector":
        return Vector(self.x * scalar, self.y * scalar)

    __rmul__ = __mul__

    def __truediv__(self, scalar: float) -> "Vector":
        return Vector(self.x / scalar, self.y / scalar)

    def length(self) -> float:
        return math.hypot(self.x, self.y)

    def normalized(self) -> "Vector":
        length = self.length()
        if length < 1e-9:
            return Vector(0.0, 0.0)
        return Vector(self.x / length, self.y / length)

    def __repr__(self) -> str:
        return f"Vector({self.x:.2f}, {self.y:.2f})"


class Point:
    def __init__(self, x: float, y: float):
        self.x = x
        self.y = y

    def __sub__(self, other: "Point") -> "Vector":
        return Vector(self.x - other.x, self.y - other.y)

    def __add__(self, vec: "Vector") -> "Point":
        return Point(self.x + vec.x, self.y + vec.y)

    def distance_to(self, other: "Point") -> float:
        return math.hypot(self.x - other.x, self.y - other.y)

    def __repr__(self) -> str:
        return f"Point({self.x:.2f}, {self.y:.2f})"
