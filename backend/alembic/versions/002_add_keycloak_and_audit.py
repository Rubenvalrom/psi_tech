"""Add missing tables and columns for Keycloak, semantic search, and audit trail

Revision ID: 002
Revises: 001
Create Date: 2026-02-20 01:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '002'
down_revision = '001'
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Add missing tables and columns for Keycloak integration, semantic search, and audit trail."""
    
    # Enable pgvector extension
    op.execute("CREATE EXTENSION IF NOT EXISTS vector")
    
    # Add keycloak_id to users table
    op.add_column('users', sa.Column('keycloak_id', sa.String(length=255), nullable=True))
    op.create_index(op.f('ix_users_keycloak_id'), 'users', ['keycloak_id'], unique=True)
    
    # Add signature and semantic search columns to documentos
    op.add_column('documentos', sa.Column('hash_firma', sa.String(length=255), nullable=True))
    op.add_column('documentos', sa.Column('firmado_por', sa.String(length=255), nullable=True))
    op.add_column('documentos', sa.Column('fecha_firma', sa.DateTime(), nullable=True))
    op.add_column('documentos', sa.Column('embedding', sa.dialects.postgresql.VECTOR(4096), nullable=True))
    
    # Create trazabilidad (audit trail) table
    op.create_table(
        'trazabilidad',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('expediente_id', sa.Integer(), nullable=False),
        sa.Column('usuario_id', sa.Integer(), nullable=True),
        sa.Column('accion', sa.String(length=255), nullable=False),
        sa.Column('descripcion', sa.Text(), nullable=True),
        sa.Column('datos_anteriores', sa.JSON(), nullable=True),
        sa.Column('datos_nuevos', sa.JSON(), nullable=True),
        sa.Column('timestamp', sa.DateTime(), server_default=sa.func.now(), nullable=True),
        sa.ForeignKeyConstraint(['expediente_id'], ['expedientes.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['usuario_id'], ['users.id'], ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_trazabilidad_expediente_id'), 'trazabilidad', ['expediente_id'], unique=False)
    op.create_index(op.f('ix_trazabilidad_usuario_id'), 'trazabilidad', ['usuario_id'], unique=False)
    op.create_index(op.f('ix_trazabilidad_timestamp'), 'trazabilidad', ['timestamp'], unique=False)
    
    # Increase metadatos_extraidos column size from String(2000) to Text
    op.alter_column('documentos', 'metadatos_extraidos',
                    existing_type=sa.String(length=2000),
                    type_=sa.Text(),
                    existing_nullable=True)


def downgrade() -> None:
    """Remove additions from upgrade."""
    
    # Drop trazabilidad table
    op.drop_index(op.f('ix_trazabilidad_timestamp'), table_name='trazabilidad')
    op.drop_index(op.f('ix_trazabilidad_usuario_id'), table_name='trazabilidad')
    op.drop_index(op.f('ix_trazabilidad_expediente_id'), table_name='trazabilidad')
    op.drop_table('trazabilidad')
    
    # Revert metadatos_extraidos column size
    op.alter_column('documentos', 'metadatos_extraidos',
                    existing_type=sa.Text(),
                    type_=sa.String(length=2000),
                    existing_nullable=True)
    
    # Drop columns from documentos
    op.drop_column('documentos', 'embedding')
    op.drop_column('documentos', 'fecha_firma')
    op.drop_column('documentos', 'firmado_por')
    op.drop_column('documentos', 'hash_firma')
    
    # Drop keycloak_id from users
    op.drop_index(op.f('ix_users_keycloak_id'), table_name='users')
    op.drop_column('users', 'keycloak_id')
    
    # Drop pgvector extension
    op.execute("DROP EXTENSION IF EXISTS vector")
