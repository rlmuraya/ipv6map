#!/bin/bash

workon ipv6map
git remote update
git checkout master
git reset --hard @{upstream}
pip install -r requirements.txt
npm install
python manage.py migrate
python manage.py collectstatic --noinput
echo "Reloading server" && touch /var/www/rlmuraya_pythonanywhere_com_wsgi.py
