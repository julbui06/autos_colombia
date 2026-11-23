CREATE TABLE IF NOT EXISTS cuenta_sistema (
    id_cuenta SERIAL PRIMARY KEY,
    nombre_completo VARCHAR(100) NOT NULL,
    correo VARCHAR(100) UNIQUE NOT NULL,
    password VARCHAR(100) NOT NULL,
    rol VARCHAR(20) NOT NULL CHECK (rol IN ('ADMINISTRADOR', 'OPERADOR')),
    estado VARCHAR(20) NOT NULL DEFAULT 'ACTIVO'
);

CREATE TABLE IF NOT EXISTS usuario (
    id_usuario SERIAL PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL,
    documento VARCHAR(20) UNIQUE NOT NULL,
    telefono VARCHAR(20)
);

CREATE TABLE IF NOT EXISTS vehiculo (
    placa VARCHAR(10) PRIMARY KEY,
    id_usuario INTEGER NOT NULL,
    tipo_vehiculo VARCHAR(20) NOT NULL,
    estado_mensualidad VARCHAR(20) NOT NULL DEFAULT 'INACTIVO',
    fecha_inicio_mensualidad DATE,
    fecha_fin_mensualidad DATE,
    CONSTRAINT fk_vehiculo_usuario FOREIGN KEY (id_usuario)
        REFERENCES usuario(id_usuario) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS celda (
    id_celda SERIAL PRIMARY KEY,
    numero_celda VARCHAR(10) UNIQUE NOT NULL,
    tipo_vehiculo VARCHAR(20) NOT NULL,
    estado VARCHAR(20) NOT NULL DEFAULT 'DISPONIBLE'
);

CREATE TABLE IF NOT EXISTS registro_acceso (
    id_registro SERIAL PRIMARY KEY,
    placa VARCHAR(10) NOT NULL,
    id_celda INTEGER NOT NULL,
    fecha_hora_ingreso TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    fecha_hora_salida TIMESTAMP,
    estado_registro VARCHAR(20) NOT NULL DEFAULT 'EN_PARQUEADERO',
    CONSTRAINT fk_registro_vehiculo FOREIGN KEY (placa)
        REFERENCES vehiculo(placa) ON DELETE CASCADE,
    CONSTRAINT fk_registro_celda FOREIGN KEY (id_celda)
        REFERENCES celda(id_celda)
);

CREATE TABLE IF NOT EXISTS pago (
    id_pago SERIAL PRIMARY KEY,
    numero_recibo VARCHAR(20) UNIQUE NOT NULL,
    placa VARCHAR(10) NOT NULL,
    monto NUMERIC(10, 2) NOT NULL CHECK (monto > 0),
    metodo_pago VARCHAR(30) NOT NULL,
    fecha_pago TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    periodo_inicio DATE NOT NULL,
    periodo_fin DATE NOT NULL,
    estado_pago VARCHAR(20) DEFAULT 'PAGADO',
    CONSTRAINT fk_pago_vehiculo FOREIGN KEY (placa)
        REFERENCES vehiculo(placa) ON DELETE CASCADE
);

INSERT INTO cuenta_sistema (nombre_completo, correo, password, rol)
VALUES 
    ('Maria Garcia', 'admin@autoscolombia.com', 'admin123', 'ADMINISTRADOR'),
    ('Carlos Operador', 'operador@autoscolombia.com', 'oper123', 'OPERADOR')
ON CONFLICT (correo) DO NOTHING;

INSERT INTO celda (numero_celda, tipo_vehiculo, estado)
VALUES 
    ('C-101', 'CARRO', 'DISPONIBLE'),
    ('C-102', 'CARRO', 'DISPONIBLE'),
    ('M-201', 'MOTO', 'DISPONIBLE'),
    ('M-202', 'MOTO', 'DISPONIBLE')
ON CONFLICT (numero_celda) DO NOTHING;

INSERT INTO usuario (nombre, documento, telefono)
VALUES 
    ('Carlos Rodriguez', '1023456789', '3001234567'),
    ('Andres Lopez', '1098765432', '3109876543')
ON CONFLICT (documento) DO NOTHING;

INSERT INTO vehiculo (placa, id_usuario, tipo_vehiculo, estado_mensualidad, fecha_inicio_mensualidad, fecha_fin_mensualidad)
VALUES 
    ('ABC-999', (SELECT id_usuario FROM usuario WHERE documento = '1023456789'), 'CARRO', 'INACTIVO', CURRENT_DATE, CURRENT_DATE),
    ('JKL-78F', (SELECT id_usuario FROM usuario WHERE documento = '1098765432'), 'MOTO', 'ACTIVO', CURRENT_DATE, CURRENT_DATE + INTERVAL '30 days')
ON CONFLICT (placa) DO NOTHING;