"""add enrich text

Revision ID: a07da69bd185
Revises: afe4d2843d94
Create Date: 2024-11-10 02:26:10.450055

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'a07da69bd185'
down_revision: Union[str, None] = 'afe4d2843d94'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('stored_file_entry', sa.Column('text_enrich', sa.String(), nullable=True))
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('stored_file_entry', 'text_enrich')
    # ### end Alembic commands ###