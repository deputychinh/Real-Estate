# Local development. Every target runs from the repository root.
.PHONY: up down logs seed test lint typecheck dev-api dev-web lock diagram \
        aws-bootstrap infra-plan infra-apply deploy rollback aws-seed

BACKEND := cd backend &&
VENV := .venv/bin

up:            ## build and start MySQL, Redis, API and web
	cp -n .env.example .env 2>/dev/null || true
	docker compose up -d --build

down:
	docker compose down

logs:
	docker compose logs -f backend frontend

seed:          ## demo data (idempotent); `make seed ARGS=--reset` to recreate
	docker compose exec backend python -m scripts.seed $(ARGS)

test:          ## backend + frontend tests
	$(BACKEND) $(VENV)/pytest -q
	cd frontend && npm run test

lint:
	$(BACKEND) $(VENV)/ruff check . && $(VENV)/ruff format --check .
	cd frontend && npm run lint

typecheck:
	$(BACKEND) $(VENV)/mypy app scripts
	cd frontend && npm run typecheck

dev-api:       ## API with reload against local MySQL/Redis (backend/.env)
	$(BACKEND) $(VENV)/uvicorn app.main:app --reload --port 8000

dev-web:
	cd frontend && npm run dev

lock:          ## re-pin backend runtime dependencies
	$(BACKEND) python3 -m venv /tmp/re-lock && /tmp/re-lock/bin/pip install -q . && /tmp/re-lock/bin/pip freeze --exclude re-portal-backend > requirements.txt

diagram:
	python3 docs/architecture/gen_aws_diagram.py --png && python3 docs/architecture/gen_business_flows.py --png

# ── AWS (plan §15). ENV=staging|prod ──
aws-bootstrap: ## once per account: Terraform state bucket + backend.hcl
	scripts/aws/bootstrap.sh

infra-plan:
	scripts/aws/infra.sh plan $(ENV)

infra-apply:
	scripts/aws/infra.sh apply $(ENV)

deploy:        ## build → push → migrate → release → smoke test
	scripts/aws/deploy.sh $(ENV) $(TAG)

rollback:
	scripts/aws/rollback.sh $(ENV) $(SERVICE)

aws-seed:      ## demo data on staging
	scripts/aws/seed.sh staging $(ARGS)
