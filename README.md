# Task counter

I made this project to count time of tasks I do at work.

## Getting Started

These instructions will get you a copy of the project up and running on your local machine.

### Prerequisites

You need to install Python 3.10 or greater and pip to run this software.
Using pyenv, you can run this command:

```
# PYTHON_CONFIGURE_OPTS allows to build with pyinstaller
env PYTHON_CONFIGURE_OPTS="--enable-shared" pyenv install 3.10.6
```

We need to [enable shared library with
pyenv](https://github.com/pyenv/pyenv/wiki#how-to-build-cpython-with---enable-shared).

### Installing

Clone the repository

```
git clone https://github.com/ardeidae/taskcounter
```

Install required packages

```
cd taskcounter
pip install -r requirements.txt
```

Run the application

```
python3 main.py
```

Build executable

```
pip install -r requirements.build
pyinstaller deploy/taskcounter.spec
# on macos, build the dmg
dmgbuild -s deploy/dmgbuild-settings.py "" ""
```

## Running the tests

```
python3 tests.py
```

## Built With

* [Python3](https://www.python.org/) - Python is a programming language that lets you work quickly and integrate systems more effectively.
* [PyQt5](https://www.riverbankcomputing.com/software/pyqt/intro) - PyQt is a set of Python bindings for [Qt application framework](https://www.qt.io/).
* [peewee](http://peewee.readthedocs.io/en/latest/) - Peewee is a simple and small ORM.
* [SQLite](https://www.sqlite.org/) - SQLite is a SQL database engine.
* [PyInstaller](http://www.pyinstaller.org/) - PyInstaller is a program that freezes (packages) Python programs into stand-alone executables.
* [dmgbuild](http://dmgbuild.readthedocs.io/) - A command line tool to build .dmg files.

## Versioning

We use [SemVer](http://semver.org/) for versioning. For the versions available, see the [tags on this repository](https://github.com/ardeidae/taskcounter/tags).

## Authors

* **Matthieu PETIOT** - [ardeidae](https://github.com/ardeidae)

## License

This project is licensed under the GPLv3 License.
