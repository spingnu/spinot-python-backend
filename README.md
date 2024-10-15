# Spinot Backend

## Pre-requisites

Install dependencies using `pip` and npm.

```bash
pip install -r requirements.txt
```

```bash
npm install
```

## Deploy with Serverless

### Install Serverless
Install the Serverless framework globally.

```bash
npm install -g serverless
```

### Deploy the Application
Deploy the application using the Serverless framework.

```bash
serverless deploy
```

## Code Formatting

### Using `black`
Ensure consistent code formatting throughout the project using `black`.

```bash
black .
```

## Pre-commit Hooks

### Install Pre-commit Hooks
Set up pre-commit hooks to maintain code quality.

```bash
pre-commit install
```

### Run Pre-commit Hooks
Run the pre-commit hooks on all files to check for any issues.

```bash
pre-commit run --all-files
```

## Local Testing

### Running the Application
To start the application locally with live reloading, use `uvicorn`.

```bash
uvicorn app.main:app --reload
```

## Documentation

### Swagger UI
Access the Swagger UI to interact with the API.

http://localhost:8000/api/v1/docs
