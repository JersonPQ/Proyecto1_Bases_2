CREATE DATABASE encuesta;

\c encuesta;

-- esta tabla es de ejemplo para ver si conecta a la base de datos
-- si necesitan modificarla, pueden hacerlo
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    name VARCHAR(200) NOT NULL,
    password VARCHAR(200) NOT NULL,
    userRol INT NOT NULL --0: USUARIO NORMAL | 1: ADMINISTRADOS | 2:CREADOR DE ENCUESTA
);