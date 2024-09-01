import { useEffect, useState } from 'react';
import Grid from './Grid';
import useWebSocket from 'react-use-websocket';
import chippy from './assets/chippy.png';

const SERVER_URL = 'ws://192.168.0.100:5000/ws';

function App() {
  // Initialize ws connection
  const { sendMessage, lastJsonMessage, readyState } = useWebSocket(SERVER_URL, {
    onOpen: () => {
      console.log('WebSocket connected.');
      sendMessage('getMatrix');
    },
    onClose: () => console.log('WebSocket disconnected.'),
    shouldReconnect: () => true,
    reconnectAttempts: 10,
    reconnectInterval: 3000,
  });

  const [matrix, setMatrix] = useState(
    Array(32).fill(Array(64).fill({ r: 0, g: 0, b: 0 }))
  );

  // Update matrix
  useEffect(() => {
    if (lastJsonMessage && lastJsonMessage.matrix) {
      setMatrix(lastJsonMessage.matrix);
      // DEBUG :3
      // console.log(`Received matrix: ${lastJsonMessage.matrix}`);
    }
  }, [lastJsonMessage]);

  // Set a pixel color via WebSocket
  const setPixel = (x: number, y: number, color: number) => {
    if (readyState === WebSocket.OPEN) {
      sendMessage(`setPixel,${x},${y},${color}`);
    } else {
      console.error('WebSocket is not open.');
    }
  };

  // Determine ws connection status and set color
  const getStatusColor = () => {
    switch (readyState) {
      case WebSocket.OPEN:
        return 'green';
      case WebSocket.CONNECTING:
        return 'orange';
      case WebSocket.CLOSING:
        return 'red';
      case WebSocket.CLOSED:
        return 'gray';
      default:
        return 'gray';
    }
  };

  return (
    <article id="appContainer">
      {/* Sticky Header */}
      <header id="appHeader">
        <div id="appTitle">
          <img src={chippy} alt="chippy" />
          <h1>Platrix</h1>
        </div>
        <div id="appStatus">
          <span style={{ color: getStatusColor() }}>
            {readyState === WebSocket.OPEN
              ? 'Connected'
              : readyState === WebSocket.CONNECTING
              ? 'Connecting...'
              : readyState === WebSocket.CLOSING
              ? 'Closing...'
              : 'Disconnected'}
          </span>
        </div>
      </header>

      {/* Grid Container with Zoom */}
      <section id="gridContainer" className={readyState === WebSocket.OPEN ? "ready"  : "not-ready"}>
        <div id="gridInner">
          <Grid
            width={64}
            height={32}
            matrix={matrix}
            setPixel={setPixel}
          />
        </div>
      </section>
    </article>
  );
}

export default App;
