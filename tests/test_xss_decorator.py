import pytest
from pydantic_validation_decorator import (
    ValidateFields,
    Xss,
    FieldValidationError,
)
from pydantic import BaseModel
from typing import Optional


class XssTestModel(BaseModel):
    user_name: Optional[str] = None

    @Xss(
        field_name='user_name',
        message='user_name cannot contain script characters',
    )
    def get_user_name(self):
        return self.user_name

    def validate_fields(self):
        self.get_user_name()


@ValidateFields(validate_model='xss_test', validate_function='get_user_name')
def sync_test_xss_decorator(xss_test: XssTestModel):
    return xss_test.model_dump()


@ValidateFields(mode='args', validate_model_index=0)
async def async_test_xss_decorator(
    xss_test: XssTestModel,
):
    return xss_test.model_dump()


class TestXssDecorator:
    """测试 Xss 装饰器功能"""

    def test_xss_decorator_valid_input(self):
        """测试有效输入（无XSS字符）"""
        xss_test = XssTestModel(user_name='test123')
        result = sync_test_xss_decorator(xss_test=xss_test)
        assert result == {'user_name': 'test123'}
        assert result['user_name'] == 'test123'

    def test_xss_decorator_empty_input(self):
        """测试空输入"""
        xss_test = XssTestModel()
        result = sync_test_xss_decorator(xss_test=xss_test)
        assert result == {'user_name': None}

    def test_xss_decorator_invalid_input(self):
        """测试包含XSS字符的输入"""
        xss_test = XssTestModel(user_name='test123<>')
        with pytest.raises(FieldValidationError) as exc_info:
            sync_test_xss_decorator(xss_test=xss_test)

        error = exc_info.value
        assert error.field_name == 'user_name'
        assert 'user_name cannot contain script characters' in error.message

    def test_xss_decorator_script_tag(self):
        """测试包含script标签的输入"""
        xss_test = XssTestModel(user_name='<script>alert("xss")</script>')
        with pytest.raises(FieldValidationError) as exc_info:
            sync_test_xss_decorator(xss_test=xss_test)

        error = exc_info.value
        assert error.field_name == 'user_name'
        assert 'user_name cannot contain script characters' in error.message

    @pytest.mark.asyncio
    async def test_async_xss_decorator_valid_input(self):
        """测试异步装饰器有效输入（无XSS字符）"""
        xss_test = XssTestModel(user_name='test123')
        result = await async_test_xss_decorator(xss_test)
        assert result == {'user_name': 'test123'}
        assert result['user_name'] == 'test123'

    @pytest.mark.asyncio
    async def test_async_xss_decorator_empty_input(self):
        """测试异步装饰器空输入"""
        xss_test = XssTestModel()
        result = await async_test_xss_decorator(xss_test)
        assert result == {'user_name': None}

    @pytest.mark.asyncio
    async def test_async_xss_decorator_invalid_input(self):
        """测试异步装饰器包含XSS字符的输入"""
        xss_test = XssTestModel(user_name='test123<>')
        with pytest.raises(FieldValidationError) as exc_info:
            await async_test_xss_decorator(xss_test)

        error = exc_info.value
        assert error.field_name == 'user_name'
        assert 'user_name cannot contain script characters' in error.message

    @pytest.mark.asyncio
    async def test_async_xss_decorator_script_tag(self):
        """测试异步装饰器包含script标签的输入"""
        xss_test = XssTestModel(user_name='<script>alert("xss")</script>')
        with pytest.raises(FieldValidationError) as exc_info:
            await async_test_xss_decorator(xss_test)

        error = exc_info.value
        assert error.field_name == 'user_name'
        assert 'user_name cannot contain script characters' in error.message
