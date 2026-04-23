import type { ChatReply, ChatRequest } from "../types/model/ChatModels";

export interface RecruitingChatRepository {
  sendMessage(request: ChatRequest): Promise<ChatReply>;
}

