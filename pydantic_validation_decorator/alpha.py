from typing import Literal

from pydantic import BaseModel

from ._decorators import FieldValidator
from .exceptions import FieldValidationError


class Alpha(FieldValidator):
    """Field Alpha Validation Decorator."""

    def __init__(
        self,
        field_name: str,
        mode: Literal['upper', 'lower', 'mixed'] = 'mixed',
        message: str | None = None,
    ) -> None:
        """Configure letter and case validation for a field.

        Args:
            field_name: Name of the field to validate.
            mode: Use 'upper' for uppercase, 'lower' for lowercase, or 'mixed' for either case.
            message: Custom error message to use when validation fails.
        """
        self.field_name = field_name
        self.mode = mode
        self.message = message

    def _validate_alpha(self, value: str) -> bool:
        """Verify whether the string conforms to the alphabetic pattern requirements.

        Args:
            value: The string to be verified.

        Returns:
            Verify whether it has passed.
        """
        if not isinstance(value, str):
            return False

        if not value.isalpha():
            return False

        if self.mode == 'upper':
            return value.isupper()
        if self.mode == 'lower':
            return value.islower()
        # mixed mode
        return True

    def _get_default_message(self) -> str:
        """Obtain the default error message.

        Returns:
            Default error message.
        """
        mode_messages = {
            'upper': f'{self.field_name} must contain only uppercase letters.',
            'lower': f'{self.field_name} must contain only lowercase letters.',
            'mixed': f'{self.field_name} must contain only letters.',
        }
        return mode_messages[self.mode]

    def _validate(self, validate_model: BaseModel) -> None:
        if not hasattr(validate_model, self.field_name):
            return
        field_value = getattr(validate_model, self.field_name)
        if field_value is not None and not self._validate_alpha(field_value):
            raise FieldValidationError(
                model_name=validate_model.__class__.__name__,
                field_name=self.field_name,
                field_value=field_value,
                validator=self.__class__.__name__,
                message=self.message if self.message else self._get_default_message(),
            )
