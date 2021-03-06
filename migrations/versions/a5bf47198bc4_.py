"""empty message

Revision ID: a5bf47198bc4
Revises: 22a60a45ffa3
Create Date: 2019-03-01 17:44:52.660819

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'a5bf47198bc4'
down_revision = '22a60a45ffa3'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('menu', 'price',
               existing_type=postgresql.DOUBLE_PRECISION(precision=53),
               type_=sa.Integer(),
               existing_nullable=True)
    op.alter_column('menu', 'weight',
               existing_type=sa.INTEGER(),
               type_=sa.String(length=36),
               existing_nullable=True)
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('menu', 'weight',
               existing_type=sa.String(length=36),
               type_=sa.INTEGER(),
               existing_nullable=True)
    op.alter_column('menu', 'price',
               existing_type=sa.Integer(),
               type_=postgresql.DOUBLE_PRECISION(precision=53),
               existing_nullable=True)
    # ### end Alembic commands ###
