# Install Python3/venv

# Activate env
source venv/bin/activate

# Dev env...
pip install -r requirements.1of2.txt on dev env

# Raspberry Pi env...
pip install -r requirements.2of2.txt on Pi

# Note: Pillow/PIL may require apt-get install of libopenjp2-7

# Update permissions of sh file for cron job
chmod +x path/to/repo/cron-run.sh

# Update your Pi cron job
# Start editing
crontab -e
# First line for 30 seconds after the Pi boots up
@reboot sleep 30 && path/to/repo/cron-run.sh > path/to/logs/file.log 2>&1
# Second entry for every 6 hours
0 */6 * * * path/to/repo/cron-run.sh > path/to/logs/file.log 2>&1
# Confirm cron entries by listing them
crontab -l