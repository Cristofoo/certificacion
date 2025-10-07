-- Script mínimo para crear tablas usadas por la app
CREATE DATABASE IF NOT EXISTS certificacion;
USE certificacion;

CREATE TABLE IF NOT EXISTS users (
	id INT AUTO_INCREMENT PRIMARY KEY,
	nombre VARCHAR(100) NOT NULL,
	apellido VARCHAR(100) NOT NULL,
	email VARCHAR(255) NOT NULL UNIQUE,
	password VARCHAR(255) NOT NULL,
	created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
-- Nueva tabla para tutores (separada de users)
CREATE TABLE IF NOT EXISTS tutors (
	id INT AUTO_INCREMENT PRIMARY KEY,
	nombre VARCHAR(100) NOT NULL,
	apellido VARCHAR(100),
	email VARCHAR(255) NOT NULL UNIQUE,
	created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS asesorias (
	id INT AUTO_INCREMENT PRIMARY KEY,
	tema VARCHAR(255) NOT NULL,
	fecha DATE NOT NULL,
	duracion INT NOT NULL,
	notas VARCHAR(50),
	usuario_id INT NOT NULL,
	tutor_id INT,
	created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
	FOREIGN KEY (usuario_id) REFERENCES users(id) ON DELETE CASCADE,
	FOREIGN KEY (tutor_id) REFERENCES tutors(id) ON DELETE SET NULL
);

-- Índices para búsquedas frecuentes
-- Crear índice solo si no existe (compatible con MySQL antiguo)
DELIMITER $$
DROP PROCEDURE IF EXISTS maybe_create_idx$$
CREATE PROCEDURE maybe_create_idx()
BEGIN
	IF (SELECT COUNT(*) FROM INFORMATION_SCHEMA.STATISTICS WHERE TABLE_SCHEMA=DATABASE() AND TABLE_NAME='asesorias' AND INDEX_NAME='idx_asesorias_fecha') = 0 THEN
		CREATE INDEX idx_asesorias_fecha ON asesorias(fecha);
	END IF;
END$$
CALL maybe_create_idx()$$
DROP PROCEDURE maybe_create_idx$$
DELIMITER ;

-- Datos de prueba: usuarios y tutores con contraseña por defecto 'password123' (hashes scrypt)
INSERT IGNORE INTO users (id, nombre, apellido, email, password) VALUES
	(1, 'Alicia', 'Perez', 'alicia@example.com', 'scrypt:32768:8:1$omvTpbkcrK6g67Ef$61bd4b229feca9bebb246b0a466a948cfbc0eb94d906bafe2168b3d0a98116172aa2da77513d524863e4dcd62a1c385bc3c144608aaac40e37ba1d08b40c32c3'),
	(2, 'Juan', 'Gomez', 'juan@example.com', 'scrypt:32768:8:1$54shApgD3TMreCyu$eb82ca2ad3857a6e7140190f22df6f88885d555a452ae8c72c49e806bb264e8ee2144281ac8819f9eea88faa9c3ebc30e7d867ee4d6eb085dcf9e92b7786494b'),
	(3, 'Liza', 'Molina', 'liza.molina@example.com', 'scrypt:32768:8:1$ff98bACRlGeA9b1W$0abc911fa70fad8c71d3d034b21c18400147486680d37b9871f02c78765a1c732821c4cf095b290155633b050211ce7cfbc7bcdd4799960645a5aecb0454d1cf'),
	(4, 'Bastian', 'Chavez', 'bastian.chavez@example.com', 'scrypt:32768:8:1$D3V2qeD3iMXWYRpP$7891297b200577e7171ea9e8f6924a5a91c4fb0dd2a7e2aef52336ccc0d0fe24c55cc62af8e928d326a37555f6f033e318a96b9d9b3e5c1b9455dc29f19062df'),
	(5, 'Fernando', 'Ojeada', 'fernando.ojeada@example.com', 'scrypt:32768:8:1$rGOwWUl5qlga5EZF$40b05753d2f77661ae58dee9cb8fa598e2d001ac0fadf7ecc032f4f90abd45f353cf0338ccf524b98d8af9886ad68aa829e56021c3da7203ad241eb6c7abc958'),
	(6, 'Carlos', 'Toro', 'carlos.toro@example.com', 'scrypt:32768:8:1$JaR7sq1L0fvrP5XN$4d316c2533c9fceda6865b5f6b7fa142946f56717e269fffc531b5cd961ad1ada468d367a5ecf61e1998e64eae49877e66cfdff9fd11e63dc9fa52bb2616c984'),
	(7, 'Medico', '', 'medico@example.com', 'scrypt:32768:8:1$CzLUN2EQ6jI5JhTt$bdeaa9d1ff4f6235ae1b5e8f80b4d256bbeb3a174e3793b377462d5044c489cf1fa03d9d1ff94cc0af1a0f9af97d42cd580758c63d7fb91f854d47a4047c8286'),
	(8, 'Electrisista', 'Juanitos', 'electrisista.juanitos@example.com', 'scrypt:32768:8:1$MHju1oRXVXWk2bJF$3acde431320ed5c4f532f4990c1e2da3c6becd960b2b8da7143aa3b4c85874b350251435f93d3ac0eac710b32469e1254f91b6f87ad7eeef148181ed43e1875c'),
	(9, 'Pablo', 'Cesar', 'pablo.cesar@example.com', 'scrypt:32768:8:1$YgN4nBVVjEII7Nia$c1887e6057ee6448b394381285a3936e5b6bda563d0b07d5b2d8a8150143a214872b9177925d7d9cb52c21d5057af0eaa14f2a9a0d1f0a6c9c395d01def0c928');

-- Insertar los tutores solicitados en la tabla tutors
INSERT IGNORE INTO tutors (id, nombre, apellido, email) VALUES
	(1, 'Liza', 'Molina', 'liza.molina@example.com'),
	(2, 'Bastian', 'Chavez', 'bastian.chavez@example.com'),
	(3, 'Fernando', 'Ojeada', 'fernando.ojeada@example.com'),
	(4, 'Carlos', 'Toro', 'carlos.toro@example.com'),
	(5, 'Medico', '', 'medico@example.com'),
	(6, 'Electrisista', 'Juanitos', 'electrisista.juanitos@example.com'),
	(7, 'Pablo', 'Cesar', 'pablo.cesar@example.com');

-- Asesorías de prueba: una pasada y una futura
INSERT IGNORE INTO asesorias (tema, fecha, duracion, notas, usuario_id, tutor_id) VALUES
	('Flask Básico', DATE_SUB(CURDATE(), INTERVAL 10 DAY), 3, 'Repaso de conceptos', 1, 2),
	('Spring Data', DATE_ADD(CURDATE(), INTERVAL 10 DAY), 6, 'Práctica avanzada', 2, 1);

