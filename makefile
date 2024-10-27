
# Directories and Variables
SRC_DIR = "src"
MANAGE_PY = "src/manage.py"


# File patterns
PY_FILES = $(shell find $(SRC_DIR) -type f -name "*.py")

# Command shortcuts
BLACK = black $(PY_FILES)
ISORT = isort $(PY_FILES)
DJLINT = djlint . --reformat
DJLINTJSCSS = djlint . --reformat --format-css --format-js


.PHONY: format
format:
	@echo "Formatting code with Black..."
	@$(BLACK)

.PHONY: lint
lint:
	# @echo "Linting code with Flake8..."
	# @$(FLAKE8)
	# @echo "Linting Templates uisng Djlint"
	@$(DJLINT)
	@echo "Formatting CSS and JS files"
	@$(DJLINTJSCSS)

.PHONY: sort-imports
sort-imports:
	@echo "Sorting imports with isort..."
	@$(ISORT)

.PHONY: check
check: format lint sort-imports
	@echo "All checks passed!"

.PHONY: help
help:
	@echo "Available targets:"
	@echo "  format        : Format code with Black"
	@echo "  lint          : Lint code with Flake8"
	@echo "  sort-imports  : Sort imports with isort"
	@echo "  check         : Run format, lint, and sort-imports"
	@echo "  help          : Show this help message"



.PHONY: createsuperuser
createsuperuser:
	@$(PYTHON) $(MANAGE_PY) createsuperuser

.PHONY: collectrequirement
collectrequirement:
	pip freeze > requirements.txt

.PHONY: migrations
migrations:
	python $(MANAGE_PY) makemigrations user && python $(MANAGE_PY) makemigrations tenant ecommerce home && python $(MANAGE_PY) migrate

.PHONY: migrate
migrate:
	python $(MANAGE_PY) migrate

.PHONY: serve
serve:
	python $(MANAGE_PY) runserver $(argument)


.PHONY: stripe_webhooks
stripe:
	stripe listen --forward-to http://localhost:8000/webhooks/success

.PHONY: stripe_check
stripe_trigger_payment_success:
	stripe trigger payment_intent.succeeded


.PHONY: stripe_check
stripe_trigger_payment_unsuccess:
	stripe trigger payment_intent.payment_failed


.PHONY: delete_connect
delete_connect:
	python $(MANAGE_PY) delete_connect_stripe
