from typing import TYPE_CHECKING, Any, Literal

from pydantic import BaseModel

from ._decorators import FieldValidator
from .exceptions import FieldValidationError

if TYPE_CHECKING:
    from collections.abc import Callable


class Compare(FieldValidator):
    """Field Compare Validation Decorator."""

    def __init__(
        self,
        left_field: str,
        right_field: str,
        operator: Literal['eq', 'ne', 'gt', 'ge', 'lt', 'le'] = 'eq',
        allow_none: bool = True,
        message: str | None = None,
    ) -> None:
        """Configure a comparison between two model fields.

        Args:
            left_field: Left field name used in comparison.
            right_field: Right field name used in comparison.
            operator: Comparison to apply: 'eq', 'ne', 'gt', 'ge', 'lt', or 'le'. Defaults to 'eq'.
            allow_none: If True, skip validation when either field is None. Defaults to True.
            message: Custom error message to use when validation fails.
        """
        self.left_field = left_field
        self.right_field = right_field
        self.operator = operator
        self.allow_none = allow_none
        self.message = message
        self._operator_map: dict[str, Callable[[Any, Any], bool]] = {
            'eq': lambda left, right: left == right,
            'ne': lambda left, right: left != right,
            'gt': lambda left, right: left > right,
            'ge': lambda left, right: left >= right,
            'lt': lambda left, right: left < right,
            'le': lambda left, right: left <= right,
        }
        if self.operator not in self._operator_map:
            raise ValueError(
                "Unsupported operator. Available options are: 'eq', 'ne', 'gt', 'ge', 'lt', 'le'.",
            )

    def _build_default_message(self, left_value: Any, right_value: Any) -> str:
        """Build the default message for compare validation failure.

        Args:
            left_value: Current value of the left field.
            right_value: Current value of the right field.

        Returns:
            Default error message with operator and actual values.
        """
        operator_symbol_map = {
            'eq': '==',
            'ne': '!=',
            'gt': '>',
            'ge': '>=',
            'lt': '<',
            'le': '<=',
        }
        operator_symbol = operator_symbol_map[self.operator]
        return (
            f'{self.left_field} must satisfy '
            f'{self.left_field} {operator_symbol} {self.right_field}, '
            f'but got {left_value} and {right_value}.'
        )

    def _validate(self, validate_model: BaseModel) -> None:
        """Execute compare validation for the current model instance.

        Args:
            validate_model: Pydantic model instance under validation.

        Raises:
            FieldValidationError: Raised when comparison fails or values are not comparable.
        """
        if not hasattr(validate_model, self.left_field) or not hasattr(validate_model, self.right_field):
            return
        left_value = getattr(validate_model, self.left_field)
        right_value = getattr(validate_model, self.right_field)
        if self.allow_none and (left_value is None or right_value is None):
            return
        try:
            compare_result = self._operator_map[self.operator](left_value, right_value)
        except TypeError:
            compare_result = False
        if not compare_result:
            raise FieldValidationError(
                model_name=validate_model.__class__.__name__,
                field_name=self.left_field,
                field_value=left_value,
                validator=self.__class__.__name__,
                message=self.message if self.message else self._build_default_message(left_value, right_value),
            )
