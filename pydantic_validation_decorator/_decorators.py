from abc import ABC, abstractmethod
from asyncio import iscoroutinefunction
from collections.abc import Callable
from functools import wraps
from typing import Any, ParamSpec, TypeVar, cast

from pydantic import BaseModel

P = ParamSpec('P')
R = TypeVar('R')


class FieldValidator(ABC):
    @abstractmethod
    def _validate(self, validate_model: BaseModel) -> None:
        """Check the fields of a model before calling the decorated method."""

    def __call__(self, func: Callable[P, R]) -> Callable[P, R]:
        if iscoroutinefunction(func):

            @wraps(func)
            async def async_wrapper(*args: P.args, **kwargs: P.kwargs) -> Any:
                model = args[0]
                if isinstance(model, BaseModel):
                    self._validate(model)
                return await func(*args, **kwargs)

            # The original coroutine function and its wrapper have the same awaited result.
            return cast('Callable[P, R]', async_wrapper)

        @wraps(func)
        def wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
            model = args[0]
            if isinstance(model, BaseModel):
                self._validate(model)
            return func(*args, **kwargs)

        return wrapper
