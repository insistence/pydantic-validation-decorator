from asyncio import iscoroutinefunction
from functools import wraps
from typing import Any, Optional

from pydantic import BaseModel

from .exceptions import FieldValidationError


class AtLeastOneOf:
    """
    Field At Least One Of Validation Decorator
    """

    def __init__(
        self,
        fields: list[str],
        min_count: int = 1,
        message: Optional[str] = None,
    ):
        """Field At Least One Of Validation Decorator

        Args:
            fields (list[str]): Field names where at least min_count fields must be provided.
            min_count (int, optional): Minimum number of fields that must be provided. Defaults to 1.
            message (Optional[str], optional): Prompt message for validation failure. Defaults to None.

        Raises:
            ValueError: fields cannot be empty.
            ValueError: min_count must be greater than 0.
            ValueError: min_count cannot be greater than the number of fields.
        """
        if not fields:
            raise ValueError('fields cannot be empty.')
        if min_count <= 0:
            raise ValueError('min_count must be greater than 0.')
        if min_count > len(fields):
            raise ValueError('min_count cannot be greater than the number of fields.')
        self.fields = fields
        self.min_count = min_count
        self.message = message

    def _is_empty(self, value: Any) -> bool:
        """Determine whether the current value should be treated as empty.

        Args:
            value (Any): Current field value.

        Returns:
            bool: True when the value is considered empty.
        """
        return value is None or value == '' or value == [] or value == () or value == {}

    def _build_default_message(self) -> str:
        """Build the default validation message.

        Returns:
            str: Default validation message.
        """
        field_names = ', '.join(self.fields)
        return f'At least {self.min_count} of {field_names} must be provided.'

    def _validate_at_least_one_of(self, validate_model: BaseModel):
        """Execute AtLeastOneOf validation for the current model instance.

        Args:
            validate_model (BaseModel): Pydantic model instance under validation.

        Raises:
            FieldValidationError: Raised when fewer than min_count fields are provided.
        """
        field_values = {field_name: getattr(validate_model, field_name) for field_name in self.fields}
        provided_count = sum(0 if self._is_empty(field_value) else 1 for field_value in field_values.values())
        if provided_count < self.min_count:
            raise FieldValidationError(
                model_name=validate_model.__class__.__name__,
                field_name=', '.join(self.fields),
                field_value=field_values,
                validator=self.__class__.__name__,
                message=self.message if self.message else self._build_default_message(),
            )

    def __call__(self, func):
        is_async = iscoroutinefunction(func)
        if is_async:

            @wraps(func)
            async def wrapper(*args, **kwargs):
                validate_model = args[0]
                if isinstance(validate_model, BaseModel) and all(
                    hasattr(validate_model, field_name) for field_name in self.fields
                ):
                    self._validate_at_least_one_of(validate_model)
                return await func(*args, **kwargs)

            return wrapper
        else:

            @wraps(func)
            def wrapper(*args, **kwargs):
                validate_model = args[0]
                if isinstance(validate_model, BaseModel) and all(
                    hasattr(validate_model, field_name) for field_name in self.fields
                ):
                    self._validate_at_least_one_of(validate_model)
                return func(*args, **kwargs)

            return wrapper
