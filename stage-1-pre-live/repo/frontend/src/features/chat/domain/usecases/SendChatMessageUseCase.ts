import type { ChatReply, ChatRequest } from "../types/model/ChatModels";
import type { RecruitingChatRepository } from "../ports/RecruitingChatRepository";

export class SendChatMessageUseCase {
  constructor(private readonly repository: RecruitingChatRepository) {}

  async execute(request: ChatRequest): Promise<ChatReply> {
    return this.repository.sendMessage(request);
  }
}

