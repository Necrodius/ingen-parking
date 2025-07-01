# 🚗 ingen-parking

**Ingenuity Trial Project – Smart Parking System**

A full-stack web application that allows users to search and reserve parking slots while providing administrators with tools to manage locations, slots, and analyze usage.

---

## 📝 Project Overview

**ingen-parking** is a Smart Parking Management System.

🧑‍💼 **As an admin, I can…**

- Log in securely to access the admin dashboard.
- Add, update, or delete parking locations.
- Define the number of slots available for each location.
- View a list of current and upcoming reservations.
- Cancel user reservations if necessary.
- View a summary of parking activity (e.g., total reservations per day).
- Manage user accounts (view and deactivate if needed).

🤳 **As a user, I can…**

- Register for an account and log in securely.
- Update account profile and password.
- View a list or visual representation of available parking locations.
- See real-time availability of parking slots of a location.
- Reserve a parking slot and receive confirmation.
- View active and past reservations.
- Cancel a reservation before the start time.
- Receive alerts for reservation expiration or cancellation.

---

## 🧰 Tech Stack

**Frontend**

- [React.js](https://reactjs.org/) (with Vite)
- React Router DOM
- Tailwind CSS
- React Hot Toast

**Backend**

- Python + [Flask](https://flask.palletsprojects.com/)
- Flask-JWT-Extended
- SQLAlchemy + Alembic
- Marshmallow for data validation

**Database**

- PostgreSQL

**Infrastructure**

- Docker & Docker Compose
- RESTful API structure
- JWT-based authentication

---

## ⚙️ Local Setup & Installation

### 1. Clone the repository

```bash
git clone https://github.com/your-username/ingen-parking.git
cd ingen-parking
```

### 2. Environment configuration

Create the `.env` file by renaming `.env.sample` to `.env` and changing environment values

### 3. Start the application

Make sure Docker is installed and running, then run:

```bash
docker compose -f infra/docker-compose.yml up --build -d
```

Access the frontend at `http://localhost:5173`  
Access the API at `http://localhost:8000/api`

### 4. Apply database migrations

Inside the backend container:

```bash
docker-compose exec backend flask db upgrade
```

### 5. Seed initial data (optional but recommended)

```bash
docker-compose exec backend flask seed
```

---

## 🧪 Development Notes

- All backend endpoints follow RESTful conventions.
- Backend services use a layered architecture (routes → services → models).
- Token-based auth is handled using JWT.
- Admin UI includes location/slot CRUD and real-time analytics.

### 🔁 Useful Docker Commands

```bash
# Run migrations
docker-compose exec backend flask db migrate -m "your message"
docker-compose exec backend flask db upgrade

# Seed database
docker-compose exec backend flask seed
```

---

## 🚀 Deployment Notes

- I have deployed this project on **Render** using a `render.yaml` blueprint file.
-
- Make sure to configure your production `.env` files when using a different platform.

---

## 📂 Project Structure

```
ingen-parking/
├── backend/
│   ├── models/
│   ├── routes/
│   ├── schemas/
│   ├── services/
│   ├── utils/
│   ├── app.py
│   └── ...
├── frontend/
│   ├── src/
│   └── ...
├── infra/
│   └── docker-compose.yml
└── README.md
```

---

## 🙋‍♂️ Author

Built for Ingenuity by **Necrodius (Earl)**  
With a lot of help from ChatGPT and Copilot

---
