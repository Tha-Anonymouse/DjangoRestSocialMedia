# Social Network API

This project is a social networking application built with Django Rest Framework.

## Features

- User Registration
- User Login
- Send Friend Requests
- Accept/Reject Friend Requests
- List Friends
- List Pending Friend Requests

## Prerequisites

Ensure you have the following software installed on your system:

- Docker: [Install Docker](https://docs.docker.com/get-docker/)
- Docker Compose: [Install Docker Compose](https://docs.docker.com/compose/install/)

## Installation

Follow these steps to set up the project:

### 1. Clone the Repository

```bash
git clone https://github.com/your-username/social-network-api.git
cd social-network-api
```

### 2. Set Up Environment Variables
Create a .env file in the root directory of the project and add the necessary environment variables. Below is an example:
```
POSTGRES_DB=<<db_name>>
POSTGRES_USER=<<db_username>>
POSTGRES_PASSWORD=<<db_password>>
DB_HOST=db
DB_PORT=5432
```

### 3. Build the Docker Containers
Build the Docker images using Docker Compose:
```bash
docker-compose build
```

### 4. Run the Docker Containers
Start the containers using Docker Compose:

```bash
docker-compose up
```

### 5. Accessing the APIs
#### Base URL
 The base URL for accessing the APIs is: http://localhost:8000/api/

#### Endpoints

##### User Registration
* URL: /api/register/
* Method: POST
* Body: (raw JSON)
```json
{
  "username": "username",
  "email": "user email",
  "password": "password"
}
```
##### User Login
* URL: /api/login/
* Method: POST
* Body: (raw JSON)
```json
{
  "email": "user1@example.com",
  "password": "password123"
}
```
##### Search Users by Email or Name
* URL: /api/users/search/
* Method: GET
* Headers: Authorization: Token your_token
* Query Parameters: search: The search keyword to match email or part of the name.

##### Send Friend Request
* URL: /api/friend-requests/send/{username}/
* Method: POST
* Headers: Authorization: Token your_token
#### Respond to Friend Request
* URL: /api/friend-requests/respond/
* Method: POST
* Headers: Authorization: Token your_token
* Body: (raw JSON)
```json
{
  "username": "username",
  "response": "accept"  // or "reject"
}
```
##### List Friends
* URL: /api/friends/
* Method: GET
* Headers: Authorization: Token your_token
#### List Pending Friend Requests
* URL: /api/friend-requests/pending/
* Method: GET
* Headers: Authorization: Token your_token

## Postman Collection
To facilitate testing and evaluation of the API endpoints, a Postman collection is provided.

### Importing the Postman Collection
* Download the Postman collection file: postman_collection.json
* Open Postman.
* Click on the Import button in the top-left corner. (File->Import) or Ctrl + O
* Select the downloaded JSON file and import it.
* The collection named "Social Network API" should now be available in your Postman application, containing all the endpoints configured with the necessary request details.
* Note that due to issue with Postman, the imported request URLs tend to have their trailing slashes silently removed, which may need to be added back, before requesting.
