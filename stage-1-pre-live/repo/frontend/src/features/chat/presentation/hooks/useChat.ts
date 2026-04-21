import { useState } from "react";

import type { ChatReply } from "../../domain/models/ChatModels";
import { useInjectedSendChatMessageUseCase } from "@/shared/di";

const STORAGE_KEY = "recruiting-chat:last-reply";

export function useChat() {
  const [messages, setMessages] = useState<ChatReply[]>(() => {
    const cachedValue = sessionStorage.getItem(STORAGE_KEY);
    if (!cachedValue) {
      return [];
    }

    try {
      return JSON.parse(cachedValue) as ChatReply[];
    } catch {
      return [];
    }
  });
  const [isLoading, setIsLoading] = useState(false);
  const sendChatMessageUseCase = useInjectedSendChatMessageUseCase();

  async function sendMessage(requesterId: string, message: string) {
    setIsLoading(true);
    const reply = await sendChatMessageUseCase.execute({ requesterId, message });
    const nextMessages = [...messages, reply];
    setMessages(nextMessages);
    sessionStorage.setItem(STORAGE_KEY, JSON.stringify(nextMessages));
    setIsLoading(false);
  }

  return {
    messages,
    isLoading,
    sendMessage
  };
}
