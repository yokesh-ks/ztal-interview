import { useState } from "react";

import type { ChatReply } from "../../domain/models/ChatModels";
import { useInjectedSendChatMessageUseCase } from "@/shared/di";

export function useChat(requesterId: string) {
  const [messages, setMessages] = useState<ChatReply[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const sendChatMessageUseCase = useInjectedSendChatMessageUseCase();

  async function sendMessage(requesterId: string, message: string) {
    try {
      setIsLoading(true);
      const reply = await sendChatMessageUseCase.execute({ requesterId, message });
      setMessages((previousMessages) => [...previousMessages, reply]);
    } finally {
      setIsLoading(false);
    }
  }

  return {
    messages,
    isLoading,
    sendMessage
  };
}
