.PHONY: run run-backend run-frontend

run-backend:
	cd backend && venv/Scripts/python -m uvicorn app.main:app --reload --port 8001

run-frontend:
	cd frontend && npm run dev

run:
	$(MAKE) -j2 run-backend run-frontend
