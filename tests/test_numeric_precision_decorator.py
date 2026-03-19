from decimal import Decimal
from typing import Optional
import pytest
from pydantic import BaseModel
from pydantic_validation_decorator import (
    FieldValidationError,
    NumericPrecision,
    ValidateFields,
)


class NumericPrecisionAmountTestModel(BaseModel):
    """NumericPrecision 金额精度场景测试模型"""

    amount: Optional[float] = None

    @NumericPrecision(
        field_name='amount',
        max_digits=6,
        decimal_places=2,
        message='amount precision is invalid',
    )
    def get_amount(self):
        return self.amount

    def validate_fields(self):
        self.get_amount()


class NumericPrecisionCountTestModel(BaseModel):
    """NumericPrecision 整数位数场景测试模型"""

    count: Optional[int] = None

    @NumericPrecision(
        field_name='count',
        max_digits=3,
        message='count precision is invalid',
    )
    def get_count(self):
        return self.count

    def validate_fields(self):
        self.get_count()


class NumericPrecisionAnyTypeTestModel(BaseModel):
    """NumericPrecision 任意类型输入场景测试模型"""

    price: Optional[object] = None

    @NumericPrecision(
        field_name='price',
        max_digits=5,
        decimal_places=2,
        allow_string_number=True,
        message='price precision is invalid',
    )
    def get_price(self):
        return self.price

    def validate_fields(self):
        self.get_price()


class NumericPrecisionNoneStrictTestModel(BaseModel):
    """NumericPrecision None 严格校验场景测试模型"""

    value: Optional[float] = None

    @NumericPrecision(
        field_name='value',
        max_digits=4,
        allow_none=False,
        message='value precision is invalid',
    )
    def get_value(self):
        return self.value

    def validate_fields(self):
        self.get_value()


@ValidateFields(validate_model='numeric_precision_amount_test')
def sync_test_numeric_precision_amount_decorator(numeric_precision_amount_test: NumericPrecisionAmountTestModel):
    return numeric_precision_amount_test.model_dump()


@ValidateFields(mode='args', validate_model_index=0)
async def async_test_numeric_precision_amount_decorator(numeric_precision_amount_test: NumericPrecisionAmountTestModel):
    return numeric_precision_amount_test.model_dump()


@ValidateFields(validate_model='numeric_precision_count_test')
def sync_test_numeric_precision_count_decorator(numeric_precision_count_test: NumericPrecisionCountTestModel):
    return numeric_precision_count_test.model_dump()


@ValidateFields(validate_model='numeric_precision_any_type_test')
def sync_test_numeric_precision_any_type_decorator(numeric_precision_any_type_test: NumericPrecisionAnyTypeTestModel):
    return numeric_precision_any_type_test.model_dump()


@ValidateFields(mode='args', validate_model_index=0)
async def async_test_numeric_precision_any_type_decorator(
    numeric_precision_any_type_test: NumericPrecisionAnyTypeTestModel,
):
    return numeric_precision_any_type_test.model_dump()


@ValidateFields(validate_model='numeric_precision_none_strict_test')
def sync_test_numeric_precision_none_strict_decorator(
    numeric_precision_none_strict_test: NumericPrecisionNoneStrictTestModel,
):
    return numeric_precision_none_strict_test.model_dump()


class TestNumericPrecisionDecorator:
    """测试 NumericPrecision 装饰器功能"""

    def test_sync_numeric_precision_amount_valid(self):
        """测试同步场景：总位数和小数位都满足约束时通过"""
        numeric_precision_amount_test = NumericPrecisionAmountTestModel(amount=1234.56)
        result = sync_test_numeric_precision_amount_decorator(
            numeric_precision_amount_test=numeric_precision_amount_test,
        )
        assert result == {'amount': 1234.56}

    def test_sync_numeric_precision_amount_decimal_places_invalid(self):
        """测试同步场景：小数位超过约束时触发验证错误"""
        numeric_precision_amount_test = NumericPrecisionAmountTestModel(amount=12.345)
        with pytest.raises(FieldValidationError) as exc_info:
            sync_test_numeric_precision_amount_decorator(
                numeric_precision_amount_test=numeric_precision_amount_test,
            )

        error = exc_info.value
        assert error.field_name == 'amount'
        assert 'amount precision is invalid' in error.message

    def test_sync_numeric_precision_count_valid(self):
        """测试同步场景：整数位数满足约束时通过"""
        numeric_precision_count_test = NumericPrecisionCountTestModel(count=999)
        result = sync_test_numeric_precision_count_decorator(
            numeric_precision_count_test=numeric_precision_count_test,
        )
        assert result == {'count': 999}

    def test_sync_numeric_precision_count_max_digits_invalid(self):
        """测试同步场景：总位数超过约束时触发验证错误"""
        numeric_precision_count_test = NumericPrecisionCountTestModel(count=1000)
        with pytest.raises(FieldValidationError):
            sync_test_numeric_precision_count_decorator(
                numeric_precision_count_test=numeric_precision_count_test,
            )

    def test_sync_numeric_precision_allow_none_skip(self):
        """测试同步场景：allow_none=True 且字段为 None 时跳过校验"""
        numeric_precision_amount_test = NumericPrecisionAmountTestModel(amount=None)
        result = sync_test_numeric_precision_amount_decorator(
            numeric_precision_amount_test=numeric_precision_amount_test,
        )
        assert result == {'amount': None}

    def test_sync_numeric_precision_allow_none_false_fail(self):
        """测试同步场景：allow_none=False 且字段为 None 时触发验证错误"""
        numeric_precision_none_strict_test = NumericPrecisionNoneStrictTestModel(value=None)
        with pytest.raises(FieldValidationError):
            sync_test_numeric_precision_none_strict_decorator(
                numeric_precision_none_strict_test=numeric_precision_none_strict_test,
            )

    def test_sync_numeric_precision_string_number_valid(self):
        """测试同步场景：允许数字字符串输入时可通过校验"""
        numeric_precision_any_type_test = NumericPrecisionAnyTypeTestModel(price='123.45')
        result = sync_test_numeric_precision_any_type_decorator(
            numeric_precision_any_type_test=numeric_precision_any_type_test,
        )
        assert result == {'price': '123.45'}

    def test_sync_numeric_precision_string_number_invalid(self):
        """测试同步场景：数字字符串超出约束时触发验证错误"""
        numeric_precision_any_type_test = NumericPrecisionAnyTypeTestModel(price='1234.567')
        with pytest.raises(FieldValidationError):
            sync_test_numeric_precision_any_type_decorator(
                numeric_precision_any_type_test=numeric_precision_any_type_test,
            )

    def test_sync_numeric_precision_non_numeric_type_invalid(self):
        """测试同步场景：非数字输入触发验证错误"""
        numeric_precision_any_type_test = NumericPrecisionAnyTypeTestModel(price={'amount': 1})
        with pytest.raises(FieldValidationError):
            sync_test_numeric_precision_any_type_decorator(
                numeric_precision_any_type_test=numeric_precision_any_type_test,
            )

    def test_sync_numeric_precision_decimal_type_valid(self):
        """测试同步场景：Decimal 输入满足约束时通过"""
        numeric_precision_any_type_test = NumericPrecisionAnyTypeTestModel(price=Decimal('12.30'))
        result = sync_test_numeric_precision_any_type_decorator(
            numeric_precision_any_type_test=numeric_precision_any_type_test,
        )
        assert result == {'price': Decimal('12.30')}

    def test_numeric_precision_invalid_init_both_none(self):
        """测试初始化场景：max_digits 和 decimal_places 不能同时为空"""
        with pytest.raises(ValueError):
            NumericPrecision(field_name='amount')

    def test_numeric_precision_invalid_init_max_digits(self):
        """测试初始化场景：max_digits 小于等于 0 时抛异常"""
        with pytest.raises(ValueError):
            NumericPrecision(field_name='amount', max_digits=0)

    def test_numeric_precision_invalid_init_decimal_places(self):
        """测试初始化场景：decimal_places 小于 0 时抛异常"""
        with pytest.raises(ValueError):
            NumericPrecision(field_name='amount', decimal_places=-1)

    def test_numeric_precision_invalid_init_decimal_places_gt_max_digits(self):
        """测试初始化场景：decimal_places 大于 max_digits 时抛异常"""
        with pytest.raises(ValueError):
            NumericPrecision(field_name='amount', max_digits=2, decimal_places=3)

    @pytest.mark.asyncio
    async def test_async_numeric_precision_amount_valid(self):
        """测试异步场景：金额精度满足约束时通过"""
        numeric_precision_amount_test = NumericPrecisionAmountTestModel(amount=1234.56)
        result = await async_test_numeric_precision_amount_decorator(numeric_precision_amount_test)
        assert result == {'amount': 1234.56}

    @pytest.mark.asyncio
    async def test_async_numeric_precision_amount_invalid(self):
        """测试异步场景：金额精度超出约束时触发验证错误"""
        numeric_precision_amount_test = NumericPrecisionAmountTestModel(amount=12345.67)
        with pytest.raises(FieldValidationError):
            await async_test_numeric_precision_amount_decorator(numeric_precision_amount_test)

    @pytest.mark.asyncio
    async def test_async_numeric_precision_string_number_valid(self):
        """测试异步场景：允许数字字符串输入时可通过校验"""
        numeric_precision_any_type_test = NumericPrecisionAnyTypeTestModel(price='1.20')
        result = await async_test_numeric_precision_any_type_decorator(numeric_precision_any_type_test)
        assert result == {'price': '1.20'}

    @pytest.mark.asyncio
    async def test_async_numeric_precision_string_number_invalid(self):
        """测试异步场景：非法数字字符串触发验证错误"""
        numeric_precision_any_type_test = NumericPrecisionAnyTypeTestModel(price='12.3.4')
        with pytest.raises(FieldValidationError):
            await async_test_numeric_precision_any_type_decorator(numeric_precision_any_type_test)
