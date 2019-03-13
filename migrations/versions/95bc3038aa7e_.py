"""empty message

Revision ID: 95bc3038aa7e
Revises: 3d4a116b25b5
Create Date: 2019-03-13 18:31:46.299701

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '95bc3038aa7e'
down_revision = '3d4a116b25b5'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('booking', sa.Column('date_to', sa.Date(), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('booking', 'date_to')
    # ### end Alembic commands ###
