"""empty message

Revision ID: 422bfcd44dcb
Revises: e5720f645762
Create Date: 2022-05-23 12:30:57.062487

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '422bfcd44dcb'
down_revision = 'e5720f645762'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('Venue', sa.Column('website_link', sa.String(length=50), nullable=True))
    op.add_column('Venue', sa.Column('seeking_talent', sa.String(), nullable=True))
    op.add_column('Venue', sa.Column('seeking_description', sa.String(), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('Venue', 'seeking_description')
    op.drop_column('Venue', 'seeking_talent')
    op.drop_column('Venue', 'website_link')
    # ### end Alembic commands ###
