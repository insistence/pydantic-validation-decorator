from typing import Optional

import pytest
from pydantic import BaseModel

from pydantic_validation_decorator import (
    AtLeastOneOf,
    FieldValidationError,
    ValidateFields,
)


class AtLeastOneOfContactTestModel(BaseModel):
    """AtLeastOneOf 基础场景测试模型"""

    email: Optional[str] = None
    mobile: Optional[str] = None

    @AtLeastOneOf(
        fields=['email', 'mobile'],
        message='email or mobile must provide at least one',
    )
    def get_contact(self):
        return self.email, self.mobile

    def validate_fields(self):
        self.get_contact()


class AtLeastOneOfMinCountTestModel(BaseModel):
    """AtLeastOneOf 最小提供数量场景测试模型"""

    contact_email: Optional[str] = None
    mobile: Optional[str] = None
    wechat: Optional[str] = None

    @AtLeastOneOf(
        fields=['contact_email', 'mobile', 'wechat'],
        min_count=2,
    )
    def get_contacts(self):
        return self.contact_email, self.mobile, self.wechat

    def validate_fields(self):
        self.get_contacts()


@ValidateFields(validate_model='at_least_one_of_contact_test')
def sync_test_at_least_one_of_decorator(at_least_one_of_contact_test: AtLeastOneOfContactTestModel):
    return at_least_one_of_contact_test.model_dump()


@ValidateFields(mode='args', validate_model_index=0)
async def async_test_at_least_one_of_decorator(at_least_one_of_contact_test: AtLeastOneOfContactTestModel):
    return at_least_one_of_contact_test.model_dump()


@ValidateFields(validate_model='at_least_one_of_min_count_test')
def sync_test_at_least_one_of_min_count_decorator(
    at_least_one_of_min_count_test: AtLeastOneOfMinCountTestModel,
):
    return at_least_one_of_min_count_test.model_dump()


class TestAtLeastOneOfDecorator:
    """测试 AtLeastOneOf 装饰器功能"""

    def test_sync_at_least_one_of_valid_with_one_field(self):
        """测试同步场景：至少提供一个字段时验证通过"""
        at_least_one_of_contact_test = AtLeastOneOfContactTestModel(email='test@example.com')
        result = sync_test_at_least_one_of_decorator(
            at_least_one_of_contact_test=at_least_one_of_contact_test,
        )
        assert result == {'email': 'test@example.com', 'mobile': None}

    def test_sync_at_least_one_of_valid_with_two_fields(self):
        """测试同步场景：提供多个字段时验证通过"""
        at_least_one_of_contact_test = AtLeastOneOfContactTestModel(
            email='test@example.com',
            mobile='13800138000',
        )
        result = sync_test_at_least_one_of_decorator(
            at_least_one_of_contact_test=at_least_one_of_contact_test,
        )
        assert result == {'email': 'test@example.com', 'mobile': '13800138000'}

    def test_sync_at_least_one_of_invalid(self):
        """测试同步场景：未提供任何字段时触发验证错误"""
        at_least_one_of_contact_test = AtLeastOneOfContactTestModel()
        with pytest.raises(FieldValidationError) as exc_info:
            sync_test_at_least_one_of_decorator(
                at_least_one_of_contact_test=at_least_one_of_contact_test,
            )

        error = exc_info.value
        assert error.field_name == 'email, mobile'
        assert 'email or mobile must provide at least one' in error.message

    def test_sync_at_least_one_of_empty_string_invalid(self):
        """测试同步场景：空字符串不计为已提供字段"""
        at_least_one_of_contact_test = AtLeastOneOfContactTestModel(email='', mobile=None)
        with pytest.raises(FieldValidationError):
            sync_test_at_least_one_of_decorator(
                at_least_one_of_contact_test=at_least_one_of_contact_test,
            )

    def test_sync_at_least_one_of_min_count_valid(self):
        """测试同步场景：满足最小提供数量时验证通过"""
        at_least_one_of_min_count_test = AtLeastOneOfMinCountTestModel(
            contact_email='test@example.com',
            wechat='tester',
        )
        result = sync_test_at_least_one_of_min_count_decorator(
            at_least_one_of_min_count_test=at_least_one_of_min_count_test,
        )
        assert result == {
            'contact_email': 'test@example.com',
            'mobile': None,
            'wechat': 'tester',
        }

    def test_sync_at_least_one_of_min_count_invalid(self):
        """测试同步场景：未满足最小提供数量时触发默认消息"""
        at_least_one_of_min_count_test = AtLeastOneOfMinCountTestModel(
            contact_email='test@example.com',
        )
        with pytest.raises(FieldValidationError) as exc_info:
            sync_test_at_least_one_of_min_count_decorator(
                at_least_one_of_min_count_test=at_least_one_of_min_count_test,
            )

        error = exc_info.value
        assert error.field_name == 'contact_email, mobile, wechat'
        assert 'At least 2 of contact_email, mobile, wechat must be provided.' in error.message

    def test_at_least_one_of_invalid_init_empty_fields(self):
        """测试初始化场景：fields 为空时抛出 ValueError"""
        with pytest.raises(ValueError):
            AtLeastOneOf(fields=[])

    def test_at_least_one_of_invalid_init_min_count_zero(self):
        """测试初始化场景：min_count 小于等于 0 时抛出 ValueError"""
        with pytest.raises(ValueError):
            AtLeastOneOf(fields=['email', 'mobile'], min_count=0)

    def test_at_least_one_of_invalid_init_min_count_too_large(self):
        """测试初始化场景：min_count 大于字段数量时抛出 ValueError"""
        with pytest.raises(ValueError):
            AtLeastOneOf(fields=['email', 'mobile'], min_count=3)

    @pytest.mark.asyncio
    async def test_async_at_least_one_of_valid(self):
        """测试异步场景：至少提供一个字段时验证通过"""
        at_least_one_of_contact_test = AtLeastOneOfContactTestModel(mobile='13800138000')
        result = await async_test_at_least_one_of_decorator(at_least_one_of_contact_test)
        assert result == {'email': None, 'mobile': '13800138000'}

    @pytest.mark.asyncio
    async def test_async_at_least_one_of_invalid(self):
        """测试异步场景：未提供任何字段时触发验证错误"""
        at_least_one_of_contact_test = AtLeastOneOfContactTestModel()
        with pytest.raises(FieldValidationError):
            await async_test_at_least_one_of_decorator(at_least_one_of_contact_test)
