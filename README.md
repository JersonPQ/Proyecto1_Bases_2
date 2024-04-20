# Proyecto 1 Bases 2

## Integrantes 
* Darío Espinoza
* Marbel Brenes
* Jerson Prendas
* Anthony Guevara

## Instrucciones para ejecutar el programa

### 1. Inicializar el servidor

Para levantar el servidor y que se realicen las conexiones a las bases de datos utilizadas (MongDB, PostgreSQL, Redis) se ejecuta el comando:

```
docker-compose up
```

Con esto se levanta un Docker container y el servidor puede recibir peticiones en el puerto 5000.

### 2. Endpoints

Se va a explicar la funcionabilidad de cada endpoint, argumentos y restricciones que poseen cada uno de ellos.

#### Endpoint de Autenticación
1. **[POST] /auth/register**

    Este endpoint registra un usuario en la base de datos, se necesitan 3 datos para poder ingresar (name, password, userRol).
    * **name:** Nombre de usuario - String.
    * **password:** Contraseña del usuario - String.
    * **userRol:** Define que rol tiene el usuario y que permisos tiene [0: usuario nomral, 1: usuario administrador, 2: usuario creado de encuestas] - int.

    * Ejemplo de peticion
    ```
    [POST] http://127.0.0.1:5000/auth/register
    ```

    * Formato de entrada de información (Ejemplo)
    ```
    {
      "name" : "Dario",
      "password" : "myPassword",
      "userRol" : 0  
    }
    ```
2. **[POST] /auth/login**

    Este endpoint incia sesión en el servidor y genera un Token que srive como llave para próximas funcionalidades.El token se guarda como una cookie. Se necesitan 2 datos para poder iniciar sesión (name, password)
    * **name:** Nombre de usuario - String.

    * **password:** Contraseña del usuario - String.

    * Ejemplo de peticion

    ```
    [POST] http://127.0.0.1:5000/auth/login
    ```

    * Formato de entrada de información (Ejemplo)

    ```
    {
      "name" : "Dario",
      "password" : "myPassword",
    }
    ```
3. **[GET] /auth/logout**

    Este endpoint cierra la sesión del usuario. Tiene como restricción que se necesita que el token exista y sea válido, de cualquier tipo de usuario para cerrar sesión. en caso contrario lanza un mensaje de error.

    * Ejemplo de peticion

    ```
    [GET] http://127.0.0.1:5000/auth/logout
    ```
#### Endpoint de Usuarios
1. **[GET] /users**

    Genera una lista con la información de todos los usuarios que estan registrados en la base de datos. **Se necesita permiso de administrador para utiliza esta funcionalidad.**

    * Ejemplo de peticion

    ```
    [GET] http://127.0.0.1:5000/users
    ```

2. **[GET] /users/{id}**

    Obtiene los datos de un usuario en específico. Se requiere pasar por la ruta el parametro **id**.

    * **id:** Este es el id que esta asignado a los usuarios en la base de datos, es el identificador único - INT.

    * Ejemplo de peticion

    ```
    [GET] http://127.0.0.1:5000/users/1
    ```

3. **[PUT] /users/{id}**

4. **[DELETE] /users/{id}**

    Elimina permanentemente un usuario de la base de datos. Se requiere pasar por la ruta el parametro **id**. **Se necesita permiso de administrador para utiliza esta funcionalidad.**

    * **id:** Este es el id que esta asignado a los usuarios en la base de datos, es el identificador único - INT.

    * Ejemplo de peticion

    ```
    [DELETE] http://127.0.0.1:5000/users/1
    ```
#### Endpoint de Encuestas

1. **[POST] /surveys**

2. **[GET] /surveys**

    Genera una lista con la información de todas las encuestas que se encuentran publicas en es respectivo momento.

    * Ejemplo de peticion

    ```
    [GET] http://127.0.0.1:5000/surveys
    ```
3. **[GET] /surveys/{id}**

    Muestra la información de encuesta en especifico, sin importar si esta pública o no. Se requiere pasar por la ruta el parametro **id**.

    * **id:** Este es el id que esta asignado a las encuestas en la base de datos - STRING.

    * Ejemplo de peticion

    ```
    [GET] http://127.0.0.1:5000/surveys/dfvsdcsdcs475SvEvfdv4
    ```
4. **[PUT] /surveys/{id}**

5. **[DELETE] /surveys/{id}**

    Elimina permanentemente una encuesta de la base de datos. Se requiere pasar por la ruta el párameto **id**. **Se necesita token de autorización de administrado o del creador de la encuesta.**

    * **id**: Este es el id que esta asignado a las encuestas en la base de datos - STRING.

    * Ejemplo de peticion

    ```
    [DELETE] http://127.0.0.1:5000/surveys/dfvsdcsdcs475SvEvfdv4
    ```

6. **[POST] /surveys/{id}/publish**

    Le cambia el estado de publicado a la encuesta en la base de datos. Se requiere pasar por la ruta el párameto **id**. **Se necesita token de autorización de administrado o del creador de la encuesta.**

    * **id**: Este es el id que esta asignado a las encuestas en la base de datos - STRING.

    * Ejemplo de peticion

    ```
    [POST] http://127.0.0.1:5000/surveys/dfvsdcsdcs475SvEvfdv4/publish
    ```

#### Endpoint de Preguntas de Encuestas

1. **[POST] /surveys/{id}/questions**

2. **[GET] /surveys/{id}/questions**

    Muestra en una lista las preguntas de una encuesta específica. Se requiere pasar por la ruta el párameto **id**. **Se necesita token de autorización de administrado o del creador de la encuesta.**

    * **id**: Este es el id que esta asignado a las encuestas en la base de datos - STRING.  

    * Ejemplo de peticion

    ```
    [GET] http://127.0.0.1:5000/surveys/dfvsdcsdcs475SvEvfdv4/questions
    ```  
3. **[PUT] /surveys/{id}/questions/{questionId}**

4. **[DELETE] /surveys/{id}/questions/{questionId}**

    Elimina permanentemente de la base de datos una pregunta específica de una encuesta en específico. Se requiere pasar por la ruta los párametros **id** y **questionId**. **Se necesita token de autorización de administrado o del creador de la encuesta.** 

    * **id**: Este es el id que esta asignado a las encuestas en la base de datos - STRING.  

    * **questionId**: Este es el id que esta adignado a cada pregunta de una encuesta en la base de datos - STRING.

    * Ejemplo de petición

    ```
    [DELETE] http://127.0.0.1:5000/surveys/dfvsdcsdcs475SvEvfdv4/questions/dfvcsdxa428csW5SvEvfdv4
    ```    

#### Endpoint de Respuestas de Encuestas
1. **[POST] /surveys/{id}/responses**

2. **[GET] /surveys/{id}/responses**

    Muestra en una lista todas las respuestas de una encuesta en específico. Se requiere pasar por la ruta los párametros **id**. **Se necesita token de autorización de administrado o del creador de la encuesta.** 

    * **id**: Este es el id que esta asignado a las encuestas en la base de datos - STRING.  

    * Ejemplo de petición

    ```
    [GET] http://127.0.0.1:5000/surveys/dfvsdcsdcs475SvEvfdv4/responses
    ```   
#### Endpoint de Encuestados
1. **[POST] /respondents**

2. **[GET] /respondents**

    Muestra por una lista todos los encuestados de la base de datos. **Se necesita token de autorización de administrado.** 

    * Ejemplo de petición

    ```
    [GET] http://127.0.0.1:5000/respondents
    ```    
3. **[GET] /respondents/{id}**

    Muestra la información de un encuestado en específico. Se requiere pasar por la ruta el parametro **id**. **Se necesita token de autorización de administrado.**

    * **id:** Este es el id que esta asignado a los encuestados en la base de datos, es el identificador único - INT.

    * Ejemplo de petición
    ```
    [GET] http://127.0.0.1:5000/respondents/1
    ``` 

4. **[PUT] /respondents/{id}**

5. **[DELETE] /respondents/{id}**

    Eliminar permanentemente la información de un usuario en específico. Se requiere pasar por la ruta el parametro **id**. **Se necesita token de autorización de administrado.**

    * **id:** Este es el id que esta asignado a los encuestados en la base de datos, es el identificador único - INT.

    * Ejemplo de petición
    ```
    [DELETE] http://127.0.0.1:5000/respondents/1
    ``` 

#### Endpoint de Resporte y Análisis
1. **[GET] /surveys/{id}/analysis**

    Genera un reporte de una encuesta en específico, muestra toda la información de las respuestas de esa encuesta. Se requiere pasar por la ruta el parametro **id**. **Se necesita token de autorización de administrado o del creador de la encuesta.** 

    * **id**: Este es el id que esta asignado a las encuestas en la base de datos - STRING.

    * Ejemplo de petición
    ```
    [GET] http://127.0.0.1:5000/surveys/dfvsdcsdcs475SvEvfdv4/analysis
    ``` 