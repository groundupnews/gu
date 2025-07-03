# Installation instructions

1. mkdir groundup
1. cd groundup
1. python -m venv env
1. git clone git@github.com:groundupnews/gu.git
1. source env/bin/activate
1. mkdir media static emails
1. cd media; mkdir uploads targets _versions features old html requisitions
1. cd ../gu
1. pip install -r requirements.txt
1. Create a local_settings.py file - TODO: Put a development ready local_settings.py into the Github repo
1. ./manage.py test
1. ./manage.py migrate
1. ./manage.py setsite localhost localhost:8000
1. scp groundup@groundup.news:/home/groundup/backups/dumpdata-latest.json . # This file is over 1GB. Perhaps zip first.
1. ./manage.py loaddata dumpdata-latest.json # This can take a long time, like over half hour
1. ./manage.py collectstatic
1. Optional download some media files from production
1. Run *./manage.py runserver* and do some testing on localhost:8000 in your browser.
