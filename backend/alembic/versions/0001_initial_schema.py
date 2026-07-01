"""initial schema: lot_sets, lots, bookings, applications

Revision ID: 0001
Revises:
Create Date: 2026-07-01

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = "0001"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "lot_sets",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("uploaded_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("lots_count", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.false()),
    )

    op.create_table(
        "lots",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("external_id", sa.String(length=255), nullable=False),
        sa.Column(
            "set_id",
            sa.Integer(),
            sa.ForeignKey("lot_sets.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("project_name", sa.String(length=255), nullable=False),
        sa.Column("address", sa.String(length=500), nullable=False),
        sa.Column("rooms", sa.Integer(), nullable=False),
        sa.Column("area", sa.Numeric(10, 2), nullable=False),
        sa.Column("floor", sa.Integer(), nullable=False),
        sa.Column("price", sa.Numeric(14, 2), nullable=False),
        sa.Column("price_base", sa.Numeric(14, 2), nullable=False),
        sa.Column(
            "status",
            sa.Enum("for_sale", "reserved", "sold", name="lot_status", native_enum=False, length=20),
            nullable=False,
            server_default="for_sale",
        ),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
    )
    op.create_index("ix_lots_external_id", "lots", ["external_id"])
    op.create_index("ix_lots_set_id", "lots", ["set_id"])
    op.create_index("ix_lots_status", "lots", ["status"])

    op.create_table(
        "bookings",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("lot_id", sa.Integer(), sa.ForeignKey("lots.id", ondelete="CASCADE"), nullable=False),
        sa.Column("contact_name", sa.String(length=255), nullable=False),
        sa.Column("contact_phone", sa.String(length=50), nullable=True),
        sa.Column("contact_email", sa.String(length=255), nullable=True),
        sa.Column(
            "status",
            sa.Enum("active", "cancelled", name="booking_status", native_enum=False, length=20),
            nullable=False,
            server_default="active",
        ),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index("ix_bookings_lot_id", "bookings", ["lot_id"])

    op.create_table(
        "applications",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("lot_id", sa.Integer(), sa.ForeignKey("lots.id", ondelete="SET NULL"), nullable=True),
        sa.Column("contact_name", sa.String(length=255), nullable=False),
        sa.Column("contact_phone", sa.String(length=50), nullable=True),
        sa.Column("contact_email", sa.String(length=255), nullable=True),
        sa.Column("comment", sa.Text(), nullable=True),
        sa.Column(
            "status",
            sa.Enum("new", "in_progress", "closed", name="application_status", native_enum=False, length=20),
            nullable=False,
            server_default="new",
        ),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index("ix_applications_lot_id", "applications", ["lot_id"])


def downgrade() -> None:
    op.drop_table("applications")
    op.drop_table("bookings")
    op.drop_index("ix_lots_status", table_name="lots")
    op.drop_index("ix_lots_set_id", table_name="lots")
    op.drop_index("ix_lots_external_id", table_name="lots")
    op.drop_table("lots")
    op.drop_table("lot_sets")
