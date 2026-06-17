const puppeteer = require('puppeteer');
(async () => {
  const browser = await puppeteer.launch();
  const page = await browser.newPage();
  await page.setViewport({ width: 794, height: 1123, deviceScaleFactor: 1 });
  await page.goto('file:///Users/kimbeomjun/.gemini/antigravity/brain/613cbc66-999b-4de8-b3aa-d0a34a99b155/scratch/mandalart_debug.html');
  await page.screenshot({ path: 'scratch/mandalart_preview.png' });
  await browser.close();
})();
