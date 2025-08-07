/**
 * Bulk registra em EroMe com OCR Tesseract.js + delays human-based
 * Logs em register.log:
 *  🟢 — e-mail livre (interrompe)
 *  🔴 — e-mail já usado
 */
const fs = require('fs');
const path = require('path');
const puppeteer = require('puppeteer');
const Tesseract = require('tesseract.js');
const sharp = require('sharp');

// sleep com tempo randômico entre min e max (ms)
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
  await sleepRandom(4000, 7000); // delay inicial

  for (const email of emails) {
    // limpa campos
    await page.evaluate(() => {
      ['name','email','password','password_confirmation','captcha']
        .forEach(n => document.querySelector(`input[name="${n}"]`).value = '');
    });

    // preenche campos
    await page.type('#name', USER);
    await page.type('#email', email);
    await page.type('#password', PASS);
    await page.type('#password-confirm', PASS);

    await sleepRandom(2000, 4000); // pausa antes do captcha

    // captura e resolve CAPTCHA
    const img = await page.waitForSelector('form .mb-10 img.initial', { timeout: 8000 });
    const buf = await img.screenshot();
    let code;
    try {
      // pré-processamento reforçado
      const proc = await sharp(buf)
        .grayscale()
        .resize({ width: 200 })
        .median(1)
        .normalize()
        .threshold(150)
        .toBuffer();

      const { data: { text } } = await Tesseract.recognize(proc, 'eng', {
        tessedit_char_whitelist: '0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz'
      });
      code = text.replace(/[^0-9A-Za-z]/g, '').substr(0,4);
      if (code.length !== 4) throw new Error('len');
    } catch {
      console.log(`⚠️ OCR falhou para ${email}, recarregando captcha`);
      await page.click('form .mb-10 img.initial');
      await sleepRandom(3000, 5000);
      continue;
    }

    await page.type('input[name="captcha"]', code);
    await sleepRandom(1000, 2000); // breve pausa antes do submit

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
    } else {
      console.log(`🟢 ${email}`);
      fs.appendFileSync(LOG_PATH, `🟢 ${email}\n`);
      break;
    }

    await sleepRandom(5000, 8000); // pausa longa entre e-mails
  }

  await browser.close();
})();
