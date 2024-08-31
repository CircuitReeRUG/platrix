import Grid from './Grid';

import useWebSocket from 'react-use-websocket';

const SERVER_URL = 'ws://127.0.0.1:8800/ws';

function App() {
  const {
    sendMessage,
    lastMessage,
    lastJsonMessage,
    readyState,
    getWebSocket,
  } = useWebSocket(SERVER_URL, {
    onOpen: () => {
      console.log('WebSocket connected.');
      sendMessage("getMatrix");
    },
    share: true,
    shouldReconnect: (closeEvent) => true,
    reconnectAttempts: 10,
    reconnectInterval: 3000,
    filter: (message) => {
      console.log(message);
    }
  });

  return (
    <>
      <h1>platrix</h1>
      <Grid height={32} width={64} />
    </>
  )
}

export default App;
