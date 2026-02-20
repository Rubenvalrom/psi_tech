"""Initial schema: users, expedientes, documentos, pasos, presupuestos, facturas

Revision ID: 001
Revises: 
Create Date: 2026-02-20 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '001'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Create initial database schema."""
    # Create enum types
    op.execute("DROP TYPE IF EXISTS estado_expediente CASCADE")
    op.execute("CREATE TYPE estado_expediente AS ENUM ('ABIERTO', 'EN_PROCESO', 'CERRADO', 'ANULADO')")
    
    op.execute("DROP TYPE IF EXISTS tipo_documento CASCADE")
    op.execute("CREATE TYPE tipo_documento AS ENUM ('SOLICITUD', 'INFORME', 'RESOLUCIÓN', 'ADJUNTO', 'OTRO')")
    
    op.execute("DROP TYPE IF EXISTS estado_paso CASCADE")
    op.execute("CREATE TYPE estado_paso AS ENUM ('PENDIENTE', 'EN_PROGRESO', 'COMPLETADO', 'RECHAZADO')")
    
    op.execute("DROP TYPE IF EXISTS estado_factura CASCADE")
    op.execute("CREATE TYPE estado_factura AS ENUM ('PENDIENTE', 'PAGADA', 'ANULADA', 'RECHAZADA')")

    # Create users table
    op.create_table(
        'users',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('email', sa.String(length=255), nullable=False),
        sa.Column('username', sa.String(length=100), nullable=False),
        sa.Column('password_hash', sa.String(length=255), nullable=False),
        sa.Column('nombre_completo', sa.String(length=255), nullable=False),
        sa.Column('roles', sa.JSON(), nullable=False),
        sa.Column('activo', sa.Boolean(), nullable=False),
        sa.Column('created_at', sa.DateTime(), server_default=sa.func.now(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.func.now(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_users_activo'), 'users', ['activo'], unique=False)
    op.create_index(op.f('ix_users_email'), 'users', ['email'], unique=True)
    op.create_index(op.f('ix_users_username'), 'users', ['username'], unique=True)

    # Create expedientes table
    op.create_table(
        'expedientes',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('numero', sa.String(length=50), nullable=False),
        sa.Column('asunto', sa.Text(), nullable=False),
        sa.Column('descripcion', sa.Text(), nullable=True),
        sa.Column('estado', sa.Enum('ABIERTO', 'EN_PROCESO', 'CERRADO', 'ANULADO', name='estado_expediente'), nullable=False),
        sa.Column('responsable_id', sa.Integer(), nullable=True),
        sa.Column('fecha_creacion', sa.DateTime(), server_default=sa.func.now(), nullable=True),
        sa.Column('fecha_actualizacion', sa.DateTime(), server_default=sa.func.now(), nullable=True),
        sa.Column('fecha_cierre', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['responsable_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_expedientes_numero'), 'expedientes', ['numero'], unique=True)
    op.create_index(op.f('ix_expedientes_estado'), 'expedientes', ['estado'], unique=False)
    op.create_index(op.f('ix_expedientes_responsable_id'), 'expedientes', ['responsable_id'], unique=False)
    op.create_index(op.f('ix_expedientes_fecha_creacion'), 'expedientes', ['fecha_creacion'], unique=False)

    # Create documentos table
    op.create_table(
        'documentos',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('expediente_id', sa.Integer(), nullable=False),
        sa.Column('nombre', sa.String(length=255), nullable=False),
        sa.Column('contenido_blob', sa.LargeBinary(), nullable=True),
        sa.Column('tipo', sa.Enum('SOLICITUD', 'INFORME', 'RESOLUCIÓN', 'ADJUNTO', 'OTRO', name='tipo_documento'), nullable=False),
        sa.Column('ruta_archivo', sa.String(length=500), nullable=True),
        sa.Column('metadatos_extraidos', sa.String(length=2000), nullable=True),
        sa.Column('fecha_carga', sa.DateTime(), server_default=sa.func.now(), nullable=True),
        sa.ForeignKeyConstraint(['expediente_id'], ['expedientes.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_documentos_expediente_id'), 'documentos', ['expediente_id'], unique=False)
    op.create_index(op.f('ix_documentos_fecha_carga'), 'documentos', ['fecha_carga'], unique=False)

    # Create pasos_tramitacion table
    op.create_table(
        'pasos_tramitacion',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('expediente_id', sa.Integer(), nullable=False),
        sa.Column('numero_paso', sa.Integer(), nullable=False),
        sa.Column('titulo', sa.String(length=255), nullable=False),
        sa.Column('descripcion', sa.Text(), nullable=True),
        sa.Column('estado', sa.Enum('PENDIENTE', 'EN_PROGRESO', 'COMPLETADO', 'RECHAZADO', name='estado_paso'), nullable=False),
        sa.Column('datetime_inicio', sa.DateTime(), nullable=True),
        sa.Column('datetime_fin', sa.DateTime(), nullable=True),
        sa.Column('responsable_id', sa.Integer(), nullable=True),
        sa.Column('comentarios', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), server_default=sa.func.now(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.func.now(), nullable=True),
        sa.ForeignKeyConstraint(['expediente_id'], ['expedientes.id'], ),
        sa.ForeignKeyConstraint(['responsable_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_pasos_tramitacion_expediente_id'), 'pasos_tramitacion', ['expediente_id'], unique=False)
    op.create_index(op.f('ix_pasos_tramitacion_estado'), 'pasos_tramitacion', ['estado'], unique=False)

    # Create partidas_presupuestarias table
    op.create_table(
        'partidas_presupuestarias',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('codigo_contable', sa.String(length=50), nullable=False),
        sa.Column('descripcion', sa.String(length=500), nullable=False),
        sa.Column('presupuestado', sa.Numeric(precision=15, scale=2), nullable=False),
        sa.Column('comprometido', sa.Numeric(precision=15, scale=2), nullable=False),
        sa.Column('pagado', sa.Numeric(precision=15, scale=2), nullable=False),
        sa.Column('created_at', sa.DateTime(), server_default=sa.func.now(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.func.now(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_partidas_presupuestarias_codigo_contable'), 'partidas_presupuestarias', ['codigo_contable'], unique=True)

    # Create facturas table
    op.create_table(
        'facturas',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('numero', sa.String(length=50), nullable=False),
        sa.Column('proveedor', sa.String(length=255), nullable=False),
        sa.Column('monto', sa.Numeric(precision=15, scale=2), nullable=False),
        sa.Column('fecha_emision', sa.DateTime(), nullable=False),
        sa.Column('fecha_recepcion', sa.DateTime(), nullable=True),
        sa.Column('estado', sa.Enum('PENDIENTE', 'PAGADA', 'ANULADA', 'RECHAZADA', name='estado_factura'), nullable=False),
        sa.Column('expediente_id', sa.Integer(), nullable=True),
        sa.Column('partida_presupuestaria_id', sa.Integer(), nullable=True),
        sa.Column('contenido_xml', sa.String(length=5000), nullable=True),
        sa.Column('created_at', sa.DateTime(), server_default=sa.func.now(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.func.now(), nullable=True),
        sa.ForeignKeyConstraint(['expediente_id'], ['expedientes.id'], ),
        sa.ForeignKeyConstraint(['partida_presupuestaria_id'], ['partidas_presupuestarias.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_facturas_numero'), 'facturas', ['numero'], unique=True)
    op.create_index(op.f('ix_facturas_estado'), 'facturas', ['estado'], unique=False)
    op.create_index(op.f('ix_facturas_created_at'), 'facturas', ['created_at'], unique=False)


def downgrade() -> None:
    """Drop all tables and types."""
    # Drop tables
    op.drop_table('facturas')
    op.drop_table('partidas_presupuestarias')
    op.drop_table('pasos_tramitacion')
    op.drop_table('documentos')
    op.drop_table('expedientes')
    op.drop_table('users')

    # Drop enums
    op.execute("DROP TYPE IF EXISTS estado_factura CASCADE")
    op.execute("DROP TYPE IF EXISTS estado_paso CASCADE")
    op.execute("DROP TYPE IF EXISTS tipo_documento CASCADE")
    op.execute("DROP TYPE IF EXISTS estado_expediente CASCADE")
