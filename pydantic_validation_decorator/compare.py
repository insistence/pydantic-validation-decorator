from asyncio import iscoroutinefunction
from functools import wraps
from typing import Optional, Literal, Any, Callable, Dict
from pydantic import BaseModel
from .exceptions import FieldValidationError


class Compare:
    """
    Field Compare Validation Decorator
    """

    def __init__(
        self,
        left_field: str,
        right_field: str,
        operator: Literal['eq', 'ne', 'gt', 'ge', 'lt', 'le'] = 'eq',
        allow_none: bool = True,
        message: Optional[str] = None,
    ):
        """Field Compare Validation Decorator

        Args:
            left_field (str): Left field name used in comparison.
            right_field (str): Right field name used in comparison.
            operator (Literal['eq', 'ne', 'gt', 'ge', 'lt', 'le'], optional): Comparison operator. Defaults to 'eq'.
            allow_none (bool, optional): If True, skip validation when either field is None. Defaults to True.
            message (Optional[str], optional): Prompt message for validation failure. Defaults to None.
        """
        self.left_field = left_field
        self.right_field = right_field
        self.operator = operator
        self.allow_none = allow_none
        self.message = message
        self._operator_map: Dict[str, Callable[[Any, Any], bool]] = {
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
            left_value (Any): Current value of the left field.
            right_value (Any): Current value of the right field.

        Returns:
            str: Default error message with operator and actual values.
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

    def _validate_compare(self, validate_model: BaseModel):
        """Execute compare validation for the current model instance.

        Args:
            validate_model (BaseModel): Pydantic model instance under validation.

        Raises:
            FieldValidationError: Raised when comparison fails or values are not comparable.
        """
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

    def __call__(self, func):
        is_async = iscoroutinefunction(func)
        if is_async:

            @wraps(func)
            async def wrapper(*args, **kwargs):
                validate_model = args[0]
                if (
                    isinstance(validate_model, BaseModel)
                    and hasattr(validate_model, self.left_field)
                    and hasattr(validate_model, self.right_field)
                ):
                    self._validate_compare(validate_model)
                return await func(*args, **kwargs)

            return wrapper
        else:

            @wraps(func)
            def wrapper(*args, **kwargs):
                validate_model = args[0]
                if (
                    isinstance(validate_model, BaseModel)
                    and hasattr(validate_model, self.left_field)
                    and hasattr(validate_model, self.right_field)
                ):
                    self._validate_compare(validate_model)
                return func(*args, **kwargs)

            return wrapper
