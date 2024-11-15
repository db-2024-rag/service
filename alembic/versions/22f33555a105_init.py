"""init

Revision ID: 22f33555a105
Revises: 
Create Date: 2024-11-10 01:05:35.973096

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '22f33555a105'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('stored_files',
    sa.Column('id', sa.UUID(), nullable=False),
    sa.Column('mime', sa.String(), nullable=False),
    sa.Column('file_name', sa.String(), nullable=False),
    sa.Column('contents', sa.LargeBinary(), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('stored_file_entry',
    sa.Column('id', sa.UUID(), nullable=False),
    sa.Column('file_id', sa.UUID(), nullable=False),
    sa.Column('page', sa.Integer(), nullable=False),
    sa.Column('text', sa.String(), nullable=False),
    sa.ForeignKeyConstraint(['file_id'], ['stored_files.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('stored_file_entry')
    op.drop_table('stored_files')
    # ### end Alembic commands ###
