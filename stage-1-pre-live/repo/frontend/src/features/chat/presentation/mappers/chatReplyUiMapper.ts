import type { ChatReply } from "../../domain/models/ChatModels";
import type { ChatMessageUi } from "../models/ChatMessageUi";

export function toChatMessageUi(reply: ChatReply): ChatMessageUi {
  return {
    id: reply.requestId,
    body: reply.answer,
    badges: reply.containsCompensation ? ["Compensation"] : []
  };
}

