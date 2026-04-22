/// <reference types="@testing-library/jest-dom" />

import { render, screen } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";

import { ChatExperience } from "../../../src/features/chat/presentation/ui/components/ChatExperience";

describe("ChatExperience", () => {
  it("renders the requester selector", () => {
    vi.stubGlobal(
      "fetch",
      vi.fn().mockResolvedValue({
        ok: true,
        json: async () => ({
          requestId: "req-1",
          answer: "Visible open jobs: J1001",
          containsCompensation: false
        })
      })
    );

    render(<ChatExperience endpoint="http://127.0.0.1:8000/api/chat/reply" />);

    expect(screen.getByLabelText("Requester")).toBeInTheDocument();
    expect(screen.getByRole("button", { name: "Query visible jobs" })).toBeInTheDocument();
  });
});
