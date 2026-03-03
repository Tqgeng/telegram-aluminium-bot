import pytest
from datetime import datetime, timezone

from services.application_service import create_application, get_application
from core.models.application import Application
from core.models.application_photo import ApplicationPhoto
from core.models import db_helper

pytestmark = pytest.mark.asyncio


class FakeSession:
    def __init__(self, app_to_return=None):
        self.added = []
        self.committed = []
        self.refreshed = []
        self.app_to_return = app_to_return

    def add(self, obj):
        self.added.append(obj)

    async def commit(self):
        self.committed = True

    async def scalar(self, smtm):
        return self.app_to_return

    async def refresh(self, obj):
        if getattr(obj, "id", None) is None:
            obj.id = 123

    async def flush(self):
        if self.added:
            last = self.added[-1]
            if getattr(last, "id", None) is None:
                last.id = 123

    async def execute(self, smtm):
        class _Result:
            def __init__(self, obj):
                self._obj = obj

            def scalar_one_or_none(self):
                return self._obj

        return _Result(self.app_to_return)


def _set_db(monkeypatch, session):
    class _Ctx:
        async def __aenter__(self_inner):
            return session

        async def __aexit__(self_inner, exc_type, exc, tb):
            return False

    def _factory():
        return _Ctx()

    monkeypatch.setattr(db_helper, "session_factory", _factory)


async def test_create_application(monkeypatch):
    session = FakeSession()
    _set_db(monkeypatch, session)

    data = {
        "user_id": 6,
        "contact_name": "Петр",
        "phone": "+79781234567",
        "email": "test@mail.ru",
        "address": "Севастополь",
        "description": "Описание",
        "status": "new",
        "estimated_cost": 15000,
        "photos": [
            {"file_id": "file1", "file_path": "photos/a.jpg"},
            {"file_id": "file2", "file_path": "photos/b.jpg"},
        ],
    }
    app_id = await create_application(data)
    assert app_id == 123
    assert session.committed is True
    assert sum(isinstance(p, Application) for p in session.added) == 1
    assert session.added[0].user_id == 6
    assert session.added[0].estimated_cost == 15000
    assert sum(isinstance(p, ApplicationPhoto) for p in session.added) == 2


async def test_get_application(monkeypatch):
    app = Application()
    app.id = 14
    app.contact_name = "Павел"
    app.created_at = datetime.now(timezone.utc)
    session = FakeSession(app_to_return=app)
    _set_db(monkeypatch, session)
    result = await get_application(14)
    assert result is app
