import threading
import paho.mqtt.client as mqtt
from utils import ANSI_BLUE, ANSI_OFF
from config import Config
from messages import BeepTagCommandMessage


class MQTTListener(threading.Thread):
    def __init__(self, messageQueue, tagCache):
        threading.Thread.__init__(self)

        self.messageQueue = messageQueue
        self.tagCache = tagCache

        self.mqttClient = mqtt.Client(client_id=Config.MQTTClientId,
                                      protocol=mqtt.MQTTv31)

        self.mqttClient.on_message = self.handleMQTTMessage

    def handleMQTTMessage(self, client, userdata, mqttMessage):
        print(ANSI_BLUE + "[MQTTListener] Received MQTT Message '" +
              mqttMessage.topic + "': '" + str(mqttMessage.payload) + "'" + ANSI_OFF)

        mac = mqttMessage.payload
        if mqttMessage.topic == 'beep': #todo template
            self.messageQueue.put(BeepTagCommandMessage(mac))

    def run(self):
        print(ANSI_BLUE + "[MQTTListener] Connecting to Broker '" +
              str(Config.ClientUrl) + "'" + ANSI_OFF)

        try:
            mqtt_errno = self.mqttClient.connect(
                Config.ClientUrl, Config.MQTTPort, 60)
            if mqtt_errno != 0:
                raise Exception(mqtt.error_string(mqtt_errno))

            self.mqttClient.loop_start()
        except BaseException as e:
            print((ANSI_BLUE + "[MQTTListener] MQTT error: %s" + ANSI_OFF) % e)

        print(ANSI_BLUE + "[MQTTListener] Shutting down" + ANSI_OFF)
