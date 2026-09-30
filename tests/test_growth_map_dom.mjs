import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";
import test from "node:test";
import { JSDOM } from "jsdom";

const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "..");

function loadMap(example, saved = {}) {
  const html = readFileSync(
    path.join(root, "examples", "learning-path-designer", example, "growth-map.html"),
    "utf8",
  );
  const dom = new JSDOM(html, { url: "https://sanqi.example/", runScripts: "outside-only" });
  for (const [key, value] of Object.entries(saved)) dom.window.localStorage.setItem(key, value);
  const script = [...dom.window.document.querySelectorAll("script")].find(
    (node) => !node.type && node.textContent.includes("const plan="),
  );
  assert.ok(script, "growth map application script exists");
  dom.window.eval(script.textContent);
  return dom;
}

for (const [example, stageCount, groupCount] of [
  ["ai-content-creator", 4, 5],
  ["data-analyst-transition", 4, 8],
]) {
  test(`${example}: stages, tasks, progress, review and persistence`, () => {
    const dom = loadMap(example);
    const { document, localStorage, Event } = dom.window;
    assert.equal(document.querySelectorAll(".stage-tab").length, stageCount);
    assert.equal(document.querySelectorAll(".phase-tab").length, groupCount);
    assert.match(document.querySelector("#globalProgress").textContent, /^0 \/ \d+ 项$/);

    const firstStage = document.querySelector("#stageDetail h3").textContent;
    document.querySelectorAll(".stage-tab")[1].click();
    assert.notEqual(document.querySelector("#stageDetail h3").textContent, firstStage);

    const firstTask = document.querySelector(".task-title").textContent;
    document.querySelectorAll(".phase-tab")[1].click();
    assert.notEqual(document.querySelector(".task-title").textContent, firstTask);

    const checkbox = document.querySelector(".task input");
    checkbox.checked = true;
    checkbox.dispatchEvent(new Event("change", { bubbles: true }));
    assert.match(document.querySelector("#globalProgress").textContent, /^1 \/ \d+ 项$/);
    assert.equal(checkbox.closest(".task").classList.contains("done"), true);

    document.querySelector("#reviewToggle").click();
    assert.equal(document.querySelector("#review").classList.contains("open"), true);

    const saved = Object.fromEntries(
      Array.from({ length: localStorage.length }, (_, index) => {
        const key = localStorage.key(index);
        return [key, localStorage.getItem(key)];
      }),
    );
    dom.window.close();

    const reopened = loadMap(example, saved);
    reopened.window.document.querySelectorAll(".phase-tab")[1].click();
    assert.equal(reopened.window.document.querySelector(".task input").checked, true);
    assert.match(reopened.window.document.querySelector("#globalProgress").textContent, /^1 \/ \d+ 项$/);
    reopened.window.close();
  });
}
