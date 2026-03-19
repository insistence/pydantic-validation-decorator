import json
from asyncio import iscoroutinefunction
from functools import wraps
from typing import Optional, Any
from pydantic import BaseModel
from .exceptions import FieldValidationError


class JsonString:
    """
    Field JSON String Validation Decorator
    """

    def __init__(
        self,
        field_name: str,
        require_object: bool = False,
        require_array: bool = False,
        max_depth: Optional[int] = None,
        allow_none: bool = True,
        message: Optional[str] = None,
    ):
        """Field JSON String Validation Decorator

        Args:
            field_name (str): Field name that needs to be validated.
            require_object (bool, optional): Require parsed JSON to be an object. Defaults to False.
            require_array (bool, optional): Require parsed JSON to be an array. Defaults to False.
            max_depth (Optional[int], optional): Maximum allowed JSON nesting depth. Defaults to None.
            allow_none (bool, optional): If True, skip validation when field value is None. Defaults to True.
            message (Optional[str], optional): Prompt message for validation failure. Defaults to None.

        Raises:
            ValueError: require_object and require_array cannot both be True. max_depth cannot be less than 1.
        """
        if require_object and require_array:
            raise ValueError('require_object and require_array cannot both be True.')
        if max_depth is not None and max_depth < 1:
            raise ValueError('max_depth cannot be less than 1.')
        self.field_name = field_name
        self.require_object = require_object
        self.require_array = require_array
        self.max_depth = max_depth
        self.allow_none = allow_none
        self.message = message

    def _get_json_depth(self, value: Any) -> int:
        """Calculate JSON nesting depth.

        Args:
            value (Any): Parsed JSON value.

        Returns:
            int: Calculated nesting depth, minimum is 1.
        """
        if isinstance(value, dict):
            if not value:
                return 1
            return 1 + max(self._get_json_depth(item) for item in value.values())
        if isinstance(value, list):
            if not value:
                return 1
            return 1 + max(self._get_json_depth(item) for item in value)
        return 1

    def _build_default_message(self, reason: str) -> str:
        """Build default validation message based on failure reason.

        Args:
            reason (str): Failure reason for JSON validation.

        Returns:
            str: Default validation message.
        """
        return f'{self.field_name} must be a valid JSON string: {reason}.'

    def _raise_validation_error(
        self,
        validate_model: BaseModel,
        field_value: Any,
        reason: str,
    ):
        """Raise a standardized field validation error.

        Args:
            validate_model (BaseModel): Pydantic model instance under validation.
            field_value (Any): Current field value.
            reason (str): Failure reason for JSON validation.

        Raises:
            FieldValidationError: Raised when JSON validation fails.
        """
        raise FieldValidationError(
            model_name=validate_model.__class__.__name__,
            field_name=self.field_name,
            field_value=field_value,
            validator=self.__class__.__name__,
            message=self.message if self.message else self._build_default_message(reason),
        )

    def _validate_json_string(self, validate_model: BaseModel):
        """Execute JSON string validation for the current model instance.

        Args:
            validate_model (BaseModel): Pydantic model instance under validation.
        """
        field_value = getattr(validate_model, self.field_name)
        if field_value is None and self.allow_none:
            return
        if not isinstance(field_value, str):
            self._raise_validation_error(validate_model, field_value, 'value type is not string')
        try:
            parsed_value = json.loads(field_value)
        except (TypeError, ValueError):
            self._raise_validation_error(validate_model, field_value, 'invalid JSON syntax')
        if self.require_object and not isinstance(parsed_value, dict):
            self._raise_validation_error(validate_model, field_value, 'JSON root type must be object')
        if self.require_array and not isinstance(parsed_value, list):
            self._raise_validation_error(validate_model, field_value, 'JSON root type must be array')
        if self.max_depth is not None:
            depth = self._get_json_depth(parsed_value)
            if depth > self.max_depth:
                self._raise_validation_error(
                    validate_model,
                    field_value,
                    f'JSON depth {depth} exceeds max_depth {self.max_depth}',
                )

    def __call__(self, func):
        is_async = iscoroutinefunction(func)
        if is_async:

            @wraps(func)
            async def wrapper(*args, **kwargs):
                validate_model = args[0]
                if isinstance(validate_model, BaseModel) and hasattr(validate_model, self.field_name):
                    self._validate_json_string(validate_model)
                return await func(*args, **kwargs)

            return wrapper
        else:

            @wraps(func)
            def wrapper(*args, **kwargs):
                validate_model = args[0]
                if isinstance(validate_model, BaseModel) and hasattr(validate_model, self.field_name):
                    self._validate_json_string(validate_model)
                return func(*args, **kwargs)

            return wrapper
