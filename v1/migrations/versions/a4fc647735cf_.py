"""empty message

Revision ID: a4fc647735cf
Revises: 47375d1d71b9
Create Date: 2019-02-26 22:30:02.941249

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'a4fc647735cf'
down_revision = '47375d1d71b9'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_foreign_key(None, 'roles_users', 'users', ['user_id'], ['user_id'])
    op.add_column('users', sa.Column('active', sa.Boolean(), nullable=True))
    op.add_column('users', sa.Column('password', sa.String(length=256), nullable=True))
    op.create_unique_constraint(None, 'users', ['email'])
    op.drop_column('users', 'id')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('users', sa.Column('id', sa.BIGINT(), autoincrement=True, nullable=False))
    op.drop_constraint(None, 'users', type_='unique')
    op.drop_column('users', 'password')
    op.drop_column('users', 'active')
    op.drop_constraint(None, 'roles_users', type_='foreignkey')
    # ### end Alembic commands ###
