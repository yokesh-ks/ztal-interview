import { useState } from "react";

import { useChat } from "../../hooks/useChat";
import { ChatWindow } from "./ChatWindow";
import { ChatDependenciesProvider } from "@/shared/di";

type ChatExperienceProps = {
  endpoint: string;
};

const REQUESTERS = [
  { id: "U001", label: "Priya Raman" },
  { id: "U002", label: "Raj Malhotra" },
  { id: "U003", label: "Anika Shah" },
  { id: "U004", label: "Neha Iyer" },
  { id: "U005", label: "Omar Khan" },
  { id: "U006", label: "Sara Ali" }
];

export function ChatExperience({ endpoint }: ChatExperienceProps) {
  const [requesterId, setRequesterId] = useState("U002");

  return (
    <ChatDependenciesProvider endpoint={endpoint}>
      <ChatExperienceContent
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
  const { messages, isLoading, sendMessage } = useChat();

  return (
    <section>
      <label htmlFor="requester-select">Requester</label>
      <select
        id="requester-select"
        value={requesterId}
        onChange={(event) => setRequesterId(event.target.value)}
      >
        {REQUESTERS.map((requester) => (
          <option key={requester.id} value={requester.id}>
            {requester.label}
          </option>
        ))}
      </select>

      <button type="button" onClick={() => void sendMessage(requesterId, "List my open jobs")}>
        Query visible jobs
      </button>

      <ChatWindow messages={messages} isLoading={isLoading} />
    </section>
  );
}
