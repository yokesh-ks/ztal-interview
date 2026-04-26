import { CopilotKit } from "@copilotkit/react-core";
import { CopilotChat } from "@copilotkit/react-ui";
import "@copilotkit/react-ui/styles.css";

type ChatExperienceProps = {
  endpoint: string;
  requesterId: string;
};

/**
 * ChatExperience
 *
 * Renders the CopilotKit chat shell scoped to the given requesterId.
 * Requester selection is handled upstream in <Header /> so this component
 * stays focused on the chat UI only.
 */
export function ChatExperience({ endpoint, requesterId }: ChatExperienceProps) {
  const runtimeUrl = (() => {
    try {
      const url = new URL(endpoint);
      return `${url.protocol}//${url.host}/api/copilotkit`;
    } catch {
      return "http://127.0.0.1:8000/api/copilotkit";
    }
  })();

  return (
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
  );
}
