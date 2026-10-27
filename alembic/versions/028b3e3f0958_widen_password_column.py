"""widen password column for salted hashes

Revision ID: 028b3e3f0958
Revises: ef497f559ba2
Create Date: 2026-10-27 17:45:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '028b3e3f0958'
down_revision = 'ef497f559ba2'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # werkzeug's scrypt hashes are ~162 chars; match the model's String(255)
    op.alter_column(
        'flask_user', 'password',
        existing_type=sa.String(length=100),
        type_=sa.String(length=255),
        existing_nullable=True,
    )


def downgrade() -> None:
    op.alter_column(
        'flask_user', 'password',
        existing_type=sa.String(length=255),
        type_=sa.String(length=100),
        existing_nullable=True,
    )
