# HNG Stage 2 Task - Backend Track

This is a simple API that allows users to register, login, create organisations and add users to organisations.

### Endpoints

-   `[POST] /auth/register`
    ```json
    {
    	"firstName": "string",
    	"lastName": "string",
    	"email": "string",
    	"password": "string",
    	"phone": "string"
    }
    ```
-   `[POST] /auth/login`
    ```json
    {
    	"email": "string",
    	"password": "string"
    }
    ```
-   `[GET] /api/users/:id [PROTECTED]`
-   `[GET] /api/organisations [PROTECTED]`
-   `[GET] /api/organisations/:orgId [PROTECTED]`
-   `[POST] /api/organisations [PROTECTED]`
    ```json
    {
    	"name": "string",
    	"description": "string"
    }
    ```
-   `[POST] /api/organisations/:orgId/users [PROTECTED]`
    ```json
    {
    	"userId": "string"
    }
    ```

### How to run

-   Clone the repository
-   Run the `setup.sh` script to install dependencies
-   Run the `run.sh` script to start the server
