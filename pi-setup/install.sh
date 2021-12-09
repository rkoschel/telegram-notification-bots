sudo cp ~pi/Apps/tbot/pi-setup/tbot.service /lib/systemd/system
sudo chmod 644 /lib/systemd/system/tbot.service
sudo systemctl daemon-reload
sudo systemctl enable tbot.service
sudo systemctl start tbot.service