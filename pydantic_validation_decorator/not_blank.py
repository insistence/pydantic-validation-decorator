from asyncio import iscoroutinefunction
from functools import wraps
from pydantic import BaseModel
from typing import Optional
from .exceptions import FieldValidationError


class NotBlank:
    """
    Field NotBlank Validation Decorator
    """

    def __init__(
        self,
        field_name: str,
        message: Optional[str] = None,
    ):
        """Field NotBlank Validation Decorator

        Args:
            field_name (str): Field name that need to be validate.
            message (Optional[str], optional): Prompt message for validation failure. Defaults to None.
        """
        self.field_name = field_name
        self.message = message

    def __call__(self, func):
        is_async = iscoroutinefunction(func)
        if is_async:

            @wraps(func)
            async def wrapper(*args, **kwargs):
                validate_model = args[0]
                if isinstance(validate_model, BaseModel) and hasattr(validate_model, self.field_name):
                    field_value = getattr(validate_model, self.field_name)
                    if (
                        field_value is None
                        or field_value == ''
                        or field_value == []
                        or field_value == ()
                        or field_value == {}
                    ):
                        raise FieldValidationError(
                            model_name=validate_model.__class__.__name__,
                            field_name=self.field_name,
                            field_value=field_value,
                            validator=self.__class__.__name__,
                            message=self.message if self.message else f'{self.field_name} cannot be empty.',
                        )
                return await func(*args, **kwargs)

            return wrapper
        else:

            @wraps(func)
            def wrapper(*args, **kwargs):
                validate_model = args[0]
                if isinstance(validate_model, BaseModel) and hasattr(validate_model, self.field_name):
                    field_value = getattr(validate_model, self.field_name)
                    if (
                        field_value is None
                        or field_value == ''
                        or field_value == []
                        or field_value == ()
                        or field_value == {}
                    ):
                        raise FieldValidationError(
                            model_name=validate_model.__class__.__name__,
                            field_name=self.field_name,
                            field_value=field_value,
                            validator=self.__class__.__name__,
                            message=self.message if self.message else f'{self.field_name} cannot be empty.',
                        )
                return func(*args, **kwargs)

            return wrapper
