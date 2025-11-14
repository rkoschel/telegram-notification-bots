sudo cp gwfjt.service /etc/systemd/system
sudo chmod 644 /etc/systemd/system/gwfjt.service
sudo systemctl daemon-reload
sudo systemctl enable gwfjt.service
sudo systemctl start gwfjt.service