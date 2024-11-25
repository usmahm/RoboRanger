#pragma once

#include "Arduino.h"
#include "env.h"
#include "WiFi.h"
#include <WebSocketsServer.h>

struct WEBSOCKET
{
  WebSocketsServer webSocket;

  WEBSOCKET();

  void initialize();

  static void onEventStatic(uint8_t num, WStype_t type, uint8_t * payload, size_t length);
};