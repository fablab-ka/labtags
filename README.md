# labtags
Bluetooth iTag utilities

# Features
- presence detection
- wireless button
- battery level warning
- notification system

# Messages
* TAG_DISCOVERED (tag_mac, time)
* TAG_CONNECTED (tag_mac, time)
* TAG_LOST (tag_mac, time)
* TAG_DISCONNECTED (tag_mac, time)
* TAG_NOTIFICATION (tag_mac, notification_type, time)
* TAG_DATA_CHANGED (tag_mac, name, battery, state, rssi, time)
* TAG_BEEP_STATE_CHANGED (tag_mac, state, time)

# Gateway Commands
* Connect tag
* Disconnect tag
* Beep tag (on/off)


# Server Commands
* Send message (gateway_mac, gateway_ip, msg)


# setup for ifttt
install ngrok (https://ngrok.com/)

wget https://bin.equinox.io/c/4VmDzA7iaHb/ngrok-stable-linux-arm.zip
unzip ngrok-stable-linux-arm.zip
rm ngrok-stable-linux-arm.zip
sudo mv ngrok /usr/bin/ngrok

signup at https://ngrok.com/
configure ngrok authtoken with:
```ngrok <authToken>```

cp blot_gateway /etc/init.d/blot_gateway
append ```/etc/init.d/blot_gateway start``` to /etc/rc.local
