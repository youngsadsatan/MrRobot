/**
 * Bulk registra em EroMe a partir de uma lista de e-mails usando OCR Tesseract.js
 * Logs em register.log:
 *  🟢 — e-mail livre (e loop interrompido)
 *  🔴 — e-mail já usado
 */
const fs = require('fs');
const path = require('path');
const puppeteer = require('puppeteer');
const Tesseract = require('tesseract.js');
const sharp = require('sharp');

(async () => {
  const SITE = process.env.SITE_URL;
  const USER = process.env.USERNAME;
  const PASS = process.env.PASSWORD;
  const LOG_PATH = path.resolve(__dirname, 'register.log');

  // inicia log
  fs.writeFileSync(LOG_PATH, '', 'utf-8');

  // carrega e-mails
  const emails = fs.readFileSync(path.resolve(__dirname, 'emails.txt'), 'utf-8')
                   .split(/\r?\n/).filter(Boolean);

  const browser = await puppeteer.launch({
    headless: "new",
    args: ['--no-sandbox','--disable-setuid-sandbox']
  });
  const page = await browser.newPage();
  await page.goto(SITE, { waitUntil: 'networkidle2' });

  for (const email of emails) {
    // limpa campos
    await page.evaluate(() => {
      ['name','email','password','password_confirmation','captcha']
        .forEach(n => document.querySelector(`input[name="${n}"]`).value = '');
    });

    // preenche
    await page.type('input[name="name"]', USER);
    await page.type('input[name="email"]', email);
    await page.type('input[name="password"]', PASS);
    await page.type('input[name="password_confirmation"]', PASS);

    // aguarda e captura captcha
    const img = await page.waitForSelector('form img', { timeout: 5000 });
    const buf = await img.screenshot();
    let code;
    try {
      // pré-processa e OCR
      const proc = await sharp(buf).grayscale().normalise().threshold(150).toBuffer();
      const { data: { text } } = await Tesseract.recognize(proc, 'eng', {
        tessedit_char_whitelist: '0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz'
      });
      code = text.replace(/[^0-9A-Za-z]/g, '').substr(0,4);
      if (code.length !== 4) throw new Error('len');
    } catch {
      console.log(`⚠️ OCR falhou para ${email}, recarregando captcha`);
      await page.click('form img');             // recarrega o captcha clicando na imagem
      await page.waitForTimeout(800);
      continue; // tenta mesmo e-mail com novo captcha
    }
    await page.type('input[name="captcha"]', code);

    // submete e aguarda resposta
    await Promise.all([
      page.click('button[type="submit"]'),
      page.waitForResponse(res => res.url().includes('/user/register') && res.status() === 200)
    ]);

    const html = await page.content();
    if (/The email is already used\./.test(html)) {
      console.log(`🔴 ${email}`);
      fs.appendFileSync(LOG_PATH, `🔴 ${email}\n`);
      // recarrega apenas o captcha
      await page.click('form img');
      await page.waitForTimeout(800);
    } else {
      console.log(`🟢 ${email}`);
      fs.appendFileSync(LOG_PATH, `🟢 ${email}\n`);
      break; // interrompe no primeiro sucesso
    }
  }

  await browser.close();
})();
