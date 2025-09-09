import pytest
from pydantic_validation_decorator import (
    ValidateFields,
    Network,
    FieldValidationError,
)
from pydantic import BaseModel
from typing import Optional


class NetworkTestModel(BaseModel):
    email: Optional[str] = None

    @Network(
        field_name='email',
        field_type='EmailStr',
        message='email is invalid',
    )
    def get_email(self):
        return self.email

    def validate_fields(self):
        self.get_email()


@ValidateFields(validate_model='network_test', validate_function='get_email')
def sync_test_network_decorator(network_test: NetworkTestModel):
    return network_test.model_dump()


@ValidateFields(mode='args', validate_model_index=1)
async def async_test_network_decorator(
    test,
    network_test,
):
    return network_test.model_dump()


class TestNetworkDecorator:
    """测试 Network 装饰器功能"""

    def test_network_decorator_valid_email(self):
        """测试有效的邮箱地址"""
        network_test = NetworkTestModel(email='test123@qq.com')
        result = sync_test_network_decorator(network_test=network_test)
        assert result == {'email': 'test123@qq.com'}
        assert result['email'] == 'test123@qq.com'

    def test_network_decorator_empty_email(self):
        """测试空邮箱地址"""
        network_test = NetworkTestModel()
        result = sync_test_network_decorator(network_test=network_test)
        assert result == {'email': None}

    def test_network_decorator_invalid_email_no_at(self):
        """测试无效邮箱地址（缺少@符号）"""
        network_test = NetworkTestModel(email='test123')
        with pytest.raises(FieldValidationError) as exc_info:
            sync_test_network_decorator(network_test=network_test)

        error = exc_info.value
        assert error.field_name == 'email'
        assert 'email is invalid' in error.message

    def test_network_decorator_invalid_email_no_domain(self):
        """测试无效邮箱地址（缺少域名）"""
        network_test = NetworkTestModel(email='test@')
        with pytest.raises(FieldValidationError) as exc_info:
            sync_test_network_decorator(network_test=network_test)

        error = exc_info.value
        assert error.field_name == 'email'
        assert 'email is invalid' in error.message

    def test_network_decorator_invalid_email_malformed(self):
        """测试格式错误的邮箱地址"""
        network_test = NetworkTestModel(email='test@domain')
        with pytest.raises(FieldValidationError) as exc_info:
            sync_test_network_decorator(network_test=network_test)

        error = exc_info.value
        assert error.field_name == 'email'
        assert 'email is invalid' in error.message

    def test_network_decorator_invalid_email_special_chars(self):
        """测试包含非法字符的邮箱地址"""
        network_test = NetworkTestModel(email='test 123@domain.com')
        with pytest.raises(FieldValidationError) as exc_info:
            sync_test_network_decorator(network_test=network_test)

        error = exc_info.value
        assert error.field_name == 'email'
        assert 'email is invalid' in error.message

    @pytest.mark.asyncio
    async def test_async_network_decorator_valid_email(self):
        """测试异步装饰器有效邮箱地址"""
        network_test = NetworkTestModel(email='test123@qq.com')
        result = await async_test_network_decorator(1, network_test)
        assert result == {'email': 'test123@qq.com'}
        assert result['email'] == 'test123@qq.com'

    @pytest.mark.asyncio
    async def test_async_network_decorator_empty_email(self):
        """测试异步装饰器空邮箱地址"""
        network_test = NetworkTestModel()
        result = await async_test_network_decorator(1, network_test)
        assert result == {'email': None}

    @pytest.mark.asyncio
    async def test_async_network_decorator_invalid_email_no_at(self):
        """测试异步装饰器无效邮箱地址（缺少@符号）"""
        network_test = NetworkTestModel(email='test123')
        with pytest.raises(FieldValidationError) as exc_info:
            await async_test_network_decorator(1, network_test)

        error = exc_info.value
        assert error.field_name == 'email'
        assert 'email is invalid' in error.message

    @pytest.mark.asyncio
    async def test_async_network_decorator_invalid_email_no_domain(self):
        """测试异步装饰器无效邮箱地址（缺少域名）"""
        network_test = NetworkTestModel(email='test@')
        with pytest.raises(FieldValidationError) as exc_info:
            await async_test_network_decorator(1, network_test)

        error = exc_info.value
        assert error.field_name == 'email'
        assert 'email is invalid' in error.message

    @pytest.mark.asyncio
    async def test_async_network_decorator_invalid_email_malformed(self):
        """测试异步装饰器格式错误的邮箱地址"""
        network_test = NetworkTestModel(email='test@domain')
        with pytest.raises(FieldValidationError) as exc_info:
            await async_test_network_decorator(1, network_test)

        error = exc_info.value
        assert error.field_name == 'email'
        assert 'email is invalid' in error.message

    @pytest.mark.asyncio
    async def test_async_network_decorator_invalid_email_special_chars(self):
        """测试异步装饰器包含非法字符的邮箱地址"""
        network_test = NetworkTestModel(email='test 123@domain.com')
        with pytest.raises(FieldValidationError) as exc_info:
            await async_test_network_decorator(1, network_test)

        error = exc_info.value
        assert error.field_name == 'email'
        assert 'email is invalid' in error.message
