import type { ChatReply } from "../../../domain/models/ChatModels";

type ChatWindowProps = {
  messages: ChatReply[];
  isLoading: boolean;
};

export function ChatWindow({ messages, isLoading }: ChatWindowProps) {
  return (
    <section>
      <h2>Recruiting Assistant</h2>
      {isLoading ? <p>Thinking...</p> : null}
      <ul>
        {messages.map((message) => (
          <li key={message.requestId}>
            <p>{message.answer}</p>
            {message.containsCompensation ? <span>Compensation</span> : null}
          </li>
        ))}
      </ul>
    </section>
  );
}

