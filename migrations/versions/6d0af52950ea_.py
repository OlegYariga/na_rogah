"""empty message

Revision ID: 6d0af52950ea
Revises: cdf7d40a059e
Create Date: 2019-03-13 10:53:41.496504

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '6d0af52950ea'
down_revision = 'cdf7d40a059e'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('timetable')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('timetable',
    sa.Column('timetable_id', sa.BIGINT(), autoincrement=True, nullable=False),
    sa.Column('week_day', postgresql.ENUM('Понедельник', 'Вторник', 'Среда', 'Четверг', 'Пятница', 'Суббота', 'Воскресенье', name='enum'), autoincrement=False, nullable=True),
    sa.Column('time_from', postgresql.TIME(), autoincrement=False, nullable=True),
    sa.Column('time_to', postgresql.TIME(), autoincrement=False, nullable=True),
    sa.PrimaryKeyConstraint('timetable_id', name='timetable_pkey')
    )
    # ### end Alembic commands ###