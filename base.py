import abc


class Entity(abc.ABC):
    @abc.abstractmethod
    def behaviors(self) -> list["Behavior"]: ...


class Behavior(abc.ABC):
    @abc.abstractmethod
    def determine(self) -> bool: ...

    @abc.abstractmethod
    def act(self): ...
