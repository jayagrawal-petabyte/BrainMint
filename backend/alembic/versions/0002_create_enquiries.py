"""create_enquiries_table

Revision ID: 0002_create_enquiries
Revises: 
Create Date: 2026-10-23

Adds the 'enquiries' table with:
- Contact fields: name, email, phone (optional)
- Enquiry content: service (optional), message
- Metadata: source, status, email_status, email_error
- Anti-spam: ip_address, idempotency_key (unique)
- Timestamps: created_at, updated_at
"""

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = "0002_create_enquiries"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create enum types first (PostgreSQL requires explicit enum creation)
    op.execute(
        """
        DO $$ BEGIN
            CREATE TYPE enquiry_source_enum AS ENUM (
                'service_enquiry',
                'contact_us'
            );
        EXCEPTION
            WHEN duplicate_object THEN null;
        END $$;
        """
    )

    op.execute(
        """
        DO $$ BEGIN
            CREATE TYPE enquiry_status_enum AS ENUM (
                'new',
                'in_review',
                'contacted',
                'converted',
                'closed'
            );
        EXCEPTION
            WHEN duplicate_object THEN null;
        END $$;
        """
    )

    op.execute(
        """
        DO $$ BEGIN
            CREATE TYPE email_status_enum AS ENUM (
                'pending',
                'sent',
                'failed'
            );
        EXCEPTION
            WHEN duplicate_object THEN null;
        END $$;
        """
    )

    op.create_table(
        "enquiries",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),

        # Contact fields
        sa.Column("name", sa.String(150), nullable=False),
        sa.Column("email", sa.String(254), nullable=False),
        sa.Column("phone", sa.String(20), nullable=True),

        # Enquiry content
        sa.Column("service", sa.String(100), nullable=True),
        sa.Column("message", sa.Text(), nullable=False),

        # Form metadata
        sa.Column(
            "source",
            sa.Enum(
                "service_enquiry",
                "contact_us",
                name="enquiry_source_enum",
                create_type=False,
            ),
            nullable=False,
        ),

        # CRM status
        sa.Column(
            "status",
            sa.Enum(
                "new",
                "in_review",
                "contacted",
                "converted",
                "closed",
                name="enquiry_status_enum",
                create_type=False,
            ),
            nullable=False,
            server_default="new",
        ),

        # Email delivery
        sa.Column(
            "email_status",
            sa.Enum(
                "pending",
                "sent",
                "failed",
                name="email_status_enum",
                create_type=False,
            ),
            nullable=False,
            server_default="pending",
        ),
        sa.Column("email_error", sa.Text(), nullable=True),

        # Anti-spam / audit
        sa.Column("ip_address", sa.String(45), nullable=True),
        sa.Column("idempotency_key", sa.String(64), nullable=True, unique=True),

        # Timestamps
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
    )

    # Indexes
    op.create_index("ix_enquiries_id", "enquiries", ["id"])
    op.create_index("ix_enquiries_email", "enquiries", ["email"])
    op.create_index("ix_enquiries_service", "enquiries", ["service"])
    op.create_index("ix_enquiries_source", "enquiries", ["source"])
    op.create_index("ix_enquiries_status", "enquiries", ["status"])
    op.create_index("ix_enquiries_ip_address", "enquiries", ["ip_address"])
    op.create_index("ix_enquiries_created_at", "enquiries", ["created_at"])
    op.create_index(
        "ix_enquiries_idempotency_key",
        "enquiries",
        ["idempotency_key"],
        unique=True,
    )


def downgrade() -> None:
    op.drop_index("ix_enquiries_idempotency_key", table_name="enquiries")
    op.drop_index("ix_enquiries_created_at", table_name="enquiries")
    op.drop_index("ix_enquiries_ip_address", table_name="enquiries")
    op.drop_index("ix_enquiries_status", table_name="enquiries")
    op.drop_index("ix_enquiries_source", table_name="enquiries")
    op.drop_index("ix_enquiries_service", table_name="enquiries")
    op.drop_index("ix_enquiries_email", table_name="enquiries")
    op.drop_index("ix_enquiries_id", table_name="enquiries")
    op.drop_table("enquiries")

    op.execute("DROP TYPE IF EXISTS enquiry_source_enum;")
    op.execute("DROP TYPE IF EXISTS enquiry_status_enum;")
    op.execute("DROP TYPE IF EXISTS email_status_enum;")
