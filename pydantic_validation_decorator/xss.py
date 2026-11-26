import re

from pydantic import BaseModel

from ._decorators import FieldValidator
from .exceptions import FieldValidationError
from .utils import StringUtils


class Xss(FieldValidator):
    """Field Xss Validation Decorator."""

    HTML_PATTERN = r'<(\S*?)[^>]*>.*?|<.*? />'

    def __init__(
        self,
        field_name: str,
        message: str | None = None,
    ) -> None:
        """Configure the field to check for HTML tags.

        Args:
            field_name: Name of the field to validate.
            message: Custom error message to use when validation fails.
        """
        self.field_name = field_name
        self.message = message

    def _validate(self, validate_model: BaseModel) -> None:
        if not hasattr(validate_model, self.field_name):
            return
        field_value = getattr(validate_model, self.field_name)
        if not StringUtils.is_blank(field_value) and field_value is not None:
            pattern = re.compile(self.HTML_PATTERN)
            if pattern.search(field_value):
                raise FieldValidationError(
                    model_name=validate_model.__class__.__name__,
                    field_name=self.field_name,
                    field_value=field_value,
                    validator=self.__class__.__name__,
                    message=self.message if self.message else f'{self.field_name} cannot contain script characters.',
                )
