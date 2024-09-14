"""add_oauth

Revision ID: 311d618b1b3d
Revises: 39a1ed7ca651
Create Date: 2024-09-14 22:11:59.435009

"""

from typing import Sequence, Union

import sqlalchemy as sa
import sqlmodel
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "311d618b1b3d"
down_revision: Union[str, None] = "39a1ed7ca651"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table(
        "oauth_account",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("user_id", sa.UUID(), nullable=False),
        sa.Column("oauth_user_id", sa.String(length=255), nullable=True),
        sa.Column("provider_type", sa.String(length=50), nullable=False),
        sa.ForeignKeyConstraint(
            ["user_id"],
            ["users.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("id"),
        sa.UniqueConstraint(
            "oauth_user_id", "provider_type", name="oauth_user_id_provider_type_unique"
        ),
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table("oauth_account")
    # ### end Alembic commands ###