"""Génère les captures d'écran (python tools/screenshots.py).

- web/screenshots/ : captures du manifeste (application installable).
- fastlane/metadata/android/fr-FR/images/phoneScreenshots/ : captures Google Play,
  1080 × 1920 (format 9:16, côté long ≤ 2 × côté court, PNG sans transparence), comme l'exige Google Play.
"""
import asyncio, functools, http.server, os, threading
from pathlib import Path
from PIL import Image
from playwright.async_api import async_playwright

ROOT = Path(__file__).resolve().parent.parent
WEB = ROOT / 'web'
OUT = WEB / 'screenshots'
PLAY = ROOT / 'fastlane/metadata/android/fr-FR/images/phoneScreenshots'

SCENES = [  # (nom, code JavaScript à exécuter avant la capture ; None = accueil)
    ('1-accueil', None),
    ('2-langue', "__T.start(__T.byId('pt-br'),0,0)"),
    ('3-musique', "__T.start(__T.byId('music'),0,0)"),
    ('4-echecs', "__T.start(__T.byId('chess'),2,0)"),
    ('5-maths', "__T.start(__T.byId('maths'),4,0)"),
    ('6-cle-de-fa', "__T.start(__T.byId('music'),1,2)"),
]


def opaque(path):
    """Google Play refuse la transparence : on aplatit sur fond blanc."""
    im = Image.open(path).convert('RGB')
    im.save(path, optimize=True)


async def main():
    class Q(http.server.SimpleHTTPRequestHandler):
        def log_message(self, *a): pass
    srv = http.server.ThreadingHTTPServer(('127.0.0.1', 0), functools.partial(Q, directory=str(WEB)))
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    base = f'http://localhost:{srv.server_address[1]}/index.html?selftest'
    kw = {'executable_path': os.environ['CHROME_PATH']} if os.environ.get('CHROME_PATH') else {}
    OUT.mkdir(parents=True, exist_ok=True)
    PLAY.mkdir(parents=True, exist_ok=True)
    for old in PLAY.glob('*.png'):
        old.unlink()
    async with async_playwright() as p:
        b = await p.chromium.launch(args=['--no-sandbox'], **kw)
        # 1. Manifeste
        pg = await b.new_page(viewport={'width': 390, 'height': 844})
        await pg.goto(base); await pg.wait_for_selector('.tile')
        await pg.screenshot(path=str(OUT / 'accueil-mobile.png'))
        await pg.evaluate("__T.start(__T.byId('music'),0,0)"); await pg.wait_for_timeout(200)
        await pg.screenshot(path=str(OUT / 'lecon-mobile.png'))
        await pg.evaluate("__T.start(__T.byId('chess'),2,0)"); await pg.wait_for_timeout(200)
        await pg.screenshot(path=str(OUT / 'echecs-mobile.png'))
        await pg.evaluate("__T.start(__T.byId('music'),1,2)"); await pg.wait_for_timeout(200)
        await pg.screenshot(path=str(OUT / 'cle-fa-mobile.png'))
        await pg.set_viewport_size({'width': 1280, 'height': 800}); await pg.goto(base); await pg.wait_for_selector('.tile')
        await pg.screenshot(path=str(OUT / 'accueil-large.png'))
        await pg.close()
        # 2. Google Play : 360 × 640 points × 3 = 1080 × 1920 pixels
        ctx = await b.new_context(viewport={'width': 360, 'height': 640}, device_scale_factor=3, is_mobile=True, has_touch=True)
        pg = await ctx.new_page()
        for name, js in SCENES:
            await pg.goto(base); await pg.wait_for_selector('.tile')
            if js:
                await pg.evaluate(js); await pg.wait_for_timeout(250)
            await pg.screenshot(path=str(PLAY / f'{name}.png'))
        await b.close()
    srv.shutdown()
    for f in list(OUT.glob('*.png')) + list(PLAY.glob('*.png')):
        opaque(f)
    print('Captures :', ', '.join(sorted(f.name for f in PLAY.glob('*.png'))))


asyncio.run(main())
