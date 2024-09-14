"""partitions_table

Revision ID: 1eeb5a236065
Revises: 020063ca7a2e
Create Date: 2024-09-14 19:20:56.790557

"""

from typing import Sequence, Union

import sqlalchemy as sa
import sqlmodel
from alembic import op
from sqlalchemy.sql import text

# revision identifiers, used by Alembic.
revision: str = "1eeb5a236065"
down_revision: Union[str, None] = "020063ca7a2e"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Удаление существующей таблицы без партиционирования
    op.execute("DROP TABLE IF EXISTS login_history CASCADE;")

    # Создание новой таблицы с партиционированием
    op.execute(
        """
        CREATE TABLE IF NOT EXISTS login_history (
            id UUID NOT NULL,
            user_id UUID NOT NULL,
            event_date TIMESTAMP WITHOUT TIME ZONE NOT NULL,
            success BOOLEAN NOT NULL,
            user_agent TEXT NOT NULL,
            PRIMARY KEY (id, event_date)
        ) PARTITION BY RANGE (event_date);
    """
    )

    # Логика для создания партиций на 12 месяцев
    connection = op.get_bind()
    for month in range(1, 13):
        next_month_year = f"2024-{month + 1:02d}-01" if month < 12 else "2025-01-01"
        connection.execute(
            text(
                f"""
                CREATE TABLE IF NOT EXISTS login_history_{month:02d} 
                PARTITION OF login_history 
                FOR VALUES FROM ('2024-{month:02d}-01') TO ('{next_month_year}');
            """
            )
        )


def downgrade() -> None:
    # Удаление партиций и самой таблицы при откате
    connection = op.get_bind()
    for month in range(1, 13):
        connection.execute(text(f"DROP TABLE IF EXISTS login_history_{month:02d};"))

    op.execute("DROP TABLE IF EXISTS login_history;")
