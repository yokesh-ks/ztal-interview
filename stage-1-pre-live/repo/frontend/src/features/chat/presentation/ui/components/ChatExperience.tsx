import { useState } from "react";
import { CopilotKit } from "@copilotkit/react-core";
import { CopilotChat } from "@copilotkit/react-ui";
import "@copilotkit/react-ui/styles.css";

import { CHAT_REQUESTERS, DEFAULT_CHAT_REQUESTER_ID } from "../../constants/chatExperience";

type ChatExperienceProps = {
  endpoint: string;
};

export function ChatExperience({ endpoint }: ChatExperienceProps) {
  const [requesterId, setRequesterId] = useState(DEFAULT_CHAT_REQUESTER_ID);

  const runtimeUrl = (() => {
    try {
      const url = new URL(endpoint);
      return `${url.protocol}//${url.host}/api/copilotkit`;
    } catch {
      return "http://127.0.0.1:8000/api/copilotkit";
    }
  })();

  return (
    <section>
      <label htmlFor="requester-select">Requester</label>
      <select
        id="requester-select"
        value={requesterId}
        onChange={(e) => setRequesterId(e.target.value)}
      >
        {CHAT_REQUESTERS.map((requester) => (
          <option key={requester.id} value={requester.id}>
            {requester.label}
          </option>
        ))}
      </select>

      <CopilotKit
        key={requesterId}
        runtimeUrl={runtimeUrl}
        headers={{ "X-Requester-Id": requesterId }}
      >
        <CopilotChat
          instructions="You are a recruiting assistant. You can list open jobs, show candidates for a job (provide the job ID), find stalled candidates in screening, and summarize the candidate pipeline."
          labels={{
            title: "Recruiting Assistant",
            initial:
              "Hello! I can help with open jobs, candidates, stalled screening, and candidate summaries. What would you like to know?",
          }}
        />
      </CopilotKit>
    </section>
  );
}
