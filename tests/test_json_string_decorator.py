import pytest
from pydantic import BaseModel
from typing import Optional
from pydantic_validation_decorator import (
    ValidateFields,
    JsonString,
    FieldValidationError,
)


class JsonStringBaseTestModel(BaseModel):
    """JsonString 基础校验场景测试模型"""

    payload: Optional[str] = None

    @JsonString(
        field_name='payload',
        message='payload must be valid json',
    )
    def get_payload(self):
        return self.payload

    def validate_fields(self):
        self.get_payload()


class JsonStringObjectTestModel(BaseModel):
    """JsonString 对象根节点场景测试模型"""

    metadata: Optional[str] = None

    @JsonString(
        field_name='metadata',
        require_object=True,
        message='metadata must be a json object',
    )
    def get_metadata(self):
        return self.metadata

    def validate_fields(self):
        self.get_metadata()


class JsonStringArrayTestModel(BaseModel):
    """JsonString 数组根节点场景测试模型"""

    items: Optional[str] = None

    @JsonString(
        field_name='items',
        require_array=True,
        message='items must be a json array',
    )
    def get_items(self):
        return self.items

    def validate_fields(self):
        self.get_items()


class JsonStringDepthTestModel(BaseModel):
    """JsonString 最大深度场景测试模型"""

    config: Optional[str] = None

    @JsonString(
        field_name='config',
        max_depth=2,
        message='config json depth cannot exceed 2',
    )
    def get_config(self):
        return self.config

    def validate_fields(self):
        self.get_config()


class JsonStringNoneStrictTestModel(BaseModel):
    """JsonString None 严格校验场景测试模型"""

    content: Optional[str] = None

    @JsonString(
        field_name='content',
        allow_none=False,
        message='content cannot be none and must be valid json',
    )
    def get_content(self):
        return self.content

    def validate_fields(self):
        self.get_content()


class JsonStringAnyTypeTestModel(BaseModel):
    """JsonString 非字符串输入场景测试模型"""

    payload: Optional[object] = None

    @JsonString(
        field_name='payload',
        message='payload must be valid json',
    )
    def get_payload(self):
        return self.payload

    def validate_fields(self):
        self.get_payload()


@ValidateFields(validate_model='json_string_base_test')
def sync_test_json_string_base_decorator(json_string_base_test: JsonStringBaseTestModel):
    return json_string_base_test.model_dump()


@ValidateFields(mode='args', validate_model_index=0)
async def async_test_json_string_base_decorator(json_string_base_test: JsonStringBaseTestModel):
    return json_string_base_test.model_dump()


@ValidateFields(validate_model='json_string_object_test')
def sync_test_json_string_object_decorator(json_string_object_test: JsonStringObjectTestModel):
    return json_string_object_test.model_dump()


@ValidateFields(validate_model='json_string_array_test')
def sync_test_json_string_array_decorator(json_string_array_test: JsonStringArrayTestModel):
    return json_string_array_test.model_dump()


@ValidateFields(validate_model='json_string_depth_test')
def sync_test_json_string_depth_decorator(json_string_depth_test: JsonStringDepthTestModel):
    return json_string_depth_test.model_dump()


@ValidateFields(mode='args', validate_model_index=0)
async def async_test_json_string_depth_decorator(json_string_depth_test: JsonStringDepthTestModel):
    return json_string_depth_test.model_dump()


@ValidateFields(validate_model='json_string_none_strict_test')
def sync_test_json_string_none_strict_decorator(json_string_none_strict_test: JsonStringNoneStrictTestModel):
    return json_string_none_strict_test.model_dump()


@ValidateFields(validate_model='json_string_any_type_test')
def sync_test_json_string_any_type_decorator(json_string_any_type_test: JsonStringAnyTypeTestModel):
    return json_string_any_type_test.model_dump()


class TestJsonStringDecorator:
    """测试 JsonString 装饰器功能"""

    def test_sync_json_string_valid(self):
        """测试同步场景：合法 JSON 字符串校验通过"""
        json_string_base_test = JsonStringBaseTestModel(payload='{"name":"test"}')
        result = sync_test_json_string_base_decorator(json_string_base_test=json_string_base_test)
        assert result == {'payload': '{"name":"test"}'}

    def test_sync_json_string_invalid_syntax(self):
        """测试同步场景：非法 JSON 语法触发验证错误"""
        json_string_base_test = JsonStringBaseTestModel(payload='{"name":"test"')
        with pytest.raises(FieldValidationError) as exc_info:
            sync_test_json_string_base_decorator(json_string_base_test=json_string_base_test)

        error = exc_info.value
        assert error.field_name == 'payload'
        assert 'payload must be valid json' in error.message

    def test_sync_json_string_non_string_type(self):
        """测试同步场景：非字符串输入触发验证错误"""
        json_string_base_test = JsonStringAnyTypeTestModel(payload=123)
        with pytest.raises(FieldValidationError):
            sync_test_json_string_any_type_decorator(json_string_any_type_test=json_string_base_test)

    def test_sync_json_string_require_object_valid(self):
        """测试同步场景：要求对象根节点且输入为对象时通过"""
        json_string_object_test = JsonStringObjectTestModel(metadata='{"id":1}')
        result = sync_test_json_string_object_decorator(json_string_object_test=json_string_object_test)
        assert result == {'metadata': '{"id":1}'}

    def test_sync_json_string_require_object_invalid(self):
        """测试同步场景：要求对象根节点但输入为数组时触发验证错误"""
        json_string_object_test = JsonStringObjectTestModel(metadata='[1,2,3]')
        with pytest.raises(FieldValidationError):
            sync_test_json_string_object_decorator(json_string_object_test=json_string_object_test)

    def test_sync_json_string_require_array_valid(self):
        """测试同步场景：要求数组根节点且输入为数组时通过"""
        json_string_array_test = JsonStringArrayTestModel(items='["a","b"]')
        result = sync_test_json_string_array_decorator(json_string_array_test=json_string_array_test)
        assert result == {'items': '["a","b"]'}

    def test_sync_json_string_require_array_invalid(self):
        """测试同步场景：要求数组根节点但输入为对象时触发验证错误"""
        json_string_array_test = JsonStringArrayTestModel(items='{"a":1}')
        with pytest.raises(FieldValidationError):
            sync_test_json_string_array_decorator(json_string_array_test=json_string_array_test)

    def test_sync_json_string_max_depth_valid(self):
        """测试同步场景：JSON 深度不超过 max_depth 时通过"""
        json_string_depth_test = JsonStringDepthTestModel(config='{"a":1}')
        result = sync_test_json_string_depth_decorator(json_string_depth_test=json_string_depth_test)
        assert result == {'config': '{"a":1}'}

    def test_sync_json_string_max_depth_invalid(self):
        """测试同步场景：JSON 深度超过 max_depth 时触发验证错误"""
        json_string_depth_test = JsonStringDepthTestModel(config='{"a":{"b":1}}')
        with pytest.raises(FieldValidationError) as exc_info:
            sync_test_json_string_depth_decorator(json_string_depth_test=json_string_depth_test)

        error = exc_info.value
        assert error.field_name == 'config'
        assert 'config json depth cannot exceed 2' in error.message

    def test_sync_json_string_allow_none_skip(self):
        """测试同步场景：allow_none=True 且字段为 None 时跳过校验"""
        json_string_base_test = JsonStringBaseTestModel(payload=None)
        result = sync_test_json_string_base_decorator(json_string_base_test=json_string_base_test)
        assert result == {'payload': None}

    def test_sync_json_string_allow_none_false_fail(self):
        """测试同步场景：allow_none=False 且字段为 None 时触发验证错误"""
        json_string_none_strict_test = JsonStringNoneStrictTestModel(content=None)
        with pytest.raises(FieldValidationError):
            sync_test_json_string_none_strict_decorator(json_string_none_strict_test=json_string_none_strict_test)

    def test_json_string_invalid_init_required_flags(self):
        """测试初始化场景：对象和数组要求不能同时为 True"""
        with pytest.raises(ValueError):
            JsonString(field_name='payload', require_object=True, require_array=True)

    def test_json_string_invalid_init_max_depth(self):
        """测试初始化场景：max_depth 小于 1 会抛出异常"""
        with pytest.raises(ValueError):
            JsonString(field_name='payload', max_depth=0)

    @pytest.mark.asyncio
    async def test_async_json_string_valid(self):
        """测试异步场景：合法 JSON 字符串校验通过"""
        json_string_base_test = JsonStringBaseTestModel(payload='{"name":"test"}')
        result = await async_test_json_string_base_decorator(json_string_base_test)
        assert result == {'payload': '{"name":"test"}'}

    @pytest.mark.asyncio
    async def test_async_json_string_invalid_syntax(self):
        """测试异步场景：非法 JSON 语法触发验证错误"""
        json_string_base_test = JsonStringBaseTestModel(payload='{"name":}')
        with pytest.raises(FieldValidationError):
            await async_test_json_string_base_decorator(json_string_base_test)

    @pytest.mark.asyncio
    async def test_async_json_string_max_depth_invalid(self):
        """测试异步场景：JSON 深度超过 max_depth 时触发验证错误"""
        json_string_depth_test = JsonStringDepthTestModel(config='{"a":{"b":{"c":1}}}')
        with pytest.raises(FieldValidationError):
            await async_test_json_string_depth_decorator(json_string_depth_test)
