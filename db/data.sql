-- Insertar usuarios de ejemplo
INSERT INTO usuarios (nombre, email, contraseña, rol)
VALUES 
('Lucía Gómez', 'martin@email.com', '1234', 'ciudadano'),
('Municipalidad Monteros', 'muni@monteros.gob', 'admin123', 'municipalidad'),
('Defensa Civil', 'defensa@monteros.gob', 'admin456', 'defensa');

-- Insertar reportes de ejemplo
INSERT INTO reportes (titulo, descripcion, nivel_urgencia, id_usuario)
VALUES 
('Basura acumulada', 'Hay basura en la esquina de San Martín y Belgrano hace 3 días.', 'medio', 1),
('Derrumbe parcial', 'Una pared se ha caído por las lluvias, puede haber heridos.', 'crítico', 1);

-- Insertar acciones de ejemplo
INSERT INTO acciones (id_reporte, id_usuario, descripcion)
VALUES 
(1, 2, 'Cuadrilla asignada para recolección'),
(2, 3, 'Emergencia atendida, se cerró el área afectada');
