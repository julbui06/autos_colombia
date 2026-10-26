-- 1. Tabla Usuario
CREATE TABLE Usuario (
    id_usuario SERIAL PRIMARY KEY,
    documento VARCHAR(20) NOT NULL UNIQUE,
    nombre VARCHAR(100) NOT NULL,
    telefono VARCHAR(15),
    estado_mensualidad VARCHAR(10) CHECK (estado_mensualidad IN ('ACTIVO', 'INACTIVO')) DEFAULT 'ACTIVO'
);

-- 2. Tabla Vehiculo
CREATE TABLE Vehiculo (
    placa VARCHAR(10) PRIMARY KEY,
    marca VARCHAR(50),
    modelo VARCHAR(50),
    id_usuario INT NOT NULL REFERENCES Usuario(id_usuario) ON DELETE CASCADE
);

-- 3. Tabla Celda
CREATE TABLE Celda (
    id_celda SERIAL PRIMARY KEY,
    numero_celda VARCHAR(10) NOT NULL UNIQUE,
    estado VARCHAR(15) CHECK (estado IN ('DISPONIBLE', 'OCUPADA', 'MANTENIMIENTO')) DEFAULT 'DISPONIBLE'
);

-- 4. Tabla Registro_Acceso
CREATE TABLE Registro_Acceso (
    id_registro SERIAL PRIMARY KEY,
    placa VARCHAR(10) NOT NULL REFERENCES Vehiculo(placa),
    id_celda INT NOT NULL REFERENCES Celda(id_celda),
    fecha_hora_ingreso TIMESTAMP NOT NULL,
    fecha_hora_salida TIMESTAMP NULL,
    estado_registro VARCHAR(15) CHECK (estado_registro IN ('EN_PARQUEADERO', 'FINALIZADO')) DEFAULT 'EN_PARQUEADERO'
);

-- DATOS DE PRUEBA
INSERT INTO Usuario (documento, nombre, telefono, estado_mensualidad) 
VALUES ('12345678', 'Carlos Pérez', '3001234567', 'ACTIVO');

INSERT INTO Vehiculo (placa, marca, modelo, id_usuario) 
VALUES ('KKL890', 'Toyota', '2022', 1);

INSERT INTO Celda (numero_celda, estado) 
VALUES ('C-01', 'DISPONIBLE'), ('C-02', 'DISPONIBLE');