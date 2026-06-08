"""여러 종이 공유하는 일반 행동들. 특정 종 고유의 스킬 행동은 각 species 파일에 둔다."""

import math
import random

import config
from base import Behavior
from geo import Point


def _wander_target(e, env) -> Point:
    """완만하게 바뀌는 방향으로 배회 목표점을 만든다."""
    e._wander_t = getattr(e, "_wander_t", 0.0) + env._dt
    if not hasattr(e, "_wander_angle") or e._wander_t > 2.0:
        e._wander_angle = random.uniform(0.0, 2 * math.pi)
        e._wander_t = 0.0
    direction = Point(math.cos(e._wander_angle), math.sin(e._wander_angle)) - Point(
        0.0, 0.0
    )
    return env.clamp(e.location + direction * 4.0)


class ProduceDung(Behavior):
    """모든 동물 공통: 주기적으로 현재 타일에 배설한다 (쇠똥구리의 먹이가 됨)."""

    def should_run(self, e, env) -> bool:
        return e.dung_timer >= config.DUNG_PRODUCE_SEC

    def act(self, e, env) -> None:
        e.produce_dung(env)


class Flee(Behavior):
    """주어진 포식자 클래스가 인지 범위에 들어오면 반대 방향으로 도망친다."""

    def __init__(self, target_classes):
        # 두려워하는 포식자 Animal 하위 클래스들 (isinstance용 튜플)
        self.target_classes = tuple(target_classes)

    def should_run(self, e, env) -> bool:
        if not self.target_classes:
            return False
        threat = env.nearest_animal(
            e.location,
            e.detection_range,
            lambda a: isinstance(a, self.target_classes),
        )
        e._threat = threat
        return threat is not None

    def act(self, e, env) -> None:
        mult = getattr(e, "flee_speed_mult", 1.0)
        e.step_away(e._threat.location, env, env._dt, mult)


class SeekWater(Behavior):
    """목이 마르면 가장 가까운 물 타일로 이동해 물을 마신다."""

    def should_run(self, e, env) -> bool:
        return e.water_ratio < config.THIRST_THRESHOLD and bool(env.water_tiles)

    def act(self, e, env) -> None:
        tile = env.nearest_tile(e.location, env.water_tiles)
        if tile is None:
            return
        if (
            e.location.distance_to(tile.center) < 0.8
            or env.tile_at(e.location).has_water()
        ):
            e.drink(tile if tile.has_water() else env.tile_at(e.location))
        else:
            e.step_toward(tile.center, env, env._dt)


class SeekPlantFood(Behavior):
    """초식동물이 배고프면 식물 타일로 이동해 식물을 먹는다."""

    def should_run(self, e, env) -> bool:
        return e.fullness_ratio < config.HUNGER_THRESHOLD and bool(env.plant_tiles)

    def act(self, e, env) -> None:
        tile = env.nearest_tile(e.location, env.plant_tiles)
        if tile is None:
            return
        if e.location.distance_to(tile.center) < 0.8:
            e.eat_plant(tile)
        else:
            e.step_toward(tile.center, env, env._dt)


class Hunt(Behavior):
    """포식자가 배고프면 주어진 사냥감 클래스를 추격해 포식한다."""

    def __init__(self, target_classes):
        # 사냥 대상 Animal 하위 클래스들 (isinstance용 튜플)
        self.target_classes = tuple(target_classes)

    def should_run(self, e, env) -> bool:
        if not self.target_classes or e.fullness_ratio >= config.HUNGER_THRESHOLD:
            return False
        target = env.nearest_animal(
            e.location,
            e.detection_range,
            lambda a: isinstance(a, self.target_classes) and not a.is_flying,
        )
        e._target = target
        return target is not None

    def act(self, e, env) -> None:
        target = e._target
        if not target.alive:
            return
        mult = e.hunt_speed_mult(target, env) if hasattr(e, "hunt_speed_mult") else 1.0
        if e.location.distance_to(target.location) <= config.CAPTURE_RADIUS:
            if self.capture_succeeds(e, target, env):
                e.eat_prey(target)
        else:
            e.step_toward(target.location, env, env._dt, mult)

    def capture_succeeds(self, e, target, env) -> bool:
        """사냥감의 회피 능력(점프/은폐 등)을 반영. 기본은 항상 성공."""
        return (
            target.is_caught_by(e, env)
            if hasattr(target, "is_caught_by")
            else True
        )


class Breed(Behavior):
    """잘 먹은 상태에서 같은 종의 다른 성별 개체가 가까이 있으면 번식한다."""

    def should_run(self, e, env) -> bool:
        if not e.can_breed():
            return False
        partner = env.nearest_animal(
            e.location,
            config.BREED_RADIUS,
            lambda a: type(a) is type(e) and a.gender != e.gender and a.can_breed(),
        )
        e._partner = partner
        # 한 쌍이 두 번 번식하지 않도록 한쪽(F)만 실행한다.
        return partner is not None and e.gender == "F"

    def act(self, e, env) -> None:
        e.breed_with(e._partner, env)


class Wander(Behavior):
    """할 일이 없을 때의 기본 배회 (가장 낮은 우선순위)."""

    def should_run(self, e, env) -> bool:
        return True

    def act(self, e, env) -> None:
        e.step_toward(_wander_target(e, env), env, env._dt, 0.5)
