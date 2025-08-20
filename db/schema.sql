-- Crear tabla de usuarios
CREATE TABLE IF NOT EXISTS usuarios (
    id SERIAL PRIMARY KEY,
    nombre TEXT NOT NULL,
    email TEXT UNIQUE NOT NULL,
    contraseña TEXT NOT NULL,
    rol TEXT NOT NULL CHECK (rol IN ('ciudadano', 'municipalidad', 'defensa'))
);

-- Crea la tabla reportes_ciudadanos si no existe
CREATE TABLE IF NOT EXISTS public.reportes_ciudadanos (
    id SERIAL PRIMARY KEY,
    titulo VARCHAR(200) NOT NULL,
    descripcion TEXT,
    ubicacion VARCHAR(300),
    estado VARCHAR(50) DEFAULT 'Pendiente',
    fecha TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    imagen TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    tipo VARCHAR(50),
    urgencia VARCHAR(20) DEFAULT 'baja',
    contacto VARCHAR(50)
);

-- Crea la tabla informes de la defensa si no existe
CREATE TABLE IF NOT EXISTS informes_defensa_civil (
    id SERIAL PRIMARY KEY,
    titulo VARCHAR(200) NOT NULL,
    descripcion TEXT,
    ubicacion VARCHAR(300),
    fecha TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    creado_por VARCHAR(100)
);
