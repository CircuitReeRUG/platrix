from flask import Flask, request, jsonify
from flask_sock import Sock
import json
from time import sleep

app = Flask(__name__)
sock = Sock(app)

PANEL_WIDTH = 64
PANEL_HEIGHT = 64
matrix = [[0 for _ in range(PANEL_HEIGHT)] for _ in range(PANEL_WIDTH)]

# List to keep track of connected WebSocket clients
connected_clients = []


def is_valid_coordinate(x, y):
    return 0 <= x < PANEL_WIDTH and 0 <= y < PANEL_HEIGHT


def is_valid_color(color):
    return 0 <= color <= 16777215


def broadcast_matrix():
    response = json.dumps({"matrix": matrix})
    disconnected_clients = []
    for client in connected_clients:
        try:
            client.send(response)
        except Exception as e:
            print(f"Failed to send to client: {e}")
            disconnected_clients.append(client)

    # Remove disconnected clients
    for client in disconnected_clients:
        connected_clients.remove(client)


@sock.route('/ws')
def ws_handler(ws):
    if ws not in connected_clients:
        connected_clients.append(ws)
        print(f"Client connected. Total: {len(connected_clients)}")
    try:
        while True:
            data = ws.receive()
            if data == "getMatrix":
                response = {"matrix": matrix}
                ws.send(json.dumps(response))
            elif data.startswith("setPixel"):
                parts = data.split(',')
                if len(parts) != 4 or parts[0] != 'setPixel':
                    raise ValueError("Invalid message format")

                x = int(parts[1])
                y = int(parts[2])
                color = int(parts[3])
                print(f"Received: x={x}, y={y}, color={color}")
                if not is_valid_coordinate(x, y) or not is_valid_color(color):
                    ws.send(json.dumps(
                        {"status": "error", "message": "invalid"}))
                    continue

                print(
                    f"Setting pixel at ({x}, {y}) to color {color}, old color: {matrix[x][y]}")
                matrix[y][x] = color
                broadcast_matrix()
                ws.send(json.dumps({"status": "success"}))

    except Exception as e:
        print(f"Error: {e}")
    finally:
        # Remove client from the list when they disconnect
        if ws in connected_clients:
            connected_clients.remove(ws)
            print("Client disconnected.")


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
