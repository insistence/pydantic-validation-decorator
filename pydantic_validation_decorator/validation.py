from asyncio import iscoroutinefunction
from functools import wraps
from pydantic import BaseModel
from typing import Literal, Optional
from .exceptions import FunctionTypeError


class ValidateFields:
    """
    Field Validation Decorator
    """

    def __init__(
        self,
        mode: Literal['args', 'kwargs'] = 'kwargs',
        validate_model: Optional[str] = None,
        validate_model_index: Optional[int] = None,
        validate_function: str = 'validate_fields',
    ):
        """_summary_

        Args:
            mode (Literal[&#39;args&#39;, &#39;kwargs&#39;]): How to obtain the model that needs to be validated.
            validate_model (str, optional): The name of the pydantic model that needs to be validated in the function.
            validate_model_index (int, optional): The index of the pydantic model that needs to be validated in the function.
            validate_function (str, optional): The name of the validation function defined in the pydantic model. Defaults to 'validate_fields'.

        Raises:
            ValueError: The validate_model_index cannot be empty in args mode. || The validate_model cannot be empty in kwargs mode.
        """
        if mode == 'args' and validate_model_index is None:
            raise ValueError('The validate_model_index cannot be empty in args mode.')
        elif mode == 'kwargs' and validate_model is None:
            raise ValueError('The validate_model cannot be empty in kwargs mode.')
        self.mode = mode
        self.validate_model = validate_model
        self.validate_model_index = validate_model_index
        self.validate_function = validate_function

    def __call__(self, func):
        is_async = iscoroutinefunction(func)
        if is_async:

            @wraps(func)
            async def wrapper(*args, **kwargs):
                if self.mode == 'args':
                    validate_model = args[self.validate_model_index]
                else:
                    validate_model = kwargs.get(self.validate_model)
                if isinstance(validate_model, BaseModel) and hasattr(validate_model, self.validate_function):
                    validate_function = getattr(
                        validate_model,
                        self.validate_function,
                    )
                    if callable(validate_function):
                        if iscoroutinefunction(validate_function):
                            await validate_function()
                        else:
                            validate_function()
                return await func(*args, **kwargs)

            return wrapper

        else:

            @wraps(func)
            def wrapper(*args, **kwargs):
                if self.mode == 'args':
                    validate_model = args[self.validate_model_index]
                else:
                    validate_model = kwargs.get(self.validate_model)
                if isinstance(validate_model, BaseModel) and hasattr(validate_model, self.validate_function):
                    validate_function = getattr(
                        validate_model,
                        self.validate_function,
                    )
                    if callable(validate_function):
                        if iscoroutinefunction(validate_function):
                            raise FunctionTypeError(
                                error=f'The current function {func.__name__}() is a synchronous function. The function {self.validate_function}() is an asynchronous function and cannot be used in synchronous functions.',
                                category=RuntimeWarning,
                            )
                        validate_function()
                return func(*args, **kwargs)

            return wrapper
