"""empty message

Revision ID: b504f78366aa
Revises: 95bc3038aa7e
Create Date: 2019-03-13 19:58:29.960359

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'b504f78366aa'
down_revision = '95bc3038aa7e'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('booking', sa.Column('date_time_from', sa.DateTime(), nullable=True))
    op.add_column('booking', sa.Column('date_time_to', sa.DateTime(), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('booking', 'date_time_to')
    op.drop_column('booking', 'date_time_from')
    # ### end Alembic commands ###