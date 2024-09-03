import asyncio
from pydantic_validation_decorator import (
    ValidateFields,
    Xss,
    FieldValidationError,
)
from pydantic import BaseModel
from typing import Optional


class XssTestModel(BaseModel):
    user_name: Optional[str] = None

    @Xss(
        field_name='user_name',
        message='user_name cannot contain script characters',
    )
    def get_user_name(self):
        return self.user_name

    def validate_fields(self):
        self.get_user_name()


@ValidateFields(validate_model='xss_test', validate_function='get_user_name')
def test_xss_decorator(xss_test: XssTestModel):
    return xss_test.model_dump()


def main():
    xss_test = XssTestModel()
    try:
        print(test_xss_decorator(xss_test=xss_test))
    except FieldValidationError as e:
        print(e.__dict__)


@ValidateFields(mode='args', validate_model_index=0)
async def async_test_xss_decorator(
    xss_test: XssTestModel,
):
    return xss_test.model_dump()


async def async_main():
    xss_test = XssTestModel(user_name='test123<>')
    try:
        print(await async_test_xss_decorator(xss_test))
    except FieldValidationError as e:
        print(e.__dict__)


if __name__ == '__main__':
    main()
    asyncio.run(async_main())
