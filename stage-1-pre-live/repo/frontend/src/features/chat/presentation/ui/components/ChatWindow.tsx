import type { ChatMessageUi } from "../../types/ui/ChatMessageUi";

type ChatWindowProps = {
  messages: ChatMessageUi[];
  isLoading: boolean;
};

export function ChatWindow({ messages, isLoading }: ChatWindowProps) {
  return (
    <section>
      <h2>Recruiting Assistant</h2>
      {isLoading ? <p>Thinking...</p> : null}
      <ul>
        {messages.map((message) => (
          <li key={message.id}>
            <p>{message.body}</p>
            {message.badges.length > 0 ? (
              <ul>
                {message.badges.map((badge) => (
                  <li key={badge}>{badge}</li>
                ))}
              </ul>
            ) : null}
          </li>
        ))}
      </ul>
    </section>
  );
}

