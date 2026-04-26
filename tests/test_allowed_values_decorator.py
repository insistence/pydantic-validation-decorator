from typing import Optional

import pytest
from pydantic import BaseModel

from pydantic_validation_decorator import (
    AllowedValues,
    FieldValidationError,
    ValidateFields,
)


class AllowedValuesStatusTestModel(BaseModel):
    """AllowedValues 基础场景测试模型"""

    status: Optional[str] = None

    @AllowedValues(
        field_name='status',
        choices=('draft', 'published', 'archived'),
        message='status is invalid',
    )
    def get_status(self):
        return self.status

    def validate_fields(self):
        self.get_status()


class AllowedValuesCaseInsensitiveTestModel(BaseModel):
    """AllowedValues 大小写不敏感场景测试模型"""

    channel: Optional[str] = None

    @AllowedValues(
        field_name='channel',
        choices=('web', 'api'),
        case_sensitive=False,
    )
    def get_channel(self):
        return self.channel

    def validate_fields(self):
        self.get_channel()


class AllowedValuesNoneStrictTestModel(BaseModel):
    """AllowedValues None 严格校验场景测试模型"""

    status: Optional[str] = None

    @AllowedValues(
        field_name='status',
        choices=('enabled', 'disabled'),
        allow_none=False,
        message='status is required and must be valid',
    )
    def get_status(self):
        return self.status

    def validate_fields(self):
        self.get_status()


@ValidateFields(validate_model='allowed_values_status_test')
def sync_test_allowed_values_decorator(allowed_values_status_test: AllowedValuesStatusTestModel):
    return allowed_values_status_test.model_dump()


@ValidateFields(mode='args', validate_model_index=0)
async def async_test_allowed_values_decorator(allowed_values_status_test: AllowedValuesStatusTestModel):
    return allowed_values_status_test.model_dump()


@ValidateFields(validate_model='allowed_values_case_insensitive_test')
def sync_test_allowed_values_case_insensitive_decorator(
    allowed_values_case_insensitive_test: AllowedValuesCaseInsensitiveTestModel,
):
    return allowed_values_case_insensitive_test.model_dump()


@ValidateFields(validate_model='allowed_values_none_strict_test')
def sync_test_allowed_values_none_strict_decorator(
    allowed_values_none_strict_test: AllowedValuesNoneStrictTestModel,
):
    return allowed_values_none_strict_test.model_dump()


class TestAllowedValuesDecorator:
    """测试 AllowedValues 装饰器功能"""

    def test_sync_allowed_values_valid(self):
        """测试同步场景：字段值在允许值范围内时验证通过"""
        allowed_values_status_test = AllowedValuesStatusTestModel(status='draft')
        result = sync_test_allowed_values_decorator(allowed_values_status_test=allowed_values_status_test)
        assert result == {'status': 'draft'}

    def test_sync_allowed_values_invalid(self):
        """测试同步场景：字段值不在允许值范围内时触发验证错误"""
        allowed_values_status_test = AllowedValuesStatusTestModel(status='deleted')
        with pytest.raises(FieldValidationError) as exc_info:
            sync_test_allowed_values_decorator(allowed_values_status_test=allowed_values_status_test)

        error = exc_info.value
        assert error.field_name == 'status'
        assert 'status is invalid' in error.message

    def test_sync_allowed_values_allow_none_skip(self):
        """测试同步场景：allow_none=True 且字段值为 None 时跳过验证"""
        allowed_values_status_test = AllowedValuesStatusTestModel(status=None)
        result = sync_test_allowed_values_decorator(allowed_values_status_test=allowed_values_status_test)
        assert result == {'status': None}

    def test_sync_allowed_values_allow_none_false_fail(self):
        """测试同步场景：allow_none=False 且字段值为 None 时触发验证错误"""
        allowed_values_none_strict_test = AllowedValuesNoneStrictTestModel(status=None)
        with pytest.raises(FieldValidationError) as exc_info:
            sync_test_allowed_values_none_strict_decorator(
                allowed_values_none_strict_test=allowed_values_none_strict_test,
            )

        error = exc_info.value
        assert error.field_name == 'status'
        assert 'status is required and must be valid' in error.message

    def test_sync_allowed_values_case_insensitive_valid(self):
        """测试同步场景：case_sensitive=False 时允许大小写不敏感匹配"""
        allowed_values_case_insensitive_test = AllowedValuesCaseInsensitiveTestModel(channel='WEB')
        result = sync_test_allowed_values_case_insensitive_decorator(
            allowed_values_case_insensitive_test=allowed_values_case_insensitive_test,
        )
        assert result == {'channel': 'WEB'}

    def test_sync_allowed_values_default_message(self):
        """测试同步场景：未传入自定义消息时使用默认错误消息"""
        allowed_values_case_insensitive_test = AllowedValuesCaseInsensitiveTestModel(channel='mobile')
        with pytest.raises(FieldValidationError) as exc_info:
            sync_test_allowed_values_case_insensitive_decorator(
                allowed_values_case_insensitive_test=allowed_values_case_insensitive_test,
            )

        error = exc_info.value
        assert error.field_name == 'channel'
        assert "channel must be one of ('web', 'api')." in error.message

    def test_allowed_values_invalid_init_empty_choices(self):
        """测试初始化场景：choices 为空时抛出 ValueError"""
        with pytest.raises(ValueError):
            AllowedValues(field_name='status', choices=())

    @pytest.mark.asyncio
    async def test_async_allowed_values_valid(self):
        """测试异步场景：字段值在允许值范围内时验证通过"""
        allowed_values_status_test = AllowedValuesStatusTestModel(status='published')
        result = await async_test_allowed_values_decorator(allowed_values_status_test)
        assert result == {'status': 'published'}

    @pytest.mark.asyncio
    async def test_async_allowed_values_invalid(self):
        """测试异步场景：字段值不在允许值范围内时触发验证错误"""
        allowed_values_status_test = AllowedValuesStatusTestModel(status='deleted')
        with pytest.raises(FieldValidationError):
            await async_test_allowed_values_decorator(allowed_values_status_test)
