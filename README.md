# TheRedCode

![Python](https://img.shields.io/badge/Python-3776AB?style=flat-square&logo=python&logoColor=white)
![Flask](https://img.shields.io/badge/Flask-000000?style=flat-square&logo=flask&logoColor=white)
![SQLite](https://img.shields.io/badge/SQLite-003B57?style=flat-square&logo=sqlite&logoColor=white)
![HTML5](https://img.shields.io/badge/HTML5-E34F26?style=flat-square&logo=html5&logoColor=white)
![CSS3](https://img.shields.io/badge/CSS3-1572B6?style=flat-square&logo=css3&logoColor=white)
![Werkzeug](https://img.shields.io/badge/Werkzeug-FF6600?style=flat-square)

A web-based Python challenge platform. Users can register, select a chapter, open a task, and submit their solution code. The system automatically checks the function against tests and saves results in the user's profile.

The project features a red-and-black minimalist design and is suitable as an educational programming platform.

In development.

## Features

* User registration and authentication
* Role management: student and administrator
* Browse chapters and tasks
* Submit Python code directly in the browser
* Automatic testing of solutions
* Save user attempt history
* Personal profile with results
* Admin panel to review submissions
* Add new chapters and tasks via admin

## Installation

### Prerequisites

* Python 3.10+
* pip

### Running the Project

```bash
git clone https://github.com/yudix10/theredcode.git
cd theredcode
```

Create a virtual environment:

```bash
python -m venv venv
```

Activate it:

```bash
# Windows
venv\Scripts\activate

# macOS / Linux
source venv/bin/activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

Start the application:

```bash
python app.py
```

After running, the website will be available at:

```bash
http://127.0.0.1:5000
```

## Project Structure

```bash
theredcode/
│
├── app.py                 # main Flask application file
├── requirements.txt       # project dependencies
├── trainer.db             # SQLite database
│
├── templates/             # HTML templates
│   ├── index.html
│   ├── login.html
│   ├── register.html
│   ├── profile.html
│   ├── chapter.html
│   └── task.html
│
└── static/
    └── style.css          # site styles
```

## Main Pages

* `/register` — user registration
* `/login` — login page
* `/` — homepage with chapters
* `/chapter/<id>` — list of tasks for a selected chapter
* `/task/<id>` — task solution page
* `/profile` — user profile and results
* `/admin` — admin panel
* `/admin/chapter/add` — add a chapter
* `/admin/task/add` — add a task

## Administrator Account

By default, an admin account is created on first run:

```bash
Email: admin@site.com
Password: admin123
```

For production use, update these credentials in `app.py`.

## How Task Checking Works

Admins create tasks with:

* task title
* description
* function name
* starter code
* test cases

Users write their solution in the input field. Upon submission, the app executes the code, locates the function, and tests it against the predefined test cases.

Example task:

```python
def square(n):
    return n * n
```

Example test cases:

```python
[(2, 4), (5, 25)]
```

## Technologies

* Python
* Flask
* SQLite
* HTML
* CSS
* Werkzeug Security

## Author

David Badalyan — project development
theredcode © 2026

## License

Educational project. Feel free to use and modify.
