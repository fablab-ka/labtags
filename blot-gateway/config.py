class ClientType:
    GetRequest = "GetRequest"
    MQTT = "MQTT"

class Config:
    ClientType = ClientType.MQTT
    ClientUrl = "192.168.1.6"

    NotificationServiceUrl = 3333
    IFTTTUrlTemplate = "https://maker.ifttt.com/trigger/tag_%s_pressed/with/key/cV2tU0tD8V2UWOjPb4H7SO"

    MQTTPathTemplate = "/FLKA/itags/%s"
    MQTTClientId = "itag_bridge"
    MQTTPort = 1880

    IPTestUrl = "gmail.com"
