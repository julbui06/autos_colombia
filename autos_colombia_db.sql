-- Eliminar tablas existentes para reconstruir el esquema limpio
DROP TABLE IF EXISTS Registro_Acceso CASCADE;
DROP TABLE IF EXISTS Vehiculo CASCADE;
DROP TABLE IF EXISTS Celda CASCADE;
DROP TABLE IF EXISTS Usuario CASCADE;

-- 1. Tabla Usuario
CREATE TABLE Usuario (
    id_usuario SERIAL PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL,
    documento VARCHAR(20) UNIQUE NOT NULL,
    telefono VARCHAR(20)
);

-- 2. Tabla Vehiculo (La mensualidad y fechas de vigencia pasan aquí)
CREATE TABLE Vehiculo (
    placa VARCHAR(10) PRIMARY KEY,
    id_usuario INT NOT NULL REFERENCES Usuario(id_usuario) ON DELETE CASCADE,
    tipo_vehiculo VARCHAR(20) NOT NULL CHECK (tipo_vehiculo IN ('CARRO', 'MOTO')),
    estado_mensualidad VARCHAR(20) NOT NULL DEFAULT 'INACTIVO' CHECK (estado_mensualidad IN ('ACTIVO', 'INACTIVO')),
    fecha_inicio_mensualidad DATE,
    fecha_fin_mensualidad DATE
);

-- 3. Tabla Celda (Con tipo de vehículo admitido)
CREATE TABLE Celda (
    id_celda SERIAL PRIMARY KEY,
    numero_celda VARCHAR(10) UNIQUE NOT NULL,
    tipo_vehiculo VARCHAR(20) NOT NULL CHECK (tipo_vehiculo IN ('CARRO', 'MOTO')),
    estado VARCHAR(20) NOT NULL DEFAULT 'DISPONIBLE' CHECK (estado IN ('DISPONIBLE', 'OCUPADA'))
);

-- 4. Tabla Registro_Acceso
CREATE TABLE Registro_Acceso (
    id_registro SERIAL PRIMARY KEY,
    placa VARCHAR(10) NOT NULL REFERENCES Vehiculo(placa),
    id_celda INT NOT NULL REFERENCES Celda(id_celda),
    fecha_hora_ingreso TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    fecha_hora_salida TIMESTAMP,
    estado_registro VARCHAR(20) NOT NULL DEFAULT 'EN_PARQUEADERO' CHECK (estado_registro IN ('EN_PARQUEADERO', 'FINALIZADO'))
);

-- Insertar datos de prueba iniciales
INSERT INTO Usuario (nombre, documento, telefono) VALUES 
('Juliana Perez', '1035123456', '3001234567'),
('Carlos Gomez', '1017987654', '3119876543');

INSERT INTO Vehiculo (placa, id_usuario, tipo_vehiculo, estado_mensualidad, fecha_inicio_mensualidad, fecha_fin_mensualidad) VALUES 
('KKL890', 1, 'CARRO', 'ACTIVO', '2026-11-01', '2026-11-30'),
('XYZ123', 2, 'MOTO', 'INACTIVO', '2026-10-01', '2026-10-31');

INSERT INTO Celda (numero_celda, tipo_vehiculo, estado) VALUES 
('C-101', 'CARRO', 'DISPONIBLE'),
('C-102', 'CARRO', 'DISPONIBLE'),
('M-201', 'MOTO', 'DISPONIBLE');