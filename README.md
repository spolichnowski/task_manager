Task Manager / Flask Application
===========

Installation
------------

Create your preferable virtualenv (Python >3.6.6)
I'm using pyenv but it's up to you!


Install all requirements and run Application
--------------------

Step 1:

    (your-venv) $ pip install -r requirements.txt

Step 2:

    (venv) $ python index.py
    
Step 3:
  Generate your own secret key:
  
    app.secret_key = "SET A NEW KEY"
    
    
    
About the App
--------------------

It's a simple task manager with SQLite database (I may upgrade it to MySQL, but there is no need for that now. User can add new tasks to the board (Edit and Delete) and in case add it to "Done" list. I used Bootstrap4 for styling and Flask as a Web Framework. I have plans to develop more features in the future.

