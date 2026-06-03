import config
from geo import Point


class DeadBody:
    """동물이 죽으면 남는 사체. 시간이 지나면 부패해 사라진다.

    하이에나 등 청소동물(scavenger)의 먹이가 된다.
    """

    def __init__(self, location: Point, species: str, size: float):
        self.location = location
        self.species = species
        self.food = config.MEAT_PER_SIZE * size   # 남은 영양가
        self.decay = config.DEAD_BODY_DECAY        # 남은 부패 시간(초)

    @property
    def depleted(self) -> bool:
        return self.food <= 0.0 or self.decay <= 0.0

    def time_decay(self, dt_sec: float) -> None:
        self.decay -= dt_sec
