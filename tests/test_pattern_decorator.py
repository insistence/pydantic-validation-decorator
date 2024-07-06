import asyncio
from pydantic_validation_decorator import (
    ValidateFields,
    Pattern,
    FieldValidationError,
)
from pydantic import BaseModel
from typing import Optional


class PatternTestModel(BaseModel):
    dict_type: Optional[str] = None

    @Pattern(
        field_name='dict_type',
        regexp='^[a-z][a-z0-9_]*$',
        message='The dict_type must start with a letter and can only be lowercase letters, numbers, and dashes',
    )
    def get_dict_type(self):
        return self.dict_type

    def validate_fields(self):
        self.get_dict_type()


@ValidateFields(validate_model='pattern_test', validate_function='get_dict_type')
def test_pattern_decorator(pattern_test: PatternTestModel):
    return pattern_test.model_dump()


def main():
    pattern_test = PatternTestModel(dict_type='test_dict_type')
    try:
        print(test_pattern_decorator(pattern_test=pattern_test))
    except FieldValidationError as e:
        print(e.__dict__)


@ValidateFields(mode='args', validate_model_index=0)
async def async_test_pattern_decorator(
    pattern_test: PatternTestModel,
):
    return pattern_test.model_dump()


async def async_main():
    pattern_test = PatternTestModel(dict_type='123')
    try:
        print(await async_test_pattern_decorator(pattern_test))
    except FieldValidationError as e:
        print(e.__dict__)


if __name__ == '__main__':
    main()
    asyncio.run(async_main())
