// Optional document QA. Requires Playwright (or Codex's bundled Node packages).
import { createRequire } from 'node:module';
import { fileURLToPath, pathToFileURL } from 'node:url';
import path from 'node:path';
import os from 'node:os';
import fs from 'node:fs';

const require = createRequire(import.meta.url);
let playwright;
try { playwright = require('playwright'); }
catch {
  const modules = process.env.DEMO_NODE_MODULES || path.join(os.homedir(), '.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules');
  playwright = require(path.join(modules, 'playwright'));
}
const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '../..');
const output = path.join(root, 'output/pdf/BANG_NHAC_DEMO.pdf');
fs.mkdirSync(path.dirname(output), { recursive: true });
const executablePath = process.env.DEMO_CHROME || path.join(process.env.ProgramFiles || 'C:/Program Files', 'Google/Chrome/Application/chrome.exe');
const browser = await playwright.chromium.launch({ executablePath, headless: true });
try {
  const page = await browser.newPage({ viewport: { width: 1200, height: 900 } });
  await page.goto(pathToFileURL(path.join(root, 'docs/demo/BANG_NHAC.html')).href);
  await page.pdf({ path: output, preferCSSPageSize: true, printBackground: true, displayHeaderFooter: false });
  console.log(output);
} finally { await browser.close(); }
