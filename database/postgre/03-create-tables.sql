\c encuesta;


CREATE TABLE surveys (
    id SERIAL PRIMARY KEY,
    titulo VARCHAR(255) NOT NULL,
    descripcion TEXT,
    publicada BOOLEAN NOT NULL,
    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE responses (
    id SERIAL PRIMARY KEY,
    survey_id INT REFERENCES surveys(id),
    user_id VARCHAR(50),
    respuestas JSONB,
    fecha_respuesta TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE trends (
    id SERIAL PRIMARY KEY,
    survey_id INT REFERENCES surveys(id),
    tendencia TEXT,
    score FLOAT,
    fecha TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);


 --DATOS DE PRUEBA PARA EL DASHBOARD, DEBEN DE VENIR DE SPARK LOS VERDAEROS.
INSERT INTO surveys (titulo, descripcion, publicada)
VALUES 
('Encuesta de Satisfacción', 'Encuesta para medir la satisfacción del cliente', TRUE),
('Encuesta de Preferencia de Producto', 'Esta encuesta mide la preferencia de un producto', TRUE),
('Encuesta de Calidad del Servicio', 'Encuesta para evaluar la calidad del servicio', TRUE),
('Encuesta de Uso de Redes Sociales', 'Encuesta sobre el uso de redes sociales', TRUE),
('Encuesta de Hábitos Alimenticios', 'Encuesta para conocer los hábitos alimenticios', TRUE);


INSERT INTO responses (survey_id, user_id, respuestas)
VALUES 
(1, 'user_1', '{"q1": "Muy satisfecho", "q2": "Sí"}'),
(1, 'user_2', '{"q1": "Satisfecho", "q2": "Sí"}'),
(2, 'user_3', '{"q1": "Producto A", "q2": "Producto B"}'),
(2, 'user_4', '{"q1": "Producto B", "q2": "Producto C"}'),
(3, 'user_6', '{"q1": "Bueno", "q2": "Bueno"}'),
(4, 'user_7', '{"q1": "Facebook", "q2": "Instagram"}'),
(4, 'user_8', '{"q1": "Twitter", "q2": "LinkedIn"}'),
(4, 'user_9', '{"q1": "Snapchat", "q2": "Twitter"}'),
(5, 'user_10', '{"q1": "Frutas", "q2": "Verduras"}'),
(2, 'user_11', '{"q1": "Producto A", "q2": "Sí"}'),
(2, 'user_12', '{"q1": "Muy satisfecho", "q2": "Sí"}');


INSERT INTO trends (survey_id, tendencia, score)
VALUES 
(1, 'Satisfacción General', 4.5),
(2, 'Preferencia por el Producto A', 3.8),
(3, 'Calidad del Servicio', 4.2),
(4, 'Uso de Facebook', 4.7),
(5, 'Consumo de Frutas', 0);