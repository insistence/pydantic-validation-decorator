from typing import Any

import pytest
from pydantic import BaseModel

from pydantic_validation_decorator import (
    FieldValidationError,
    Size,
    ValidateFields,
)


class SizeTestModel(BaseModel):
    dict_type: str | None = None
    dict_sort: int | None = None

    @Size(
        field_name='dict_type',
        min_length=0,
        max_length=10,
        message='The length of the dict_type cannot exceed 10 characters',
    )
    def get_dict_type(self) -> str | None:
        return self.dict_type

    @Size(
        field_name='dict_sort',
        gt=7,
        message='The value of the dict_sort must be greater than 7',
    )
    def get_dict_sort(self) -> int | None:
        return self.dict_sort

    def validate_fields(self) -> None:
        self.get_dict_type()
        self.get_dict_sort()


@ValidateFields(validate_model='size_test', validate_function='get_dict_sort')
def sync_test_size_decorator(size_test: SizeTestModel) -> dict[str, Any]:
    return size_test.model_dump()


@ValidateFields(mode='args', validate_model_index=0)
async def async_test_size_decorator(size_test: SizeTestModel) -> dict[str, Any]:
    return size_test.model_dump()


class TestSizeDecorator:
    """测试 Size 装饰器功能."""

    @pytest.mark.asyncio
    async def test_async_field_method_with_optional_min_length(self) -> None:
        class TextModel(BaseModel):
            text: str

            @Size(field_name='text', min_length=None, max_length=3)
            async def validate_fields(self) -> str:
                return self.text

        @ValidateFields(validate_model='model')
        async def read_text(*, model: TextModel) -> str:
            return model.text

        assert await TextModel(text='abc').validate_fields() == 'abc'
        assert await read_text(model=TextModel(text='')) == ''
        with pytest.raises(FieldValidationError) as exc_info:
            await read_text(model=TextModel(text='long'))
        assert exc_info.value.field_name == 'text'

    def test_size_decorator_valid_dict_sort(self) -> None:
        """测试有效的dict_sort值（大于7）."""
        size_test = SizeTestModel(dict_type='test', dict_sort=8)
        result = sync_test_size_decorator(size_test=size_test)
        assert result == {'dict_type': 'test', 'dict_sort': 8}

    def test_size_decorator_invalid_dict_sort_equal_to_7(self) -> None:
        """测试等于7的dict_sort值（应该失败）."""
        size_test = SizeTestModel(dict_type='test', dict_sort=7)
        with pytest.raises(FieldValidationError) as exc_info:
            sync_test_size_decorator(size_test=size_test)

        error = exc_info.value
        assert error.field_name == 'dict_sort'
        assert error.message == 'The value of the dict_sort must be greater than 7'

    def test_size_decorator_invalid_dict_sort_less_than_7(self) -> None:
        """测试小于7的dict_sort值（应该失败）."""
        size_test = SizeTestModel(dict_type='test', dict_sort=5)
        with pytest.raises(FieldValidationError) as exc_info:
            sync_test_size_decorator(size_test=size_test)

        error = exc_info.value
        assert error.field_name == 'dict_sort'
        assert error.message == 'The value of the dict_sort must be greater than 7'

    def test_size_decorator_none_dict_sort(self) -> None:
        """测试None的dict_sort值（Size装饰器不会验证None值）."""
        size_test = SizeTestModel(dict_type='test')
        # Size 装饰器只验证 int, float, str 类型，对 None 值不会触发验证
        result = sync_test_size_decorator(size_test=size_test)
        assert result == {'dict_type': 'test', 'dict_sort': None}
        assert result['dict_sort'] is None

    @pytest.mark.asyncio
    async def test_async_size_decorator_valid_dict_sort(self) -> None:
        """测试异步装饰器有效的dict_sort值（大于7）."""
        size_test = SizeTestModel(dict_type='test', dict_sort=8)
        result = await async_test_size_decorator(size_test)
        assert result == {'dict_type': 'test', 'dict_sort': 8}

    @pytest.mark.asyncio
    async def test_async_size_decorator_long_dict_type_triggers_validation(self) -> None:
        """测试异步装饰器过长的dict_type会触发验证失败."""
        # 过长的 dict_type 会触发 get_dict_type 中的长度验证失败
        size_test = SizeTestModel(dict_type='test_dict_type_too_long', dict_sort=10)
        with pytest.raises(FieldValidationError) as exc_info:
            await async_test_size_decorator(size_test)

        error = exc_info.value
        assert error.field_name == 'dict_type'
        assert error.message == 'The length of the dict_type cannot exceed 10 characters'

    @pytest.mark.asyncio
    async def test_async_size_decorator_invalid_dict_sort_equal_to_7(self) -> None:
        """测试异步装饰器等于7的dict_sort值（应该失败）."""
        size_test = SizeTestModel(dict_type='test', dict_sort=7)
        with pytest.raises(FieldValidationError) as exc_info:
            await async_test_size_decorator(size_test)

        error = exc_info.value
        assert error.field_name == 'dict_sort'
        assert error.message == 'The value of the dict_sort must be greater than 7'

    @pytest.mark.asyncio
    async def test_async_size_decorator_invalid_dict_sort_less_than_7(self) -> None:
        """测试异步装饰器小于7的dict_sort值（应该失败）."""
        size_test = SizeTestModel(dict_type='test', dict_sort=5)
        with pytest.raises(FieldValidationError) as exc_info:
            await async_test_size_decorator(size_test)

        error = exc_info.value
        assert error.field_name == 'dict_sort'
        assert error.message == 'The value of the dict_sort must be greater than 7'

    @pytest.mark.asyncio
    async def test_async_size_decorator_none_dict_sort(self) -> None:
        """测试异步装饰器None的dict_sort值（Size装饰器不会验证None值）."""
        size_test = SizeTestModel(dict_type='test')
        # Size 装饰器只验证 int, float, str 类型，对 None 值不会触发验证
        result = await async_test_size_decorator(size_test)
        assert result == {'dict_type': 'test', 'dict_sort': None}
        assert result['dict_sort'] is None
