import pytest
from decimal import Decimal

from core.models.material import Material, MaterialType, MaterialCategory
from core.models.price_coefficient import CoefficientType


class FakeScalarResult:
    def __init__(self, items):
        self._items = items

    def all(self):
        return list(self._items)


class FakeExecuteResult:
    def __init__(self, rows):
        self._rows = rows

    def all(self):
        return list(self._rows)


class FakeSession:
    def __init__(self, materials=None, coefficients=None):
        self._materials = materials or []
        self._coefficients = coefficients or []

    async def scalars(self, stmt):
        return FakeScalarResult(self._materials)

    async def execute(self, stmt):
        return FakeExecuteResult(self._coefficients)


class FakeSessionFactory:
    def __init__(self, session):
        self._session = session

    async def __aenter__(self):
        return self._session

    async def __aexit__(self, exc_type, exc, tb):
        return False


@pytest.fixture
def make_material():
    def _make(
        name: str,
        category: MaterialCategory = MaterialCategory.windows,
        type_: MaterialType = MaterialType.profile,
        price: Decimal | str | int = "1000",
        unit: str = "м2",
        in_stock: bool = True,
    ):
        material = Material()
        material.name = name
        material.category = category
        material.type = type_
        material.price_per_unit = Decimal(str(price))
        material.unit = unit
        material.in_stock = in_stock
        return material

    return _make


@pytest.fixture
def make_coefficient_row():
    def _make(name: str, type_: CoefficientType, value: Decimal):
        return (name, type_, Decimal(str(value)))

    return _make
