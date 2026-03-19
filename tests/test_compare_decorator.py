import pytest
from pydantic import BaseModel
from typing import Optional
from pydantic_validation_decorator import (
    ValidateFields,
    Compare,
    FieldValidationError,
)


class CompareRangeTestModel(BaseModel):
    """Compare 数值范围场景测试模型"""

    min_value: Optional[int] = None
    max_value: Optional[int] = None

    @Compare(
        left_field='min_value',
        right_field='max_value',
        operator='le',
        message='min_value must be less than or equal to max_value',
    )
    def validate_range(self):
        return (self.min_value, self.max_value)

    def validate_fields(self):
        self.validate_range()


class CompareEqualTestModel(BaseModel):
    """Compare 相等场景测试模型"""

    password: Optional[str] = None
    confirm_password: Optional[str] = None

    @Compare(
        left_field='password',
        right_field='confirm_password',
        operator='eq',
        message='password and confirm_password must be equal',
    )
    def validate_password(self):
        return self.password

    def validate_fields(self):
        self.validate_password()


class CompareNoneStrictTestModel(BaseModel):
    """Compare None 严格校验场景测试模型"""

    left_value: Optional[int] = None
    right_value: Optional[int] = None

    @Compare(
        left_field='left_value',
        right_field='right_value',
        operator='gt',
        allow_none=False,
        message='left_value must be greater than right_value',
    )
    def validate_values(self):
        return self.left_value

    def validate_fields(self):
        self.validate_values()


@ValidateFields(validate_model='compare_range_test')
def sync_test_compare_range_decorator(compare_range_test: CompareRangeTestModel):
    return compare_range_test.model_dump()


@ValidateFields(mode='args', validate_model_index=0)
async def async_test_compare_range_decorator(compare_range_test: CompareRangeTestModel):
    return compare_range_test.model_dump()


@ValidateFields(validate_model='compare_equal_test')
def sync_test_compare_equal_decorator(compare_equal_test: CompareEqualTestModel):
    return compare_equal_test.model_dump()


@ValidateFields(mode='args', validate_model_index=0)
async def async_test_compare_equal_decorator(compare_equal_test: CompareEqualTestModel):
    return compare_equal_test.model_dump()


@ValidateFields(validate_model='compare_none_strict_test')
def sync_test_compare_none_strict_decorator(compare_none_strict_test: CompareNoneStrictTestModel):
    return compare_none_strict_test.model_dump()


@ValidateFields(mode='args', validate_model_index=0)
async def async_test_compare_none_strict_decorator(compare_none_strict_test: CompareNoneStrictTestModel):
    return compare_none_strict_test.model_dump()


class TestCompareDecorator:
    """测试 Compare 装饰器功能"""

    def test_sync_compare_range_valid(self):
        """测试同步场景：min_value <= max_value 时验证通过"""
        compare_range_test = CompareRangeTestModel(min_value=1, max_value=3)
        result = sync_test_compare_range_decorator(compare_range_test=compare_range_test)
        assert result == {'min_value': 1, 'max_value': 3}

    def test_sync_compare_range_invalid(self):
        """测试同步场景：min_value > max_value 时触发验证错误"""
        compare_range_test = CompareRangeTestModel(min_value=5, max_value=3)
        with pytest.raises(FieldValidationError) as exc_info:
            sync_test_compare_range_decorator(compare_range_test=compare_range_test)

        error = exc_info.value
        assert error.field_name == 'min_value'
        assert 'min_value must be less than or equal to max_value' in error.message

    def test_sync_compare_equal_valid(self):
        """测试同步场景：两个字段相等时验证通过"""
        compare_equal_test = CompareEqualTestModel(password='abc123', confirm_password='abc123')
        result = sync_test_compare_equal_decorator(compare_equal_test=compare_equal_test)
        assert result == {'password': 'abc123', 'confirm_password': 'abc123'}

    def test_sync_compare_equal_invalid(self):
        """测试同步场景：两个字段不相等时触发验证错误"""
        compare_equal_test = CompareEqualTestModel(password='abc123', confirm_password='abc456')
        with pytest.raises(FieldValidationError) as exc_info:
            sync_test_compare_equal_decorator(compare_equal_test=compare_equal_test)

        error = exc_info.value
        assert error.field_name == 'password'
        assert 'password and confirm_password must be equal' in error.message

    def test_sync_compare_allow_none_skip(self):
        """测试同步场景：allow_none=True 且存在 None 时跳过比较"""
        compare_range_test = CompareRangeTestModel(min_value=None, max_value=3)
        result = sync_test_compare_range_decorator(compare_range_test=compare_range_test)
        assert result == {'min_value': None, 'max_value': 3}

    def test_sync_compare_allow_none_false_fail(self):
        """测试同步场景：allow_none=False 且存在 None 时触发验证错误"""
        compare_none_strict_test = CompareNoneStrictTestModel(left_value=None, right_value=1)
        with pytest.raises(FieldValidationError) as exc_info:
            sync_test_compare_none_strict_decorator(compare_none_strict_test=compare_none_strict_test)

        error = exc_info.value
        assert error.field_name == 'left_value'
        assert 'left_value must be greater than right_value' in error.message

    def test_compare_invalid_operator(self):
        """测试初始化场景：非法操作符会抛出 ValueError"""
        with pytest.raises(ValueError):
            Compare(left_field='a', right_field='b', operator='invalid')

    @pytest.mark.asyncio
    async def test_async_compare_range_valid(self):
        """测试异步场景：min_value <= max_value 时验证通过"""
        compare_range_test = CompareRangeTestModel(min_value=1, max_value=3)
        result = await async_test_compare_range_decorator(compare_range_test)
        assert result == {'min_value': 1, 'max_value': 3}

    @pytest.mark.asyncio
    async def test_async_compare_range_invalid(self):
        """测试异步场景：min_value > max_value 时触发验证错误"""
        compare_range_test = CompareRangeTestModel(min_value=5, max_value=3)
        with pytest.raises(FieldValidationError):
            await async_test_compare_range_decorator(compare_range_test)

    @pytest.mark.asyncio
    async def test_async_compare_equal_valid(self):
        """测试异步场景：两个字段相等时验证通过"""
        compare_equal_test = CompareEqualTestModel(password='abc123', confirm_password='abc123')
        result = await async_test_compare_equal_decorator(compare_equal_test)
        assert result == {'password': 'abc123', 'confirm_password': 'abc123'}

    @pytest.mark.asyncio
    async def test_async_compare_equal_invalid(self):
        """测试异步场景：两个字段不相等时触发验证错误"""
        compare_equal_test = CompareEqualTestModel(password='abc123', confirm_password='abc456')
        with pytest.raises(FieldValidationError):
            await async_test_compare_equal_decorator(compare_equal_test)

    @pytest.mark.asyncio
    async def test_async_compare_allow_none_skip(self):
        """测试异步场景：allow_none=True 且存在 None 时跳过比较"""
        compare_range_test = CompareRangeTestModel(min_value=1, max_value=None)
        result = await async_test_compare_range_decorator(compare_range_test)
        assert result == {'min_value': 1, 'max_value': None}

    @pytest.mark.asyncio
    async def test_async_compare_allow_none_false_fail(self):
        """测试异步场景：allow_none=False 且存在 None 时触发验证错误"""
        compare_none_strict_test = CompareNoneStrictTestModel(left_value=2, right_value=None)
        with pytest.raises(FieldValidationError):
            await async_test_compare_none_strict_decorator(compare_none_strict_test)
