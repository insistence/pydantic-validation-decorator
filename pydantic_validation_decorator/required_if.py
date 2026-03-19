from asyncio import iscoroutinefunction
from functools import wraps
from typing import Any, Optional
from pydantic import BaseModel
from .exceptions import FieldValidationError


class RequiredIf:
    """
    Field Conditional Required Validation Decorator
    """

    def __init__(
        self,
        field_name: str,
        when_field: str,
        when_value: Any,
        message: Optional[str] = None,
    ):
        """Field Conditional Required Validation Decorator

        Args:
            field_name (str): Field name that needs to be validated.
            when_field (str): Condition field name used to trigger validation.
            when_value (Any): Trigger value for the condition field. Supports single value or collection.
            message (Optional[str], optional): Prompt message for validation failure. Defaults to None.
        """
        self.field_name = field_name
        self.when_field = when_field
        self.when_value = when_value
        self.message = message

    def _should_validate(self, value: Any) -> bool:
        """Determine whether conditional required validation should be triggered.

        Args:
            value (Any): Current value of the condition field.

        Returns:
            bool: True when the condition matches and required validation should run.
        """
        if isinstance(self.when_value, (list, tuple, set, frozenset)):
            return value in self.when_value
        return value == self.when_value

    def _is_empty(self, value: Any) -> bool:
        """Determine whether the target field should be treated as empty.

        Args:
            value (Any): Current value of the target field.

        Returns:
            bool: True when the value is considered empty for required validation.
        """
        return value is None or value == '' or value == [] or value == () or value == {}

    def __call__(self, func):
        is_async = iscoroutinefunction(func)
        if is_async:

            @wraps(func)
            async def wrapper(*args, **kwargs):
                validate_model = args[0]
                if (
                    isinstance(validate_model, BaseModel)
                    and hasattr(validate_model, self.field_name)
                    and hasattr(validate_model, self.when_field)
                ):
                    when_field_value = getattr(validate_model, self.when_field)
                    if self._should_validate(when_field_value):
                        field_value = getattr(validate_model, self.field_name)
                        if self._is_empty(field_value):
                            raise FieldValidationError(
                                model_name=validate_model.__class__.__name__,
                                field_name=self.field_name,
                                field_value=field_value,
                                validator=self.__class__.__name__,
                                message=(
                                    self.message
                                    if self.message
                                    else f'{self.field_name} is required when {self.when_field} is {self.when_value}.'
                                ),
                            )
                return await func(*args, **kwargs)

            return wrapper
        else:

            @wraps(func)
            def wrapper(*args, **kwargs):
                validate_model = args[0]
                if (
                    isinstance(validate_model, BaseModel)
                    and hasattr(validate_model, self.field_name)
                    and hasattr(validate_model, self.when_field)
                ):
                    when_field_value = getattr(validate_model, self.when_field)
                    if self._should_validate(when_field_value):
                        field_value = getattr(validate_model, self.field_name)
                        if self._is_empty(field_value):
                            raise FieldValidationError(
                                model_name=validate_model.__class__.__name__,
                                field_name=self.field_name,
                                field_value=field_value,
                                validator=self.__class__.__name__,
                                message=(
                                    self.message
                                    if self.message
                                    else f'{self.field_name} is required when {self.when_field} is {self.when_value}.'
                                ),
                            )
                return func(*args, **kwargs)

            return wrapper
