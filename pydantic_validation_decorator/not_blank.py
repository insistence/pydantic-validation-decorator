from pydantic import BaseModel

from ._decorators import FieldValidator
from .exceptions import FieldValidationError


class NotBlank(FieldValidator):
    """Field NotBlank Validation Decorator.

    Can validate required fields, or optional fields if they are set.
    """

    def __init__(
        self,
        field_name: str,
        allow_unset: bool | None = False,
        message: str | None = None,
    ) -> None:
        """Configure when to reject an empty field.

        Args:
            field_name: Name of the field to validate.
            allow_unset: If True, validation only runs when the optional field is explicitly
                provided. Defaults to False.
            message: Custom error message to use when validation fails.
        """
        self.field_name = field_name
        self.allow_unset = allow_unset
        self.message = message

    def _validate(self, validate_model: BaseModel) -> None:
        if not hasattr(validate_model, self.field_name):
            return
        if not self.allow_unset or self.field_name in validate_model.model_fields_set:
            field_value = getattr(validate_model, self.field_name)
            if field_value is None or field_value in ('', [], (), {}):
                raise FieldValidationError(
                    model_name=validate_model.__class__.__name__,
                    field_name=self.field_name,
                    field_value=field_value,
                    validator=self.__class__.__name__,
                    message=self.message if self.message else f'{self.field_name} cannot be empty.',
                )
