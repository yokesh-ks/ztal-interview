import { createContext, useContext, useMemo, type ReactNode } from "react";

import { HttpRecruitingChatRepository } from "@/features/chat/data/repositories/HttpRecruitingChatRepository";
import { SendChatMessageUseCase } from "@/features/chat/domain/usecases/SendChatMessageUseCase";

type ChatDependencies = {
  sendChatMessageUseCase: SendChatMessageUseCase;
};

const ChatDependenciesContext = createContext<ChatDependencies | null>(null);

type ChatDependenciesProviderProps = {
  children: ReactNode;
  endpoint: string;
};

export function ChatDependenciesProvider({
  children,
  endpoint
}: ChatDependenciesProviderProps) {
  const value = useMemo<ChatDependencies>(() => {
    const repository = new HttpRecruitingChatRepository(endpoint);

    return {
      sendChatMessageUseCase: new SendChatMessageUseCase(repository)
    };
  }, [endpoint]);

  return <ChatDependenciesContext.Provider value={value}>{children}</ChatDependenciesContext.Provider>;
}

export function useInjectedSendChatMessageUseCase(): SendChatMessageUseCase {
  const dependencies = useContext(ChatDependenciesContext);

  if (!dependencies) {
    throw new Error("ChatDependenciesProvider is missing from the component tree.");
  }

  return dependencies.sendChatMessageUseCase;
}

