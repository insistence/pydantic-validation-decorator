import asyncio
from pydantic_validation_decorator import (
    ValidateFields,
    NotBlank,
    FieldValidationError,
)
from pydantic import BaseModel
from typing import Optional


class NotBlankTestModel(BaseModel):
    user_name: Optional[str] = None

    @NotBlank(
        field_name='user_name',
        message='user_name cannot be blank',
    )
    def get_user_name(self):
        return self.user_name

    def validate_fields(self):
        self.get_user_name()


@ValidateFields(validate_model='not_blank_test', validate_function='get_user_name')
def test_not_blank_decorator(not_blank_test: NotBlankTestModel):
    return not_blank_test.model_dump()


def main():
    not_blank_test = NotBlankTestModel(user_name='test123')
    try:
        print(test_not_blank_decorator(not_blank_test=not_blank_test))
    except FieldValidationError as e:
        print(e.__dict__)


@ValidateFields(mode='args', validate_model_index=0)
async def async_test_not_blank_decorator(
    not_blank_test: NotBlankTestModel,
):
    return not_blank_test.model_dump()


async def async_main():
    not_blank_test = NotBlankTestModel()
    try:
        print(await async_test_not_blank_decorator(not_blank_test))
    except FieldValidationError as e:
        print(e.__dict__)


if __name__ == '__main__':
    main()
    asyncio.run(async_main())
