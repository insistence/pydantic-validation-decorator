<h1 align="center">pydantic-validation-decorator</h1>
<div align="center">

[![GitHub](https://shields.io/badge/license-MIT-informational)](https://github.com/insistence/pydantic-validation-decorator/blob/master/LICENSE)
[![PyPI](https://img.shields.io/pypi/v/pydantic-validation-decorator.svg?color=dark-green)](https://pypi.org/project/pydantic-validation-decorator/)

</div>

简体中文 | [English](./README-en_US.md)

## 目录
[安装](#install)<br>
[开始使用](#get-started)<br>
[已有装饰器列表](#decorators-list)<br>
[参与贡献](#contribute)

<a name="install" ></a>

## 安装
```bash
pip install pydantic-validation-decorator -U
```

<a name="get-started" ></a>

## 开始使用
1.创建一个`Pydantic`模型
```python
from pydantic import BaseModel
from typing import Optional


class NotBlankTestModel(BaseModel):
    user_name: Optional[str] = None
```
2.在`Pydantic`模型中引入验证装饰器，以`@NotBlank`装饰器为例
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
3.在需要手动触发校验的函数中使用`@ValidateFields`验证装饰器
```python
from pydantic_validation_decorator import ValidateFields


@ValidateFields(validate_model='not_blank_test', validate_function='validate_fields')
def test_not_blank_decorator(not_blank_test: NotBlankTestModel):
    return not_blank_test.model_dump()
```
4.调用这个函数即可触发校验，当校验不通过时，会抛出`FieldValidationError`异常，异常对象中包含`message`属性，值为`@NotBlank`装饰器中设置的`message`属性。
```python
from pydantic_validation_decorator import FieldValidationError


if __name__ == '__main__':
    not_blank_test = NotBlankTestModel()
    try:
        print(test_not_blank_decorator(not_blank_test=not_blank_test))
    except FieldValidationError as e:
        print(e.__dict__)
```
调用这个函数最后的输出结果为：
```python
{'model_name': 'NotBlankTestModel', 'field_name': 'user_name', 'field_value': None, 'validator': 'NotBlank', 'message': 'user_name cannot be blank'}
```
完整的代码示例为：
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

## 已有装饰器列表

### `@ValidateFields` 字段验证装饰器
| 参数名称 | 类型 | 参数说明 | 默认值 |
| - | - | - | - |
| `mode` | str, optional | 如何获得需要验证的模型。可选的有'args'（从位置参数中获取）和'kwargs'（从关键字参数中获取） | 'kwargs' |
| `validate_model` | str, optional | 需要在函数中验证的`Pydantic`模型的名称（从关键字参数中获取） | - |
| `validate_model_index` | int, optional | 需要在函数中验证的`Pydantic`模型的索引（从位置参数中获取） | - |
| `validate_function` | str, optional | 在`Pydantic`模型中定义的验证函数的名称 | 'validate_fields' |

### `@Network`    字段网络类型验证装饰器 
| 参数名称 | 类型 | 参数说明 | 默认值 |
| - | - | - | - |
| `field_name` | str | 需要验证的字段名称 | - |
| `field_type` | str | 需要验证的字段类型，可选的有'AnyUrl', 'AnyHttpUrl', 'HttpUrl', 'AnyWebsocketUrl', 'WebsocketUrl', 'FileUrl', 'FtpUrl', 'PostgresDsn', 'CockroachDsn', 'AmqpDsn', 'RedisDsn', 'MongoDsn', 'KafkaDsn', 'NatsDsn', 'MySQLDsn', 'MariaDBDsn', 'ClickHouseDsn', 'EmailStr', 'NameEmail', 'IPvAnyAddress', | - |
| `message` | str, optional | 验证失败提示消息 | `'{field_name} is not the correct {field_type} type.'` |

### `@NotBlank`   字段非空验证装饰器
| 参数名称 | 类型 | 参数说明 | 默认值 |
| - | - | - | - |
| `field_name` | str | 需要验证的字段名称 | - |
| `message` | str, optional | 验证失败提示消息 | `'{field_name} cannot be empty.'` |

### `@Pattern`    字段正则验证装饰器
| 参数名称 | 类型 | 参数说明 | 默认值 |
| - | - | - | - |
| `field_name` | str | 需要验证的字段名称 | - |
| `regexp` | str | 正则表达式 | - |
| `message` | str, optional | 验证失败提示消息 | `'The format of {field_name} is incorrect.'` |

### `@Size`   字段大小验证装饰器
| 参数名称 | 类型 | 参数说明 | 默认值 |
| - | - | - | - |
| `field_name` | str | 需要验证的字段名称 | - |
| `gt` | float, optional | 数字型字段值必须要大于gt | - |
| `ge` | float, optional | 数字型字段值必须要大于等于ge | - |
| `lt` | float, optional | 数字型字段值必须要小于lt | - |
| `le` | float, optional | 数字型字段值必须要小于等于le | - |
| `min_length` | int, optional | 字符串型字段长度不能小于min_length | 0 |
| `max_length` | int, optional | 字符串型字段长度不能大于max_length | - |
| `message` | str, optional | 验证失败提示消息 | `'{field_name} must be greater than {gt}.'` OR `'{field_name} must be greater than or equal to {ge}.'` OR `'{field_name} must be less than {lt}.'` OR `'{field_name} must be less than or equal to {le}.'` OR `'The length of {field_name} cannot be less than {min_length}.'` OR `'The length of {field_name} cannot be greater than {max_length}.'` |

### `@Xss`    字段Xss验证装饰器
| 参数名称 | 类型 | 参数说明 | 默认值 |
| - | - | - | - |
| `field_name` | str | 需要验证的字段名称 | - |
| `message` | str, optional | 验证失败提示消息 | `'{field_name} cannot contain script characters.'` |

<a name="contribute" ></a>

## 参与贡献
```bash
git clone https://github.com/insistence/pydantic-validation-decorator.git
cd pydantic-validation-decorator
# 安装开发环境所需依赖
pip install -r requirements.txt
```
