import asyncio
from pydantic_validation_decorator import (
    ValidateFields,
    Network,
    FieldValidationError,
)
from pydantic import BaseModel
from typing import Optional


class NetworkTestModel(BaseModel):
    email: Optional[str] = None

    @Network(
        field_name='email',
        field_type='EmailStr',
        message='email is invalid',
    )
    def get_email(self):
        return self.email

    def validate_fields(self):
        self.get_email()


@ValidateFields(validate_model='network_test', validate_function='get_email')
def test_network_decorator(network_test: NetworkTestModel):
    return network_test.model_dump()


def main():
    network_test = NetworkTestModel(email='test123@qq.com')
    try:
        print(test_network_decorator(network_test=network_test))
    except FieldValidationError as e:
        print(e.__dict__)
        

@ValidateFields(mode='args', validate_model_index=1)
async def async_test_network_decorator(
    test,
    network_test,
):
    return network_test.model_dump()


async def async_main():
    network_test = NetworkTestModel(email='test123')
    try:
        print(await async_test_network_decorator(1, network_test))
    except FieldValidationError as e:
        print(e.__dict__)


if __name__ == '__main__':
    main()
    asyncio.run(async_main())
