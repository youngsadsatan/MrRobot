/**
 * Bulk registra em EroMe usando Puppeteer + PaddleOCR
 * – recarrega a página após cada tentativa
 * – 🟢 e 🔴 em register.log
 */
const fs = require('fs');
const path = require('path');
const { spawnSync } = require('child_process');
const puppeteer = require('puppeteer');

function sleepRandom(min, max) {
  const t = Math.floor(Math.random() * (max - min + 1)) + min;
  return new Promise(r => setTimeout(r, t));
}

(async () => {
  const SITE = process.env.SITE_URL;
  const USER = process.env.USERNAME;
  const PASS = process.env.PASSWORD;
  const LOG = path.resolve(__dirname, 'register.log');

  // limpa/cria log
  fs.writeFileSync(LOG, '', 'utf8');

  // lê emails.txt na raiz do projeto
  const emailsPath = path.resolve(__dirname, 'emails.txt');
  const emails = fs.readFileSync(emailsPath, 'utf8')
    .split(/\r?\n/)
    .map(l => l.trim())
    .filter(l => l && !l.startsWith('#'));

  const browser = await puppeteer.launch({
    headless: "new",
    args: ['--no-sandbox','--disable-setuid-sandbox']
  });
  const page = await browser.newPage();

  for (const email of emails) {
    // carrega página limpa
    await page.goto(SITE, { waitUntil: 'networkidle2' });
    await sleepRandom(5000, 8000);

    // preenche formulário
    await page.type('#name', USER, { delay: 100 });
    await page.type('#email', email, { delay: 100 });
    await page.type('#password', PASS, { delay: 100 });
    await page.type('#password-confirm', PASS, { delay: 100 });

    await sleepRandom(3000, 5000);

    // captura CAPTCHA
    const img = await page.waitForSelector('form .mb-10 img.initial', { timeout: 10000 });
    const buf = await img.screenshot();
    const tmpImg = path.resolve(__dirname, 'captcha.png');
    fs.writeFileSync(tmpImg, buf);

    // resolve com captcha.py
    const res = spawnSync('python3', ['automation/captcha.py', tmpImg], { encoding: 'utf8' });
    const code = (res.stdout || '').trim();
    if (!/^[0-9A-Za-z]{4}$/.test(code)) {
      console.log(`⚠️ OCR falhou para ${email}`);
      fs.appendFileSync(LOG, `⚠️ OCR falhou para ${email}\n`);
      continue; // próximo email
    }

    await page.type('input[name="captcha"]', code, { delay: 100 });
    await sleepRandom(1000, 2000);

    // submit
    await Promise.all([
      page.click('button[type="submit"]'),
      page.waitForNavigation({ waitUntil: 'networkidle2' })
    ]);

    const html = await page.content();
    if (/The email is already used\./.test(html)) {
      console.log(`🔴 ${email}`);
      fs.appendFileSync(LOG, `🔴 ${email}\n`);
    } else {
      console.log(`🟢 ${email}`);
      fs.appendFileSync(LOG, `🟢 ${email}\n`);
      break; // sucesso
    }

    await sleepRandom(6000, 10000);
  }

  await browser.close();
})();
```0
