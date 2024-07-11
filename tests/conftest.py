import logging

import pytest
from sqlalchemy import text

import tests.__factories__.configs as configs_factories
import tests.__factories__.prompt_templates as prompt_templates_factories
import tests.__factories__.responses as responses_factories
from src.core.containers import container
from src.core.deps.database import Base, MySQLBase
from src.repositories.audit import AuditData

from .utils import override_settings as _override_settings


def _refresh_database():
    db = container.db()
    engine = db.engine
    with db.session() as session:
        session.close()
        Base.metadata.drop_all(engine)
        session.execute(text("CREATE EXTENSION IF NOT EXISTS vector"))
        session.commit()
    Base.metadata.create_all(engine)


def _refresh_mysql_database():
    db = container.mysql_db()
    engine = db.engine
    with db.session() as session:
        session.close()
        MySQLBase.metadata.drop_all(engine)
        session.commit()
    MySQLBase.metadata.create_all(engine)


@pytest.fixture
def refresh_database():
    _refresh_database()


@pytest.fixture
def refresh_mysql_database():
    _refresh_mysql_database()


@pytest.fixture(scope="class")
def class_refresh_database():
    _refresh_database()


@pytest.fixture
def db_session():
    db = container.db()
    with db.session() as session:
        yield session
    session.close()


@pytest.fixture
def override_settings():
    yield _override_settings


@pytest.fixture
def mock_audit_in_memory():
    container.audit_repository().data = AuditData(
        user_id=2,
        causer_id=1,
        causer_type="user",
        org_id=4,
        project_id=123,
    )


####################################################################
# Factories
####################################################################
@pytest.fixture
def make_base_prompt_plain(**rest):
    yield prompt_templates_factories.make_base_prompt_plain(**rest)


@pytest.fixture
def make_completion_prompt_plain(**rest):
    yield prompt_templates_factories.make_completion_prompt_plain(**rest)


@pytest.fixture
def make_chat_completion_prompt_plain(**rest):
    yield prompt_templates_factories.make_chat_completion_prompt_plain(**rest)


@pytest.fixture
def make_prompt_templates_plain(**rest):
    yield prompt_templates_factories.make_prompt_templates_plain(**rest)


@pytest.fixture
def make_base_prompt(**rest):
    yield prompt_templates_factories.make_base_prompt(**rest)


@pytest.fixture
def make_completion_prompt(**rest):
    yield prompt_templates_factories.make_completion_prompt(**rest)


@pytest.fixture
def make_chat_completion_prompt(**rest):
    yield prompt_templates_factories.make_chat_completion_prompt(**rest)


@pytest.fixture
def make_prompt_templates(**rest):
    yield prompt_templates_factories.make_prompt_templates(**rest)


@pytest.fixture
def make_success_response_plain(**data):
    yield responses_factories.make_successful_response_wrapper_plain(**data)


@pytest.fixture
def make_summarizer_config_plain(**rest):
    yield configs_factories.make_summarizer_config_plain(**rest)


####################################################################
# Logs
####################################################################
@pytest.fixture
def check_log_message(caplog):
    caplog.set_level(logging.DEBUG)

    def assert_log_message(level, message):
        for line in caplog.text.splitlines():
            # Assert log level and message
            if level in line and message in line:
                return

        assert (
            False
        ), f"Log not found: [{level}] {message} \n in: {caplog.text}"

    return assert_log_message
