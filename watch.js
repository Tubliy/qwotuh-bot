const puppeteer = require('puppeteer');

const username = 'qwotuh';

(async () => {
    const browser = await puppeteer.launch({ headless: true });
    const page = await browser.newPage();
    await page.goto(`https://www.tiktok.com/@${username}`, { waitUntil: 'networkidle2' });

    const isLive = await page.evaluate(() => {
        return !!document.querySelector('span[data-e2e="live-badge"]');
    });

    console.log(isLive ? 'User is LIVE!' : 'User is offline.');
    await browser.close();
})();
