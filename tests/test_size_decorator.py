import asyncio
from pydantic_validation_decorator import (
    ValidateFields,
    Size,
    FieldValidationError,
)
from pydantic import BaseModel
from typing import Optional


class SizeTestModel(BaseModel):
    dict_type: Optional[str] = None

    @Size(
        field_name='dict_type',
        min_length=0,
        max_length=10,
        message='The length of the dict_type cannot exceed 100 characters',
    )
    def get_dict_type(self):
        return self.dict_type

    def validate_fields(self):
        self.get_dict_type()


@ValidateFields(validate_model='size_test', validate_function='get_dict_type')
def test_size_decorator(size_test: SizeTestModel):
    return size_test.model_dump()


def main():
    size_test = SizeTestModel(dict_type='test')
    try:
        print(test_size_decorator(size_test=size_test))
    except FieldValidationError as e:
        print(e.__dict__)


@ValidateFields(mode='args', validate_model_index=0)
async def async_test_size_decorator(
    size_test: SizeTestModel,
):
    return size_test.model_dump()


async def async_main():
    size_test = SizeTestModel(dict_type='test_dict_type')
    try:
        print(await async_test_size_decorator(size_test))
    except FieldValidationError as e:
        print(e.__dict__)


if __name__ == '__main__':
    main()
    asyncio.run(async_main())
