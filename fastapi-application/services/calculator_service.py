from __future__ import annotations
from dataclasses import dataclass, field
from decimal import Decimal, ROUND_HALF_UP
from typing import Any, NamedTuple
from sqlalchemy import select, tuple_
from core.models import db_helper, Material, PriceCoefficient, Calculation
from core.models.material import MaterialType
from core.models.price_coefficient import CoefficientType

MIN_W_CM = Decimal("50")
MIN_H_CM = Decimal("50")
MAX_W_CM = Decimal("300")
MAX_H_CM = Decimal("300")
MIN_QTY = 1
MAX_QTY = 100
MIN_AREA_M2 = Decimal("0.25")
MAX_AREA_M2 = Decimal("90")

AREA_UNITS = {"м²", "м2", "m2", "m²", "кв.м", "квм"}
PIECE_UNITS = {"шт", "pcs", "piece", "pieces"}
LINEAR_UNITS = {"м.п.", "мп", "п.м.", "пм", "m", "метр", "метры"}


def _to_decimal(v: Any) -> Decimal:
    try:
        return Decimal(str(v).replace(",", "."))
    except Exception as e:
        raise ValueError(f"Некорректное число: {v}") from e


def _q2(v: Decimal) -> Decimal:
    return v.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)


def _q3(v: Decimal) -> Decimal:
    return v.quantize(Decimal("0.001"), rounding=ROUND_HALF_UP)


@dataclass
class CalcInput:
    width_cm: Decimal
    height_cm: Decimal
    quantity: int

    profile_name: str
    glazing_name: str
    fittings_name: str

    package_names: list[str]
    service_names: list[str]
    complexity_name: str | None = None

    is_new_client: bool = False
    new_client_discount_name: str = "Новый клиент"
    seasonal_discount_name: str | None = None
    promo_discount_names: list[str] = field(default_factory=list)

    delivery_service_name: str = "Доставка"
    delivery_pricing_name: str = "Доставка"
    free_delivery_threshold: Decimal = Decimal("500000")


@dataclass
class CalcResult:
    area_m2: Decimal
    material_cost: Decimal
    labor_cost: Decimal
    delivery_cost: Decimal
    discount_value: Decimal
    total_cost: Decimal


class CoeffKey(NamedTuple):
    name: str
    type: CoefficientType


def _validate_input(inp: CalcInput) -> None:
    w = _to_decimal(inp.width_cm)
    h = _to_decimal(inp.height_cm)

    if not (MIN_W_CM <= w <= MAX_W_CM):
        raise ValueError(f"width_cm вне диапазона {MIN_W_CM}-{MAX_W_CM}: {w}")
    if not (MIN_H_CM <= h <= MAX_H_CM):
        raise ValueError(f"height_cm вне диапазона {MIN_H_CM}-{MAX_H_CM}: {h}")
    if not (MIN_QTY <= inp.quantity <= MAX_QTY):
        raise ValueError(f"quantity вне диапазона {MIN_QTY}-{MAX_QTY}: {inp.quantity}")

    area = _area_m2(w, h, inp.quantity)
    if not (MIN_AREA_M2 <= area <= MAX_AREA_M2):
        raise ValueError(f"area_m2 вне диапазона {MIN_AREA_M2}-{MAX_AREA_M2}: {area}")


def _area_m2(width_cm: Decimal, height_cm: Decimal, quantity: int) -> Decimal:
    return (width_cm / Decimal(100)) * (height_cm / Decimal(100)) * Decimal(quantity)


def _perimeter_m(width_cm: Decimal, height_cm: Decimal) -> Decimal:
    return (Decimal(2) * (width_cm + height_cm)) / Decimal(100)


def _qty_discount(quantity: int) -> Decimal:
    if quantity > 20:
        return Decimal("0.15")
    if quantity > 10:
        return Decimal("0.10")
    if quantity > 5:
        return Decimal("0.05")
    return Decimal("0")


def _norm_unit(unit: str | None) -> str:
    if not unit:
        return ""
    return unit.strip().lower().replace(" ", "")


def _is_delivery_selected(inp: CalcInput) -> bool:
    return any(
        s.strip().lower() == inp.delivery_service_name.strip().lower()
        for s in inp.service_names
    )


def _split_material_cost(
    m: Material,
    *,
    area_m2: Decimal,
    perimeter_one_m: Decimal,
    quantity: int,
) -> tuple[Decimal, Decimal]:
    price = _to_decimal(m.price_per_unit)
    unit = _norm_unit(getattr(m, "unit", None))

    if unit in {u.lower().replace(" ", "") for u in AREA_UNITS}:
        return price * area_m2, Decimal("0")

    if unit in {u.lower().replace(" ", "") for u in LINEAR_UNITS}:
        return price * perimeter_one_m * Decimal(quantity), Decimal("0")

    if unit in {u.lower().replace(" ", "") for u in PIECE_UNITS}:
        return Decimal("0"), price * Decimal(quantity)

    return Decimal("0"), price * Decimal(quantity)


async def _fetch_materials_by_names(session, names: list[str]) -> dict[str, Material]:
    unique = [n for n in dict.fromkeys([x.strip() for x in names if x and x.strip()])]
    if not unique:
        return {}
    stmt = select(Material).where(Material.name.in_(unique))
    res = await session.scalars(stmt)
    rows = res.all()
    return {m.name: m for m in rows}


def _require_material(
    material: dict[str, Material], name: str, type_: MaterialType
) -> Material:
    m = material.get(name)
    if not m:
        raise ValueError(f"Material not found: {name}")
    if m.type != type_:
        raise ValueError(f"Material {name} имеет type={m.type}, ожидался {type_}")
    return m


async def _fetch_coeffs_by_keys(
    session, keys: list[CoeffKey]
) -> dict[CoeffKey, Decimal]:
    unique_keys = list(dict.fromkeys(keys))
    if not unique_keys:
        return {}

    stmt = select(
        PriceCoefficient.name,
        PriceCoefficient.type,
        PriceCoefficient.value,
    ).where(
        tuple_(PriceCoefficient.name, PriceCoefficient.type).in_(
            [(k.name, k.type) for k in unique_keys]
        )
    )
    rows = (await session.execute(stmt)).all()
    return {CoeffKey(name, type_): _to_decimal(value) for name, type_, value in rows}


def _coeff_or_zero(coeffs: dict[CoeffKey, Decimal], key: CoeffKey | None) -> Decimal:
    if not key:
        return Decimal("0")
    return coeffs.get(key, Decimal("0"))


async def calculate(inp: CalcInput) -> CalcResult:
    _validate_input(inp)

    width_cm = _to_decimal(inp.width_cm)
    height_cm = _to_decimal(inp.height_cm)
    area = _area_m2(width_cm, height_cm, inp.quantity)
    perim_one = _perimeter_m(width_cm, height_cm)

    material_names: list[str] = [
        inp.profile_name,
        inp.glazing_name,
        inp.fittings_name,
        *inp.package_names,
    ]

    coeff_keys: list[CoeffKey] = []

    if inp.complexity_name:
        coeff_keys.append(CoeffKey(inp.complexity_name, CoefficientType.complexity))

    services_no_delivery = [
        s
        for s in inp.service_names
        if s and s.strip().lower() != inp.delivery_service_name.strip().lower()
    ]
    for s in services_no_delivery:
        coeff_keys.append(CoeffKey(s, CoefficientType.region))

    if _is_delivery_selected(inp):
        coeff_keys.append(CoeffKey(inp.delivery_pricing_name, CoefficientType.region))

    if inp.is_new_client:
        coeff_keys.append(
            CoeffKey(inp.new_client_discount_name, CoefficientType.discount)
        )
    if inp.seasonal_discount_name:
        coeff_keys.append(
            CoeffKey(inp.seasonal_discount_name, CoefficientType.seasonal)
        )
    for dn in inp.promo_discount_names:
        coeff_keys.append(CoeffKey(dn, CoefficientType.promo))

    async with db_helper.session_factory() as session:
        materials = await _fetch_materials_by_names(session, material_names)
        coeffs = await _fetch_coeffs_by_keys(session, coeff_keys)

    profile = _require_material(materials, inp.profile_name, MaterialType.profile)
    glazing = _require_material(materials, inp.glazing_name, MaterialType.glazing)
    fittings = _require_material(materials, inp.fittings_name, MaterialType.fittings)

    complexity = Decimal("1.0")
    if inp.complexity_name:
        complexity = _coeff_or_zero(
            coeffs, CoeffKey(inp.complexity_name, CoefficientType.complexity)
        ) or Decimal("1.0")

    profile_size, profile_piece = _split_material_cost(
        profile, area_m2=area, perimeter_one_m=perim_one, quantity=inp.quantity
    )
    glazing_size, glazing_piece = _split_material_cost(
        glazing, area_m2=area, perimeter_one_m=perim_one, quantity=inp.quantity
    )
    fittings_size, fittings_piece = _split_material_cost(
        fittings, area_m2=area, perimeter_one_m=perim_one, quantity=inp.quantity
    )

    packages_size = Decimal("0")
    packages_piece = Decimal("0")
    for name in inp.package_names:
        m = materials.get(name)
        if not m:
            raise ValueError(f"Package material not found: {name}")
        sz, pc = _split_material_cost(
            m, area_m2=area, perimeter_one_m=perim_one, quantity=inp.quantity
        )
        packages_size += sz
        packages_piece += pc

    size_dependent_materials = (
        profile_size + glazing_size + fittings_size + packages_size
    )
    piece_materials = profile_piece + glazing_piece + fittings_piece + packages_piece

    material_cost = (size_dependent_materials * complexity) + piece_materials

    labor_cost = Decimal("0")
    base_for_percent_services = material_cost

    for svc in services_no_delivery:
        v = _coeff_or_zero(coeffs, CoeffKey(svc, CoefficientType.region))
        if v == 0:
            raise ValueError(f"Service coefficient not found: {svc}")
        if v < 1:
            labor_cost += base_for_percent_services * v
        else:
            labor_cost += v * Decimal(inp.quantity)

    delivery_cost = Decimal("0")
    if _is_delivery_selected(inp):
        delivery_v = _coeff_or_zero(
            coeffs, CoeffKey(inp.delivery_pricing_name, CoefficientType.region)
        )
        if delivery_v == 0:
            raise ValueError(
                f"Delivery coefficient not found: {inp.delivery_pricing_name}"
            )

        base_before_delivery = material_cost + labor_cost

        if base_before_delivery >= _to_decimal(inp.free_delivery_threshold):
            delivery_cost = Decimal("0")
        else:
            delivery_cost = (
                (base_before_delivery * delivery_v) if delivery_v < 1 else delivery_v
            )

    subtotal = material_cost + labor_cost + delivery_cost

    discount_percent = _qty_discount(inp.quantity)

    if inp.is_new_client:
        discount_percent += _coeff_or_zero(
            coeffs, CoeffKey(inp.new_client_discount_name, CoefficientType.discount)
        )
    if inp.seasonal_discount_name:
        discount_percent += _coeff_or_zero(
            coeffs, CoeffKey(inp.seasonal_discount_name, CoefficientType.seasonal)
        )
    for dn in inp.promo_discount_names:
        discount_percent += _coeff_or_zero(coeffs, CoeffKey(dn, CoefficientType.promo))

    if discount_percent < 0:
        discount_percent = Decimal("0")
    if discount_percent > Decimal("0.50"):
        discount_percent = Decimal("0.50")

    discount_value = subtotal * discount_percent
    total = subtotal - discount_value

    return CalcResult(
        area_m2=_q3(area),
        material_cost=_q2(material_cost),
        labor_cost=_q2(labor_cost),
        delivery_cost=_q2(delivery_cost),
        discount_value=_q2(discount_value),
        total_cost=_q2(total),
    )


async def save_calculation(
    inp: CalcInput,
    result: CalcResult,
    *,
    user_id: int | None,
    construction_type: str | None,
    profile_system: str | None,
) -> int:
    async with db_helper.session_factory() as session:
        calc = Calculation(
            user_id=user_id,
            construction_type=construction_type or "unknown",
            profile_system=profile_system,
            width=inp.width_cm,
            height=inp.height_cm,
            quantity=inp.quantity,
            area=result.area_m2,
            material_cost=result.material_cost,
            labor_cost=result.labor_cost,
            additional_cost=result.delivery_cost,
            total_cost=result.total_cost,
        )
        session.add(calc)
        await session.commit()
        await session.refresh(calc)
        return calc.id
