#include <Arduino.h>
#include "WiFi.h"
#include "AsyncTCP.h"
#include "ESPAsyncWebServer.h"
#include "matrix.h"

#define PANEL_WIDTH 4
#define PANEL_HEIGHT 4
#define CHAIN_LENGTH 1

const char* ssid = "CircuitRee";
const char* password = "ChippyIsTheGoat";
Matrix matrix = createMatrix(PANEL_HEIGHT, PANEL_WIDTH, CHAIN_LENGTH);

AsyncWebServer server(80);
AsyncWebSocket ws("/ws");

uint16_t packColor(uint32_t packedColor) {
    uint8_t r = (packedColor >> 16) & 0xFF;
    uint8_t g = (packedColor >> 8) & 0xFF;
    uint8_t b = packedColor & 0xFF;
    return ((r & 0xF8) << 8) | ((g & 0xFC) << 3) | (b >> 3);
}

// Set pixel on matrix go boom
bool setPixelColor(int x, int y, uint32_t packedColor) {
    if (x >= 0 && x < PANEL_WIDTH && y >= 0 && y < PANEL_HEIGHT) {
        uint16_t color = packColor(packedColor);
        changePixel(matrix, y, x, color);
        return true;
    }
    return false;
}

// Convert matrix data to a JSON string
String jsonMatrix() {
    String json = "{ \"matrix\": [";
    for (int y = 0; y < matrix.rows; y++) {
        json += "[";
        for (int x = 0; x < matrix.cols; x++) {
            uint16_t color = getPixel(matrix, y, x);
            uint32_t packedColor = ((color & 0xF800) << 8) | ((color & 0x07E0) << 5) | ((color & 0x001F) << 3);
            json += String(packedColor);
            if (x < matrix.cols - 1) json += ",";
        }
        json += "]";
        if (y < matrix.rows - 1) json += ",";
    }
    json += "] }";
    return json;
}

// ws events
void onWsEvent(AsyncWebSocket *server, AsyncWebSocketClient *client, AwsEventType type, void *arg, uint8_t *data, size_t len) {
    if (type == WS_EVT_DATA) {
        String msg = (char*)data;

        // getMatrix
        if (msg.startsWith("getMatrix")) {
            String json = jsonMatrix();
            client->text(json);
        } else if (msg.startsWith("setPixel")) { // setPixel
            // Unpacking Message
            int comma1 = msg.indexOf(',');
            int comma2 = msg.lastIndexOf(',');
            int x = msg.substring(9, comma1).toInt();
            int y = msg.substring(comma1 + 1, comma2).toInt();
            uint32_t packedColor = msg.substring(comma2 + 1).toInt();

            // Setting pixel and repsonding
            if (setPixelColor(x, y, packedColor)) {
                client->text("{\"status\": \"success\"}");
            } else {
                client->text("{\"status\": \"error\", \"message\": \"invalid\"}");
            }
        }
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

    // /getMatrix endpoint
    server.on("/getMatrix", HTTP_GET, [](AsyncWebServerRequest *request){
        request->send(200, "application/json", jsonMatrix());
    });

    // /setPixel endpoint
    server.on("/setPixel", HTTP_POST, [](AsyncWebServerRequest *request){
        if (request->hasParam("x", true) && request->hasParam("y", true) && request->hasParam("color", true)) {
            int x = request->getParam("x", true)->value().toInt();
            int y = request->getParam("y", true)->value().toInt();
            uint32_t packedColor = request->getParam("color", true)->value().toInt();

            if (setPixelColor(x, y, packedColor)) {
                request->send(200, "application/json", "{\"status\": \"success\"}");
            } else {
                request->send(400, "application/json", "{\"status\": \"error\", \"message\": \"invalid\"}");
            }
        } else {
            request->send(400, "application/json", "{\"status\": \"error\", \"message\": \"malformed request\"}");
        }
    });

    server.begin();
}

void loop() {
    ws.cleanupClients();
}
