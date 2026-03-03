from core.models import db_helper, Application, ApplicationPhoto, User
from sqlalchemy import select, update, func
from services.crm_service import crm_client
import logging
from datetime import datetime, timedelta, timezone


async def create_application(data: dict) -> int:
    async with db_helper.session_factory() as session:
        app = Application(
            user_id=data.get("user_id"),
            contact_name=data.get("contact_name"),
            phone=data.get("phone"),
            email=data.get("email"),
            address=data.get("address"),
            description=data.get("description"),
            estimated_cost=data.get("estimated_cost"),
            status="new",
        )
        session.add(app)
        await session.flush()

        for item in data.get("photos", []):
            session.add(
                ApplicationPhoto(
                    application_id=app.id,
                    file_id=item.get("file_id"),
                    file_path=item.get("file_path"),
                )
            )

        await session.commit()

        try:
            crm_response = await crm_client.send_application(
                {
                    "application_id": app.id,
                    "user_id": app.user_id,
                    "phone": app.phone,
                    "name": app.contact_name,
                    "email": app.email,
                    "address": app.address,
                    "description": app.description,
                    "estimated_cost": (
                        str(app.estimated_cost) if app.estimated_cost else None
                    ),
                    "attachments": [p.get("file_id") for p in data.get("photos", [])],
                }
            )
            crm_id = crm_response.get("crm_id")
            if crm_id:
                app.crm_id = crm_id
                await session.commit()
        except Exception as e:
            logging.getLogger("crm").warning("crm failed: %s", e)

        return app.id


async def list_user_applications(user_id: int):
    async with db_helper.session_factory() as session:
        stmt = (
            select(Application)
            .where(Application.user_id == user_id)
            .order_by(Application.created_at.desc())
        )
        result = await session.scalars(stmt)
        return list(result)


async def sync_crm_statuses(notify_fn):
    async with db_helper.session_factory() as session:
        stmt = select(Application).where(Application.crm_id.is_not(None))
        apps = (await session.scalars(stmt)).all()
        for app in apps:
            new_status = await crm_client.get_application_status(app.crm_id)
            if new_status != app.status:
                app.status = new_status
                await session.commit()

                if app.user_id:
                    user = await session.get(User, app.user_id)
                    if user and user.telegram_id:
                        await notify_fn(user.telegram_id, app.id, new_status)


async def set_application_status(app_id: int, status: str) -> int | None:
    async with db_helper.session_factory() as session:
        await session.execute(
            update(Application).where(Application.id == app_id).values(status=status)
        )
        await session.commit()

        stmt = select(Application.user_id).where(Application.id == app_id)
        return await session.scalar(stmt)


async def get_application(app_id: int) -> Application | None:
    async with db_helper.session_factory() as session:
        stmt = select(Application).where(Application.id == app_id)
        return await session.scalar(stmt)


async def count_today_applications():
    async with db_helper.session_factory() as session:
        stmt = select(func.count()).where(
            func.date(Application.created_at) == func.current_date()
        )
        return await session.scalar(stmt)


async def get_stale_applications(hours: int = 1):
    cutoff = datetime.now(timezone.utc) - timedelta(hours=hours)
    async with db_helper.session_factory() as session:
        stmt = select(Application).where(
            Application.status == "new",
            Application.created_at < cutoff,
        )
        return (await session.scalars(stmt)).all()
