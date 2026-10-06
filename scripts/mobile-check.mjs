#!/usr/bin/env node
/* ==============================================================================
   AUTOMATED MOBILE CHECK — the 7th audit dimension (see CLAUDE.md)
   Dev-only. The tool itself stays single-file / zero-dependency; this script is
   NOT shipped. It needs Playwright installed globally (keeps package.json out of the repo):
   npm i -g playwright && npx playwright install chromium

   USAGE
     node scripts/mobile-check.mjs index.html
     node scripts/mobile-check.mjs index.html --cycle '#themeBtn' --cycles 3
   OPTIONS
     --cycle <selector>   button that switches color schemes; the whole check
                          repeats once per scheme (--cycles N = how many to visit)
     --out <dir>          screenshot folder (default: mobile-check-out)
   ENV
     CHARTJS_LOCAL=/path/chart.umd.js   serve this file for any chart.umd*.js
                                        request (only for offline sandboxes)
     CHROMIUM_PATH=/path/to/chromium    use an existing Chromium build
   EXIT CODE  0 = all checks passed, 1 = at least one failure.
   ============================================================================== */
import { mkdirSync } from 'node:fs';
import { execSync } from 'node:child_process';
import { createRequire } from 'node:module';
import { resolve } from 'node:path';
import { pathToFileURL } from 'node:url';

/* Playwright: project-local install first, then a global one (ES modules ignore NODE_PATH). */
let chromium;
try { ({ chromium } = await import('playwright')); }
catch { chromium = createRequire(execSync('npm root -g').toString().trim() + '/')('playwright').chromium; }

/* ---- tuning constants (what each number controls) ---- */
const VIEWPORTS = [                     // phone widths that cover small Android → large iPhone, plus landscape
  { name:'360x740',  width:360, height:740 },
  { name:'390x844',  width:390, height:844 },
  { name:'430x932',  width:430, height:932 },
  { name:'844x390-landscape', width:844, height:390 },
];
const MIN_TARGET_PX     = 40;   // PMR standard: touch targets >= 40px on the short side (44px for primary controls)
const MIN_TEXT_PX       = 11;   // smallest DOM text allowed on a phone (canvas text is exempt)
const FIRST_CONTROL_MAX = 0.75; // first control must start within this fraction of viewport height (portrait only)
const SETTLE_MS         = 1200; // wait after load/theme switch for charts to draw

const args = process.argv.slice(2);
const file = args.find(a => !a.startsWith('--') && args[args.indexOf(a) - 1] !== '--cycle' && args[args.indexOf(a) - 1] !== '--cycles' && args[args.indexOf(a) - 1] !== '--out');
const opt = (n, d) => { const i = args.indexOf('--' + n); return i >= 0 ? args[i + 1] : d; };
if (!file) { console.error('usage: node scripts/mobile-check.mjs <file.html> [--cycle <selector> --cycles N] [--out dir]'); process.exit(2); }
const cycleSel = opt('cycle', null), cycles = +opt('cycles', 1), outDir = opt('out', 'mobile-check-out');
mkdirSync(outDir, { recursive: true });

const browser = await chromium.launch(process.env.CHROMIUM_PATH ? { executablePath: process.env.CHROMIUM_PATH } : {});
let failures = 0;
const fail = (msg) => { failures++; console.log('  FAIL ' + msg); };

for (const vp of VIEWPORTS) {
  const ctx = await browser.newContext({ viewport:{ width:vp.width, height:vp.height }, hasTouch:true, isMobile:true, deviceScaleFactor:2 });
  const page = await ctx.newPage();
  const errors = [];
  page.on('pageerror', e => errors.push(e.message));
  if (process.env.CHARTJS_LOCAL) await page.route(/chart\.umd.*\.js/, r => r.fulfill({ path: process.env.CHARTJS_LOCAL, contentType:'application/javascript' }));
  await page.route(/fonts\.(googleapis|gstatic)\.com/, r => r.abort());   // never let web-font loading stall the check
  await page.goto(pathToFileURL(resolve(file)).href);
  await page.waitForTimeout(SETTLE_MS);

  for (let k = 0; k < cycles; k++) {
    const scheme = cycleSel ? await page.evaluate(() => document.getElementById('themeName')?.textContent || '?') : 'default';
    console.log(`\n[${vp.name}] scheme: ${scheme}`);
    const before = failures;

    const r = await page.evaluate(({ MIN_TARGET_PX, MIN_TEXT_PX }) => {
      const vis = e => { const b = e.getBoundingClientRect(), s = getComputedStyle(e); return b.width > 0 && b.height > 0 && s.visibility !== 'hidden' && s.display !== 'none'; };
      const doc = document.documentElement;
      // touch targets: buttons, links outside the footer (inline links are exempt), summaries, checkbox/range inputs (a checkbox counts via its label)
      const targets = [...document.querySelectorAll('button, summary, a[href]:not(.ftr a), input')].filter(vis).map(e => {
        const hit = (e.type === 'checkbox' && e.closest('label')) ? e.closest('label') : e;
        const b = hit.getBoundingClientRect();
        return { id: (e.id || e.className || e.tagName).toString().slice(0, 40), w: Math.round(b.width), h: Math.round(b.height) };
      }).filter(t => Math.min(t.w, t.h) < MIN_TARGET_PX);
      // DOM text smaller than MIN_TEXT_PX (walk text nodes so empty wrappers do not count)
      const small = new Map();
      const walker = document.createTreeWalker(document.body, NodeFilter.SHOW_TEXT);
      for (let n; (n = walker.nextNode());) {
        if (!n.textContent.trim()) continue;
        const el = n.parentElement; if (!el || !vis(el) || el.closest('script,style,canvas,sub,sup')) continue;
        const fs = parseFloat(getComputedStyle(el).fontSize);
        if (fs < MIN_TEXT_PX) small.set((el.className || el.tagName).toString().slice(0, 30), fs);
      }
      const first = document.querySelector('.sz-btn, input[type=range]');
      const meta = document.querySelector('meta[name=viewport]')?.content || '';
      return {
        overflowPx: doc.scrollWidth - doc.clientWidth,
        targets, small: [...small.entries()],
        firstTop: first ? Math.round(first.getBoundingClientRect().top) : null,
        zoomBlocked: /user-scalable\s*=\s*(no|0)/i.test(meta) || /maximum-scale\s*=\s*1(\.0)?\b/i.test(meta),
      };
    }, { MIN_TARGET_PX, MIN_TEXT_PX });

    if (r.overflowPx > 0) fail(`horizontal overflow: page is ${r.overflowPx}px wider than the viewport`);
    if (r.targets.length) fail(`${r.targets.length} touch target(s) under ${MIN_TARGET_PX}px: ` + r.targets.map(t => `${t.id} ${t.w}x${t.h}`).join('; '));
    if (r.small.length) fail(`text under ${MIN_TEXT_PX}px: ` + r.small.map(([c, f]) => `${c} ${f}px`).join('; '));
    if (r.zoomBlocked) fail('viewport meta blocks pinch-zoom (remove user-scalable=no / maximum-scale=1)');
    if (vp.height > vp.width && r.firstTop !== null && r.firstTop > vp.height * FIRST_CONTROL_MAX)
      fail(`first control starts at ${r.firstTop}px — below ${Math.round(FIRST_CONTROL_MAX * 100)}% of the ${vp.height}px viewport (too much chrome above it)`);
    if (errors.length) fail('JS errors: ' + [...new Set(errors)].join(' | '));
    if (failures === before) console.log('  ok');

    if (cycleSel && k < cycles - 1) { await page.click(cycleSel); await page.waitForTimeout(SETTLE_MS / 2); }
  }
  await ctx.close();

  /* Screenshots come AFTER all measuring, each in a throwaway page. Any full-page capture in a
     mobile-emulated page turns pointer:coarse off for the rest of that page's life, which would
     make later schemes get measured as a desktop mouse (found the hard way). */
  for (let k = 0; k < cycles; k++) {
    const sctx = await browser.newContext({ viewport:{ width:vp.width, height:vp.height }, hasTouch:true, isMobile:true, deviceScaleFactor:2 });
    const sp = await sctx.newPage();
    if (process.env.CHARTJS_LOCAL) await sp.route(/chart\.umd.*\.js/, r => r.fulfill({ path: process.env.CHARTJS_LOCAL, contentType:'application/javascript' }));
    await sp.route(/fonts\.(googleapis|gstatic)\.com/, r => r.abort());
    await sp.goto(pathToFileURL(resolve(file)).href);
    await sp.waitForTimeout(SETTLE_MS);
    for (let c = 0; c < k; c++) { await sp.click(cycleSel); await sp.waitForTimeout(SETTLE_MS / 2); }
    await sp.screenshot({ path: `${outDir}/${vp.name}-scheme${k + 1}.png`, fullPage: true });
    await sctx.close();
  }
}
await browser.close();
console.log(failures ? `\n${failures} check(s) FAILED` : '\nAll mobile checks passed');
process.exit(failures ? 1 : 0);
