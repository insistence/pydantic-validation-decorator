from typing import Any

import pytest
from pydantic import BaseModel

from pydantic_validation_decorator import (
    FieldValidationError,
    RequiredIf,
    ValidateFields,
)


class RequiredIfTestModel(BaseModel):
    """RequiredIf 基础场景测试模型."""

    auth_type: str | None = None
    access_token: str | None = None

    @RequiredIf(
        field_name='access_token',
        when_field='auth_type',
        when_value='token',
        message='access_token is required when auth_type is token',
    )
    def get_access_token(self) -> str | None:
        return self.access_token

    def validate_fields(self) -> None:
        self.get_access_token()


class RequiredIfMultiValueTestModel(BaseModel):
    """RequiredIf 多触发值场景测试模型."""

    login_type: str | None = None
    credential: str | None = None

    @RequiredIf(
        field_name='credential',
        when_field='login_type',
        when_value=('token', 'oauth'),
        message='credential is required for token or oauth login type',
    )
    def get_credential(self) -> str | None:
        return self.credential

    def validate_fields(self) -> None:
        self.get_credential()


@ValidateFields(validate_model='required_if_test')
def sync_test_required_if_decorator(required_if_test: RequiredIfTestModel) -> dict[str, Any]:
    return required_if_test.model_dump()


@ValidateFields(mode='args', validate_model_index=0)
async def async_test_required_if_decorator(required_if_test: RequiredIfTestModel) -> dict[str, Any]:
    return required_if_test.model_dump()


@ValidateFields(validate_model='required_if_multi_value_test')
def sync_test_required_if_multi_value_decorator(
    required_if_multi_value_test: RequiredIfMultiValueTestModel,
) -> dict[str, Any]:
    return required_if_multi_value_test.model_dump()


@ValidateFields(mode='args', validate_model_index=0)
async def async_test_required_if_multi_value_decorator(
    required_if_multi_value_test: RequiredIfMultiValueTestModel,
) -> dict[str, Any]:
    return required_if_multi_value_test.model_dump()


class TestRequiredIfDecorator:
    """测试 RequiredIf 装饰器功能."""

    def test_sync_required_if_with_valid_value(self) -> None:
        """测试同步场景：条件命中且目标字段有值，验证通过."""
        required_if_test = RequiredIfTestModel(auth_type='token', access_token='abc123')
        result = sync_test_required_if_decorator(required_if_test=required_if_test)
        assert result == {'auth_type': 'token', 'access_token': 'abc123'}

    def test_sync_required_if_with_none_when_required(self) -> None:
        """测试同步场景：条件命中且目标字段为None，触发验证错误."""
        required_if_test = RequiredIfTestModel(auth_type='token')
        with pytest.raises(FieldValidationError) as exc_info:
            sync_test_required_if_decorator(required_if_test=required_if_test)

        error = exc_info.value
        assert error.field_name == 'access_token'
        assert error.message == 'access_token is required when auth_type is token'

    def test_sync_required_if_not_triggered(self) -> None:
        """测试同步场景：条件未命中，跳过必填校验."""
        required_if_test = RequiredIfTestModel(auth_type='password')
        result = sync_test_required_if_decorator(required_if_test=required_if_test)
        assert result == {'auth_type': 'password', 'access_token': None}

    def test_sync_required_if_with_empty_string_when_required(self) -> None:
        """测试同步场景：条件命中且目标字段为空字符串，触发验证错误."""
        required_if_test = RequiredIfTestModel(auth_type='token', access_token='')
        with pytest.raises(FieldValidationError):
            sync_test_required_if_decorator(required_if_test=required_if_test)

    def test_sync_required_if_multi_value_triggered(self) -> None:
        """测试同步场景：多触发值命中时，目标字段必填."""
        required_if_multi_value_test = RequiredIfMultiValueTestModel(login_type='oauth')
        with pytest.raises(FieldValidationError) as exc_info:
            sync_test_required_if_multi_value_decorator(
                required_if_multi_value_test=required_if_multi_value_test,
            )

        error = exc_info.value
        assert error.field_name == 'credential'
        assert error.message == 'credential is required for token or oauth login type'

    def test_sync_required_if_multi_value_not_triggered(self) -> None:
        """测试同步场景：多触发值未命中时，跳过必填校验."""
        required_if_multi_value_test = RequiredIfMultiValueTestModel(login_type='password')
        result = sync_test_required_if_multi_value_decorator(
            required_if_multi_value_test=required_if_multi_value_test,
        )
        assert result == {'login_type': 'password', 'credential': None}

    @pytest.mark.asyncio
    async def test_async_required_if_with_valid_value(self) -> None:
        """测试异步场景：条件命中且目标字段有值，验证通过."""
        required_if_test = RequiredIfTestModel(auth_type='token', access_token='abc123')
        result = await async_test_required_if_decorator(required_if_test)
        assert result == {'auth_type': 'token', 'access_token': 'abc123'}

    @pytest.mark.asyncio
    async def test_async_required_if_with_none_when_required(self) -> None:
        """测试异步场景：条件命中且目标字段为None，触发验证错误."""
        required_if_test = RequiredIfTestModel(auth_type='token')
        with pytest.raises(FieldValidationError) as exc_info:
            await async_test_required_if_decorator(required_if_test)

        error = exc_info.value
        assert error.field_name == 'access_token'
        assert error.message == 'access_token is required when auth_type is token'

    @pytest.mark.asyncio
    async def test_async_required_if_not_triggered(self) -> None:
        """测试异步场景：条件未命中，跳过必填校验."""
        required_if_test = RequiredIfTestModel(auth_type='password')
        result = await async_test_required_if_decorator(required_if_test)
        assert result == {'auth_type': 'password', 'access_token': None}

    @pytest.mark.asyncio
    async def test_async_required_if_multi_value_triggered(self) -> None:
        """测试异步场景：多触发值命中时，目标字段必填."""
        required_if_multi_value_test = RequiredIfMultiValueTestModel(login_type='token')
        with pytest.raises(FieldValidationError) as exc_info:
            await async_test_required_if_multi_value_decorator(required_if_multi_value_test)

        error = exc_info.value
        assert error.field_name == 'credential'
        assert error.message == 'credential is required for token or oauth login type'

    @pytest.mark.asyncio
    async def test_async_required_if_multi_value_not_triggered(self) -> None:
        """测试异步场景：多触发值未命中时，跳过必填校验."""
        required_if_multi_value_test = RequiredIfMultiValueTestModel(login_type='password')
        result = await async_test_required_if_multi_value_decorator(required_if_multi_value_test)
        assert result == {'login_type': 'password', 'credential': None}
