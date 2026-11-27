"""football dataset type: BaseDataset discriminator, football metadata and metrics, results files

The hub keeps UVL as a dataset type and adds the football results type (#15, #16):

- ``data_set.dataset_type`` tells the type of each dataset (single-table inheritance). Existing
  rows are UVL datasets, so the column defaults to ``'uvl'``.
- ``data_set`` gets the football metadata (competition, country, season, number of teams and
  data source). They are nullable because UVL rows leave them empty.
- ``ds_metrics`` gets the football metrics (number of matches and number of teams).
- ``results_file`` is the football counterpart of ``feature_model``.
- ``file`` can now belong to a feature model or to a results file, never both and never neither.

Revision ID: 002
Revises: 001
Create Date: 2026-11-27 12:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '002'
down_revision = '001'
branch_labels = None
depends_on = None


def upgrade():
    with op.batch_alter_table('data_set', schema=None) as batch_op:
        batch_op.add_column(sa.Column('dataset_type', sa.String(length=20), server_default='uvl', nullable=False))
        batch_op.add_column(sa.Column('competition', sa.String(length=120), nullable=True))
        batch_op.add_column(sa.Column('country', sa.String(length=120), nullable=True))
        batch_op.add_column(sa.Column('season', sa.String(length=9), nullable=True))
        batch_op.add_column(sa.Column('number_of_teams', sa.Integer(), nullable=True))
        batch_op.add_column(sa.Column('data_source', sa.String(length=255), nullable=True))

    with op.batch_alter_table('ds_metrics', schema=None) as batch_op:
        batch_op.add_column(sa.Column('number_of_matches', sa.Integer(), nullable=True))
        batch_op.add_column(sa.Column('number_of_teams', sa.Integer(), nullable=True))

    op.create_table('results_file',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('data_set_id', sa.Integer(), nullable=False),
    sa.Column('number_of_matches', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['data_set_id'], ['data_set.id'], ),
    sa.PrimaryKeyConstraint('id')
    )

    with op.batch_alter_table('file', schema=None) as batch_op:
        batch_op.add_column(sa.Column('results_file_id', sa.Integer(), nullable=True))
        batch_op.alter_column('feature_model_id', existing_type=sa.Integer(), nullable=True)
        batch_op.create_foreign_key('fk_file_results_file_id', 'results_file', ['results_file_id'], ['id'])
        batch_op.create_check_constraint(
            'ck_file_exactly_one_parent', '(feature_model_id IS NULL) <> (results_file_id IS NULL)'
        )


def downgrade():
    # The schema of 001 has no place for football data: remove it before going back.
    op.execute('DELETE FROM file WHERE results_file_id IS NOT NULL')
    op.execute("DELETE FROM ds_download_record WHERE dataset_id IN (SELECT id FROM data_set WHERE dataset_type = 'football')")
    op.execute("DELETE FROM ds_view_record WHERE dataset_id IN (SELECT id FROM data_set WHERE dataset_type = 'football')")
    op.execute('DELETE FROM results_file')
    op.execute("DELETE FROM data_set WHERE dataset_type = 'football'")

    with op.batch_alter_table('file', schema=None) as batch_op:
        batch_op.drop_constraint('ck_file_exactly_one_parent', type_='check')
        batch_op.drop_constraint('fk_file_results_file_id', type_='foreignkey')
        batch_op.alter_column('feature_model_id', existing_type=sa.Integer(), nullable=False)
        batch_op.drop_column('results_file_id')

    op.drop_table('results_file')

    with op.batch_alter_table('ds_metrics', schema=None) as batch_op:
        batch_op.drop_column('number_of_teams')
        batch_op.drop_column('number_of_matches')

    with op.batch_alter_table('data_set', schema=None) as batch_op:
        batch_op.drop_column('data_source')
        batch_op.drop_column('number_of_teams')
        batch_op.drop_column('season')
        batch_op.drop_column('country')
        batch_op.drop_column('competition')
        batch_op.drop_column('dataset_type')
