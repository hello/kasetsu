#/bin/bash

# run as sudo to get port 80, exposed publicly
FLASK_APP=server.py flask run --host=0.0.0.0 --port=80
