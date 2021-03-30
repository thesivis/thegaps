# TheGaps

## Configure VirtualEnv
>virtualenv -p <PATH_TO_PYTHON> <NAME>

Example

`virtualenv -p /usr/bin/python3.6 venv`

## Activate virtualenv

> source <PATH_TO_VENV_ACTIVATE>

Example

`source <PATH>/venv/bin/activate`

## Installing package

`pip3 install Django pymongo tornado celery requests rpy2 django-celery-beat django-mathfilters django_celery_results flower redis`

## Installing mongo and redis from docker

### Mongo

`docker run --name mongo -p 27017:27017 -d mongo`

### Redis

`docker run --name redis-server -d -p 6379:6379 redis`

### Start

`docker start mongo`

`docker start redis-server`

## Start TheGaps

Before start is necessary to configure the path to folders, edit setting.py:

```
BASE_MEDIA_URL = '/path/to/files/test'
MEDIA_URL = os.path.join(BASE_MEDIA_URL,'file/tests/')
COMPACTA_URL = os.path.join(BASE_MEDIA_URL,'folder/to/compact/')
APPEND_FILES = os.path.join(BASE_DIR,'files/to/append/')
```

Start celery:

Enter at folder estagio:

`cd <PATH>/estagio`

`celery -A estagio  worker -l info -c 1 &`

`celery flower -A estagio --addr ess=127.0.0.1 --port=5555 &`

And start django:

`python3 manage.py runserver 0.0.0.0:8000 &`
