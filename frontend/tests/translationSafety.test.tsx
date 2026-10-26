import React from "react";
import { describe, it, expect, vi } from "vitest";
import { render, screen, cleanup } from "@testing-library/react";
import { MemoryRouter, Routes, Route } from "react-router-dom";
import { ResultPage } from "../src/pages/ResultPage";
import i18n from "../src/i18n/i18n";
import { AnalysisResponse } from "../src/types";
import english from "../../backend/app/data/i18n/en/diseases.json";

vi.mock("../src/components/AudioNarrator", () => ({
  AudioNarrator: () => <div data-testid="narration" />,
}));

describe("Localized uncertain results", () => {
  for (const lang of ["en", "hi", "ta", "te", "kn"]) {
    it(`shows uncertainty and suppresses treatment and narration in ${lang}`, async () => {
      await i18n.changeLanguage(lang);
      const result = {
        language: lang,
        id: "guest_test",
        predicted_label: english.diseases[0].id,
        crop: "Apple",
        disease_name: "Apple Scab",
        confidence: 0.4,
        confidence_display: "40%",
        is_uncertain: true,
        top_k: [],
        model_version: "test",
        image_url: "",
        created_at: "2026-10-16T00:00:00Z",
        disease_details: english.diseases[0],
      } as unknown as AnalysisResponse;
      render(
        <MemoryRouter initialEntries={["/result/guest_test"]}>
          <Routes>
            <Route
              path="/result/:id"
              element={<ResultPage lastAnalysis={result} />}
            />
          </Routes>
        </MemoryRouter>,
      );
      expect(
        await screen.findByText(i18n.t("farmer.uncertain_note")),
      ).toBeInTheDocument();
      expect(
        screen.queryByText(i18n.t("result.actions_title")),
      ).not.toBeInTheDocument();
      expect(screen.queryByTestId("narration")).not.toBeInTheDocument();
      cleanup();
      await i18n.changeLanguage("en");
    });
  }
});
