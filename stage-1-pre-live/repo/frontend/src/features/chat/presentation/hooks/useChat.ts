import { useEffect, useState } from "react";

import type { ChatReply } from "../../domain/models/ChatModels";
import { useInjectedSendChatMessageUseCase } from "@/shared/di";

const STORAGE_KEY_PREFIX = "recruiting-chat:last-reply";

function getStorageKey(requesterId: string) {
  return `${STORAGE_KEY_PREFIX}:${requesterId}`;
}

function loadMessages(requesterId: string) {
  const cachedValue = sessionStorage.getItem(getStorageKey(requesterId));
  if (!cachedValue) {
    return [];
  }

  try {
    return JSON.parse(cachedValue) as ChatReply[];
  } catch {
    return [];
  }
}

export function useChat(requesterId: string) {
  const [messages, setMessages] = useState<ChatReply[]>(() => loadMessages(requesterId));
  const [isLoading, setIsLoading] = useState(false);
  const sendChatMessageUseCase = useInjectedSendChatMessageUseCase();

  useEffect(() => {
    setMessages(loadMessages(requesterId));
  }, [requesterId]);

  async function sendMessage(requesterId: string, message: string) {
    try {
      setIsLoading(true);
      const reply = await sendChatMessageUseCase.execute({ requesterId, message });
      setMessages((previousMessages) => {
        const nextMessages = [...previousMessages, reply];
        sessionStorage.setItem(getStorageKey(requesterId), JSON.stringify(nextMessages));
        return nextMessages;
      });
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
