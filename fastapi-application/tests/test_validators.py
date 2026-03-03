import pytest
from services.calculator_service import CalcInput, calculate
from core.models.material import MaterialType
from tests.conftest import FakeSession, make_coefficient_row
from tests.test_calculator import _set_db

pytestmark = pytest.mark.asyncio


async def test_validate_min_size(monkeypatch, make_material):
    materials = [
        make_material("profileA", type_=MaterialType.profile),
        make_material("glazingA", type_=MaterialType.glazing),
        make_material("fittingsA", type_=MaterialType.fittings, unit="шт"),
    ]
    session = FakeSession(materials=materials, coefficients=[])

    input = CalcInput(
        width_cm=10,
        height_cm=120,
        quantity=1,
        profile_name="profileA",
        glazing_name="glazingA",
        fittings_name="fittingsA",
        package_names=[],
        service_names=[],
    )

    _set_db(monkeypatch, session)
    with pytest.raises(ValueError):
        await calculate(input)


async def test_validate_area(monkeypatch, make_material):
    materials = [
        make_material("profileA", type_=MaterialType.profile),
        make_material("glazingA", type_=MaterialType.glazing),
        make_material("fittingsA", type_=MaterialType.fittings, unit="шт"),
    ]
    session = FakeSession(materials=materials, coefficients=[])

    input = CalcInput(
        width_cm=40,
        height_cm=40,
        quantity=1,
        profile_name="profileA",
        glazing_name="glazingA",
        fittings_name="fittingsA",
        package_names=[],
        service_names=[],
    )

    _set_db(monkeypatch, session)
    with pytest.raises(ValueError):
        await calculate(input)
