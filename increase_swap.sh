sudo dd if=/dev/zero of=/swapfile bs=10M count=1
sudo chmod 600 /swapfile
sudo mkswap /swapfile
sudo swapon /swapfile

