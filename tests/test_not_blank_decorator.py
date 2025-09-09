import pytest
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


@ValidateFields(validate_model='not_blank_test', validate_function='get_user_name')
def sync_test_not_blank_decorator(not_blank_test: NotBlankTestModel):
    return not_blank_test.model_dump()


@ValidateFields(mode='args', validate_model_index=0)
async def async_test_not_blank_decorator(
    not_blank_test: NotBlankTestModel,
):
    return not_blank_test.model_dump()


class TestNotBlankDecorator:
    """测试 NotBlank 装饰器功能"""

    def test_not_blank_decorator_valid_input(self):
        """测试有效输入（非空字符串）"""
        not_blank_test = NotBlankTestModel(user_name='test123')
        result = sync_test_not_blank_decorator(not_blank_test=not_blank_test)
        assert result == {'user_name': 'test123'}
        assert result['user_name'] == 'test123'

    def test_not_blank_decorator_none_input(self):
        """测试None输入（应该抛出异常）"""
        not_blank_test = NotBlankTestModel()
        with pytest.raises(FieldValidationError) as exc_info:
            sync_test_not_blank_decorator(not_blank_test=not_blank_test)

        error = exc_info.value
        assert error.field_name == 'user_name'
        assert 'user_name cannot be blank' in error.message

    def test_not_blank_decorator_empty_string(self):
        """测试空字符串输入（应该抛出异常）"""
        not_blank_test = NotBlankTestModel(user_name='')
        with pytest.raises(FieldValidationError) as exc_info:
            sync_test_not_blank_decorator(not_blank_test=not_blank_test)

        error = exc_info.value
        assert error.field_name == 'user_name'
        assert 'user_name cannot be blank' in error.message

    def test_not_blank_decorator_whitespace_string(self):
        """测试空格字符串输入（NotBlank不会验证空格字符串）"""
        not_blank_test = NotBlankTestModel(user_name='   ')
        # NotBlank 装饰器不会检查空格字符串，只检查 None 和空字符串
        result = sync_test_not_blank_decorator(not_blank_test=not_blank_test)
        assert result == {'user_name': '   '}
        assert result['user_name'] == '   '

    def test_not_blank_decorator_string_with_content(self):
        """测试包含内容的字符串（即使包含空格）"""
        not_blank_test = NotBlankTestModel(user_name='  test  ')
        result = sync_test_not_blank_decorator(not_blank_test=not_blank_test)
        assert result == {'user_name': '  test  '}
        assert result['user_name'] == '  test  '

    @pytest.mark.asyncio
    async def test_async_not_blank_decorator_valid_input(self):
        """测试异步装饰器有效输入（非空字符串）"""
        not_blank_test = NotBlankTestModel(user_name='test123')
        result = await async_test_not_blank_decorator(not_blank_test)
        assert result == {'user_name': 'test123'}
        assert result['user_name'] == 'test123'

    @pytest.mark.asyncio
    async def test_async_not_blank_decorator_none_input(self):
        """测试异步装饰器None输入（应该抛出异常）"""
        not_blank_test = NotBlankTestModel()
        with pytest.raises(FieldValidationError) as exc_info:
            await async_test_not_blank_decorator(not_blank_test)

        error = exc_info.value
        assert error.field_name == 'user_name'
        assert 'user_name cannot be blank' in error.message

    @pytest.mark.asyncio
    async def test_async_not_blank_decorator_empty_string(self):
        """测试异步装饰器空字符串输入（应该抛出异常）"""
        not_blank_test = NotBlankTestModel(user_name='')
        with pytest.raises(FieldValidationError) as exc_info:
            await async_test_not_blank_decorator(not_blank_test)

        error = exc_info.value
        assert error.field_name == 'user_name'
        assert 'user_name cannot be blank' in error.message

    @pytest.mark.asyncio
    async def test_async_not_blank_decorator_whitespace_string(self):
        """测试异步装饰器空格字符串输入（NotBlank不会验证空格字符串）"""
        not_blank_test = NotBlankTestModel(user_name='   ')
        # NotBlank 装饰器不会检查空格字符串，只检查 None 和空字符串
        result = await async_test_not_blank_decorator(not_blank_test)
        assert result == {'user_name': '   '}
        assert result['user_name'] == '   '

    @pytest.mark.asyncio
    async def test_async_not_blank_decorator_string_with_content(self):
        """测试异步装饰器包含内容的字符串（即使包含空格）"""
        not_blank_test = NotBlankTestModel(user_name='  test  ')
        result = await async_test_not_blank_decorator(not_blank_test)
        assert result == {'user_name': '  test  '}
        assert result['user_name'] == '  test  '
