#! /bin/bash
sudo cp plant.service /lib/systemd/system/plant.service
sudo systemctl daemon-reload
sudo systemctl enableqq plant.service
