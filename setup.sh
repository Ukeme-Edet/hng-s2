#!/usr/bin/bash
# This script is used to setup the environment for the project

# Install python3, python3-pip, python3-venv, python3-dev
sudo apt-get update -y
sudo apt-get install -y python3-pip python3-venv python3-dev nginx
python3 -m venv venv

# Set up the postgres database
sudo apt-get install -y postgresql postgresql-contrib
sudo systemctl start postgresql
sudo systemctl enable postgresql
sudo -u postgres psql -c "CREATE USER hng2 WITH PASSWORD 'hng2_pwd';"
sudo -u postgres psql -c "CREATE DATABASE hng_db;"
sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE hng_db TO hng2;"
sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO hng2;"
sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO hng2;"
sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON SCHEMA public TO hng2;"
sudo -u postgres psql -c "ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL PRIVILEGES ON TABLES TO hng2;"
sudo apt install -y libpq-dev

# Activate the virtual environment
source venv/bin/activate

# Install the required packages
pip install -r requirements.txt

# Create the service configuration file
sudo cp app_service.service /etc/systemd/system/app_service.service

# Reload the systemd manager configuration
sudo systemctl daemon-reload

# Enable the service to start on boot
sudo systemctl enable app_service.service

# Configure the nginx server
sudo cp app_server.conf /etc/nginx/sites-available/app_server.conf
sudo ln -sf /etc/nginx/sites-available/app_server.conf /etc/nginx/sites-enabled/app_server.conf

# Change the permissions of the home directory
sudo chmod 755 /home/tech-wiz
