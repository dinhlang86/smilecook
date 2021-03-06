"""empty message

Revision ID: 6443a112f397
Revises: f5fd64cc7ebf
Create Date: 2022-07-14 19:05:06.184646

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '6443a112f397'
down_revision = 'f5fd64cc7ebf'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('recipe', sa.Column('cover_image', sa.String(length=100), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('recipe', 'cover_image')
    # ### end Alembic commands ###
