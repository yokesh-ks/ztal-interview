import { useState } from "react";
import { Header } from "./features/chat/presentation/ui/components/Header";
import { ChatExperience } from "./features/chat/presentation/ui/components/ChatExperience";
import { DEFAULT_CHAT_REQUESTER_ID } from "./features/chat/presentation/constants/chatExperience";
import "./styles.css";

const CHAT_ENDPOINT =
  import.meta.env.VITE_CHAT_ENDPOINT ?? "http://127.0.0.1:8000/api/chat/reply";

export function App() {
  const [requesterId, setRequesterId] = useState(DEFAULT_CHAT_REQUESTER_ID);

  return (
    <div className="app-shell">
      <Header requesterId={requesterId} onRequesterChange={setRequesterId} />
      <div className="chat-wrapper">
        <ChatExperience endpoint={CHAT_ENDPOINT} requesterId={requesterId} />
      </div>
    </div>
  );
}
