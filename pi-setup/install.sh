sudo cp ~pi/Apps/gwfjt/pi-setup/gwfjt.service /lib/systemd/system
sudo chmod 644 /lib/systemd/system/gwfjt.service
sudo systemctl daemon-reload
sudo systemctl enable gwfjt.service
sudo systemctl start gwfjt.service