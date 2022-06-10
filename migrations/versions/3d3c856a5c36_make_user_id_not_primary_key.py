"""make user id not primary key

Revision ID: 3d3c856a5c36
Revises: 1a8580f36577
Create Date: 2022-04-27 15:20:46.905324

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "3d3c856a5c36"
down_revision = "1a8580f36577"
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column(
        "members", sa.Column("user_id", sa.BigInteger(), nullable=False)
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column("members", "user_id")
    # ### end Alembic commands ###