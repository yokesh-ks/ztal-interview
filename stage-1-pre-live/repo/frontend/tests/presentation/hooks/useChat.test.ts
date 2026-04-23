import { renderHook, act, waitFor } from "@testing-library/react";
import { beforeEach, describe, expect, it, vi } from "vitest";

const mockExecute = vi.fn();

vi.mock("@/shared/di", () => ({
  useInjectedSendChatMessageUseCase: () => ({
    execute: mockExecute
  })
}));

import { CHAT_VISIBLE_JOBS_QUERY } from "../../../src/features/chat/presentation/constants/chatExperience";
import { useChat } from "../../../src/features/chat/presentation/hooks/useChat";

describe("useChat", () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it("maps chat replies to Ui messages and sends the visible jobs query", async () => {
    mockExecute.mockResolvedValueOnce({
      requestId: "req-1",
      answer: "Visible open jobs: J1001",
      containsCompensation: true
    });

    const { result } = renderHook(() => useChat("U001"));

    await act(async () => {
      await result.current.submitChatQuery(CHAT_VISIBLE_JOBS_QUERY);
    });

    await waitFor(() => {
      expect(result.current.isLoading).toBe(false);
    });

    expect(mockExecute).toHaveBeenCalledWith({
      requesterId: "U001",
      message: CHAT_VISIBLE_JOBS_QUERY
    });
    expect(result.current.messages).toEqual([
      {
        id: "req-1",
        body: "Visible open jobs: J1001",
        badges: ["Compensation"]
      }
    ]);
  });
});
