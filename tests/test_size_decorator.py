import pytest
from pydantic_validation_decorator import (
    ValidateFields,
    Size,
    FieldValidationError,
)
from pydantic import BaseModel
from typing import Optional


class SizeTestModel(BaseModel):
    dict_type: Optional[str] = None
    dict_sort: Optional[int] = None

    @Size(
        field_name='dict_type',
        min_length=0,
        max_length=10,
        message='The length of the dict_type cannot exceed 10 characters',
    )
    def get_dict_type(self):
        return self.dict_type

    @Size(
        field_name='dict_sort',
        gt=7,
        message='The value of the dict_sort must be greater than 7',
    )
    def get_dict_sort(self):
        return self.dict_sort

    def validate_fields(self):
        self.get_dict_type()
        self.get_dict_sort()


@ValidateFields(validate_model='size_test', validate_function='get_dict_sort')
def sync_test_size_decorator(size_test: SizeTestModel):
    return size_test.model_dump()


@ValidateFields(mode='args', validate_model_index=0)
async def async_test_size_decorator(
    size_test: SizeTestModel,
):
    return size_test.model_dump()


class TestSizeDecorator:
    """测试 Size 装饰器功能"""

    def test_size_decorator_valid_dict_sort(self):
        """测试有效的dict_sort值（大于7）"""
        size_test = SizeTestModel(dict_type='test', dict_sort=8)
        result = sync_test_size_decorator(size_test=size_test)
        assert result == {'dict_type': 'test', 'dict_sort': 8}
        assert result['dict_sort'] == 8

    def test_size_decorator_invalid_dict_sort_equal_to_7(self):
        """测试等于7的dict_sort值（应该失败）"""
        size_test = SizeTestModel(dict_type='test', dict_sort=7)
        with pytest.raises(FieldValidationError) as exc_info:
            sync_test_size_decorator(size_test=size_test)

        error = exc_info.value
        assert error.field_name == 'dict_sort'
        assert 'The value of the dict_sort must be greater than 7' in error.message

    def test_size_decorator_invalid_dict_sort_less_than_7(self):
        """测试小于7的dict_sort值（应该失败）"""
        size_test = SizeTestModel(dict_type='test', dict_sort=5)
        with pytest.raises(FieldValidationError) as exc_info:
            sync_test_size_decorator(size_test=size_test)

        error = exc_info.value
        assert error.field_name == 'dict_sort'
        assert 'The value of the dict_sort must be greater than 7' in error.message

    def test_size_decorator_none_dict_sort(self):
        """测试None的dict_sort值（Size装饰器不会验证None值）"""
        size_test = SizeTestModel(dict_type='test')
        # Size 装饰器只验证 int, float, str 类型，对 None 值不会触发验证
        result = sync_test_size_decorator(size_test=size_test)
        assert result == {'dict_type': 'test', 'dict_sort': None}
        assert result['dict_sort'] is None

    @pytest.mark.asyncio
    async def test_async_size_decorator_valid_dict_sort(self):
        """测试异步装饰器有效的dict_sort值（大于7）"""
        size_test = SizeTestModel(dict_type='test', dict_sort=8)
        result = await async_test_size_decorator(size_test)
        assert result == {'dict_type': 'test', 'dict_sort': 8}
        assert result['dict_sort'] == 8

    @pytest.mark.asyncio
    async def test_async_size_decorator_long_dict_type_triggers_validation(self):
        """测试异步装饰器过长的dict_type会触发验证失败"""
        # 过长的 dict_type 会触发 get_dict_type 中的长度验证失败
        size_test = SizeTestModel(dict_type='test_dict_type_too_long', dict_sort=10)
        with pytest.raises(FieldValidationError) as exc_info:
            await async_test_size_decorator(size_test)

        error = exc_info.value
        assert error.field_name == 'dict_type'
        assert 'The length of the dict_type cannot exceed 10 characters' in error.message

    @pytest.mark.asyncio
    async def test_async_size_decorator_invalid_dict_sort_equal_to_7(self):
        """测试异步装饰器等于7的dict_sort值（应该失败）"""
        size_test = SizeTestModel(dict_type='test', dict_sort=7)
        with pytest.raises(FieldValidationError) as exc_info:
            await async_test_size_decorator(size_test)

        error = exc_info.value
        assert error.field_name == 'dict_sort'
        assert 'The value of the dict_sort must be greater than 7' in error.message

    @pytest.mark.asyncio
    async def test_async_size_decorator_invalid_dict_sort_less_than_7(self):
        """测试异步装饰器小于7的dict_sort值（应该失败）"""
        size_test = SizeTestModel(dict_type='test', dict_sort=5)
        with pytest.raises(FieldValidationError) as exc_info:
            await async_test_size_decorator(size_test)

        error = exc_info.value
        assert error.field_name == 'dict_sort'
        assert 'The value of the dict_sort must be greater than 7' in error.message

    @pytest.mark.asyncio
    async def test_async_size_decorator_none_dict_sort(self):
        """测试异步装饰器None的dict_sort值（Size装饰器不会验证None值）"""
        size_test = SizeTestModel(dict_type='test')
        # Size 装饰器只验证 int, float, str 类型，对 None 值不会触发验证
        result = await async_test_size_decorator(size_test)
        assert result == {'dict_type': 'test', 'dict_sort': None}
        assert result['dict_sort'] is None
