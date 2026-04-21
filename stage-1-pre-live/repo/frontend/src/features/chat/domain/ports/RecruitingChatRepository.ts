import type { ChatReply, ChatRequest } from "../models/ChatModels";

export interface RecruitingChatRepository {
  sendMessage(request: ChatRequest): Promise<ChatReply>;
}

