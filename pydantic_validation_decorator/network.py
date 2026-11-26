from __future__ import annotations

from typing import Literal

from pydantic import (
    AmqpDsn,
    AnyHttpUrl,
    AnyUrl,
    AnyWebsocketUrl,
    BaseModel,
    ClickHouseDsn,
    CockroachDsn,
    EmailStr,
    Field,
    FileUrl,
    FtpUrl,
    HttpUrl,
    IPvAnyAddress,
    KafkaDsn,
    MariaDBDsn,
    MongoDsn,
    MySQLDsn,
    NameEmail,
    NatsDsn,
    PostgresDsn,
    RedisDsn,
    WebsocketUrl,
)

from ._decorators import FieldValidator
from .exceptions import FieldValidationError


class NetworkAnnotationModel(BaseModel):
    any_url: AnyUrl | None = Field(default=None, description='Base type for all URLs.')
    any_http_url: AnyHttpUrl | None = Field(
        default=None,
        description='A type that will accept any http or https URL.',
    )
    http_url: HttpUrl | None = Field(
        default=None,
        description='A type that will accept any http or https URL and max length 2083.',
    )
    any_websocket_url: AnyWebsocketUrl | None = Field(
        default=None,
        description='A type that will accept any ws or wss URL.',
    )
    websocket_url: WebsocketUrl | None = Field(
        default=None,
        description='A type that will accept any ws or wss URL and max length 2083.',
    )
    file_url: FileUrl | None = Field(default=None, description='A type that will accept any file URL.')
    ftp_url: FtpUrl | None = Field(default=None, description='A type that will accept ftp URL.')
    postgres_dsn: PostgresDsn | None = Field(
        default=None,
        description='A type that will accept any Postgres DSN.',
    )
    cockroach_dsn: CockroachDsn | None = Field(
        default=None,
        description='A type that will accept any Cockroach DSN.',
    )
    amqp_dsn: AmqpDsn | None = Field(default=None, description='A type that will accept any AMQP DSN.')
    redis_dsn: RedisDsn | None = Field(default=None, description='A type that will accept any Redis DSN.')
    mongo_dsn: MongoDsn | None = Field(
        default=None,
        description='A type that will accept any MongoDB DSN.',
    )
    kafka_dsn: KafkaDsn | None = Field(default=None, description='A type that will accept any Kafka DSN.')
    nats_dsn: NatsDsn | None = Field(default=None, description='A type that will accept any NATS DSN.')
    mysql_dsn: MySQLDsn | None = Field(default=None, description='A type that will accept any MySQL DSN.')
    mariadb_dsn: MariaDBDsn | None = Field(
        default=None,
        description='A type that will accept any MariaDB DSN.',
    )
    clickhouse_dsn: ClickHouseDsn | None = Field(
        default=None,
        description='A type that will accept any ClickHouse DSN.',
    )
    email_str: EmailStr | None = Field(default=None, description='Validate email addresses.')
    name_email: NameEmail | None = Field(
        default=None,
        description='Validate a name and email address combination, as specified by RFC 5322.',
    )
    ipv_any_address: IPvAnyAddress | None = Field(default=None, description='Validate an IPv4 or IPv6 address.')


_NETWORK_FIELDS = {
    'AnyUrl': 'any_url',
    'AnyHttpUrl': 'any_http_url',
    'HttpUrl': 'http_url',
    'AnyWebsocketUrl': 'any_websocket_url',
    'WebsocketUrl': 'websocket_url',
    'FileUrl': 'file_url',
    'FtpUrl': 'ftp_url',
    'PostgresDsn': 'postgres_dsn',
    'CockroachDsn': 'cockroach_dsn',
    'AmqpDsn': 'amqp_dsn',
    'RedisDsn': 'redis_dsn',
    'MongoDsn': 'mongo_dsn',
    'KafkaDsn': 'kafka_dsn',
    'NatsDsn': 'nats_dsn',
    'MySQLDsn': 'mysql_dsn',
    'MariaDBDsn': 'mariadb_dsn',
    'ClickHouseDsn': 'clickhouse_dsn',
    'EmailStr': 'email_str',
    'NameEmail': 'name_email',
    'IPvAnyAddress': 'ipv_any_address',
}


class Network(FieldValidator):
    """Field Network Type Validation Decorator."""

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
        message: str | None = None,
    ) -> None:
        """Select the network type used to validate a field.

        Args:
            field_name: Name of the field to validate.
            field_type: Pydantic network type to check, such as HttpUrl, EmailStr, or IPvAnyAddress.
            message: Custom error message to use when validation fails.
        """
        self.field_name = field_name
        self.field_type = field_type
        self.message = message

    def _validate(self, validate_model: BaseModel) -> None:
        if not hasattr(validate_model, self.field_name):
            return
        field_value = getattr(validate_model, self.field_name)
        model_field = _NETWORK_FIELDS.get(self.field_type)
        if not field_value or model_field is None:
            return
        try:
            NetworkAnnotationModel.model_validate({model_field: field_value})
        except ValueError as exc:
            raise FieldValidationError(
                model_name=validate_model.__class__.__name__,
                field_name=self.field_name,
                field_value=field_value,
                validator=self.__class__.__name__,
                message=self.message or f'{self.field_name} is not the correct {self.field_type} type.',
            ) from exc
