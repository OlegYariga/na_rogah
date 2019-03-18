"""empty message

Revision ID: 7c1807a69d26
Revises: 6d0af52950ea
Create Date: 2019-03-13 11:01:41.274946

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '7c1807a69d26'
down_revision = '6d0af52950ea'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('timetable',
    sa.Column('timetable_id', sa.BigInteger(), nullable=False),
    sa.Column('week_day', sa.Enum('Понедельник', 'Вторник', 'Среда', 'Четверг', 'Пятница', 'Суббота', 'Воскресенье', name='enum'), nullable=True),
    sa.Column('time_from', sa.Time(), nullable=True),
    sa.Column('time_to', sa.Time(), nullable=True),
    sa.PrimaryKeyConstraint('timetable_id')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('timetable')
    # ### end Alembic commands ###