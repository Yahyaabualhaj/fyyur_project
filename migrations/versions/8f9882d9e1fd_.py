"""empty message

Revision ID: 8f9882d9e1fd
Revises: 
Create Date: 2020-07-25 10:00:45.717885

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '8f9882d9e1fd'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('show_artist', sa.Column('start_time', sa.DateTime(), nullable=False))
    op.drop_column('show_artist', 'start_date')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('show_artist', sa.Column('start_date', postgresql.TIMESTAMP(), autoincrement=False, nullable=False))
    op.drop_column('show_artist', 'start_time')
    # ### end Alembic commands ###
