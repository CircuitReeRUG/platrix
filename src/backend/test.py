# Tests the functionality of the ESP32 webserver
# We are assuming a 64x32 matrix

import unittest
from os import environ
import requests
import websocket
import json
import time

PORT = 5000
IP = "localhost"

class TestESP32WebServer(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.base_url = f'http://{IP}:{PORT}'
        cls.ws_url = f'ws://{IP}:{PORT}/ws'

    def test_get_matrix_http(self):
        response = requests.get(self.base_url + '/getMatrix')
        self.assertEqual(response.status_code, 200)
        self.assertTrue(isinstance(response.json(), dict))
        self.assertIn('matrix', response.json())

    def test_set_pixel_http(self):
        # valid parameters
        payload = {'x': '10', 'y': '10', 'color': '16711680'}
        response = requests.post(self.base_url + '/setPixel', json=payload)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"status": "success"})

        # invalid parameters
        payload_invalid = {'x': '100', 'y': '100', 'color': '16777216'} 
        response_invalid = requests.post(self.base_url + '/setPixel', json=payload_invalid)
        self.assertEqual(response_invalid.status_code, 400)
        self.assertEqual(response_invalid.json()["status"], "error")

    def test_websocket_get_matrix(self):
        # getMatrix
        ws = websocket.create_connection(self.ws_url)
        ws.send("getMatrix")
        result = ws.recv()
        response = json.loads(result)
        self.assertTrue(isinstance(response, dict))
        self.assertIn('matrix', response)
        ws.close()

    def test_websocket_set_pixel(self):
        # valid parameters
        ws = websocket.create_connection(self.ws_url)
        ws.send("setPixel,10,10,16711680")
        result = ws.recv()
        response = json.loads(result)
        self.assertEqual(response["status"], "success")

        # invalid parameters
        ws.send("setPixel,100,100,16777216")
        result_invalid = ws.recv()
        response_invalid = json.loads(result_invalid)
        self.assertEqual(response_invalid["status"], "error")
        ws.close()
        
    # def test_set_matrix_to_white(self):
    #     ws = websocket.create_connection(self.ws_url)
    #     for x in range(64):
    #         for y in range(32):
    #             ws.send(f"setPixel,{x},{y},16777215")
    #             time.sleep(0.01)
                
    #     ws.close()
        
    # def test_set_matrix_to_black(self):
    #     ws = websocket.create_connection(self.ws_url)
    #     for x in range(64):
    #         for y in range(32):
    #             ws.send(f"setPixel,{x},{y},0")
    #             time.sleep(0.01)
                
    #     ws.close()

if __name__ == '__main__':
    unittest.main()
