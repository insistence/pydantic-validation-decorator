from typing import Any

import pytest
from pydantic import BaseModel

from pydantic_validation_decorator import (
    FieldValidationError,
    Pattern,
    ValidateFields,
)


class PatternTestModel(BaseModel):
    dict_type: str | None = None

    @Pattern(
        field_name='dict_type',
        regexp='^[a-z][a-z0-9_]*$',
        message='The dict_type must start with a letter and can only be lowercase letters, numbers, and dashes',
    )
    def get_dict_type(self) -> str | None:
        return self.dict_type

    def validate_fields(self) -> None:
        self.get_dict_type()


@ValidateFields(validate_model='pattern_test', validate_function='get_dict_type')
def sync_test_pattern_decorator(pattern_test: PatternTestModel) -> dict[str, Any]:
    return pattern_test.model_dump()


@ValidateFields(mode='args', validate_model_index=0)
async def async_test_pattern_decorator(pattern_test: PatternTestModel) -> dict[str, Any]:
    return pattern_test.model_dump()


class TestPatternDecorator:
    """测试 Pattern 装饰器功能."""

    def test_pattern_decorator_valid_input(self) -> None:
        """测试有效输入（符合正则表达式）."""
        pattern_test = PatternTestModel(dict_type='test_dict_type')
        result = sync_test_pattern_decorator(pattern_test=pattern_test)
        assert result == {'dict_type': 'test_dict_type'}
        assert result['dict_type'] == 'test_dict_type'

    def test_pattern_decorator_empty_input(self) -> None:
        """测试空输入."""
        pattern_test = PatternTestModel()
        result = sync_test_pattern_decorator(pattern_test=pattern_test)
        assert result == {'dict_type': None}

    def test_pattern_decorator_invalid_input_starts_with_number(self) -> None:
        """测试以数字开头的无效输入."""
        pattern_test = PatternTestModel(dict_type='123')
        with pytest.raises(FieldValidationError) as exc_info:
            sync_test_pattern_decorator(pattern_test=pattern_test)

        error = exc_info.value
        assert error.field_name == 'dict_type'
        assert error.message is not None
        assert error.message.startswith('The dict_type must start with a letter')

    def test_pattern_decorator_invalid_input_with_uppercase(self) -> None:
        """测试包含大写字母的无效输入."""
        pattern_test = PatternTestModel(dict_type='TestDict')
        with pytest.raises(FieldValidationError) as exc_info:
            sync_test_pattern_decorator(pattern_test=pattern_test)

        error = exc_info.value
        assert error.field_name == 'dict_type'
        assert error.message is not None
        assert error.message.startswith('The dict_type must start with a letter')

    def test_pattern_decorator_invalid_input_with_special_chars(self) -> None:
        """测试包含特殊字符的无效输入."""
        pattern_test = PatternTestModel(dict_type='test-dict')
        with pytest.raises(FieldValidationError) as exc_info:
            sync_test_pattern_decorator(pattern_test=pattern_test)

        error = exc_info.value
        assert error.field_name == 'dict_type'
        assert error.message is not None
        assert error.message.startswith('The dict_type must start with a letter')

    @pytest.mark.asyncio
    async def test_async_pattern_decorator_valid_input(self) -> None:
        """测试异步装饰器有效输入（符合正则表达式）."""
        pattern_test = PatternTestModel(dict_type='test_dict_type')
        result = await async_test_pattern_decorator(pattern_test)
        assert result == {'dict_type': 'test_dict_type'}
        assert result['dict_type'] == 'test_dict_type'

    @pytest.mark.asyncio
    async def test_async_pattern_decorator_empty_input(self) -> None:
        """测试异步装饰器空输入."""
        pattern_test = PatternTestModel()
        result = await async_test_pattern_decorator(pattern_test)
        assert result == {'dict_type': None}

    @pytest.mark.asyncio
    async def test_async_pattern_decorator_invalid_input_starts_with_number(self) -> None:
        """测试异步装饰器以数字开头的无效输入."""
        pattern_test = PatternTestModel(dict_type='123')
        with pytest.raises(FieldValidationError) as exc_info:
            await async_test_pattern_decorator(pattern_test)

        error = exc_info.value
        assert error.field_name == 'dict_type'
        assert error.message is not None
        assert error.message.startswith('The dict_type must start with a letter')

    @pytest.mark.asyncio
    async def test_async_pattern_decorator_invalid_input_with_uppercase(self) -> None:
        """测试异步装饰器包含大写字母的无效输入."""
        pattern_test = PatternTestModel(dict_type='TestDict')
        with pytest.raises(FieldValidationError) as exc_info:
            await async_test_pattern_decorator(pattern_test)

        error = exc_info.value
        assert error.field_name == 'dict_type'
        assert error.message is not None
        assert error.message.startswith('The dict_type must start with a letter')

    @pytest.mark.asyncio
    async def test_async_pattern_decorator_invalid_input_with_special_chars(self) -> None:
        """测试异步装饰器包含特殊字符的无效输入."""
        pattern_test = PatternTestModel(dict_type='test-dict')
        with pytest.raises(FieldValidationError) as exc_info:
            await async_test_pattern_decorator(pattern_test)

        error = exc_info.value
        assert error.field_name == 'dict_type'
        assert error.message is not None
        assert error.message.startswith('The dict_type must start with a letter')
