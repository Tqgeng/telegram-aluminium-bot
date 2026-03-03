import pytest
from decimal import Decimal

from services.calculator_service import CalcInput, calculate
from core.models.material import MaterialType
from core.models.price_coefficient import CoefficientType
from core.models import db_helper
from tests.conftest import FakeSession, make_coefficient_row

pytestmark = pytest.mark.asyncio


def _set_db(monkeypatch, session):
    class _Ctx:
        async def __aenter__(self_inner):
            return session

        async def __aexit__(self_inner, exc_type, exc, tb):
            return False

    def _factory():
        return _Ctx()

    monkeypatch.setattr(db_helper, "session_factory", _factory)


async def _run_calc(monkeypatch, session, input: CalcInput):
    _set_db(monkeypatch, session)
    return await calculate(input)


async def test_calculate_basic_area(monkeypatch, make_material):
    materials = [
        make_material("profileA", type_=MaterialType.profile, price=1000, unit="м2"),
        make_material("glazingA", type_=MaterialType.glazing, price=800, unit="м2"),
        make_material("fittingsA", type_=MaterialType.fittings, price=300, unit="шт"),
    ]

    session = FakeSession(materials=materials, coefficients=[])

    input = CalcInput(
        width_cm=120,
        height_cm=120,
        quantity=2,
        profile_name="profileA",
        glazing_name="glazingA",
        fittings_name="fittingsA",
        package_names=[],
        service_names=[],
    )
    result = await _run_calc(monkeypatch, session, input)

    assert result.area_m2 == Decimal("2.880")
    # materials = (1000+800)*2.88 + 300*2 = 5184 + 600 = 5784
    assert result.material_cost == Decimal("5784.00")
    assert result.labor_cost == Decimal("0.00")
    assert result.delivery_cost == Decimal("0.00")
    assert result.discount_value == Decimal("0.00")
    assert result.total_cost == Decimal("5784.00")


async def test_calculate_profile_linear(monkeypatch, make_material):
    materials = [
        make_material("profileL", type_=MaterialType.profile, price=200, unit="м.п."),
        make_material("glazingB", type_=MaterialType.glazing, price=500, unit="м2"),
        make_material("fittingsB", type_=MaterialType.fittings, price=100, unit="шт"),
    ]
    session = FakeSession(materials=materials, coefficients=[])

    input = CalcInput(
        width_cm=100,
        height_cm=50,
        quantity=1,
        profile_name="profileL",
        glazing_name="glazingB",
        fittings_name="fittingsB",
        package_names=[],
        service_names=[],
    )

    result = await _run_calc(monkeypatch, session, input)

    # perim = 2*(1+0.5)=3, area=0.5
    # materials = 200*3 + 500*0.5 + 100*1 = 600+250+100=950
    assert result.material_cost == Decimal("950.00")


async def test_calculate_service_percent(
    monkeypatch, make_material, make_coefficient_row
):
    materials = [
        make_material("profileA", type_=MaterialType.profile, price=1000, unit="м2"),
        make_material("glazingA", type_=MaterialType.glazing, price=800, unit="м2"),
        make_material("fittingsA", type_=MaterialType.fittings, price=300, unit="шт"),
    ]
    coefficients = [make_coefficient_row("Монтаж", CoefficientType.region, "0.10")]
    session = FakeSession(materials=materials, coefficients=coefficients)

    input = CalcInput(
        width_cm=120,
        height_cm=120,
        quantity=2,
        profile_name="profileA",
        glazing_name="glazingA",
        fittings_name="fittingsA",
        package_names=[],
        service_names=["Монтаж"],
    )
    # materials = 5784 * 0.1 = 578.4
    result = await _run_calc(monkeypatch, session, input)
    assert result.labor_cost == Decimal("578.40")


async def test_calculate_service_fixed(
    monkeypatch, make_material, make_coefficient_row
):
    materials = [
        make_material("profileA", type_=MaterialType.profile, price=1000, unit="м2"),
        make_material("glazingA", type_=MaterialType.glazing, price=800, unit="м2"),
        make_material("fittingsA", type_=MaterialType.fittings, price=300, unit="шт"),
    ]
    coefficients = [make_coefficient_row("Монтаж", CoefficientType.region, "500")]
    session = FakeSession(materials=materials, coefficients=coefficients)

    input = CalcInput(
        width_cm=120,
        height_cm=120,
        quantity=2,
        profile_name="profileA",
        glazing_name="glazingA",
        fittings_name="fittingsA",
        package_names=[],
        service_names=["Монтаж"],
    )
    # 500 * 2 = 1000
    result = await _run_calc(monkeypatch, session, input)
    assert result.labor_cost == Decimal("1000.00")


async def test_delivery_free_threshold(
    monkeypatch, make_material, make_coefficient_row
):
    materials = [
        make_material("profileA", type_=MaterialType.profile, price=200000, unit="м2"),
        make_material("glazingA", type_=MaterialType.glazing, price=200000, unit="м2"),
        make_material("fittingsA", type_=MaterialType.fittings, price=1000, unit="шт"),
    ]
    coefficients = [make_coefficient_row("Доставка", CoefficientType.region, "0.10")]
    session = FakeSession(materials=materials, coefficients=coefficients)

    input = CalcInput(
        width_cm=200,
        height_cm=200,
        quantity=2,
        profile_name="profileA",
        glazing_name="glazingA",
        fittings_name="fittingsA",
        package_names=[],
        service_names=["Доставка"],
    )
    # materials = 3202000 > 500000
    result = await _run_calc(monkeypatch, session, input)
    assert result.delivery_cost == Decimal("0.00")


async def test_delivery_percent(monkeypatch, make_material, make_coefficient_row):
    materials = [
        make_material("profileA", type_=MaterialType.profile, price=1000, unit="м2"),
        make_material("glazingA", type_=MaterialType.glazing, price=800, unit="м2"),
        make_material("fittingsA", type_=MaterialType.fittings, price=300, unit="шт"),
    ]
    coefficients = [make_coefficient_row("Доставка", CoefficientType.region, "0.05")]
    session = FakeSession(materials=materials, coefficients=coefficients)

    input = CalcInput(
        width_cm=120,
        height_cm=120,
        quantity=2,
        profile_name="profileA",
        glazing_name="glazingA",
        fittings_name="fittingsA",
        package_names=[],
        service_names=["Доставка"],
    )

    result = await _run_calc(monkeypatch, session, input)
    # material = 5784, доставка 5% = 289.20
    assert result.delivery_cost == Decimal("289.20")


async def test_discount_qty(monkeypatch, make_material):
    materials = [
        make_material("profileA", type_=MaterialType.profile, price=1000, unit="м2"),
        make_material("glazingA", type_=MaterialType.glazing, price=800, unit="м2"),
        make_material("fittingsA", type_=MaterialType.fittings, price=300, unit="шт"),
    ]
    session = FakeSession(materials=materials, coefficients=[])

    input = CalcInput(
        width_cm=120,
        height_cm=120,
        quantity=11,
        profile_name="profileA",
        glazing_name="glazingA",
        fittings_name="fittingsA",
        package_names=[],
        service_names=[],
    )

    result = await _run_calc(monkeypatch, session, input)
    # qty=11 => 10% скидка
    assert result.discount_value > Decimal("0.00")
