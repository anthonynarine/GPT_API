
import { Route, Routes } from "react-router-dom";
import ChatComponent from './chat/ChatComponent';

function App() {
  return (
    <>
      <Routes>
        <Route path="/" element={<ChatComponent />} />
      </Routes>
    </>
  );
}

export default App;
