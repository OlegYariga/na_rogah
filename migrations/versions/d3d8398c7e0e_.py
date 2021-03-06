"""empty message

Revision ID: d3d8398c7e0e
Revises: 22902b987863
Create Date: 2019-03-09 22:09:43.775785

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'd3d8398c7e0e'
down_revision = '22902b987863'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('booking', sa.Column('time_from', sa.Time(), nullable=True))
    op.add_column('booking', sa.Column('time_to', sa.Time(), nullable=True))
    op.drop_column('booking', 'time')
    op.drop_column('booking', 'period')
    op.drop_column('tables', 'number')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('tables', sa.Column('number', sa.INTEGER(), autoincrement=False, nullable=True))
    op.add_column('booking', sa.Column('period', sa.INTEGER(), autoincrement=False, nullable=True))
    op.add_column('booking', sa.Column('time', postgresql.TIME(), autoincrement=False, nullable=True))
    op.drop_column('booking', 'time_to')
    op.drop_column('booking', 'time_from')
    # ### end Alembic commands ###
