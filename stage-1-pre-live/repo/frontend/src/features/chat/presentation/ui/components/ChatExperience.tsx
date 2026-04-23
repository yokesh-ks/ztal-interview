import { useState } from "react";

import { CHAT_REQUESTERS, DEFAULT_CHAT_REQUESTER_ID, CHAT_VISIBLE_JOBS_QUERY } from "../../constants/chatExperience";
import { useChat } from "../../hooks/useChat";
import { ChatWindow } from "./ChatWindow";
import { ChatDependenciesProvider } from "@/shared/di";

type ChatExperienceProps = {
  endpoint: string;
};

export function ChatExperience({ endpoint }: ChatExperienceProps) {
  const [requesterId, setRequesterId] = useState(DEFAULT_CHAT_REQUESTER_ID);

  return (
    <ChatDependenciesProvider endpoint={endpoint}>
      <ChatExperienceContent
        key={requesterId}
        requesterId={requesterId}
        setRequesterId={setRequesterId}
      />
    </ChatDependenciesProvider>
  );
}

type ChatExperienceContentProps = {
  requesterId: string;
  setRequesterId: (requesterId: string) => void;
};

function ChatExperienceContent({
  requesterId,
  setRequesterId
}: ChatExperienceContentProps) {
  const { messages, isLoading, submitChatQuery } = useChat(requesterId);

  return (
    <section>
      <label htmlFor="requester-select">Requester</label>
      <select
        id="requester-select"
        value={requesterId}
        onChange={(event) => setRequesterId(event.target.value)}
      >
        {CHAT_REQUESTERS.map((requester) => (
          <option key={requester.id} value={requester.id}>
            {requester.label}
          </option>
        ))}
      </select>

      <button type="button" onClick={() => void submitChatQuery(CHAT_VISIBLE_JOBS_QUERY)}>
        Query visible jobs
      </button>

      <ChatWindow messages={messages} isLoading={isLoading} />
    </section>
  );
}
