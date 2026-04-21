import { describe, expect, it } from "vitest";

import { toChatMessageUi } from "../../../src/features/chat/presentation/mappers/chatReplyUiMapper";

describe("toChatMessageUi", () => {
  it("adds a compensation badge when the reply includes compensation", () => {
    const result = toChatMessageUi({
      requestId: "req-1",
      answer: "Alice Chen is stuck in screening",
      containsCompensation: true
    });

    expect(result).toEqual({
      id: "req-1",
      body: "Alice Chen is stuck in screening",
      badges: ["Compensation"]
    });
  });
});
