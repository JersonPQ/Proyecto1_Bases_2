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

