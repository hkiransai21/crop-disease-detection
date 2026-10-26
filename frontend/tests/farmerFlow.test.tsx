import React, { StrictMode } from "react";
import { beforeEach, afterEach, describe, expect, it, vi } from "vitest";
import { fireEvent, render, screen, waitFor } from "@testing-library/react";
import { MemoryRouter, Route, Routes } from "react-router-dom";
import { AnalyzePage } from "../src/pages/AnalyzePage";
import { LanguageChoice } from "../src/components/LanguageChoice";
import { api } from "../src/api/client";
import i18n from "../src/i18n/i18n";
import { AnalysisResponse } from "../src/types";

beforeEach(async () => {
  localStorage.clear();
  await i18n.changeLanguage("en");
  vi.stubGlobal(
    "URL",
    Object.assign(URL, {
      createObjectURL: vi.fn(() => "blob:leaf"),
      revokeObjectURL: vi.fn(),
    }),
  );
});
afterEach(() => {
  vi.restoreAllMocks();
  vi.unstubAllGlobals();
});

describe("Farmer capture flow", () => {
  const file = new File(["leaf"], "leaf.jpg", { type: "image/jpeg" });
  const response = { id: "guest_one", language: "en" } as AnalysisResponse;
  function setup(complete = vi.fn(async () => response)) {
    render(
      <StrictMode>
        <MemoryRouter
          initialEntries={[
            { pathname: "/analyze", state: { file, automatic: true } },
          ]}
        >
          <Routes>
            <Route
              path="/analyze"
              element={<AnalyzePage onAnalysisComplete={complete} />}
            />
            <Route path="/result/:id" element={<h1>Result ready</h1>} />
          </Routes>
        </MemoryRouter>
      </StrictMode>,
    );
    return complete;
  }
  it("submits the home camera selection once in StrictMode and reaches the result", async () => {
    const request = vi.spyOn(api, "analyzeImage").mockResolvedValue(response);
    const complete = setup();
    expect(await screen.findByText("Result ready")).toBeInTheDocument();
    expect(request).toHaveBeenCalledTimes(1);
    expect(request.mock.calls[0][0]).toBe(file);
    expect(complete).toHaveBeenCalledWith(response, file);
  });
  it("retains the photo and offers a working retry after network failure", async () => {
    const request = vi
      .spyOn(api, "analyzeImage")
      .mockRejectedValueOnce(new Error("network"))
      .mockResolvedValue(response);
    setup();
    const retry = await screen.findByRole("button", {
      name: i18n.t("farmer.retry"),
    });
    expect(screen.getByAltText(i18n.t("farmer.preview"))).toBeInTheDocument();
    fireEvent.click(retry);
    expect(await screen.findByText("Result ready")).toBeInTheDocument();
    expect(request).toHaveBeenCalledTimes(2);
  });
  it("shows five native choices, then a skippable tutorial, and remembers both choices", async () => {
    render(
      <LanguageChoice>
        <h1>Home ready</h1>
      </LanguageChoice>,
    );
    expect(document.querySelectorAll(".language-name")).toHaveLength(5);
    fireEvent.click(
      screen.getByRole("button", { name: "English", exact: true }),
    );
    expect(document.querySelectorAll(".tutorial li")).toHaveLength(3);
    fireEvent.click(screen.getByRole("button", { name: "Skip", exact: true }));
    await waitFor(() =>
      expect(screen.getByText("Home ready")).toBeInTheDocument(),
    );
    expect(localStorage.getItem("agrishield_language")).toBe("en");
    expect(localStorage.getItem("leaf_tutorial")).toBe("done");
  });
});
