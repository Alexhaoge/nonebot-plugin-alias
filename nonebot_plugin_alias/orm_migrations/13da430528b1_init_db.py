"""Init DB

Revision ID: 13da430528b1
Revises: 
Create Date: 2024-04-01 11:11:37.240334

"""
from typing import Sequence, Union
from pathlib import Path
from alembic import op
import sqlalchemy as sa
import json

# revision identifiers, used by Alembic.
revision: str = '13da430528b1'
down_revision: str | Sequence[str] | None = None
branch_labels: str | Sequence[str] | None = ("nonebot_plugin_alias",)
depends_on: str | Sequence[str] | None = None


def upgrade(name: str = "") -> None:
    if name:
        return
    bind = op.get_bind()
    alias_table = op.create_table(
        "alias_alias",
        sa.Column("id", sa.String(), nullable=False),
        sa.Column("name", sa.String(), nullable=False),
        sa.Column("command", sa.String(), nullable=False),
        sa.PrimaryKeyConstraint("id", "name"),
    )

    json_path = Path("data/alias/aliases.json")
    if json_path.exists():
        alias = json.load(json_path.open("r", encoding="utf-8"))
        for id in alias:
            for i, (aname, command) in enumerate(alias[id].items()):
                if i < 25 or id == 'global':
                    op.execute(alias_table.insert().values(id=id, name=aname, command=command))
    bind.commit()

def downgrade(name: str = "") -> None:
    if name:
        return
    alias = dict()
    bind = op.get_bind()
    cursor = bind.execute("SELECT id, name, command FROM alias_alias;")
    for id, aname, command in cursor.fetchall():
        if id not in alias:
            alias[id] = dict()
        alias[id][aname] = command
    data_path = Path("data/alias")
    data_path.mkdir(parents=True, exist_ok=True)
    with open(data_path/"aliases.json", 'w', encoding='utf-8') as f:
        json.dump(alias, f)

    op.drop_table("alias_alias")