"""empty message

Revision ID: a68a7e52d0f6
Revises: ca2d57fc2e09
Create Date: 2019-03-06 17:35:58.170950

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'a68a7e52d0f6'
down_revision = 'ca2d57fc2e09'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('category',
    sa.Column('category_id', sa.BigInteger(), nullable=False),
    sa.Column('name', sa.String(length=64), nullable=False),
    sa.Column('order', sa.Integer(), nullable=True),
    sa.PrimaryKeyConstraint('category_id')
    )
    op.add_column('menu', sa.Column('category_id', sa.BigInteger(), nullable=True))
    op.alter_column('menu', 'name',
               existing_type=sa.VARCHAR(length=128),
               nullable=False)
    op.create_foreign_key(None, 'menu', 'category', ['category_id'], ['category_id'])
    op.drop_column('menu', 'class_id')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('menu', sa.Column('class_id', sa.BIGINT(), autoincrement=False, nullable=True))
    op.drop_constraint(None, 'menu', type_='foreignkey')
    op.alter_column('menu', 'name',
               existing_type=sa.VARCHAR(length=128),
               nullable=True)
    op.drop_column('menu', 'category_id')
    op.drop_table('category')
    # ### end Alembic commands ###