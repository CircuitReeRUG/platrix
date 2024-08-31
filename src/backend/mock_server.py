from flask import Flask, request, jsonify
from flask_sock import Sock
import json

app = Flask(__name__)
sock = Sock(app)

# Initialize a 64x32 matrix filled with zeros (representing black color)
PANEL_WIDTH = 64
PANEL_HEIGHT = 32
matrix = [[0 for _ in range(PANEL_HEIGHT)] for _ in range(PANEL_WIDTH)]

# Utility function to check if coordinates are within the matrix bounds
def is_valid_coordinate(x, y):
    return 0 <= x < PANEL_WIDTH and 0 <= y < PANEL_HEIGHT

# Utility function to check if the color is valid (0 to 16777215)
def is_valid_color(color):
    return 0 <= color <= 16777215

# HTTP endpoint to get the current state of the matrix
@app.route('/getMatrix', methods=['GET'])
def get_matrix():
    return jsonify({"matrix": matrix}), 200

@app.route('/setPixel', methods=['POST'])
def set_pixel():
    data = request.json
    x = int(data.get('x', -1))
    y = int(data.get('y', -1))
    color = int(data.get('color', -1))
    
    if not is_valid_coordinate(x, y) or not is_valid_color(color):
        return jsonify({"status": "error", "message": "invalid"}), 400

    matrix[x][y] = color
    return jsonify({"status": "success"}), 200

@sock.route('/ws')
def ws_handler(ws):
    while True:
        data = ws.receive()
        try:
            if data == "getMatrix":
                # Handle getMatrix request
                response = {"matrix": matrix}
                ws.send(json.dumps(response))
            else:
                # Handle setPixel request
                parts = data.split(',')
                if len(parts) != 4 or parts[0] != 'setPixel':
                    raise ValueError("Invalid message format")
                
                x = int(parts[1])
                y = int(parts[2])
                color = int(parts[3])

                if not is_valid_coordinate(x, y) or not is_valid_color(color):
                    ws.send(json.dumps({"status": "error", "message": "invalid"}))
                    continue

                matrix[x][y] = color
                ws.send(json.dumps({"status": "success"}))
        except Exception as e:
            ws.send(json.dumps({"status": "error", "message": "invalid"}))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
