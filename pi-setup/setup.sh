
#sudo pip install flask
#sudo pip install beautifulsoup4
sudo pip install pyTelegramBotAPI
sudo pip install feedparser

# setup and start bot clock service
sudo cp ~pi/Apps/gwfjtpy/pi-setup/gwfjtpy.service /lib/systemd/system
sudo chmod 644 /lib/systemd/system/gwfjtpy.service
sudo systemctl daemon-reload
sudo systemctl enable gwfjtpy.service
sudo systemctl start gwfjtpy.service