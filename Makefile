# repo-forge:tareas
.PHONY: doctor test smoke validate check all

doctor:
	python scripts/doctor.py

validate:
	python tools/validate_repository.py

test:
	python -m pytest

smoke:
	python tests/smoke_runtime.py

check: doctor validate test smoke

all: check
