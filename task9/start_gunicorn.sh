#!/bin/sh

gunicorn --workers 3 --bind 127.0.0.1:5000 wiki_search_app:app
