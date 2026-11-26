from asyncio import iscoroutinefunction
from collections.abc import Callable, Mapping
from functools import wraps
from typing import Any, Literal, cast

from pydantic import BaseModel

from ._decorators import P, R
from .exceptions import FunctionTypeError


class ValidateFields:
    """Field Validation Decorator."""

    def __init__(
        self,
        mode: Literal['args', 'kwargs'] = 'kwargs',
        validate_model: str | None = None,
        validate_model_index: int | None = None,
        validate_function: str = 'validate_fields',
    ) -> None:
        """Choose the model argument and validation method to call.

        Args:
            mode: Use 'args' to find the model by position or 'kwargs' to find it by name.
            validate_model: The name of the pydantic model that needs to be validated in the
                function.
            validate_model_index: The index of the pydantic model that needs to be validated in the
                function.
            validate_function: The name of the validation function defined in the pydantic model.
                Defaults to 'validate_fields'.

        Raises:
            ValueError: If the selected mode is missing its model index or keyword name.
        """
        if mode == 'args' and validate_model_index is None:
            raise ValueError('The validate_model_index cannot be empty in args mode.')
        if mode == 'kwargs' and validate_model is None:
            raise ValueError('The validate_model cannot be empty in kwargs mode.')
        self.mode = mode
        self.validate_model = validate_model
        self.validate_model_index = validate_model_index
        self.validate_function = validate_function

    def _get_validator(self, args: tuple[object, ...], kwargs: Mapping[str, object]) -> Callable[[], Any] | None:
        if self.mode == 'args':
            if self.validate_model_index is None:
                raise ValueError('The validate_model_index cannot be empty in args mode.')
            model = args[self.validate_model_index]
        else:
            model = kwargs.get(self.validate_model) if self.validate_model is not None else None
        if isinstance(model, BaseModel):
            validator = getattr(model, self.validate_function, None)
            if callable(validator):
                return validator
        return None

    def __call__(self, func: Callable[P, R]) -> Callable[P, R]:
        if iscoroutinefunction(func):

            @wraps(func)
            async def async_wrapper(*args: P.args, **kwargs: P.kwargs) -> Any:
                validator = self._get_validator(args, kwargs)
                if validator is not None:
                    if iscoroutinefunction(validator):
                        await validator()
                    else:
                        validator()
                return await func(*args, **kwargs)

            return cast('Callable[P, R]', async_wrapper)

        @wraps(func)
        def wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
            validator = self._get_validator(args, kwargs)
            if validator is not None:
                if iscoroutinefunction(validator):
                    name = getattr(func, '__name__', type(func).__name__)
                    raise FunctionTypeError(
                        error=f'The current function {name}() is a synchronous function. '
                        f'The function {self.validate_function}() is an asynchronous function and cannot be used in synchronous functions.',
                        category=RuntimeWarning,
                    )
                validator()
            return func(*args, **kwargs)

        return wrapper
