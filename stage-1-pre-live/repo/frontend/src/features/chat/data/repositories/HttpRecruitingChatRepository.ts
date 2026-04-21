import type { ChatReply, ChatRequest } from "../../domain/models/ChatModels";
import type { RecruitingChatRepository } from "../../domain/ports/RecruitingChatRepository";

export class HttpRecruitingChatRepository implements RecruitingChatRepository {
  constructor(private readonly endpoint: string) {}

  async sendMessage(request: ChatRequest): Promise<ChatReply> {
    const response = await fetch(this.endpoint, {
      method: "POST",
      headers: {
        "Content-Type": "application/json"
      },
      body: JSON.stringify({
        requester_id: request.requesterId,
        message: request.message
      })
    });

    if (!response.ok) {
      throw new Error("Unable to send message");
    }

    return response.json() as Promise<ChatReply>;
  }
}

