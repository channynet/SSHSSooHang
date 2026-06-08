import config
from base import Entity, Behavior
from geo import Point


class Decay(Behavior):
    """시간이 지나면 사체가 부패한다."""

    def should_run(self, entity: "DeadBody", env) -> bool:
        return True

    def act(self, entity: "DeadBody", env) -> None:
        entity.decay -= env._dt


class DeadBody(Entity):
    """동물이 죽으면 남는 사체. 시간이 지나면 부패해 사라진다.

    필드 위의 다른 개체들처럼 Entity이며, 부패는 Decay 행동으로 표현된다.
    하이에나 등 청소동물(scavenger)의 먹이가 된다.
    """

    def __init__(self, location: Point, species: str, size: float):
        self.location = location
        self.species = species
        self.size = size
        self.food = config.MEAT_PER_SIZE * size  # 남은 영양가
        self.decay = config.DEAD_BODY_DECAY  # 남은 부패 시간(초)
        self._behaviors = [Decay()]

    def behaviors(self) -> list:
        return self._behaviors

    @property
    def depleted(self) -> bool:
        return self.food <= 0.0 or self.decay <= 0.0
