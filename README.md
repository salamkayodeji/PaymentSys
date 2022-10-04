# PaymentSys
===================================

Local installation
------------

Once unzipped, follow the installation guides below.

### Installation in Windows

* Download and install [Python](https://www.python.org/downloads/). For this
  guide, we assume Python is installed in `C:\Python36`.
* Download the Pip (Python package installer) bootstrap script
  [get-pip.py](https://bootstrap.pypa.io/get-pip.py).
* In the command prompt, run `C:\Python36\python.exe get-pip.py` to install
  `pip`.
* In the command prompt, run `C:\Python36\scripts\pip install virtualenv` to
  install `virtualenv`.

### Installation in Ubuntu

Python 3 is preinstalled in Ubuntu. Virtualenv and pip necessarily aren't, so:

* `sudo apt-get install python-virtualenv python-pip`

### Creating and activating a virtualenv

Go to the project root directory and run:

Windows:

```
c:\location_of_project>c:\Python35\scripts\virtualenv --system-site-packages venv
c:\location_of_project>venv\Scripts\activate
```

Ubuntu:

```
virtualenv -p /usr/bin/python3 --system-site-packages venv

for python 3.9

python -m venv "virtual env name"

source venv/bin/activate
```

Starting the project
--------------------

After activating the virtualenv do the following

```
pip install -r requirements.txt

python manage.py runserver
```

Login details:
username: admin
password: rootaccess1234

You need to create a .env file with your PAYSTACKS Secret Key