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
* TAG_BUTTON_PRESSED (tag_mac, time)
* TAG_BUTTON_DOUBLE_PRESSED (tag_mac, time)
* TAG_DATA_CHANGED (tag_mac, name, battery, state, rssi, time)
* TAG_BEEP_STATE_CHANGED (tag_mac, state, time)

# Gateway Commands
* Connect tag
* Disconnect tag
* Beep tag (on/off)


# Server Commands
* Send message (gateway_mac, gateway_ip, msg)
