from typing import Any

from pydantic import BaseModel

from ._decorators import FieldValidator
from .exceptions import FieldValidationError


class AtLeastOneOf(FieldValidator):
    """Field At Least One Of Validation Decorator."""

    def __init__(
        self,
        fields: list[str],
        min_count: int = 1,
        message: str | None = None,
    ) -> None:
        """Require a minimum number of populated fields.

        Args:
            fields: Field names where at least min_count fields must be provided.
            min_count: Minimum number of fields that must be provided. Defaults to 1.
            message: Custom error message to use when validation fails.

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
            value: Current field value.

        Returns:
            True when the value is considered empty.
        """
        return value is None or value in ('', [], (), {})

    def _build_default_message(self) -> str:
        """Build the default validation message.

        Returns:
            Default validation message.
        """
        field_names = ', '.join(self.fields)
        return f'At least {self.min_count} of {field_names} must be provided.'

    def _validate(self, validate_model: BaseModel) -> None:
        """Execute AtLeastOneOf validation for the current model instance.

        Args:
            validate_model: Pydantic model instance under validation.

        Raises:
            FieldValidationError: Raised when fewer than min_count fields are provided.
        """
        if not all(hasattr(validate_model, field_name) for field_name in self.fields):
            return
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
