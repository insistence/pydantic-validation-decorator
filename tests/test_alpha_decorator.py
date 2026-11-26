from typing import Any

import pytest
from pydantic import BaseModel

from pydantic_validation_decorator import (
    Alpha,
    FieldValidationError,
    ValidateFields,
)


class AlphaTestModel(BaseModel):
    username: str | None = None
    upper_name: str | None = None
    lower_name: str | None = None
    mixed_name: str | None = None

    @Alpha(
        field_name='username',
        mode='mixed',
        message='用户名必须只包含字母',
    )
    def get_username(self) -> str | None:
        return self.username

    @Alpha(
        field_name='upper_name',
        mode='upper',
        message='名称必须只包含大写字母',
    )
    def get_upper_name(self) -> str | None:
        return self.upper_name

    @Alpha(
        field_name='lower_name',
        mode='lower',
        message='名称必须只包含小写字母',
    )
    def get_lower_name(self) -> str | None:
        return self.lower_name

    @Alpha(
        field_name='mixed_name',
        mode='mixed',
    )
    def get_mixed_name(self) -> str | None:
        return self.mixed_name

    def validate_fields(self) -> None:
        self.get_username()
        self.get_upper_name()
        self.get_lower_name()
        self.get_mixed_name()


@ValidateFields(validate_model='alpha_test', validate_function='get_username')
def sync_test_alpha_decorator(alpha_test: AlphaTestModel) -> dict[str, Any]:
    return alpha_test.model_dump()


@ValidateFields(mode='args', validate_model_index=1)
async def async_test_alpha_decorator(test: int, alpha_test: AlphaTestModel) -> dict[str, Any]:
    return alpha_test.model_dump()


class TestAlphaDecorator:
    """测试 Alpha 装饰器功能."""

    def test_alpha_decorator_valid_mixed_case(self) -> None:
        """测试有效的混合大小写字母."""
        alpha_test = AlphaTestModel(username='HelloWorld')
        result = sync_test_alpha_decorator(alpha_test=alpha_test)
        assert result == {'username': 'HelloWorld', 'upper_name': None, 'lower_name': None, 'mixed_name': None}

    def test_alpha_decorator_valid_uppercase(self) -> None:
        """测试有效的纯大写字母."""
        alpha_test = AlphaTestModel(username='HELLO')
        result = sync_test_alpha_decorator(alpha_test=alpha_test)
        assert result == {'username': 'HELLO', 'upper_name': None, 'lower_name': None, 'mixed_name': None}

    def test_alpha_decorator_valid_lowercase(self) -> None:
        """测试有效的纯小写字母."""
        alpha_test = AlphaTestModel(username='hello')
        result = sync_test_alpha_decorator(alpha_test=alpha_test)
        assert result == {'username': 'hello', 'upper_name': None, 'lower_name': None, 'mixed_name': None}

    def test_alpha_decorator_empty_username(self) -> None:
        """测试空用户名."""
        alpha_test = AlphaTestModel()
        result = sync_test_alpha_decorator(alpha_test=alpha_test)
        assert result == {'username': None, 'upper_name': None, 'lower_name': None, 'mixed_name': None}

    def test_alpha_decorator_invalid_with_numbers(self) -> None:
        """测试包含数字的无效用户名."""
        alpha_test = AlphaTestModel(username='hello123')
        with pytest.raises(FieldValidationError) as exc_info:
            sync_test_alpha_decorator(alpha_test=alpha_test)

        error = exc_info.value
        assert error.field_name == 'username'
        assert error.message == '用户名必须只包含字母'

    def test_alpha_decorator_invalid_with_special_chars(self) -> None:
        """测试包含特殊字符的无效用户名."""
        alpha_test = AlphaTestModel(username='hello@world')
        with pytest.raises(FieldValidationError) as exc_info:
            sync_test_alpha_decorator(alpha_test=alpha_test)

        error = exc_info.value
        assert error.field_name == 'username'
        assert error.message == '用户名必须只包含字母'

    def test_alpha_decorator_invalid_with_spaces(self) -> None:
        """测试包含空格的无效用户名."""
        alpha_test = AlphaTestModel(username='hello world')
        with pytest.raises(FieldValidationError) as exc_info:
            sync_test_alpha_decorator(alpha_test=alpha_test)

        error = exc_info.value
        assert error.field_name == 'username'
        assert error.message == '用户名必须只包含字母'

    def test_alpha_decorator_invalid_empty_string(self) -> None:
        """测试空字符串."""
        alpha_test = AlphaTestModel(username='')
        with pytest.raises(FieldValidationError) as exc_info:
            sync_test_alpha_decorator(alpha_test=alpha_test)

        error = exc_info.value
        assert error.field_name == 'username'
        assert error.message == '用户名必须只包含字母'

    def test_alpha_decorator_upper_mode_valid(self) -> None:
        """测试大写模式 - 有效输入."""
        alpha_test = AlphaTestModel(upper_name='HELLO')
        assert alpha_test.get_upper_name() == 'HELLO'

    def test_alpha_decorator_upper_mode_invalid_lowercase(self) -> None:
        """测试大写模式 - 包含小写字母的无效输入."""
        alpha_test = AlphaTestModel(upper_name='Hello')
        with pytest.raises(FieldValidationError) as exc_info:
            alpha_test.get_upper_name()

        error = exc_info.value
        assert error.field_name == 'upper_name'
        assert error.message == '名称必须只包含大写字母'

    def test_alpha_decorator_lower_mode_valid(self) -> None:
        """测试小写模式 - 有效输入."""
        alpha_test = AlphaTestModel(lower_name='hello')
        assert alpha_test.get_lower_name() == 'hello'

    def test_alpha_decorator_lower_mode_invalid_uppercase(self) -> None:
        """测试小写模式 - 包含大写字母的无效输入."""
        alpha_test = AlphaTestModel(lower_name='Hello')
        with pytest.raises(FieldValidationError) as exc_info:
            alpha_test.get_lower_name()

        error = exc_info.value
        assert error.field_name == 'lower_name'
        assert error.message == '名称必须只包含小写字母'

    def test_alpha_decorator_default_message(self) -> None:
        """测试默认错误消息."""
        alpha_test = AlphaTestModel(mixed_name='hello123')
        with pytest.raises(FieldValidationError) as exc_info:
            alpha_test.get_mixed_name()

        error = exc_info.value
        assert error.field_name == 'mixed_name'
        assert error.message == 'mixed_name must contain only letters.'

    @pytest.mark.asyncio
    async def test_async_alpha_decorator_valid_mixed_case(self) -> None:
        """测试异步装饰器有效的混合大小写字母."""
        alpha_test = AlphaTestModel(username='HelloWorld')
        result = await async_test_alpha_decorator(1, alpha_test)
        assert result == {'username': 'HelloWorld', 'upper_name': None, 'lower_name': None, 'mixed_name': None}

    @pytest.mark.asyncio
    async def test_async_alpha_decorator_valid_uppercase(self) -> None:
        """测试异步装饰器有效的纯大写字母."""
        alpha_test = AlphaTestModel(username='HELLO')
        result = await async_test_alpha_decorator(1, alpha_test)
        assert result == {'username': 'HELLO', 'upper_name': None, 'lower_name': None, 'mixed_name': None}

    @pytest.mark.asyncio
    async def test_async_alpha_decorator_valid_lowercase(self) -> None:
        """测试异步装饰器有效的纯小写字母."""
        alpha_test = AlphaTestModel(username='hello')
        result = await async_test_alpha_decorator(1, alpha_test)
        assert result == {'username': 'hello', 'upper_name': None, 'lower_name': None, 'mixed_name': None}

    @pytest.mark.asyncio
    async def test_async_alpha_decorator_empty_username(self) -> None:
        """测试异步装饰器空用户名."""
        alpha_test = AlphaTestModel()
        result = await async_test_alpha_decorator(1, alpha_test)
        assert result == {'username': None, 'upper_name': None, 'lower_name': None, 'mixed_name': None}

    @pytest.mark.asyncio
    async def test_async_alpha_decorator_invalid_with_numbers(self) -> None:
        """测试异步装饰器包含数字的无效用户名."""
        alpha_test = AlphaTestModel(username='hello123')
        with pytest.raises(FieldValidationError) as exc_info:
            await async_test_alpha_decorator(1, alpha_test)

        error = exc_info.value
        assert error.field_name == 'username'
        assert error.message == '用户名必须只包含字母'

    @pytest.mark.asyncio
    async def test_async_alpha_decorator_invalid_with_special_chars(self) -> None:
        """测试异步装饰器包含特殊字符的无效用户名."""
        alpha_test = AlphaTestModel(username='hello@world')
        with pytest.raises(FieldValidationError) as exc_info:
            await async_test_alpha_decorator(1, alpha_test)

        error = exc_info.value
        assert error.field_name == 'username'
        assert error.message == '用户名必须只包含字母'

    @pytest.mark.asyncio
    async def test_async_alpha_decorator_invalid_with_spaces(self) -> None:
        """测试异步装饰器包含空格的无效用户名."""
        alpha_test = AlphaTestModel(username='hello world')
        with pytest.raises(FieldValidationError) as exc_info:
            await async_test_alpha_decorator(1, alpha_test)

        error = exc_info.value
        assert error.field_name == 'username'
        assert error.message == '用户名必须只包含字母'

    @pytest.mark.asyncio
    async def test_async_alpha_decorator_invalid_empty_string(self) -> None:
        """测试异步装饰器空字符串."""
        alpha_test = AlphaTestModel(username='')
        with pytest.raises(FieldValidationError) as exc_info:
            await async_test_alpha_decorator(1, alpha_test)

        error = exc_info.value
        assert error.field_name == 'username'
        assert error.message == '用户名必须只包含字母'

    def test_alpha_decorator_non_string_type(self) -> None:
        """测试非字符串类型的输入."""
        alpha_test = AlphaTestModel()
        # 设置一个非字符串类型的值（虽然 Pydantic 会尝试转换，但我们可以直接设置）
        alpha_test.__dict__['username'] = 123

        with pytest.raises(FieldValidationError) as exc_info:
            alpha_test.get_username()

        error = exc_info.value
        assert error.field_name == 'username'
        assert error.message == '用户名必须只包含字母'
