from abc import ABC, abstractmethod

from fastapi import APIRouter


class RouterController(ABC):
    def __init__(self, route_prefix: str, *arsg, **kwargs) -> None: ...

    @abstractmethod
    def register_routes(self) -> APIRouter: ...
