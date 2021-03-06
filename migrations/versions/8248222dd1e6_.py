"""empty message

Revision ID: 8248222dd1e6
Revises: 
Create Date: 2020-06-20 18:16:34.703948

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '8248222dd1e6'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('movies')
    op.drop_table('actors')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('actors',
    sa.Column('id', sa.INTEGER(), server_default=sa.text('nextval(\'"actors_id_seq"\'::regclass)'), autoincrement=True, nullable=False),
    sa.Column('name', sa.VARCHAR(), autoincrement=False, nullable=True),
    sa.Column('age', sa.INTEGER(), autoincrement=False, nullable=True),
    sa.Column('gender', sa.VARCHAR(), autoincrement=False, nullable=True),
    sa.PrimaryKeyConstraint('id', name='actors_pkey')
    )
    op.create_table('movies',
    sa.Column('id', sa.INTEGER(), server_default=sa.text('nextval(\'"movies_id_seq"\'::regclass)'), autoincrement=True, nullable=False),
    sa.Column('title', sa.VARCHAR(), autoincrement=False, nullable=True),
    sa.Column('release_date', sa.DATE(), autoincrement=False, nullable=True),
    sa.PrimaryKeyConstraint('id', name='movies_pkey')
    )
    # ### end Alembic commands ###
