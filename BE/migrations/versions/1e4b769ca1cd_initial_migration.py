"""Initial migration.

Revision ID: 1e4b769ca1cd
Revises: 
Create Date: 2024-09-29 11:44:25.432146

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '1e4b769ca1cd'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('factor',
    sa.Column('id', sa.String(), nullable=False),
    sa.Column('name', sa.String(), nullable=False),
    sa.Column('factor', sa.Float(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('trigger',
    sa.Column('id', sa.String(), nullable=False),
    sa.Column('name', sa.String(), nullable=False),
    sa.Column('date', sa.Date(), nullable=True),
    sa.Column('time', sa.Time(), nullable=True),
    sa.Column('weekdays', sa.JSON(), nullable=True),
    sa.Column('from_date', sa.Date(), nullable=True),
    sa.Column('to_date', sa.Date(), nullable=True),
    sa.Column('duration', sa.DateTime(), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('user',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('username', sa.String(length=80), nullable=False),
    sa.Column('password_hash', sa.String(length=128), nullable=False),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('username')
    )
    op.create_table('valve',
    sa.Column('id', sa.String(), nullable=False),
    sa.Column('name', sa.String(), nullable=False),
    sa.Column('io_pin', sa.Integer(), nullable=False),
    sa.Column('status', sa.Enum('ON', 'OFF'), nullable=True),
    sa.Column('high_to_switch_on', sa.Boolean(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('trigger_factor_association',
    sa.Column('trigger_id', sa.String(), nullable=False),
    sa.Column('factor_id', sa.String(), nullable=False),
    sa.ForeignKeyConstraint(['factor_id'], ['factor.id'], ),
    sa.ForeignKeyConstraint(['trigger_id'], ['trigger.id'], ),
    sa.PrimaryKeyConstraint('trigger_id', 'factor_id')
    )
    op.create_table('valve_trigger_association',
    sa.Column('valve_id', sa.String(), nullable=False),
    sa.Column('trigger_id', sa.String(), nullable=False),
    sa.ForeignKeyConstraint(['trigger_id'], ['trigger.id'], ),
    sa.ForeignKeyConstraint(['valve_id'], ['valve.id'], ),
    sa.PrimaryKeyConstraint('valve_id', 'trigger_id')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('valve_trigger_association')
    op.drop_table('trigger_factor_association')
    op.drop_table('valve')
    op.drop_table('user')
    op.drop_table('trigger')
    op.drop_table('factor')
    # ### end Alembic commands ###
