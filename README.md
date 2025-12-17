# Webpage for IPv6 SRA Scanning Campaign 
This webpage is used to provide our measurement results from our active IPv6 Subnet-Router anycast scans.

## Requirements
- Python 3.12 or newer
- Python venv, e.g., `sudo apt install python3-venv`

## Setup (Linux, e.g., Ubuntu 24.04)
1. Run `make python_env`
2. Activate virtual environment with `source .venv/bin/activate`
3. Run `python app.py` in the project's root directory, where the app.py file is located.

The webpage can be deployed without `make`, the only thing required are the python modules in `requirements.txt`

## Run with Gunicorn for improved performance
1. Activate your venv
2. Install gunicorn (already included in `requirements.txt` or install using `pip install gunicorn`)
3. Run `gunicorn -c gunicorn_config.py app:app` in the project's root

## Nginx and systemd setup
1. Adjust the variables for your domain and the ssl certificates in the `webpage.conf.temp` file
2. Adjust User, WorkingDirectory, and ExecStart in the `gunicorn.service` file
3. Remove the `.temp` ending
4. Copy the files into the corresponding directories with `cp gunicorn.service /etc/systemd/system/` and `cp webpage.conf /etc/nginx/conf.d/`
5. Restart nginx with `systemctl restart nginx`
6. Reload the systemd daemon `systemctl daemon-reload`
7. Start the app with `systemctl start gunicorn`
