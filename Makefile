# Simple developer Makefile

.PHONY: backend frontend test install-backend install-frontend preflight

backend:
	cd backend && uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload

frontend:
	cd frontend && npm start

test:
	cd backend && pytest -q

install-backend:
	cd backend && python3 -m venv .venv && . .venv/bin/activate && pip install --upgrade pip setuptools wheel && pip install -r requirements.txt

install-frontend:
	cd frontend && npm install

preflight:
	bash preflight.sh
