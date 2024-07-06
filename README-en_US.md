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
| `message` | str, optional | Prompt message for validation failure. Defaults to None. | `'{field_name} cannot be empty.'` |

### `@Pattern`    Field Pattern Validation Decorator
| Parameter | Type | Parameter Description | Default Value |
| - | - | - | - |
| `field_name` | str | Field name that need to be validate. | - |
| `regexp` | str | Regular expression. | - |
| `message` | str, optional | Prompt message for validation failure. Defaults to None. | `'The format of {field_name} is incorrect.'` |

### `@Size`   Field Size Validation Decorator
| Parameter | Type | Parameter Description | Default Value |
| - | - | - | - |
| `field_name` | str | Field name that need to be validate. | - |
| `gt` | float, optional | The numerical field value must be greater than gt. | - |
| `ge` | float, optional | The numerical field value must be greater than or equal to ge. | - |
| `lt` | float, optional | The numerical field value must be less than lt. | - |
| `le` | float, optional | The numerical field value must be less than or equal to le. | - |
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
pip install -r requirements.txt
```
