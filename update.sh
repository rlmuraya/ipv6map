#!/bin/bash

git remote update
git checkout master
git reset --hard @{upstream}
pip install -r requirements.txt
npm install
python manage.py migrate
python manage.py collecstatic --noinput
