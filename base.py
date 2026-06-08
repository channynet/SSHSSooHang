import abc


class Entity(abc.ABC):
    @abc.abstractmethod
    def behaviors(self) -> list["Behavior"]:
        """매 프레임 평가될 행동 목록을 우선순위 순서로 반환."""
        ...


class Behavior(abc.ABC):
    """하나의 의사결정 단위. should_run()이 참이면 act()가 실행된다."""

    @abc.abstractmethod
    def should_run(self, entity: "Entity", env) -> bool:
        """이번 프레임에 이 행동을 실행할 조건인지 판단."""
        ...

    @abc.abstractmethod
    def act(self, entity: "Entity", env) -> None:
        """행동 실행. Animal의 기본 메서드들을 조합해 호출한다."""
        ...
