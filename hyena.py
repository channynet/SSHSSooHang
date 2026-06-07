"""담당: 박시은"""

import config
from animal import Animal
from base import Behavior
from behaviors import ProduceDung, Flee, Hunt, SeekWater, Breed, Wander


class StealFood(Behavior):
    """식량을 비축하는 주어진 종(치타/사자)에게서 식량을 빼앗는다."""

    def __init__(self, target_classes):
        # 비축 식량을 노릴 Animal 하위 클래스들 (isinstance용 튜플)
        self.target_classes = tuple(target_classes)

    def determine(self, e, env) -> bool:
        if e.hunger_ratio >= config.HUNGER_THRESHOLD:
            return False
        target = env.nearest_animal(
            e.location,
            e.detection_range,
            lambda a: isinstance(a, self.target_classes) and a.food_store > 0.0,
        )
        e._steal_target = target
        return target is not None

    def act(self, e, env) -> None:
        t = e._steal_target
        if e.location.distance_to(t.location) <= config.INTERACT_RADIUS:
            stolen = t.food_store
            t.food_store = 0.0
            e.fullness = min(e.max_fullness, e.fullness + stolen)
            print(f"하이에나가 {t.species}의 비축 식량을 빼앗았습니다.")
        else:
            e.step_toward(t.location, env, env._dt, e.hunt_speed_mult(t, env))


class Scavenge(Behavior):
    """사체를 먹는다 (eat_dead_body)."""

    def determine(self, e, env) -> bool:
        if e.hunger_ratio >= config.HUNGER_THRESHOLD:
            return False
        body = env.nearest_dead_body(e.location, e.detection_range)
        e._body = body
        return body is not None

    def act(self, e, env) -> None:
        b = e._body
        if e.location.distance_to(b.location) <= config.INTERACT_RADIUS:
            taken = min(b.food, config.MEAT_PER_SIZE)
            b.food -= taken
            e.fullness = min(e.max_fullness, e.fullness + taken)
        else:
            e.step_toward(b.location, env, env._dt)


class Hyena(Animal):
    species = "hyena"
    color = (160, 140, 90)
    base_speed = 2.3
    size = 1.5
    detection_range = 8.0

    def hunt_speed_mult(self, target, env) -> float:
        # dash(skill): 스태미나가 있는 동안 한 번에 더 많은 타일 이동
        if self.stamina > 15.0:
            self.stamina = max(
                0.0, self.stamina - config.SPRINT_STAMINA_COST * 0.7 * env._dt
            )
            return 1.9
        return 1.0

    def build_behaviors(self) -> list:
        from lion import Lion
        from cheetah import Cheetah
        from zebra import Zebra
        from rabbit import Rabbit

        return [
            ProduceDung(),
            Flee(target_classes=[Lion]),
            SeekWater(),
            StealFood(target_classes=[Cheetah, Lion]),
            Scavenge(),
            Hunt(target_classes=[Zebra, Rabbit]),
            Breed(),
            Wander(),
        ]
