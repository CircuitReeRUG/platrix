# Platrix!

## Overview

Inspired by r/place. Allows users to manipulate pixel colors on LED matrices in real time. The system supports commands to retrieve the current state of the matrix and set individual pixel colors. The application is built using ESP32 with an asynchronous web server.

Made for the [Cover Committee Market 2024](https://svcover.nl/calendar?agenda_id=4557)

## TODOs
- [x] Barebones WS API
- [x] Barebones frontend
- [ ] Frontend fixes
  - [ ] ~~Make it look good~~
  - [ ] Remove trailing space after grid, better yet, make the grid be the whole page
  - [ ] Figure out a way to make FUCKING chrome's color picker BEHAVE (it's sending a setPixel each time it moves a mm)
  - [ ] Display funny images on the board while disconnected
  - [ ] Display timeout (top bar + lightly dimmed body for example)
  - [ ] Add a minimap (maybe? probably not.)

- [ ] Backend fixes
  - [ ] Test on actual hardware
  - [ ] Implement timeout
  - [ ] Test concurrency and fix (i know there's gonna be problems)

- [ ] Deployment (farrrr from it)
  - [ ] OH NOOOOOOOOOOOOOOOO WE GOTTA DO REVERSE PROXYING ON TOP OF AN SSH TUNNEL ON DATA 
    - it's ok we can always go back to people joining our wifi 

- [Platrix!](#platrix)
  - [Overview](#overview)
  - [TODOs](#todos)
  - [ToC](#toc)
  - [Endpoints](#endpoints)
    - [/getMatrix](#getmatrix)
      - [Request](#request)
      - [Response](#response)
    - [/setPixel](#setpixel)
      - [Request](#request-1)
      - [Response](#response-1)
    - [Dependencies and Setup](#dependencies-and-setup)

---

## Endpoints

When interacting with the API through WS, just prepend the endpoint with `/ws` and use the WebSocket protocol.

### /getMatrix

**Description**: Retrieves the current state of the matrix in a JSON format.

#### Request
No request body is required.

#### Response

```json
{
  "matrix": [
    [16777215, 0, 0, 16711680],
    [0, 255, 0, 0],
    [0, 0, 65280, 0],
    [0, 0, 0, 255]
  ]
}
```

- **matrix**: A 2D array representing the matrix, where each value is a packed 32-bit RGB color.

### /setPixel

**Description**: Sets the color of a specific pixel on the matrix.

#### Request

```json
{
  "x": 1,
  "y": 2,
  "color": 16711680
}
```

- **x**: X-coordinate of the pixel.
- **y**: Y-coordinate of the pixel.
- **color**: The color in packed 32-bit RGB format.

#### Response

**Success:**

```json
{
  "status": "success"
}
```

**Error:**

```json
{
  "status": "error",
  "message": "invalid"
}
```

- **message**: Pretty useless error message.
---

### Dependencies and Setup

- **Arduino Libraries**: 
  - `WiFi.h`: For WiFi connectivity.
  - `AsyncTCP.h` and `ESPAsyncWebServer.h`: For setting up async WebSocket server.
  - `matrix.h`: Custom library for matrix manipulation.
- **Constants**:
  - `PANEL_WIDTH`, `PANEL_HEIGHT`, `CHAIN_LENGTH`: Define the dimensions of the LED matrix.

Then, you just flash the thing and connect it to the according pins and you're good to go!

