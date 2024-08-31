import { useEffect, useState } from 'react';
import Grid from './Grid';
import useWebSocket from 'react-use-websocket';

const SERVER_URL = 'ws://127.0.0.1:5000/ws';

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
    <div style={appContainerStyle}>
      {/* Sticky Header */}
      <header style={headerStyle}>
        <div style={leftContainerStyle}>
          <img src="/chippy.png" alt="icon" style={faviconStyle} />
          <span style={titleStyle}>Platrix</span>
        </div>
        <div style={rightContainerStyle}>
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
      <div style={gridOuterContainerStyle}>
        <div style={zoomContainerStyle}>
          <Grid
            width={64}
            height={32}
            matrix={matrix}
            setPixel={setPixel}
          />
        </div>
      </div>
    </div>
  );
}

export default App;


// These need fixing :arrow_down:
const appContainerStyle: React.CSSProperties = {
  display: 'flex',
  flexDirection: 'column',
  height: '100vh',
  width: '100vw',
  margin: 0,
  padding: 0,
  overflow: 'hidden',
};

const gridOuterContainerStyle: React.CSSProperties = {
  flexGrow: 1,
  marginTop: '2.5rem', 
  overflow: 'auto',
};

const zoomContainerStyle: React.CSSProperties = {
  transform: 'scale(2)', 
  transformOrigin: 'top left',
  display: 'inline-block',
};

const headerStyle: React.CSSProperties = {
  position: 'fixed',
  top: 0,
  left: 0,
  right: 0,
  backgroundColor: '#333',
  color: 'white',
  display: 'flex',
  justifyContent: 'space-between',
  alignItems: 'center',
  padding: '0.5rem 1rem',
  zIndex: 1000,
  boxSizing: 'border-box',
  height: '2.5rem',
  borderBottom: '1px solid #444',
};

const leftContainerStyle: React.CSSProperties = {
  display: 'flex',
  alignItems: 'center',
};

const rightContainerStyle: React.CSSProperties = {
  display: 'flex',
  alignItems: 'center',
};

const faviconStyle: React.CSSProperties = {
  width: '1.5rem',
  height: '1.5rem',
  marginRight: '0.5rem',
};

const titleStyle: React.CSSProperties = {
  fontSize: '1.2rem',
  fontWeight: 'bold',
};
