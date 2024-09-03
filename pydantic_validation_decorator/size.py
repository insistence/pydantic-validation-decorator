from asyncio import iscoroutinefunction
from functools import wraps
from typing import Optional, Union
from pydantic import BaseModel
from .exceptions import FieldValidationError


class Size:
    """
    Field Size Validation Decorator
    """

    def __init__(
        self,
        field_name: str,
        gt: Optional[Union[float, int]] = None,
        ge: Optional[Union[float, int]] = None,
        lt: Optional[Union[float, int]] = None,
        le: Optional[Union[float, int]] = None,
        min_length: Optional[int] = 0,
        max_length: Optional[int] = None,
        message: Optional[str] = None,
    ):
        """Field Size Validation Decorator

        Args:
            field_name (str): Field name that need to be validate.
            gt (Optional[Union[float, int]], optional): The numerical field value must be greater than gt. Defaults to None.
            ge (Optional[Union[float, int]], optional): The numerical field value must be greater than or equal to ge. Defaults to None.
            lt (Optional[Union[float, int]], optional): The numerical field value must be less than lt. Defaults to None.
            le (Optional[Union[float, int]], optional): The numerical field value must be less than or equal to le. Defaults to None.
            min_length (Optional[int], optional): The length of a string field cannot be less than min_length. Defaults to 0.
            max_length (Optional[int], optional): The length of a string field cannot be greater than max_length. Defaults to None.
            message (Optional[str], optional): Prompt message for validation failure. Defaults to None.
        """
        self.field_name = field_name
        self.gt = gt
        self.ge = ge
        self.lt = lt
        self.le = le
        self.min_length = min_length if min_length >= 0 else 0
        self.max_length = max_length
        self.message = message

    def __call__(self, func):
        is_async = iscoroutinefunction(func)
        if is_async:

            @wraps(func)
            async def wrapper(*args, **kwargs):
                validate_model = args[0]
                if isinstance(validate_model, BaseModel) and hasattr(validate_model, self.field_name):
                    field_value = getattr(validate_model, self.field_name)
                    if isinstance(field_value, (int, float)):
                        if self.gt is not None and field_value <= self.gt:
                            raise FieldValidationError(
                                model_name=validate_model.__class__.__name__,
                                field_name=self.field_name,
                                field_value=field_value,
                                validator=self.__class__.__name__,
                                message=self.message
                                if self.message
                                else f'{self.field_name} must be greater than {self.gt}.',
                            )
                        elif self.ge is not None and field_value < self.ge:
                            raise FieldValidationError(
                                model_name=validate_model.__class__.__name__,
                                field_name=self.field_name,
                                field_value=field_value,
                                validator=self.__class__.__name__,
                                message=self.message
                                if self.message
                                else f'{self.field_name} must be greater than or equal to {self.ge}.',
                            )
                        elif self.lt is not None and field_value >= self.lt:
                            raise FieldValidationError(
                                model_name=validate_model.__class__.__name__,
                                field_name=self.field_name,
                                field_value=field_value,
                                validator=self.__class__.__name__,
                                message=self.message
                                if self.message
                                else f'{self.field_name} must be less than {self.lt}.',
                            )
                        elif self.le is not None and field_value > self.le:
                            raise FieldValidationError(
                                model_name=validate_model.__class__.__name__,
                                field_name=self.field_name,
                                field_value=field_value,
                                validator=self.__class__.__name__,
                                message=self.message
                                if self.message
                                else f'{self.field_name} must be less than or equal to {self.le}.',
                            )
                    elif isinstance(field_value, str):
                        if len(field_value) < self.min_length:
                            raise FieldValidationError(
                                model_name=validate_model.__class__.__name__,
                                field_name=self.field_name,
                                field_value=field_value,
                                validator=self.__class__.__name__,
                                message=self.message
                                if self.message
                                else f'The length of {self.field_name} cannot be less than {self.min_length}.',
                            )
                        elif self.max_length is not None and len(field_value) > self.max_length:
                            raise FieldValidationError(
                                model_name=validate_model.__class__.__name__,
                                field_name=self.field_name,
                                field_value=field_value,
                                validator=self.__class__.__name__,
                                message=self.message
                                if self.message
                                else f'The length of {self.field_name} cannot be greater than {self.max_length}.',
                            )
                return await func(*args, **kwargs)

            return wrapper

        else:

            @wraps(func)
            def wrapper(*args, **kwargs):
                validate_model = args[0]
                if isinstance(validate_model, BaseModel) and hasattr(validate_model, self.field_name):
                    field_value = getattr(validate_model, self.field_name)
                    if isinstance(field_value, (int, float)):
                        if self.gt is not None and field_value <= self.gt:
                            raise FieldValidationError(
                                model_name=validate_model.__class__.__name__,
                                field_name=self.field_name,
                                field_value=field_value,
                                validator=self.__class__.__name__,
                                message=self.message
                                if self.message
                                else f'{self.field_name} must be greater than {self.gt}.',
                            )
                        elif self.ge is not None and field_value < self.ge:
                            raise FieldValidationError(
                                model_name=validate_model.__class__.__name__,
                                field_name=self.field_name,
                                field_value=field_value,
                                validator=self.__class__.__name__,
                                message=self.message
                                if self.message
                                else f'{self.field_name} must be greater than or equal to {self.ge}.',
                            )
                        elif self.lt is not None and field_value >= self.lt:
                            raise FieldValidationError(
                                model_name=validate_model.__class__.__name__,
                                field_name=self.field_name,
                                field_value=field_value,
                                validator=self.__class__.__name__,
                                message=self.message
                                if self.message
                                else f'{self.field_name} must be less than {self.lt}.',
                            )
                        elif self.le is not None and field_value > self.le:
                            raise FieldValidationError(
                                model_name=validate_model.__class__.__name__,
                                field_name=self.field_name,
                                field_value=field_value,
                                validator=self.__class__.__name__,
                                message=self.message
                                if self.message
                                else f'{self.field_name} must be less than or equal to {self.le}.',
                            )
                    elif isinstance(field_value, str):
                        if len(field_value) < self.min_length:
                            raise FieldValidationError(
                                model_name=validate_model.__class__.__name__,
                                field_name=self.field_name,
                                field_value=field_value,
                                validator=self.__class__.__name__,
                                message=self.message
                                if self.message
                                else f'The length of {self.field_name} cannot be less than {self.min_length}.',
                            )
                        elif self.max_length is not None and len(field_value) > self.max_length:
                            raise FieldValidationError(
                                model_name=validate_model.__class__.__name__,
                                field_name=self.field_name,
                                field_value=field_value,
                                validator=self.__class__.__name__,
                                message=self.message
                                if self.message
                                else f'The length of {self.field_name} cannot be greater than {self.max_length}.',
                            )
                return func(*args, **kwargs)

            return wrapper
