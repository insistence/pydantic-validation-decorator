import re
from asyncio import iscoroutinefunction
from functools import wraps
from typing import Optional
from pydantic import BaseModel
from .exceptions import FieldValidationError


class Pattern:
    """
    Field Pattern Validation Decorator
    """

    def __init__(
        self,
        field_name: str,
        regexp: str,
        message: Optional[str] = None,
    ):
        """Field Pattern Validation Decorator

        Args:
            field_name (str): Field name that need to be validate.
            regexp (str): Regular expression.
            message (Optional[str], optional): Prompt message for validation failure. Defaults to None.
        """
        self.field_name = field_name
        self.regexp = regexp
        self.message = message

    def __call__(self, func):
        is_async = iscoroutinefunction(func)
        if is_async:

            @wraps(func)
            async def wrapper(*args, **kwargs):
                validate_model = args[0]
                if isinstance(validate_model, BaseModel) and hasattr(validate_model, self.field_name):
                    field_value = getattr(validate_model, self.field_name)
                    if isinstance(field_value, str) and not re.match(self.regexp, field_value):
                        raise FieldValidationError(
                            model_name=validate_model.__class__.__name__,
                            field_name=self.field_name,
                            field_value=field_value,
                            validator=self.__class__.__name__,
                            message=self.message if self.message else f'The format of {self.field_name} is incorrect.',
                        )
                return await func(*args, **kwargs)

            return wrapper

        else:

            @wraps(func)
            def wrapper(*args, **kwargs):
                validate_model = args[0]
                if isinstance(validate_model, BaseModel) and hasattr(validate_model, self.field_name):
                    field_value = getattr(validate_model, self.field_name)
                    if isinstance(field_value, str) and not re.match(self.regexp, field_value):
                        raise FieldValidationError(
                            model_name=validate_model.__class__.__name__,
                            field_name=self.field_name,
                            field_value=field_value,
                            validator=self.__class__.__name__,
                            message=self.message if self.message else f'The format of {self.field_name} is incorrect.',
                        )
                return func(*args, **kwargs)

            return wrapper
