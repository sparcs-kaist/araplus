init:
	./manage.py makemigrations
	./manage.py migrate
	./manage.py loaddata ./apps/session/fixtures/*
	./manage.py loaddata ./apps/board/fixtures/*
