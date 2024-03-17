# Airport_API_Service
## Description
This project is a RESTful API for an airline ticket booking system, developed using Django REST Framework. The system allows users to view available flights, book tickets, and manage their orders.

## Features
- View available flights and their information.
- Book airline tickets.
- Manage orders (create, view, cancel).
- User authentication and authorization.
- Administrative interface for managing flights, tickets, orders, routes and airplane.

## Technologies
- Django & Django REST Framework
- PostgreSQL
- Docker & Docker Compose
- JWT for authentication
- Swagger and redoc for documentation

## Installation and Setup

### Prerequisites
- Docker and Docker Compose

### Installation Steps

1. **Clone the repository**

`git clone https://github.com/Marinel444/Airport_API_Service.git`

### How to run:
- Copy .env.sample -> .env and populate with all required data
- run `docker-compose up --build`
- create admin user

### DB schema
![images](airport_schema.webp)

