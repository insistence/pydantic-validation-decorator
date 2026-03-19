<h1 align="center">pydantic-validation-decorator</h1>
<h3 align="center">支持手动调用的实用的pydantic验证装饰器</h3>
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

### `@Alpha`    字段字母验证装饰器
| 参数名称 | 类型 | 参数说明 | 默认值 |
| - | - | - | - |
| `field_name` | str | 需要验证的字段名称 | - |
| `mode` | Literal['upper', 'lower', 'mixed'], optional | 验证模式。可选项：'upper'（仅大写字母）、'lower'（仅小写字母）、'mixed'（大小写混合） | 'mixed' |
| `message` | str, optional | 验证失败提示消息 | `'{field_name} must contain only letters.'` OR `'{field_name} must contain only uppercase letters.'` OR `'{field_name} must contain only lowercase letters.'` |

### `@Compare`    字段比较验证装饰器
| 参数名称 | 类型 | 参数说明 | 默认值 |
| - | - | - | - |
| `left_field` | str | 左侧比较字段名称 | - |
| `right_field` | str | 右侧比较字段名称 | - |
| `operator` | Literal['eq', 'ne', 'gt', 'ge', 'lt', 'le'], optional | 比较操作符。`eq`(==)、`ne`(!=)、`gt`(>)、`ge`(>=)、`lt`(<)、`le`(<=) | 'eq' |
| `allow_none` | bool, optional | 如果为True，当任一比较字段为None时跳过验证 | True |
| `message` | str, optional | 验证失败提示消息 | `'{left_field} must satisfy {left_field} {operator_symbol} {right_field}, but got {left_value} and {right_value}.'` |

### `@JsonString`    字段JSON字符串验证装饰器
| 参数名称 | 类型 | 参数说明 | 默认值 |
| - | - | - | - |
| `field_name` | str | 需要验证的字段名称 | - |
| `require_object` | bool, optional | 如果为True，要求JSON根节点必须是对象 | False |
| `require_array` | bool, optional | 如果为True，要求JSON根节点必须是数组 | False |
| `max_depth` | int, optional | JSON最大嵌套深度限制 | - |
| `allow_none` | bool, optional | 如果为True，当字段值为None时跳过验证 | True |
| `message` | str, optional | 验证失败提示消息 | `'{field_name} must be a valid JSON string: {reason}.'` |

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
| `allow_unset` | bool, optional | 如果为True，仅当可选字段被显式提供时才运行验证 | False |
| `message` | str, optional | 验证失败提示消息 | `'{field_name} cannot be empty.'` |

### `@NumericPrecision`   字段数值精度验证装饰器
| 参数名称 | 类型 | 参数说明 | 默认值 |
| - | - | - | - |
| `field_name` | str | 需要验证的字段名称 | - |
| `max_digits` | int, optional | 数值允许的最大总位数（整数位 + 小数位） | - |
| `decimal_places` | int, optional | 数值允许的最大小数位数 | - |
| `allow_none` | bool, optional | 如果为True，当字段值为None时跳过验证 | True |
| `allow_string_number` | bool, optional | 如果为True，允许数字字符串参与精度校验 | False |
| `message` | str, optional | 验证失败提示消息 | `'{field_name} precision validation failed: {reason}.'` |

### `@Pattern`    字段正则验证装饰器
| 参数名称 | 类型 | 参数说明 | 默认值 |
| - | - | - | - |
| `field_name` | str | 需要验证的字段名称 | - |
| `regexp` | str | 正则表达式 | - |
| `message` | str, optional | 验证失败提示消息 | `'The format of {field_name} is incorrect.'` |

### `@RequiredIf`   条件必填验证装饰器
| 参数名称 | 类型 | 参数说明 | 默认值 |
| - | - | - | - |
| `field_name` | str | 需要被判定为必填的字段名称 | - |
| `when_field` | str | 触发条件字段名称 | - |
| `when_value` | Any | 触发条件值。支持单值或集合(list/tuple/set/frozenset) | - |
| `message` | str, optional | 验证失败提示消息 | `'{field_name} is required when {when_field} is {when_value}.'` |

### `@Size`   字段大小验证装饰器
| 参数名称 | 类型 | 参数说明 | 默认值 |
| - | - | - | - |
| `field_name` | str | 需要验证的字段名称 | - |
| `gt` | float or int, optional | 数字型字段值必须要大于gt | - |
| `ge` | float or int, optional | 数字型字段值必须要大于等于ge | - |
| `lt` | float or int, optional | 数字型字段值必须要小于lt | - |
| `le` | float or int, optional | 数字型字段值必须要小于等于le | - |
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
pip install -r requirements-dev.txt
```
