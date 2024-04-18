\c encuesta;

-- Crear la tabla de encuestados
CREATE TABLE respondents (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL
);