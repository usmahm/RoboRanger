#include "websocketServer.h"

// WEBSOCKET::webSocket = WebSocketsServer(81);
static WEBSOCKET* websocketInstance = nullptr;

WEBSOCKET::WEBSOCKET() : webSocket(81)
{
  websocketInstance =  this;
};

void WEBSOCKET::initialize() {
  WiFi.begin(WIFISSID, WIFI_PASSWORD);

    int wifi_retry = 0;
    while (WiFi.status() != WL_CONNECTED && wifi_retry < 20) {
        delay(500);
        Serial.print(".");
        wifi_retry++;
    }

    if (WiFi.status() == WL_CONNECTED) {
        Serial.println("");
        Serial.println("WiFi connected.");
        Serial.print("IP address: ");
        Serial.println(WiFi.localIP());
    } else {
        Serial.println("");
        Serial.println("WiFi connection failed.");
        // You can add retry logic or enter a safe state here
    }


  webSocket.begin();
  // WEBSOCKET::onEvent();
  webSocket.onEvent(WEBSOCKET::onEventStatic);
}

void WEBSOCKET::onEventStatic(uint8_t num, WStype_t type, uint8_t * payload, size_t length)
{

}