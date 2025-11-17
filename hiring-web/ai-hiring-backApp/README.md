# AI Hiring Backend

This is the backend application for the Hiring Web Application. It is built with Node.js and Express and handles user authentication, CV uploads, and communication with the database.

## Features
- User authentication (JWT-based)
- CV upload and processing
- Integration with MongoDB

## Installation
1. Navigate to the `ai-hiring-backApp` directory:
   ```bash
   cd ai-hiring-backApp
   ```
2. Install dependencies:
   ```bash
   npm install
   ```

## Scripts
- Start the server:
  ```bash
  npm start
  ```

## Dependencies
- Express
- Mongoose
- JSON Web Token (JWT)
- Multer
- Nodemailer

## Environment Variables
Create a `.env` file in the root of the `ai-hiring-backApp` directory with the following variables:
```
MONGO_URI=<your-mongodb-uri>
JWT_SECRET=<your-jwt-secret>
```