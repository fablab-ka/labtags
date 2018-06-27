import paho.mqtt.client as mqtt
from messages import TagNotificationMessage, ConnectToTagCommandMessage, BeepTagCommandMessage, COMMAND_CONNECT_TAG, COMMAND_BEEP_TAG
from utils import ANSI_YELLOW, ANSI_OFF

from config import Config, ClientType

class MQTTClient:
    def __init__(self, messageQueue, clientUrl, gatewayMac, gatewayIp):
        self.messageQueue = messageQueue
        self.clientUrl = clientUrl
        self.gatewayMac = gatewayMac
        self.gatewayIp = gatewayIp

        self.mqttClient = mqtt.Client(client_id=Config.MQTTClientId,
                                      protocol=mqtt.MQTTv31)

        try:
            mqtt_errno = self.mqttClient.connect(
                Config.mqtt_broker, Config.mqtt_broker_port, 60)
            if mqtt_errno != 0:
                raise Exception(mqtt.error_string(mqtt_errno))
        except BaseException as e:
            print((ANSI_YELLOW + "[MQTTClient] MQTT error: %s" + ANSI_OFF) % e)

    def handleConnectResponse(self, commandMessage):
        print(ANSI_YELLOW + "[MQTTClient] Received Connect Command for Tag '" +
              str(commandMessage["tag_mac"]) + "'" + ANSI_OFF)

        if not isinstance(commandMessage["tag_mac"], basestring):
            print(ANSI_YELLOW + "[MQTTClient] invalid message format expected string for mac, got '" + str(
                commandMessage["tag_mac"]) + "'" + ANSI_OFF)
            return

        self.messageQueue.put(
            ConnectToTagCommandMessage(commandMessage["tag_mac"]))

    def handleBeepResponse(self, commandMessage):
        print(ANSI_YELLOW + "[MQTTClient] Received Beep Command for Tag '" +
              str(commandMessage["tag_mac"]) + "'" + ANSI_OFF)

        if not isinstance(commandMessage["tag_mac"], basestring):
            print(ANSI_YELLOW + "[MQTTClient] invalid message format expected string for mac, got '" + str(
                commandMessage["tag_mac"]) + "'" + ANSI_OFF)
            return

        self.messageQueue.put(BeepTagCommandMessage(commandMessage["tag_mac"]))

    def handleResponse(self, result):
        if not isinstance(result, list):
            result = [result]

        for commandMessage in result:
            if commandMessage and commandMessage.has_key("command"):
                if not isinstance(commandMessage["command"], basestring):
                    print(ANSI_YELLOW + "[MQTTClient] invalid message format '" +
                          str(commandMessage["command"]) + "'" + ANSI_OFF)
                    continue

                if commandMessage["command"] == COMMAND_CONNECT_TAG:
                    self.handleConnectResponse(commandMessage)
                elif commandMessage["command"] == COMMAND_BEEP_TAG:
                    self.handleBeepResponse(commandMessage)
                else:
                    print(ANSI_YELLOW + "[MQTTClient] unknown result command '" +
                          commandMessage["command"] + "'" + ANSI_OFF)

    def sendMessage(self, message):
        print(ANSI_YELLOW + "[MQTTClient] sendMessage" + str(message) + ANSI_OFF)

        if Config.ClientType == ClientType.MQTT:
            payload = message.toMQTTMessage()
            topic = Config.MQTTPathTemplate % (message.tag.mac)

            try:
                result = self.mqttClient.publish(topic, payload)
                if not (result[0] == mqtt.MQTT_ERR_SUCCESS):
                    print((ANSI_YELLOW + "[MQTTClient] Error publishing message \"%s\" to topic \"%s\". Return code %s: %s" + ANSI_OFF) % (
                        payload, topic, str(result[0]), mqtt.error_string(result[0]
                                                                        )))
            except BaseException as e:
                print((ANSI_YELLOW + "Error relaying message {%s} '%s'. Error: {%s}" + ANSI_OFF) % (payload, topic, e))

            if res.text == "" or res.text == "OK":
                print(ANSI_YELLOW + "[MQTTClient] No Command response" + ANSI_OFF)
            else:
                try:
                    self.handleResponse(res.json())
                except:
                    print(
                        ANSI_YELLOW + "[MQTTClient] Broken Server response '" + str(res.text) + "'" + ANSI_OFF)
