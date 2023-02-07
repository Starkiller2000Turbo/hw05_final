WORKDIR = yatube
TEMPLATES-DIR = $(WORKDIR)/templates
MANAGE = python $(WORKDIR)/manage.py

style:
	isort $(WORKDIR)
	black -S -l 79 $(WORKDIR)
	flake8 $(WORKDIR)
	djlint $(TEMPLATES-DIR) --reformat --indent 2
	mypy $(WORKDIR)

migrations:
	$(MANAGE) makemigrations

migrate:
	$(MANAGE) migrate

superuser:
	$(MANAGE) createsuperuser

run:
	$(MANAGE) runserver

test:
	$(MANAGE) test $(WORKDIR)

shell:
	$(MANAGE) shell 

venv:
	source venv/Scripts/activate
