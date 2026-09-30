import ssl
from pathlib import Path

import pytest
from pydantic import SecretStr

from app.common.enums import Environment
from app.core.config import Settings
from app.db.session import connect_args

CA_BUNDLE = Path(ssl.get_default_verify_paths().cafile or "")


def settings(**overrides: object) -> Settings:
    return Settings(environment=Environment.TEST, jwt_secret=SecretStr("x" * 40), **overrides)  # type: ignore[arg-type]


def test_no_tls_without_a_ca_bundle() -> None:
    assert connect_args(settings()) == {}


@pytest.mark.skipif(not CA_BUNDLE.is_file(), reason="no system CA bundle on this machine")
def test_tls_context_verifies_the_server() -> None:
    context = connect_args(settings(database_ssl_ca=str(CA_BUNDLE)))["ssl"]
    assert isinstance(context, ssl.SSLContext)
    assert context.verify_mode == ssl.CERT_REQUIRED
    assert context.check_hostname is True
