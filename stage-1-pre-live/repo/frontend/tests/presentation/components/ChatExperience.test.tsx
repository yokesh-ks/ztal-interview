/// <reference types="@testing-library/jest-dom" />

import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { beforeEach, describe, expect, it, vi } from "vitest";

import { ChatExperience } from "../../../src/features/chat/presentation/ui/components/ChatExperience";

const mockSubmitChatQuery = vi.fn();

vi.mock("../../../src/features/chat/presentation/hooks/useChat", () => ({
  useChat: () => ({
    messages: [],
    isLoading: false,
    submitChatQuery: mockSubmitChatQuery
  })
}));

describe("ChatExperience", () => {
  beforeEach(() => {
    vi.unstubAllGlobals();
    vi.clearAllMocks();
  });

  it("renders the requester selector", () => {
    render(<ChatExperience endpoint="http://127.0.0.1:8000/api/chat/reply" />);

    expect(screen.getByLabelText("Requester")).toBeInTheDocument();
    expect(screen.getByRole("button", { name: "Query visible jobs" })).toBeInTheDocument();
    expect(screen.getByRole("option", { name: "Raj Malhotra" })).toBeInTheDocument();
  });

  it("calls the chat action when the query button is clicked", async () => {
    const user = userEvent.setup();

    render(<ChatExperience endpoint="http://127.0.0.1:8000/api/chat/reply" />);

    await user.selectOptions(screen.getByLabelText("Requester"), "U001");
    await user.click(screen.getByRole("button", { name: "Query visible jobs" }));

    expect(mockSubmitChatQuery).toHaveBeenCalledWith("List my open jobs");
  });
});
