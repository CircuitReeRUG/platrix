from flask import Flask, jsonify
import flask_sock
import json
from time import sleep
import logging

app = Flask(__name__)
sock = flask_sock.Sock(app)

# set logging level
logging.basicConfig(level=logging.INFO)

# Set Matrix dimensions
PANEL_WIDTH = 64
PANEL_HEIGHT = 32
matrix = [[0 for _ in range(PANEL_WIDTH)] for _ in range(PANEL_HEIGHT)]


def __is_valid_coordinate(x:int, y:int) -> bool:
    return 0 <= x < PANEL_WIDTH and 0 <= y < PANEL_HEIGHT

def __is_valid_color(color:int) -> bool:
    return 0 <= color <= 16777215 # 0xFFFFFF

def broadcast_matrix(connected_clients:set) -> None:
    """Broadcasts the current matrix to all connected clients.
    """
    for client in app.connected_clients:
        try:
            response = json.dumps({"matrix": matrix})
            client.send(response)
        # Except if client is disconnected (specific exception)
        except Exception as e:
            logging.warn(f"Failed to send to client: {e}")
            app.connected_clients.remove(client)
            client.close(reason="Failed to receive data")
    return None

@sock.route('/ws')
def websocket_handler(ws):
    if not hasattr(app, 'connected_clients'):
        app.connected_clients = set()

    if ws in app.connected_clients:
        ws.close(reason="Already connected. Begone!")
        return
    
    app.connected_clients.add(ws)
    logging.info(f"Client connected. Total: {len(app.connected_clients)}")

    try:
        while True:
            message = ws.receive()
            if message is None:
                raise ConnectionAbortedError("No data received")

            # Handle the `getMatrix` command
            if message.strip() == "getMatrix":
                response = json.dumps({"matrix": matrix})
                ws.send(response)

            # Handle the `setPixel` command
            elif message.startswith("setPixel"):
                try:
                    _, x, y, color = message.split(',')
                    x, y, color = int(x), int(y), int(color)

                    if not __is_valid_coordinate(x, y):
                        raise ValueError("Invalid coordinates")
                    if not __is_valid_color(color):
                        raise ValueError("Invalid color")

                    matrix[y][x] = color

                    response = json.dumps({"matrix": matrix})
                    broadcast_matrix(app.connected_clients)

                except ValueError as ve:
                    error_response = json.dumps({
                        "status": "error",
                        "message": str(ve)
                    })
                    ws.send(error_response)
                except Exception as e:
                    raise ConnectionAbortedError("Hell no. Whatever you sent is not it.")
            else:
                raise ConnectionAbortedError("You can't do that!")
           
    except ConnectionAbortedError as cae:
        ws.close(reason=str(cae))
         
    except Exception as e:
        if ("1001" or "1006") not in str(e):
            logging.error(f"WebSocket connection error: {e}")
    finally:
        # Cleanup when the client disconnects
        logging.info(f"Client disconnected. Total: {len(app.connected_clients)}")
        if ws in app.connected_clients:
            app.connected_clients.remove(ws)

if __name__ == "__main__":
    app.run(port=5000, debug=True)