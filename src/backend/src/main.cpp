/* 
 * Server for controlling LED matrix
 * Creator: CircuitRee - Boyan
 * 
*/
#include <Arduino.h>
#include "WiFi.h"
#include "AsyncTCP.h"
#include "ESPAsyncWebServer.h"
#include "matrix.h"

#define PANEL_WIDTH 64
#define PANEL_HEIGHT 32
#define CHAIN_LENGTH 1

const char *ssid = "CircuitRee";
const char *password = "ChippyIsTheGoat";
Matrix matrix = createMatrix(PANEL_HEIGHT, PANEL_WIDTH, CHAIN_LENGTH);

AsyncWebServer server(80);
AsyncWebSocket ws("/ws");

uint16_t packColor(uint32_t packedColor) {
    uint8_t r = (packedColor >> 16) & 0xFF;
    uint8_t g = (packedColor >> 8) & 0xFF;
    uint8_t b = packedColor & 0xFF;
    return ((r & 0xF8) << 8) | ((g & 0xFC) << 3) | (b >> 3);
}

// Set pixel on matrix
bool setPixelColor(int x, int y, uint32_t packedColor) {
    if (x >= 0 && x < PANEL_WIDTH && y >= 0 && y < PANEL_HEIGHT) {
        uint16_t color = packColor(packedColor);
        changePixel(matrix, y, x, color);
        return true;
    }
    return false;
}

bool isValidPixel(int x, int y, uint32_t packedColor) {
    return !(x < 0 || x >= PANEL_WIDTH || y < 0 || y >= PANEL_HEIGHT || packedColor > 0xFFFFFF);
}

void sendJsonResponse(AsyncWebServerRequest *request, int statusCode, const char *message) {
    request->send(statusCode, "application/json", message);
}

void sendJsonResponse(AsyncWebSocketClient *client, const char *message) {
    client->text(message);
}

// matrix state -> JSON
String jsonMatrix() {
    String json = "{ \"matrix\": [";
    for (int y = 0; y < matrix.rows; y++) {
        json += "[";
        for (int x = 0; x < matrix.cols; x++) {
            uint16_t color = getPixel(matrix, y, x);
            uint8_t r = (color >> 8) & 0xF8;
            uint8_t g = (color >> 3) & 0xFC;
            uint8_t b = (color << 3) & 0xF8;
            uint32_t packedColor = (r << 16) | (g << 8) | b;

            json += String(packedColor);
            if (x < matrix.cols - 1) json += ",";
        }
        json += "]";
        if (y < matrix.rows - 1) json += ",";
    }
    json += "] }";
    return json;
}

void handleWS(AsyncWebSocketClient *client, String msg) {
    if (msg.startsWith("getMatrix")) {
        sendJsonResponse(client, jsonMatrix().c_str());
    } else if (msg.startsWith("setPixel")) {
        int comma1 = msg.indexOf(',');
        int comma2 = msg.lastIndexOf(',');
        if (comma1 == -1 || comma2 == -1 || comma1 == comma2) {
            sendJsonResponse(client, "{\"status\": \"error\", \"message\": \"malformed request\"}");
            return;
        }

        int x = msg.substring(9, comma1).toInt();
        int y = msg.substring(comma1 + 1, comma2).toInt();
        uint32_t packedColor = msg.substring(comma2 + 1).toInt();

        if (isValidPixel(x, y, packedColor) && setPixelColor(x, y, packedColor)) {
            sendJsonResponse(client, "{\"status\": \"success\"}");
        } else {
            sendJsonResponse(client, "{\"status\": \"error\", \"message\": \"invalid parameters\"}");
        }
    } else {
        sendJsonResponse(client, "{\"status\": \"error\", \"message\": \"unknown command\"}");
    }
}

// WebSocket events
void onWsEvent(AsyncWebSocket *server, AsyncWebSocketClient *client, AwsEventType type, void *arg, uint8_t *data, size_t len) {
    if (type == WS_EVT_DATA) {
        data[len] = '\0';
        String msg = (char *)data;
        handleWS(client, msg);
    }
}

void setup() {
    Serial.begin(115200);

    WiFi.begin(ssid, password);
    while (WiFi.status() != WL_CONNECTED) {
        delay(1000);
        Serial.println("Connecting to WiFi...");
    }
    Serial.println("Connected to WiFi");

    ws.onEvent(onWsEvent);
    server.addHandler(&ws);

    server.begin();
}

void loop() {
    ws.cleanupClients();
}
