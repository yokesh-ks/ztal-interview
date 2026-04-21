import { describe, expect, it, vi } from "vitest";

import { SendChatMessageUseCase } from "../../../src/features/chat/domain/usecases/SendChatMessageUseCase";
import type { RecruitingChatRepository } from "../../../src/features/chat/domain/ports/RecruitingChatRepository";

describe("SendChatMessageUseCase", () => {
  it("delegates to the repository", async () => {
    const repository: RecruitingChatRepository = {
      sendMessage: vi.fn().mockResolvedValue({
        requestId: "req-1",
        answer: "Visible open jobs: J1001",
        containsCompensation: false
      })
    };

    const useCase = new SendChatMessageUseCase(repository);
    const result = await useCase.execute({
      requesterId: "U003",
      message: "List my open jobs"
    });

    expect(repository.sendMessage).toHaveBeenCalledWith({
      requesterId: "U003",
      message: "List my open jobs"
    });
    expect(result.answer).toBe("Visible open jobs: J1001");
  });
});

