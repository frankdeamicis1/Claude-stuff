#!/usr/bin/env node
// Renders story.html frame-by-frame with headless Chromium (Playwright).
//
//   node render.js stills <outDir> 0,1.6,4.5        -> PNG stills at those times (seconds)
//   node render.js frames <outDir> <start> <end>    -> frames [start, end) as 00000.png ...
//   node render.js cues <out.json>                  -> dump the audio cue list from the page
//   node render.js all <framesDir> [workers]        -> render every frame in parallel workers
//
// Then encode with ffmpeg (see build.sh).
'use strict';
const path = require('path');
const fs = require('fs');
const { spawn } = require('child_process');
const { chromium } = require('playwright');

const FPS = 30;
const PAGE = 'file://' + path.resolve(__dirname, 'story.html') + '?render=1';

async function openPage() {
  const browser = await chromium.launch();
  const page = await browser.newPage({ viewport: { width: 1080, height: 1920 }, deviceScaleFactor: 1 });
  page.on('pageerror', e => { console.error('PAGE ERROR:', e.message); process.exitCode = 1; });
  page.on('console', m => { if (m.type() === 'error' || m.type() === 'warning') console.error('console:', m.text()); });
  await page.goto(PAGE);
  await page.waitForFunction(() => window.READY === true);
  await page.evaluate(() => document.fonts.ready);
  const dur = await page.evaluate(() => DUR);
  return { browser, page, total: Math.round(FPS * dur) };
}

async function shoot(page, t, file) {
  await page.evaluate(tt => window.renderFrame(tt), t);
  await page.screenshot({ path: file, type: 'png', clip: { x: 0, y: 0, width: 1080, height: 1920 } });
}

async function main() {
  const [mode, out, a, b] = process.argv.slice(2);
  if (mode === 'stills') {
    fs.mkdirSync(out, { recursive: true });
    const { browser, page } = await openPage();
    for (const s of a.split(',')) {
      const t = parseFloat(s);
      await shoot(page, t, path.join(out, `t${t.toFixed(2).padStart(6, '0')}.png`));
    }
    await browser.close();
  } else if (mode === 'frames') {
    fs.mkdirSync(out, { recursive: true });
    const { browser, page, total } = await openPage();
    const start = parseInt(a, 10), end = Math.min(parseInt(b, 10), total);
    for (let f = start; f < end; f++) await shoot(page, f / FPS, path.join(out, String(f).padStart(5, '0') + '.png'));
    await browser.close();
  } else if (mode === 'cues') {
    const { browser, page } = await openPage();
    const cues = await page.evaluate(() => window.CUES);
    fs.writeFileSync(out, JSON.stringify(cues, null, 2));
    await browser.close();
  } else if (mode === 'all') {
    const workers = parseInt(a || '4', 10);
    const probe = await openPage(); const TOTAL = probe.total; await probe.browser.close();
    const per = Math.ceil(TOTAL / workers);
    const jobs = [];
    for (let w = 0; w < workers; w++) {
      const s = w * per, e = Math.min(TOTAL, s + per);
      jobs.push(new Promise((res, rej) => {
        const p = spawn(process.execPath, [__filename, 'frames', out, String(s), String(e)], { stdio: 'inherit' });
        p.on('exit', code => code === 0 ? res() : rej(new Error('worker ' + w + ' failed')));
      }));
    }
    await Promise.all(jobs);
    console.log(`rendered ${TOTAL} frames to ${out}`);
  } else {
    console.error('usage: render.js stills|frames|cues|all ...');
    process.exit(2);
  }
}
main().catch(e => { console.error(e); process.exit(1); });
