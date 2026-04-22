/// <reference types="@testing-library/jest-dom" />

import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { beforeEach, describe, expect, it, vi } from "vitest";

import { ChatExperience } from "../../../src/features/chat/presentation/ui/components/ChatExperience";

describe("ChatExperience", () => {
  beforeEach(() => {
    vi.unstubAllGlobals();
  });

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

  it("messages are isolated per requester", async () => {
    const user = userEvent.setup();

    const mockFetch = vi.fn(async (url, options) => {
      const body = JSON.parse(options.body);
      if (body.requester_id === "U001") {
        return {
          ok: true,
          json: async () => ({
            requestId: "req-1",
            answer: "Jobs for Priya: J1001",
            containsCompensation: false
          })
        };
      } else if (body.requester_id === "U002") {
        return {
          ok: true,
          json: async () => ({
            requestId: "req-2",
            answer: "Jobs for Raj: J2001",
            containsCompensation: false
          })
        };
      }
      return { ok: false };
    });

    vi.stubGlobal("fetch", mockFetch);

    render(<ChatExperience endpoint="http://127.0.0.1:8000/api/chat/reply" />);

    // Switch to U001 and send message
    await user.selectOptions(screen.getByLabelText("Requester"), "U001");
    await user.click(screen.getByRole("button", { name: "Query visible jobs" }));

    await screen.findByText("Jobs for Priya: J1001");

    // Switch to U002
    await user.selectOptions(screen.getByLabelText("Requester"), "U002");

    // Assert previous messages are not visible when requester changes
    expect(screen.queryByText("Jobs for Priya: J1001")).not.toBeInTheDocument();

    // Send message as U002
    await user.click(screen.getByRole("button", { name: "Query visible jobs" }));

    await screen.findByText("Jobs for Raj: J2001");

    // Assert only U002's message is shown
    expect(screen.getByText("Jobs for Raj: J2001")).toBeInTheDocument();
    expect(screen.queryByText("Jobs for Priya: J1001")).not.toBeInTheDocument();
  });

  it("messages start empty for each requester", async () => {
    const user = userEvent.setup();
    const mockFetch = vi.fn(async (url, options) => {
      const body = JSON.parse(options.body);
      if (body.requester_id === "U001") {
        return {
          ok: true,
          json: async () => ({
            requestId: "req-u001",
            answer: "Jobs for Priya: J1001",
            containsCompensation: false
          })
        };
      }
      return {
        ok: true,
        json: async () => ({
          requestId: "req-u002",
          answer: "Jobs for Raj: J2001",
          containsCompensation: false
        })
      };
    });

    vi.stubGlobal("fetch", mockFetch);

    render(<ChatExperience endpoint="http://127.0.0.1:8000/api/chat/reply" />);

    await user.selectOptions(screen.getByLabelText("Requester"), "U001");
    await user.click(screen.getByRole("button", { name: "Query visible jobs" }));
    await screen.findByText("Jobs for Priya: J1001");

    await user.selectOptions(screen.getByLabelText("Requester"), "U002");

    expect(screen.queryByText("Jobs for Priya: J1001")).not.toBeInTheDocument();
    expect(screen.queryByText("Jobs for Raj: J2001")).not.toBeInTheDocument();
  });
});
