// Renders social-share images (assets/og/<lang>.png) and app icons.
// Needs Node + Playwright:   node tools/make_images.mjs
// Optional: FONT_DIR=/path/to/woff2 files (Noto Sans Sinhala / Tamil) for nicer Sinhala & Tamil text.
import { createRequire } from "module";
import fs from "fs";
import path from "path";
import { fileURLToPath } from "url";

const require = createRequire(import.meta.url);
const { chromium } = require("playwright");
const ROOT = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "..");
const cfg = JSON.parse(fs.readFileSync(path.join(ROOT, "config.json"), "utf8"));
const esc = (s) => s.replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;");

function fontFaces() {
  const dir = process.env.FONT_DIR;
  if (!dir || !fs.existsSync(dir)) return "";
  const files = fs.readdirSync(dir, { recursive: true }).map(String);
  let css = "";
  for (const [fam, re] of [["Space Grotesk", /space-grotesk-latin-(\d00)-normal\.woff2$/], ["Noto Sans Sinhala", /sinhala-sinhala-(\d00)-normal\.woff2$/], ["Noto Sans Tamil", /tamil-tamil-(\d00)-normal\.woff2$/]]) {
    for (const f of files.filter((f) => re.test(f))) {
      css += `@font-face{font-family:"${fam}";font-weight:${f.match(re)[1]};src:url("file://${path.join(dir, f)}") format("woff2")}`;
    }
  }
  return css;
}

function ogHtml(lang, c) {
  const reward = cfg.reward[lang] || cfg.reward[cfg.default_language];
  const big = esc(c.og_sub).replace("{reward}", `<span class="mk">${esc(reward)}</span>`);
  const latin = lang === "en";
  return `<!doctype html><html lang="${lang}"><head><meta charset="utf-8"><style>
${fontFaces()}
*{box-sizing:border-box}html,body{margin:0}
body{width:1200px;height:630px;overflow:hidden;background:#F7F5F0;color:#111318;font-family:Inter,"Noto Sans Sinhala","Noto Sans Tamil",FreeSans,sans-serif;position:relative;display:flex;gap:52px;align-items:center;padding:60px 68px}
.bg{position:absolute;inset:0}
.l{flex:1;min-width:0;position:relative;display:flex;flex-direction:column;gap:20px}
.brand{display:flex;align-items:center;gap:12px;font:700 24px "Space Grotesk",Inter,sans-serif}.brand b{font-weight:500;color:#575C66}
.kick{font-size:${latin ? 28 : 25}px;font-weight:600;color:#1F4FD1;line-height:1.35}
h1{margin:0;font-family:"Space Grotesk",Inter,"Noto Sans Sinhala","Noto Sans Tamil",sans-serif;font-size:${latin ? 84 : 60}px;line-height:${latin ? 1.02 : 1.25};letter-spacing:${latin ? "-.04em" : "0"};font-weight:700}
.mk{box-shadow:inset 0 -.24em 0 #F8D58A;font-family:"Space Grotesk",Inter,sans-serif}
.line{font-size:${latin ? 26 : 23}px;color:#3A3F49;line-height:1.45}
.t{flex:0 0 340px;position:relative;background:#fff;border:1px solid #E4E1D8;border-radius:28px;overflow:hidden;box-shadow:0 30px 60px -36px rgba(17,19,24,.4)}
.h{padding:24px 20px 20px;text-align:center}.h+.h{border-top:2px dashed #D6D2C7}
.h span{display:block;font-size:${latin ? 16 : 18}px;font-weight:600;color:#575C66;${latin ? "letter-spacing:.06em;text-transform:uppercase" : ""}}
.h strong{font:700 46px/1.15 "Space Grotesk",Inter,sans-serif;letter-spacing:-.02em}
.p{margin:0;padding:14px 18px;background:#111318;color:#fff;text-align:center;font-weight:600;font-size:${latin ? 18 : 17}px}
</style></head><body>
<svg class="bg" viewBox="0 0 1200 630"><path d="M640 640 Q980 120 1240 230" fill="none" stroke="#1F4FD1" stroke-opacity=".35" stroke-width="2" stroke-dasharray="5 11"/><path d="M560 660 Q900 40 1240 80" fill="none" stroke="#1F4FD1" stroke-opacity=".16" stroke-width="1.5" stroke-dasharray="3 12"/></svg>
<div class="l">
 <div class="brand"><svg width="40" height="40" viewBox="0 0 32 32"><circle cx="16" cy="16" r="15" fill="#111318"/><ellipse cx="16" cy="16" rx="12.5" ry="4.6" fill="none" stroke="#fff" stroke-opacity=".55" stroke-width="1.4" transform="rotate(-24 16 16)"/><circle cx="16" cy="16" r="4" fill="#1F4FD1"/><circle cx="26" cy="11.6" r="2.2" fill="#F2A60C"/></svg>Starlink Referral <b>· Sri Lanka</b></div>
 <div class="kick">${esc(c.og_text)}</div>
 <h1>${big}</h1>
 <div class="line">${esc(c.og_line)}</div>
</div>
<div class="t">
 <div class="h"><span>${esc(c.ticket_you)}</span><strong>${esc(reward)}</strong></div>
 <div class="h"><span>${esc(c.ticket_me)}</span><strong>${esc(reward)}</strong></div>
 <p class="p">${esc(c.ticket_paid)}</p>
</div>
</body></html>`;
}

const browser = await chromium.launch();
const ctx = await browser.newContext({ viewport: { width: 1200, height: 630 }, deviceScaleFactor: 1 });
const page = await ctx.newPage();
fs.mkdirSync(path.join(ROOT, "assets", "og"), { recursive: true });
for (const lang of cfg.languages) {
  const c = JSON.parse(fs.readFileSync(path.join(ROOT, "content", `${lang}.json`), "utf8"));
  await page.setContent(ogHtml(lang, c), { waitUntil: "load" });
  await page.evaluate(() => document.fonts.ready);
  await page.screenshot({ path: path.join(ROOT, "assets", "og", `${lang}.png`) });
  console.log("og", lang);
}
const svg = fs.readFileSync(path.join(ROOT, "assets", "favicon.svg"), "utf8");
for (const [name, size] of [["icon-192.png", 192], ["apple-touch-icon.png", 180]]) {
  await page.setViewportSize({ width: size, height: size });
  await page.setContent(`<html><body style="margin:0;background:#F7F5F0">${svg.replace("<svg ", `<svg width="${size}" height="${size}" `)}</body></html>`);
  await page.screenshot({ path: path.join(ROOT, "assets", name) });
  console.log("icon", name);
}
await browser.close();
