"""Add timezone support to smoked_at

Revision ID: ff07d8515622
Revises: a6303ae7f82d
Create Date: 2024-12-12 16:23:10.396134

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'ff07d8515622'
down_revision = 'a6303ae7f82d'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('users', schema=None) as batch_op:
        batch_op.drop_column('timezone')

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('users', schema=None) as batch_op:
        batch_op.add_column(sa.Column('timezone', sa.VARCHAR(length=50), nullable=True))

    # ### end Alembic commands ###
