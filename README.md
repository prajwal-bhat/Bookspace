# Bookspace
Web application written in Python with Flask micro web framework to search, browse the details, check reviews and save favorite books. User after logged in can search books either by name of the book or name of the authon or by isbn.

### Prerequisites
-Flask
-SQLAlchemy

### Setup
Set the environment variable FLASK_APP to be application.py. On a Mac or on Linux, the command to do this is export FLASK_APP=application.py. On Windows, the command is instead set FLASK_APP=application.py. You may optionally want to set the environment variable FLASK_DEBUG to 1, which will activate Flask’s debugger and will automatically reload your web application whenever you save a change to a file.
Set the environment variable DATABASE_URL to be the URI of your database, which you should be able to see from the credentials page on Heroku.
