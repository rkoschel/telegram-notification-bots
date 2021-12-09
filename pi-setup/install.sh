sudo cp ~pi/Apps/yttb/pi-setup/yttb.service /lib/systemd/system
sudo chmod 644 /lib/systemd/system/yttb.service
sudo systemctl daemon-reload
sudo systemctl enable yttb.service
sudo systemctl start yttb.service