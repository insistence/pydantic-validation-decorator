from asyncio import iscoroutinefunction
from functools import wraps
from typing import Literal, Optional
from pydantic import (
    BaseModel,
    Field,
    AnyUrl,
    AnyHttpUrl,
    HttpUrl,
    AnyWebsocketUrl,
    WebsocketUrl,
    FileUrl,
    FtpUrl,
    PostgresDsn,
    CockroachDsn,
    AmqpDsn,
    RedisDsn,
    MongoDsn,
    KafkaDsn,
    NatsDsn,
    MySQLDsn,
    MariaDBDsn,
    ClickHouseDsn,
    EmailStr,
    NameEmail,
    IPvAnyAddress,
    ValidationError,
)
from .exceptions import FieldValidationError


class NetworkAnnotationModel(BaseModel):
    any_url: Optional[AnyUrl] = Field(default=None, description='Base type for all URLs.')
    any_http_url: Optional[AnyHttpUrl] = Field(
        default=None,
        description='A type that will accept any http or https URL.',
    )
    http_url: Optional[HttpUrl] = Field(
        default=None,
        description='A type that will accept any http or https URL and max length 2083.',
    )
    any_websocket_url: Optional[AnyWebsocketUrl] = Field(
        default=None,
        description='A type that will accept any ws or wss URL.',
    )
    websocket_url: Optional[WebsocketUrl] = Field(
        default=None,
        description='A type that will accept any ws or wss URL and max length 2083.',
    )
    file_url: Optional[FileUrl] = Field(default=None, description='A type that will accept any file URL.')
    ftp_url: Optional[FtpUrl] = Field(default=None, description='A type that will accept ftp URL.')
    postgres_dsn: Optional[PostgresDsn] = Field(
        default=None,
        description='A type that will accept any Postgres DSN.',
    )
    cockroach_dsn: Optional[CockroachDsn] = Field(
        default=None,
        description='A type that will accept any Cockroach DSN.',
    )
    amqp_dsn: Optional[AmqpDsn] = Field(default=None, description='A type that will accept any AMQP DSN.')
    redis_dsn: Optional[RedisDsn] = Field(default=None, description='A type that will accept any Redis DSN.')
    mongo_dsn: Optional[MongoDsn] = Field(
        default=None,
        description='A type that will accept any MongoDB DSN.',
    )
    kafka_dsn: Optional[KafkaDsn] = Field(default=None, description='A type that will accept any Kafka DSN.')
    nats_dsn: Optional[NatsDsn] = Field(default=None, description='A type that will accept any NATS DSN.')
    mysql_dsn: Optional[MySQLDsn] = Field(default=None, description='A type that will accept any MySQL DSN.')
    mariadb_dsn: Optional[MariaDBDsn] = Field(
        default=None,
        description='A type that will accept any MariaDB DSN.',
    )
    clickhouse_dsn: Optional[ClickHouseDsn] = Field(
        default=None,
        description='A type that will accept any ClickHouse DSN.',
    )
    email_str: Optional[EmailStr] = Field(default=None, description='Validate email addresses.')
    name_email: Optional[NameEmail] = Field(
        default=None,
        description='Validate a name and email address combination, as specified by RFC 5322.',
    )
    ipv_any_address: Optional[IPvAnyAddress] = Field(default=None, description='Validate an IPv4 or IPv6 address.')


class Network:
    """
    Field Network Type Validation Decorator
    """

    def __init__(
        self,
        field_name: str,
        field_type: Literal[
            'AnyUrl',
            'AnyHttpUrl',
            'HttpUrl',
            'AnyWebsocketUrl',
            'WebsocketUrl',
            'FileUrl',
            'FtpUrl',
            'PostgresDsn',
            'CockroachDsn',
            'AmqpDsn',
            'RedisDsn',
            'MongoDsn',
            'KafkaDsn',
            'NatsDsn',
            'MySQLDsn',
            'MariaDBDsn',
            'ClickHouseDsn',
            'EmailStr',
            'NameEmail',
            'IPvAnyAddress',
        ],
        message: Optional[str] = None,
    ):
        """Field Network Type Validation Decorator

        Args:
            field_name (str): Field name that need to be validate.
            field_type (Literal[ &#39;AnyUrl&#39;, &#39;AnyHttpUrl&#39;, &#39;HttpUrl&#39;, &#39;AnyWebsocketUrl&#39;, &#39;WebsocketUrl&#39;, &#39;FileUrl&#39;, &#39;FtpUrl&#39;, &#39;PostgresDsn&#39;, &#39;CockroachDsn&#39;, &#39;AmqpDsn&#39;, &#39;RedisDsn&#39;, &#39;MongoDsn&#39;, &#39;KafkaDsn&#39;, &#39;NatsDsn&#39;, &#39;MySQLDsn&#39;, &#39;MariaDBDsn&#39;, &#39;ClickHouseDsn&#39;, &#39;EmailStr&#39;, &#39;NameEmail&#39;, &#39;IPvAnyAddress&#39;, ]): Field type that need to be validate.
            message (Optional[str], optional): Prompt message for validation failure. Defaults to None.
        """
        self.field_name = field_name
        self.field_type = field_type
        self.message = message

    def __call__(self, func):
        is_async = iscoroutinefunction(func)
        if is_async:

            @wraps(func)
            async def wrapper(*args, **kwargs):
                validate_model = args[0]
                if isinstance(validate_model, BaseModel) and hasattr(validate_model, self.field_name):
                    field_value = getattr(validate_model, self.field_name)
                    if field_value:
                        try:
                            if self.field_type == 'AnyUrl':
                                NetworkAnnotationModel(any_url=field_value)
                            elif self.field_type == 'AnyHttpUrl':
                                NetworkAnnotationModel(any_http_url=field_value)
                            elif self.field_type == 'HttpUrl':
                                NetworkAnnotationModel(http_url=field_value)
                            elif self.field_type == 'AnyWebsocketUrl':
                                NetworkAnnotationModel(any_websocket_url=field_value)
                            elif self.field_type == 'WebsocketUrl':
                                NetworkAnnotationModel(websocket_url=field_value)
                            elif self.field_type == 'FileUrl':
                                NetworkAnnotationModel(file_url=field_value)
                            elif self.field_type == 'FtpUrl':
                                NetworkAnnotationModel(ftp_url=field_value)
                            elif self.field_type == 'PostgresDsn':
                                NetworkAnnotationModel(postgres_dsn=field_value)
                            elif self.field_type == 'CockroachDsn':
                                NetworkAnnotationModel(cockroach_dsn=field_value)
                            elif self.field_type == 'AmqpDsn':
                                NetworkAnnotationModel(amqp_dsn=field_value)
                            elif self.field_type == 'RedisDsn':
                                NetworkAnnotationModel(redis_dsn=field_value)
                            elif self.field_type == 'MongoDsn':
                                NetworkAnnotationModel(mongo_dsn=field_value)
                            elif self.field_type == 'KafkaDsn':
                                NetworkAnnotationModel(kafka_dsn=field_value)
                            elif self.field_type == 'NatsDsn':
                                NetworkAnnotationModel(nats_dsn=field_value)
                            elif self.field_type == 'MySQLDsn':
                                NetworkAnnotationModel(mysql_dsn=field_value)
                            elif self.field_type == 'MariaDBDsn':
                                NetworkAnnotationModel(mariadb_dsn=field_value)
                            elif self.field_type == 'ClickHouseDsn':
                                NetworkAnnotationModel(clickhouse_dsn=field_value)
                            elif self.field_type == 'EmailStr':
                                NetworkAnnotationModel(email_str=field_value)
                            elif self.field_type == 'NameEmail':
                                NetworkAnnotationModel(name_email=field_value)
                            elif self.field_type == 'IPvAnyAddress':
                                NetworkAnnotationModel(ipv_any_address=field_value)
                        except (
                            ValidationError,
                            ValueError,
                        ):
                            raise FieldValidationError(
                                model_name=validate_model.__class__.__name__,
                                field_name=self.field_name,
                                field_value=field_value,
                                validator=self.__class__.__name__,
                                message=self.message
                                if self.message
                                else f'{self.field_name} is not the correct {self.field_type} type.',
                            )
                return await func(*args, **kwargs)

            return wrapper

        else:

            @wraps(func)
            def wrapper(*args, **kwargs):
                validate_model = args[0]
                if isinstance(validate_model, BaseModel) and hasattr(validate_model, self.field_name):
                    field_value = getattr(validate_model, self.field_name)
                    if field_value:
                        try:
                            if self.field_type == 'AnyUrl':
                                NetworkAnnotationModel(any_url=field_value)
                            elif self.field_type == 'AnyHttpUrl':
                                NetworkAnnotationModel(any_http_url=field_value)
                            elif self.field_type == 'HttpUrl':
                                NetworkAnnotationModel(http_url=field_value)
                            elif self.field_type == 'AnyWebsocketUrl':
                                NetworkAnnotationModel(any_websocket_url=field_value)
                            elif self.field_type == 'WebsocketUrl':
                                NetworkAnnotationModel(websocket_url=field_value)
                            elif self.field_type == 'FileUrl':
                                NetworkAnnotationModel(file_url=field_value)
                            elif self.field_type == 'FtpUrl':
                                NetworkAnnotationModel(ftp_url=field_value)
                            elif self.field_type == 'PostgresDsn':
                                NetworkAnnotationModel(postgres_dsn=field_value)
                            elif self.field_type == 'CockroachDsn':
                                NetworkAnnotationModel(cockroach_dsn=field_value)
                            elif self.field_type == 'AmqpDsn':
                                NetworkAnnotationModel(amqp_dsn=field_value)
                            elif self.field_type == 'RedisDsn':
                                NetworkAnnotationModel(redis_dsn=field_value)
                            elif self.field_type == 'MongoDsn':
                                NetworkAnnotationModel(mongo_dsn=field_value)
                            elif self.field_type == 'KafkaDsn':
                                NetworkAnnotationModel(kafka_dsn=field_value)
                            elif self.field_type == 'NatsDsn':
                                NetworkAnnotationModel(nats_dsn=field_value)
                            elif self.field_type == 'MySQLDsn':
                                NetworkAnnotationModel(mysql_dsn=field_value)
                            elif self.field_type == 'MariaDBDsn':
                                NetworkAnnotationModel(mariadb_dsn=field_value)
                            elif self.field_type == 'ClickHouseDsn':
                                NetworkAnnotationModel(clickhouse_dsn=field_value)
                            elif self.field_type == 'EmailStr':
                                NetworkAnnotationModel(email_str=field_value)
                            elif self.field_type == 'NameEmail':
                                NetworkAnnotationModel(name_email=field_value)
                            elif self.field_type == 'IPvAnyAddress':
                                NetworkAnnotationModel(ipv_any_address=field_value)
                        except (
                            ValidationError,
                            ValueError,
                        ):
                            raise FieldValidationError(
                                model_name=validate_model.__class__.__name__,
                                field_name=self.field_name,
                                field_value=field_value,
                                validator=self.__class__.__name__,
                                message=self.message
                                if self.message
                                else f'{self.field_name} is not the correct {self.field_type} type.',
                            )
                return func(*args, **kwargs)

            return wrapper
