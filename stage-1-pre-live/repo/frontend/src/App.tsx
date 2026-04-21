import { ChatExperience } from "./features/chat/presentation/ui/components/ChatExperience";

const CHAT_ENDPOINT =
  import.meta.env.VITE_CHAT_ENDPOINT ?? "http://127.0.0.1:8000/api/chat/reply";

export function App() {
  return (
    <main className="app-shell">
      <header className="hero">
        <p className="eyebrow">Assignment Demo</p>
        <h1>Recruiting Chat</h1>
        <p className="subtitle">Explore requester-aware recruiting data through the existing chat shell.</p>
      </header>

      <ChatExperience endpoint={CHAT_ENDPOINT} />
    </main>
  );
}
