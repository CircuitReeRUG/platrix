from flask import Flask, jsonify
import flask_sock
import json
from time import sleep
import logging
from rgbmatrix import RGBMatrix, RGBMatrixOptions

USING_MATRIX = False
M_WIDTH = 64
M_HEIGHT = 32
M_CHAIN = 1

app = Flask(__name__)
sock = flask_sock.Sock(app)

# set logging level
logging.basicConfig(level=logging.INFO)

# Set Matrix dimensions
if USING_MATRIX:
    options = RGBMatrixOptions()
    options.rows = M_HEIGHT
    options.cols = M_WIDTH
    options.chain_length = M_CHAIN
    options.parallel = 1
    options.hardware_mapping = 'regular'

    matrix = RGBMatrix(options = options)
    matrix.Fill(0, 0, 0) # Fill the matrix with black color

matrix_data = [[0 for _ in range(M_WIDTH)] for _ in range(M_HEIGHT)]

def __update_pixel(x:int, y:int, color:int) -> None:
    matrix_data[y][x] = color
    if USING_MATRIX:
        matrix.SetPixel(x, y, (color >> 16) & 0xFF, (color >> 8) & 0xFF, color & 0xFF)
    return None

def __is_valid_coordinate(x:int, y:int) -> bool:
    return 0 <= x < options.rows and 0 <= y < options.cols

def __is_valid_color(color:int) -> bool:
    return 0 <= color <= 16777215 # 0xFFFFFF

def broadcast_matrix(connected_clients:set) -> None:
    """Broadcasts the current matrix to all connected clients.
    """
    for client in app.connected_clients:
        try:
            response = json.dumps({"matrix": matrix_data})
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
                response = json.dumps({"matrix": matrix_data})
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

                    __update_pixel(x, y, color)

                    response = json.dumps({"matrix": matrix_data})
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