import { useState } from "react";

import type { ChatMessageUi } from "../types/ui/ChatMessageUi";
import { toChatMessageUi } from "../mappers/chatReplyUiMapper";
import { useInjectedSendChatMessageUseCase } from "@/shared/di";

export function useChat(requesterId: string) {
  const [messages, setMessages] = useState<ChatMessageUi[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const sendChatMessageUseCase = useInjectedSendChatMessageUseCase();

  async function submitChatQuery(message: string) {
    try {
      setIsLoading(true);
      const reply = await sendChatMessageUseCase.execute({
        requesterId,
        message
      });
      setMessages((previousMessages) => [...previousMessages, toChatMessageUi(reply)]);
    } finally {
      setIsLoading(false);
    }
  }

  return {
    messages,
    isLoading,
    submitChatQuery
  };
}
