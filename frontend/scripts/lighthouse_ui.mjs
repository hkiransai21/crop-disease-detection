import fs from "node:fs";
import path from "node:path";
import lighthouse from "lighthouse";
import { launch } from "chrome-launcher";
import puppeteer from "puppeteer-core";
const root = path.resolve("..");
const base = "http://127.0.0.1:4173";
const chrome = await launch({
  chromePath:
    process.env.CHROME_PATH ||
    "C:/Program Files (x86)/Microsoft/Edge/Application/msedge.exe",
  chromeFlags: ["--headless", "--no-sandbox"],
});
try {
  const browser = await puppeteer.connect({
    browserURL: `http://127.0.0.1:${chrome.port}`,
  });
  const page = await browser.newPage();
  await page.goto(base);
  const report = [];
  for (const [screen, lang] of [
    ["home", "en"],
    ["result", "ta"],
  ]) {
    const entry = JSON.parse(
      fs.readFileSync(
        path.join(root, `backend/app/data/i18n/${lang}/diseases.json`),
        "utf8",
      ),
    ).diseases[0];
    const result = {
      id: "guest_lighthouse",
      language: lang,
      predicted_label: entry.id,
      crop: entry.crop,
      disease_name: entry.disease_name,
      confidence: 0.95,
      confidence_display: "95%",
      is_uncertain: false,
      top_k: [],
      model_version: "ui-fixture",
      image_url: "/icon.svg",
      disease_details: entry,
      created_at: "2026-10-17T00:00:00Z",
    };
    await page.evaluate(
      async ({ lang, result }) => {
        localStorage.setItem("agrishield_language", lang);
        localStorage.setItem("leaf_tutorial", "done");
        await new Promise((resolve, reject) => {
          const req = indexedDB.open("leaf-checks", 1);
          req.onupgradeneeded = () =>
            req.result.createObjectStore("checks", { keyPath: "id" });
          req.onsuccess = () => {
            const db = req.result;
            const tx = db.transaction("checks", "readwrite");
            tx.objectStore("checks").put({
              id: result.id,
              result,
              variants: { [lang]: result },
            });
            tx.oncomplete = () => {
              db.close();
              resolve();
            };
            tx.onerror = reject;
          };
          req.onerror = reject;
        });
      },
      { lang, result },
    );
    const url = base + (screen === "home" ? "/" : "/result/guest_lighthouse");
    const run = await lighthouse(url, {
      port: chrome.port,
      output: ["json", "html"],
      logLevel: "error",
      onlyCategories: ["performance", "accessibility"],
      disableStorageReset: true,
      formFactor: "mobile",
      screenEmulation: {
        mobile: true,
        width: 360,
        height: 640,
        deviceScaleFactor: 1,
        disabled: false,
      },
      throttlingMethod: "simulate",
      throttling: {
        rttMs: 150,
        throughputKbps: 1638.4,
        cpuSlowdownMultiplier: 6,
        requestLatencyMs: 562.5,
        downloadThroughputKbps: 1474.56,
        uploadThroughputKbps: 675,
      },
    });
    const prefix = path.join(root, `docs/ui-lighthouse-${screen}-${lang}`);
    fs.writeFileSync(prefix + ".json", run.report[0]);
    fs.writeFileSync(prefix + ".html", run.report[1]);
    const scores = Object.fromEntries(
      Object.entries(run.lhr.categories).map(([k, v]) => [
        k,
        Math.round(v.score * 100),
      ]),
    );
    report.push({ screen, lang, ...scores });
    console.log(JSON.stringify(report.at(-1)));
  }
  fs.writeFileSync(
    path.join(root, "docs/ui-lighthouse-summary.json"),
    JSON.stringify(report, null, 2),
  );
  await browser.disconnect();
} finally {
  await chrome.kill();
}
