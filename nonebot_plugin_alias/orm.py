from nonebot_plugin_orm import Model
from sqlalchemy.orm import Mapped, MappedAsDataclass, mapped_column


class AliasORM(MappedAsDataclass, Model):
    __tablename__ = "alias_alias"
    __table_args__ = {"extend_existing": True}

    id: Mapped[str] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(primary_key=True)
    command: Mapped[str]

    # @property
    # def is_global(self) -> bool:
    #     return self.id == 'global'

__all__ = ['AliasORM']