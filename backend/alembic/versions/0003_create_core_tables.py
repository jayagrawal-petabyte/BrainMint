from alembic import op
import sqlalchemy as sa

revision = "0003_create_core_tables"
down_revision = "0002_create_enquiries"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "admin_users",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("email", sa.String(), nullable=False),
        sa.Column("hashed_password", sa.String(), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=True),
        sa.Column("failed_login_attempts", sa.Integer(), nullable=True),
        sa.Column("locked_until", sa.DateTime(), nullable=True),
    )
    op.create_index("ix_admin_users_id", "admin_users", ["id"])
    op.create_index("ix_admin_users_email", "admin_users", ["email"], unique=True)

    op.create_table(
        "services",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("slug", sa.String(100), nullable=False),
        sa.Column("name", sa.String(150), nullable=False),
        sa.Column("short_description", sa.String(300), nullable=False),
        sa.Column("description", sa.Text(), nullable=False),
        sa.Column("icon", sa.String(255), nullable=True),
        sa.Column("image_url", sa.String(255), nullable=True),
        sa.Column("features", sa.JSON(), nullable=False),
        sa.Column("benefits", sa.JSON(), nullable=False),
        sa.Column("meta_title", sa.String(200), nullable=True),
        sa.Column("meta_description", sa.String(300), nullable=True),
        sa.Column("og_image", sa.String(255), nullable=True),
        sa.Column("canonical_url", sa.String(255), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=False),
        sa.Column("display_order", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index("ix_services_id", "services", ["id"])
    op.create_index("ix_services_slug", "services", ["slug"], unique=True)

    op.create_table(
        "site_settings",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("key", sa.String(100), nullable=False),
        sa.Column("value", sa.JSON(), nullable=False),
        sa.Column("description", sa.String(255), nullable=True),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index("ix_site_settings_id", "site_settings", ["id"])
    op.create_index("ix_site_settings_key", "site_settings", ["key"], unique=True)

    op.create_table(
        "faqs",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("question", sa.String(300), nullable=False),
        sa.Column("answer", sa.Text(), nullable=False),
        sa.Column("category", sa.String(50), nullable=False),
        sa.Column("display_order", sa.Integer(), nullable=False),
        sa.Column("is_published", sa.Boolean(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index("ix_faqs_id", "faqs", ["id"])

    op.create_table(
        "social_links",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("platform", sa.String(50), nullable=False),
        sa.Column("url", sa.String(255), nullable=False),
        sa.Column("icon", sa.String(100), nullable=True),
        sa.Column("display_order", sa.Integer(), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False),
    )
    op.create_index("ix_social_links_id", "social_links", ["id"])


def downgrade() -> None:
    op.drop_table("social_links")
    op.drop_table("faqs")
    op.drop_table("site_settings")
    op.drop_table("services")
    op.drop_table("admin_users")