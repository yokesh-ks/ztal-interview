import type { ChatReply } from "../../domain/types/model/ChatModels";
import type { ChatMessageUi } from "../types/ui/ChatMessageUi";

export function toChatMessageUi(reply: ChatReply): ChatMessageUi {
  return {
    id: reply.requestId,
    body: reply.answer,
    badges: reply.containsCompensation ? ["Compensation"] : []
  };
}

