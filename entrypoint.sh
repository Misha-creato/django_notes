#!/bin/bash

python manage.py runworkers
redis-server
celery -A config worker -l INFO
python manage.py runserver
