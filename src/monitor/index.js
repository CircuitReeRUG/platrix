const fs = require('fs');
const process = require('process');

let url = 'ws://localhost:8800/ws';
const outFile = 'pixel-timelapse.log';
const reconnectAfter = 1000;

let ws;
let storage;

function connect() {
    console.log(`connecting to: ${url}`)
    ws = new WebSocket(url)

    // Set timeout for reconnect and cancel it on successfull open
    let reconnectSoon = setTimeout(connect, reconnectAfter)
    ws.onopen = function() {
        clearTimeout(reconnectSoon);
    }

    ws.addEventListener('message', (event) => {
        const timestamp = Math.floor(Date.now() / 1000);
        console.log(`${timestamp} Pixel updated`);
        storage.write(timestamp + " " + event.data + "\n")
    });
    ws.addEventListener('close', event => {
        console.log(`Disconnected [${event.code}].`)
        // Endless reconnect
        if (!event.wasClean) {
            connect()
        }
    })
}

// Try to play nice and close the file on ^C
let exiting = false;
process.on('SIGINT', function() {
    if (!exiting) {
        storage.end();
        ws.close();
        process.exit();
    }
    exiting = true;
});

// Read optional first argument as websocket server url
if (process.argv.length > 2) {
    url = process.argv[2]
    if (!url.startsWith('ws://') || !url.startsWith('wss://')) {
        url = 'ws://' + url
    }
}

// Open log file for recording
storage = fs.createWriteStream(outFile, {flags: 'a'});

connect()

