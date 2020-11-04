# NaRogah mobile application backend
Na-Rogah project is a mobile appication for Android and IOS built in client-server architecture. Server part developed with Python 3.7 and Flask micro framework.

## Backend structure
|file name|description|
|--|--|
|app.py|contains defenition of all base classes of application ( Flask, SQLAlchemy, Migrate, Manager, Session, LoginManager, Admin, Security, SQLAlchemyUserDatastore, Mail)
|admin.py| this file contains admin panel settings (user roles, timetable editing, booking records, etc. |
|config.py|includes application settings (SMTP, DBMS) |
|main.py| application launching |
|manage.py| database migrations providing |
|view.py|all application GET and POST endpoints (timetable, booking, menu view, service information, etc.)|
|Procfile|launch web gunicorn server with dyno on Heroku|
|requirements.txt|all required libraries|

## Making migrations
	python manage.py db migrate
	python manage.py db upgrade

## Deploying to Heroku

	git commit -am "Commit name"
	git push heroku master
	heroku logs  # see build status

additional information read here: https://dashboard.heroku.com/

When Heroku detects Procfile and requirements.txt, it will automatically install all requirements and launch the application.

Now this backend application hosts in https://na-rogah-api.herokuapp.com/
 
