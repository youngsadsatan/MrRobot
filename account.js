/**
 * Bulk registra em EroMe com OCR Tesseract.js + pré-processamento avançado
 * Logs em register.log:
 *  🟢 — e-mail livre (interrompe)
 *  🔴 — e-mail já usado
 */
const fs = require('fs');
const path = require('path');
const puppeteer = require('puppeteer');
const Tesseract = require('tesseract.js');
const sharp = require('sharp');

function sleepRandom(min, max) {
  const t = Math.floor(Math.random() * (max - min + 1)) + min;
  return new Promise(r => setTimeout(r, t));
}

(async () => {
  const SITE = process.env.SITE_URL;
  const USER = process.env.USERNAME;
  const PASS = process.env.PASSWORD;
  const LOG_PATH = path.resolve(__dirname, 'register.log');

  fs.writeFileSync(LOG_PATH, '', 'utf-8');
  const emails = fs.readFileSync(path.resolve(__dirname, 'emails.txt'), 'utf-8')
                   .split(/\r?\n/)
                   .map(l => l.trim())
                   .filter(l => l && !l.startsWith('#'));

  const browser = await puppeteer.launch({
    headless: "new",
    args: ['--no-sandbox','--disable-setuid-sandbox']
  });
  const page = await browser.newPage();
  await page.goto(SITE, { waitUntil: 'networkidle2' });
  await sleepRandom(5000, 8000);

  for (const email of emails) {
    // limpa campos
    await page.evaluate(() => {
      ['name','email','password','password_confirmation','captcha']
        .forEach(n => {
          const el = document.querySelector(`input[name="${n}"]`);
          if (el) el.value = '';
        });
    });

    // preenche
    await page.type('#name', USER, { delay: 100 });
    await page.type('#email', email, { delay: 100 });
    await page.type('#password', PASS, { delay: 100 });
    await page.type('#password-confirm', PASS, { delay: 100 });

    await sleepRandom(3000, 5000);

    // captura e resolve CAPTCHA
    const img = await page.waitForSelector('form .mb-10 img.initial', { timeout: 10000 });
    const buf = await img.screenshot();
    let code;
    try {
      // pré-processamento avançado:
      // 1) inverte cores (é “inverse”)
      // 2) grayscale
      // 3) resize
      // 4) blur para reduzir ruído
      // 5) threshold adaptativo
      let proc = await sharp(buf)
        .negate()
        .grayscale()
        .resize({ width: 200 })
        .blur(1)
        .toBuffer();

      // aplica threshold manualmente
      proc = await sharp(proc)
        .threshold(180)
        .toBuffer();

      const { data: { text } } = await Tesseract.recognize(proc, 'eng', {
        tessedit_char_whitelist: '0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz'
      });
      code = text.replace(/[^0-9A-Za-z]/g, '').substr(0,4);
      if (code.length !== 4) throw new Error('len');
    } catch (e) {
      console.log(`⚠️ OCR falhou para ${email}, recarregando captcha`);
      await page.click('form .mb-10 img.initial');
      await sleepRandom(4000, 6000);
      continue;
    }

    await page.type('input[name="captcha"]', code, { delay: 100 });
    await sleepRandom(1000, 2000);

    // submete e aguarda resposta
    await Promise.all([
      page.click('button[type="submit"]'),
      page.waitForResponse(res => res.url().includes('/user/register') && res.status() === 200)
    ]);

    const html = await page.content();
    if (/The email is already used\./.test(html)) {
      console.log(`🔴 ${email}`);
      fs.appendFileSync(LOG_PATH, `🔴 ${email}\n`);
      await page.click('form .mb-10 img.initial');
      await sleepRandom(4000, 6000);
    } else {
      console.log(`🟢 ${email}`);
      fs.appendFileSync(LOG_PATH, `🟢 ${email}\n`);
      break;
    }

    await sleepRandom(6000, 10000);
  }

  await browser.close();
})();
