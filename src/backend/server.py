from flask import Flask, jsonify
import flask_sock
import json
from time import sleep
import logging
from rgbmatrix import RGBMatrix, RGBMatrixOptions
from PIL import Image
import os

USING_MATRIX = True # CHANGE THIS TO FALSE IF TESTING
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
    options.disable_hardware_pulsing = True

    matrix = RGBMatrix(options = options)
    matrix.Fill(0, 0, 0) # Fill the matrix with black color

matrix_data = [[0 for _ in range(M_WIDTH)] for _ in range(M_HEIGHT)]

def encode_color(r:int, g:int, b:int) -> int:
    return (r << 16) | (g << 8) | b

def decode_color(color:int) -> tuple[int,int,int]:
    r = (color >> 16) & 0xFF
    g = (color >> 8) & 0xFF
    b = color & 0xFF
    return r, g, b

ORDER = ("R","B","G")

def _apply_order(r:int,g:int,b:int) -> tuple[int,int,int]:
    return tuple({"R": r, "G": g, "B": b}[c] for c in ORDER)

def __update_pixel(x:int, y:int, color:int) -> None:
    matrix_data[y][x] = color
    if USING_MATRIX:
        r, g, b = decode_color(color)
        hr, hg, hb = _apply_order(r,g,b)
        matrix.SetPixel(x, y, hr, hg, hb)
    return None

def __is_valid_coordinate(x:int, y:int) -> bool:
    return 0 <= x < M_WIDTH and 0 <= y < M_HEIGHT

def __is_valid_color(color:int) -> bool:
    return 0 <= color <= 0xFFFFFF

def load_image(path:str) -> list[list[int]]:
    img = Image.open(path).convert("RGB")

    for y in range(M_HEIGHT):
        for x in range(M_WIDTH):
            r, g, b = img.getpixel((x, y))
            if USING_MATRIX:
                hr, hg, hb = _apply_order(r,g,b)
                matrix.SetPixel(x, y, hr, hg, hb)


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


def test_matrix():
    if not USING_MATRIX:
        return None
    # flash r,g,b and white
    colors = [(255, 0, 0), (0, 0, 255), (0, 255, 0), (255, 255, 255)]
    for color in colors:
        matrix.Fill(color[0], color[1], color[2])
        sleep(0.3)
    matrix.Fill(0, 0, 0)
    
    # flash splash screens
    for splash in os.listdir("img"):
        load_image(os.path.join("img", splash))
        sleep(3)
        
    matrix.Fill(0, 0, 0)
    
    return None

if __name__ == "__main__":
    test_matrix()
    app.run(host="0.0.0.0", port=5000)
