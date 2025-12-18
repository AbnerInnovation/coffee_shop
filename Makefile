.PHONY: run run-backend run-frontend

run-backend:
	cd backend && venv/Scripts/python -m uvicorn app.main:app --reload --port 8001

run-frontend:
	cd frontend && npm run dev

run-electron:
	cd frontend && npm run electron:dev

run:
	$(MAKE) -j2 run-backend run-frontend

electron: 
	$(MAKE) -j2 run-backend run-electron
