from datetime import datetime
from typing import Optional
import pytest
from pydantic import BaseModel
from pydantic_validation_decorator import (
    DateTimeRange,
    FieldValidationError,
    ValidateFields,
)


class DateTimeRangeBasicTestModel(BaseModel):
    """DateTimeRange 基础范围场景测试模型"""

    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None

    @DateTimeRange(
        start_field='start_time',
        end_field='end_time',
        message='start_time must be less than or equal to end_time',
    )
    def get_time_range(self):
        return self.start_time, self.end_time

    def validate_fields(self):
        self.get_time_range()


class DateTimeRangeStrictTestModel(BaseModel):
    """DateTimeRange 严格小于场景测试模型"""

    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None

    @DateTimeRange(
        start_field='start_time',
        end_field='end_time',
        allow_equal=False,
        message='start_time must be less than end_time',
    )
    def get_time_range(self):
        return self.start_time, self.end_time

    def validate_fields(self):
        self.get_time_range()


class DateTimeRangeStringTestModel(BaseModel):
    """DateTimeRange 字符串解析场景测试模型"""

    start_time: Optional[str] = None
    end_time: Optional[str] = None

    @DateTimeRange(
        start_field='start_time',
        end_field='end_time',
        coerce_from_str=True,
        message='string datetime range is invalid',
    )
    def get_time_range(self):
        return self.start_time, self.end_time

    def validate_fields(self):
        self.get_time_range()


class DateTimeRangeTimezoneTestModel(BaseModel):
    """DateTimeRange 时区一致性场景测试模型"""

    start_time: Optional[str] = None
    end_time: Optional[str] = None

    @DateTimeRange(
        start_field='start_time',
        end_field='end_time',
        require_timezone_consistency=True,
        message='timezone awareness must be consistent',
    )
    def get_time_range(self):
        return self.start_time, self.end_time

    def validate_fields(self):
        self.get_time_range()


class DateTimeRangeNoneStrictTestModel(BaseModel):
    """DateTimeRange None 严格校验场景测试模型"""

    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None

    @DateTimeRange(
        start_field='start_time',
        end_field='end_time',
        allow_none=False,
        message='datetime cannot be none',
    )
    def get_time_range(self):
        return self.start_time, self.end_time

    def validate_fields(self):
        self.get_time_range()


@ValidateFields(validate_model='datetime_range_basic_test')
def sync_test_datetime_range_basic_decorator(datetime_range_basic_test: DateTimeRangeBasicTestModel):
    return datetime_range_basic_test.model_dump()


@ValidateFields(mode='args', validate_model_index=0)
async def async_test_datetime_range_basic_decorator(datetime_range_basic_test: DateTimeRangeBasicTestModel):
    return datetime_range_basic_test.model_dump()


@ValidateFields(validate_model='datetime_range_strict_test')
def sync_test_datetime_range_strict_decorator(datetime_range_strict_test: DateTimeRangeStrictTestModel):
    return datetime_range_strict_test.model_dump()


@ValidateFields(validate_model='datetime_range_string_test')
def sync_test_datetime_range_string_decorator(datetime_range_string_test: DateTimeRangeStringTestModel):
    return datetime_range_string_test.model_dump()


@ValidateFields(mode='args', validate_model_index=0)
async def async_test_datetime_range_string_decorator(datetime_range_string_test: DateTimeRangeStringTestModel):
    return datetime_range_string_test.model_dump()


@ValidateFields(validate_model='datetime_range_timezone_test')
def sync_test_datetime_range_timezone_decorator(datetime_range_timezone_test: DateTimeRangeTimezoneTestModel):
    return datetime_range_timezone_test.model_dump()


@ValidateFields(validate_model='datetime_range_none_strict_test')
def sync_test_datetime_range_none_strict_decorator(datetime_range_none_strict_test: DateTimeRangeNoneStrictTestModel):
    return datetime_range_none_strict_test.model_dump()


class TestDateTimeRangeDecorator:
    """测试 DateTimeRange 装饰器功能"""

    def test_sync_datetime_range_valid(self):
        """测试同步场景：start_time 小于 end_time 时验证通过"""
        datetime_range_basic_test = DateTimeRangeBasicTestModel(
            start_time=datetime(2026, 1, 1, 8, 0, 0),
            end_time=datetime(2026, 1, 1, 9, 0, 0),
        )
        result = sync_test_datetime_range_basic_decorator(
            datetime_range_basic_test=datetime_range_basic_test,
        )
        assert result == {
            'start_time': datetime(2026, 1, 1, 8, 0, 0),
            'end_time': datetime(2026, 1, 1, 9, 0, 0),
        }

    def test_sync_datetime_range_equal_allowed(self):
        """测试同步场景：allow_equal=True 且时间相等时验证通过"""
        datetime_range_basic_test = DateTimeRangeBasicTestModel(
            start_time=datetime(2026, 1, 1, 8, 0, 0),
            end_time=datetime(2026, 1, 1, 8, 0, 0),
        )
        result = sync_test_datetime_range_basic_decorator(
            datetime_range_basic_test=datetime_range_basic_test,
        )
        assert result['start_time'] == result['end_time']

    def test_sync_datetime_range_equal_not_allowed(self):
        """测试同步场景：allow_equal=False 且时间相等时触发验证错误"""
        datetime_range_strict_test = DateTimeRangeStrictTestModel(
            start_time=datetime(2026, 1, 1, 8, 0, 0),
            end_time=datetime(2026, 1, 1, 8, 0, 0),
        )
        with pytest.raises(FieldValidationError) as exc_info:
            sync_test_datetime_range_strict_decorator(
                datetime_range_strict_test=datetime_range_strict_test,
            )

        error = exc_info.value
        assert error.field_name == 'start_time'
        assert 'start_time must be less than end_time' in error.message

    def test_sync_datetime_range_invalid_order(self):
        """测试同步场景：start_time 大于 end_time 时触发验证错误"""
        datetime_range_basic_test = DateTimeRangeBasicTestModel(
            start_time=datetime(2026, 1, 1, 10, 0, 0),
            end_time=datetime(2026, 1, 1, 9, 0, 0),
        )
        with pytest.raises(FieldValidationError):
            sync_test_datetime_range_basic_decorator(
                datetime_range_basic_test=datetime_range_basic_test,
            )

    def test_sync_datetime_range_allow_none_skip(self):
        """测试同步场景：allow_none=True 且存在 None 时跳过验证"""
        datetime_range_basic_test = DateTimeRangeBasicTestModel(
            start_time=None,
            end_time=datetime(2026, 1, 1, 9, 0, 0),
        )
        result = sync_test_datetime_range_basic_decorator(
            datetime_range_basic_test=datetime_range_basic_test,
        )
        assert result['start_time'] is None

    def test_sync_datetime_range_allow_none_false_fail(self):
        """测试同步场景：allow_none=False 且存在 None 时触发验证错误"""
        datetime_range_none_strict_test = DateTimeRangeNoneStrictTestModel(
            start_time=None,
            end_time=datetime(2026, 1, 1, 9, 0, 0),
        )
        with pytest.raises(FieldValidationError):
            sync_test_datetime_range_none_strict_decorator(
                datetime_range_none_strict_test=datetime_range_none_strict_test,
            )

    def test_sync_datetime_range_string_valid(self):
        """测试同步场景：ISO 时间字符串可成功解析并校验"""
        datetime_range_string_test = DateTimeRangeStringTestModel(
            start_time='2026-01-01T08:00:00',
            end_time='2026-01-01T09:00:00',
        )
        result = sync_test_datetime_range_string_decorator(
            datetime_range_string_test=datetime_range_string_test,
        )
        assert result == {
            'start_time': '2026-01-01T08:00:00',
            'end_time': '2026-01-01T09:00:00',
        }

    def test_sync_datetime_range_string_invalid(self):
        """测试同步场景：非法时间字符串触发验证错误"""
        datetime_range_string_test = DateTimeRangeStringTestModel(
            start_time='2026-01-01 08:00:00',
            end_time='bad-format',
        )
        with pytest.raises(FieldValidationError):
            sync_test_datetime_range_string_decorator(
                datetime_range_string_test=datetime_range_string_test,
            )

    def test_sync_datetime_range_timezone_inconsistent(self):
        """测试同步场景：启用时区一致性时，aware/naive 混用触发验证错误"""
        datetime_range_timezone_test = DateTimeRangeTimezoneTestModel(
            start_time='2026-01-01T08:00:00+00:00',
            end_time='2026-01-01T09:00:00',
        )
        with pytest.raises(FieldValidationError):
            sync_test_datetime_range_timezone_decorator(
                datetime_range_timezone_test=datetime_range_timezone_test,
            )

    def test_datetime_range_invalid_init_same_field(self):
        """测试初始化场景：开始和结束字段不能相同"""
        with pytest.raises(ValueError):
            DateTimeRange(start_field='time', end_field='time')

    @pytest.mark.asyncio
    async def test_async_datetime_range_valid(self):
        """测试异步场景：start_time 小于 end_time 时验证通过"""
        datetime_range_basic_test = DateTimeRangeBasicTestModel(
            start_time=datetime(2026, 1, 1, 8, 0, 0),
            end_time=datetime(2026, 1, 1, 9, 0, 0),
        )
        result = await async_test_datetime_range_basic_decorator(datetime_range_basic_test)
        assert result['start_time'] == datetime(2026, 1, 1, 8, 0, 0)

    @pytest.mark.asyncio
    async def test_async_datetime_range_invalid_order(self):
        """测试异步场景：start_time 大于 end_time 时触发验证错误"""
        datetime_range_basic_test = DateTimeRangeBasicTestModel(
            start_time=datetime(2026, 1, 1, 10, 0, 0),
            end_time=datetime(2026, 1, 1, 9, 0, 0),
        )
        with pytest.raises(FieldValidationError):
            await async_test_datetime_range_basic_decorator(datetime_range_basic_test)

    @pytest.mark.asyncio
    async def test_async_datetime_range_string_valid(self):
        """测试异步场景：ISO 时间字符串可成功解析并校验"""
        datetime_range_string_test = DateTimeRangeStringTestModel(
            start_time='2026-01-01T08:00:00',
            end_time='2026-01-01T09:00:00',
        )
        result = await async_test_datetime_range_string_decorator(datetime_range_string_test)
        assert result['end_time'] == '2026-01-01T09:00:00'
