from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import Mapped


class IdIntPkMix:
    id: Mapped[int] = mapped_column(primary_key=True)
