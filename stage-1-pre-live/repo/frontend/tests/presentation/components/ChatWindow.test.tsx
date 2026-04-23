/// <reference types="@testing-library/jest-dom" />

import { render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";

import { ChatWindow } from "../../../src/features/chat/presentation/ui/components/ChatWindow";

describe("ChatWindow", () => {
  it("renders ui messages and badges", () => {
    render(
      <ChatWindow
        isLoading
        messages={[
          {
            id: "req-1",
            body: "Visible open jobs: J1001",
            badges: ["Compensation"]
          }
        ]}
      />
    );

    expect(screen.getByText("Recruiting Assistant")).toBeInTheDocument();
    expect(screen.getByText("Thinking...")).toBeInTheDocument();
    expect(screen.getByText("Visible open jobs: J1001")).toBeInTheDocument();
    expect(screen.getByText("Compensation")).toBeInTheDocument();
  });
});
