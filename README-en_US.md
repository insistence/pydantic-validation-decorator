<h1 align="center">pydantic-validation-decorator</h1>
<h3 align="center">Practical pydantic validation decorators that support manual invocation</h3>
<div align="center">

[![GitHub](https://shields.io/badge/license-MIT-informational)](https://github.com/insistence/pydantic-validation-decorator/blob/master/LICENSE)
[![PyPI](https://img.shields.io/pypi/v/pydantic-validation-decorator.svg?color=dark-green)](https://pypi.org/project/pydantic-validation-decorator/)

</div>

English | [简体中文](./README.md)

## Directory
[Install](#install)<br>
[Get Started](#get-started)<br>
[List of Existing Decorators](#decorators-list)<br>
[Contribute](#contribute)

<a name="install" ></a>

## Install
```bash
pip install pydantic-validation-decorator -U
```

<a name="get-started" ></a>

## Get Started
1.Create a `Pydantic` Model.
```python
from pydantic import BaseModel
from typing import Optional


class NotBlankTestModel(BaseModel):
    user_name: Optional[str] = None
```
2.Introducing a validation decorator into the `Pydantic` model, using the `@NotBlank` decorator as an example.
```python
from pydantic import BaseModel
from typing import Optional
from pydantic_validation_decorator import NotBlank


class NotBlankTestModel(BaseModel):
    user_name: Optional[str] = None

    @NotBlank(
        field_name='user_name',
        message='user_name cannot be blank',
    )
    def get_user_name(self):
        return self.user_name

    def validate_fields(self):
        self.get_user_name()
```
3.Use the `@ValidateFields` validation decorator in functions that require manual triggering of validation.
```python
from pydantic_validation_decorator import ValidateFields


@ValidateFields(validate_model='not_blank_test', validate_function='validate_fields')
def test_not_blank_decorator(not_blank_test: NotBlankTestModel):
    return not_blank_test.model_dump()
```
4.Calling this function triggers validation. When the validation fails, a  `FieldValidationError` exception will be thrown. The exception object contains a `message` attribute with a value of the `message` attribute set in the `@NotBlank` decorator.
```python
from pydantic_validation_decorator import FieldValidationError


if __name__ == '__main__':
    not_blank_test = NotBlankTestModel()
    try:
        print(test_not_blank_decorator(not_blank_test=not_blank_test))
    except FieldValidationError as e:
        print(e.__dict__)
```
The final output result of calling this function is：
```python
{'model_name': 'NotBlankTestModel', 'field_name': 'user_name', 'field_value': None, 'validator': 'NotBlank', 'message': 'user_name cannot be blank'}
```
The complete code example is：
```python
from pydantic_validation_decorator import (
    ValidateFields,
    NotBlank,
    FieldValidationError,
)
from pydantic import BaseModel
from typing import Optional


class NotBlankTestModel(BaseModel):
    user_name: Optional[str] = None

    @NotBlank(
        field_name='user_name',
        message='user_name cannot be blank',
    )
    def get_user_name(self):
        return self.user_name

    def validate_fields(self):
        self.get_user_name()


@ValidateFields(validate_model='not_blank_test', validate_function='validate_fields')
def test_not_blank_decorator(not_blank_test: NotBlankTestModel):
    return not_blank_test.model_dump()


if __name__ == '__main__':
    not_blank_test = NotBlankTestModel()
    try:
        print(test_not_blank_decorator(not_blank_test=not_blank_test))
    except FieldValidationError as e:
        print(e.__dict__)
```

<a name="decorators-list" ></a>

## List of Existing Decorators

### `@ValidateFields` Field Validation Decorator
| Parameter | Type | Parameter Description | Default Value |
| - | - | - | - |
| `mode` | str, optional | How to obtain the model that needs to be validate. Optional options include 'args' (obtained from positional parameters) and' kwargs' (obtained from keyword parameters) | 'kwargs' |
| `validate_model` | str, optional | The name of the `Pydantic` model that needs to be validated in the function.(obtained from keyword parameters) | - |
| `validate_model_index` | int, optional | The index of the `Pydantic` model that needs to be validated in the function.(obtained from positional parameters) | - |
| `validate_function` | str, optional | The name of the validation function defined in the `Pydantic` model. | 'validate_fields' |

### `@AllowedValues`    Field Allowed Values Validation Decorator
| Parameter | Type | Parameter Description | Default Value |
| - | - | - | - |
| `field_name` | str | Field name that needs to be validated. | - |
| `choices` | Iterable[Any] | Allowed values for the field. | - |
| `allow_none` | bool, optional | If True, skip validation when field value is None. | True |
| `case_sensitive` | bool, optional | If False, compare string values case-insensitively. | True |
| `message` | str, optional | Prompt message for validation failure. Defaults to None. | `'{field_name} must be one of {choices}.'` |

### `@Alpha`    Field Alpha Validation Decorator
| Parameter | Type | Parameter Description | Default Value |
| - | - | - | - |
| `field_name` | str | Field name that need to be validate. | - |
| `mode` | Literal['upper', 'lower', 'mixed'], optional | Validation mode. Options: 'upper' (only uppercase), 'lower' (only lowercase), 'mixed' (both upper and lower). | 'mixed' |
| `message` | str, optional | Prompt message for validation failure. Defaults to None. | `'{field_name} must contain only letters.'` OR `'{field_name} must contain only uppercase letters.'` OR `'{field_name} must contain only lowercase letters.'` |

### `@AtLeastOneOf`    Field At Least One Of Validation Decorator
| Parameter | Type | Parameter Description | Default Value |
| - | - | - | - |
| `fields` | list[str] | Field names where at least `min_count` fields must be provided. | - |
| `min_count` | int, optional | Minimum number of fields that must be provided. | 1 |
| `message` | str, optional | Prompt message for validation failure. Defaults to None. | `'At least {min_count} of {fields} must be provided.'` |

### `@Compare`    Field Compare Validation Decorator
| Parameter | Type | Parameter Description | Default Value |
| - | - | - | - |
| `left_field` | str | Left field name used in comparison. | - |
| `right_field` | str | Right field name used in comparison. | - |
| `operator` | Literal['eq', 'ne', 'gt', 'ge', 'lt', 'le'], optional | Comparison operator. `eq`(==), `ne`(!=), `gt`(>), `ge`(>=), `lt`(<), `le`(<=). | 'eq' |
| `allow_none` | bool, optional | If True, skip validation when either compare field is None. | True |
| `message` | str, optional | Prompt message for validation failure. Defaults to None. | `'{left_field} must satisfy {left_field} {operator_symbol} {right_field}, but got {left_value} and {right_value}.'` |

### `@DateTimeRange`    Field DateTime Range Validation Decorator
| Parameter | Type | Parameter Description | Default Value |
| - | - | - | - |
| `start_field` | str | Start datetime field name. | - |
| `end_field` | str | End datetime field name. | - |
| `allow_equal` | bool, optional | If True, allow start datetime equal to end datetime. | True |
| `allow_none` | bool, optional | If True, skip validation when either field value is None. | True |
| `coerce_from_str` | bool, optional | If True, allow ISO datetime string conversion for comparison. | True |
| `require_timezone_consistency` | bool, optional | If True, require both datetimes to be timezone-aware or both timezone-naive. | False |
| `message` | str, optional | Prompt message for validation failure. Defaults to None. | `'{start_field} must satisfy {start_field} <= {end_field}, but got {start_value} and {end_value}. Reason: {reason}.'` |

### `@JsonString`    Field JSON String Validation Decorator
| Parameter | Type | Parameter Description | Default Value |
| - | - | - | - |
| `field_name` | str | Field name that needs to be validated. | - |
| `require_object` | bool, optional | If True, require JSON root type to be object. | False |
| `require_array` | bool, optional | If True, require JSON root type to be array. | False |
| `max_depth` | int, optional | Maximum allowed JSON nesting depth. | - |
| `allow_none` | bool, optional | If True, skip validation when field value is None. | True |
| `message` | str, optional | Prompt message for validation failure. Defaults to None. | `'{field_name} must be a valid JSON string: {reason}.'` |

### `@Network`    Field Network Type Validation Decorator 
| Parameter | Type | Parameter Description | Default Value |
| - | - | - | - |
| `field_name` | str | Field name that need to be validate. | - |
| `field_type` | str | Field type that need to be validate. Optional options include 'AnyUrl', 'AnyHttpUrl', 'HttpUrl', 'AnyWebsocketUrl', 'WebsocketUrl', 'FileUrl', 'FtpUrl', 'PostgresDsn', 'CockroachDsn', 'AmqpDsn', 'RedisDsn', 'MongoDsn', 'KafkaDsn', 'NatsDsn', 'MySQLDsn', 'MariaDBDsn', 'ClickHouseDsn', 'EmailStr', 'NameEmail', 'IPvAnyAddress', | - |
| `message` | str, optional | Prompt message for validation failure. Defaults to None. | `'{field_name} is not the correct {field_type} type.'` |

### `@NotBlank`   Field NotBlank Validation Decorator
| Parameter | Type | Parameter Description | Default Value |
| - | - | - | - |
| `field_name` | str | Field name that need to be validate. | - |
| `allow_unset` | bool, optional | If True, validation only runs when the optional field is explicitly provided. | False |
| `message` | str, optional | Prompt message for validation failure. Defaults to None. | `'{field_name} cannot be empty.'` |

### `@NumericPrecision`   Field Numeric Precision Validation Decorator
| Parameter | Type | Parameter Description | Default Value |
| - | - | - | - |
| `field_name` | str | Field name that needs to be validated. | - |
| `max_digits` | int, optional | Maximum allowed total digits (integer and decimal digits combined). | - |
| `decimal_places` | int, optional | Maximum allowed decimal places. | - |
| `allow_none` | bool, optional | If True, skip validation when field value is None. | True |
| `allow_string_number` | bool, optional | If True, allow numeric string input for precision validation. | False |
| `message` | str, optional | Prompt message for validation failure. Defaults to None. | `'{field_name} precision validation failed: {reason}.'` |

### `@Pattern`    Field Pattern Validation Decorator
| Parameter | Type | Parameter Description | Default Value |
| - | - | - | - |
| `field_name` | str | Field name that need to be validate. | - |
| `regexp` | str | Regular expression. | - |
| `message` | str, optional | Prompt message for validation failure. Defaults to None. | `'The format of {field_name} is incorrect.'` |

### `@RequiredIf`   Field Conditional Required Validation Decorator
| Parameter | Type | Parameter Description | Default Value |
| - | - | - | - |
| `field_name` | str | Field name that should become required under condition. | - |
| `when_field` | str | Condition field name used to trigger required validation. | - |
| `when_value` | Any | Trigger value for condition field. Supports single value or collection(list/tuple/set/frozenset). | - |
| `message` | str, optional | Prompt message for validation failure. Defaults to None. | `'{field_name} is required when {when_field} is {when_value}.'` |

### `@Size`   Field Size Validation Decorator
| Parameter | Type | Parameter Description | Default Value |
| - | - | - | - |
| `field_name` | str | Field name that need to be validate. | - |
| `gt` | float or int, optional | The numerical field value must be greater than gt. | - |
| `ge` | float or int, optional | The numerical field value must be greater than or equal to ge. | - |
| `lt` | float or int, optional | The numerical field value must be less than lt. | - |
| `le` | float or int, optional | The numerical field value must be less than or equal to le. | - |
| `min_length` | int, optional | The length of a string field cannot be less than min_length. | 0 |
| `max_length` | int, optional | The length of a string field cannot be greater than max_length. | - |
| `message` | str, optional | Prompt message for validation failure. Defaults to None. | `'{field_name} must be greater than {gt}.'` OR `'{field_name} must be greater than or equal to {ge}.'` OR `'{field_name} must be less than {lt}.'` OR `'{field_name} must be less than or equal to {le}.'` OR `'The length of {field_name} cannot be less than {min_length}.'` OR `'The length of {field_name} cannot be greater than {max_length}.'` |

### `@Xss`    Field Xss Validation Decorator
| Parameter | Type | Parameter Description | Default Value |
| - | - | - | - |
| `field_name` | str | Field name that need to be validate. | - |
| `message` | str, optional | Prompt message for validation failure. Defaults to None. | `'{field_name} cannot contain script characters.'` |

<a name="contribute" ></a>

## Contribute
```bash
git clone https://github.com/insistence/pydantic-validation-decorator.git
cd pydantic-validation-decorator
# Install dependencies required for development environment
pip install -r requirements-dev.txt
```
