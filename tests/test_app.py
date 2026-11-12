"""Tests automatisés de Bialingo (version web installable).

Lancement :  python tests/test_app.py
Prérequis :  pip install playwright  puis  python -m playwright install chromium
Variables facultatives : CHROME_PATH=/chemin/vers/chrome (navigateur déjà installé) ;
            BROWSERS=chromium,webkit pour tester aussi le moteur de Safari (iPhone 13).

Le script échoue (code de sortie 1) au moindre problème :
 - une leçon ne se termine pas ou une bonne réponse est refusée ;
 - une requête part vers un autre site que l'application elle-même ;
 - la politique de sécurité (CSP) bloque quelque chose, ou une erreur JavaScript survient ;
 - un « code de sauvegarde » piégé parvient à injecter du code (XSS) ;
 - un contraste de couleur est inférieur à 4,5:1 (WCAG 2.1 AA) ;
 - le manifeste, le mode hors ligne ou les pages légales sont incomplets.
"""
import asyncio, base64, functools, http.server, json, os, re, sys, threading
from pathlib import Path
from playwright.async_api import async_playwright

ROOT = Path(__file__).resolve().parent.parent
WEB = ROOT / 'web'
FAILS = []


def fail(msg):
    FAILS.append(msg)
    print('ÉCHEC :', msg)


def serve():
    class Quiet(http.server.SimpleHTTPRequestHandler):
        def log_message(self, *a): pass
    handler = functools.partial(Quiet, directory=str(WEB))
    srv = http.server.ThreadingHTTPServer(('127.0.0.1', 0), handler)
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    return srv


# ---------- contrastes (WCAG 2.1) ----------
def lum(hexc):
    h = hexc.lstrip('#')
    r, g, b = (int(h[i:i + 2], 16) / 255 for i in (0, 2, 4))
    f = lambda c: c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4
    return 0.2126 * f(r) + 0.7152 * f(g) + 0.0722 * f(b)


def ratio(a, b):
    la, lb = sorted((lum(a), lum(b)), reverse=True)
    return (la + 0.05) / (lb + 0.05)


def check_contrast():
    css = (WEB / 'app.css').read_text(encoding='utf-8')
    light = dict(re.findall(r'--([\w-]+):(#[0-9A-Fa-f]{6})', css.split('@media')[0]))
    dark_block = re.search(r':root\[data-theme="dark"\]\{(.*?)\}', css, re.S).group(1)
    dark = dict(light, **dict(re.findall(r'--([\w-]+):(#[0-9A-Fa-f]{6})', dark_block)))
    pairs = [('ink', 'bg'), ('ink', 'surface'), ('muted', 'bg'), ('muted', 'surface'), ('on-accent', 'accent'),
             ('good', 'good-soft'), ('bad', 'bad-soft'), ('gold', 'gold-soft'), ('ink', 'accent-soft'),
             ('good', 'surface'), ('bad', 'surface')]
    pairs += [('ink', 'p%d' % i) for i in range(1, 9)] + [('muted', 'p%d' % i) for i in range(1, 9)]
    for theme, t in (('clair', light), ('sombre', dark)):
        for fg, bg in pairs:
            r = ratio(t[fg], t[bg])
            if r < 4.5:
                fail(f'contraste {theme} --{fg} sur --{bg} = {r:.2f}:1 (< 4,5:1)')
    print('Contrastes vérifiés :', len(pairs) * 2, 'paires')


ANSWER = r"""() => {
 const L=__T.L(), e=L.queue[L.i]; const q=s=>document.querySelector(s), qa=s=>[...document.querySelectorAll(s)];
 const words=s=>s.replace(/[¿¡?!.,;]/g,' ').split(/\s+/).filter(Boolean);
 if(e.type==='choice'){ q(`.opt[data-k="${e.answer}"]`).click(); q('#checkbtn').click(); }
 else if(e.type==='type'){ let v; if(e.numeric!=null) v=String(e.numeric).replace('.',','); else if(e.frac) v=e.frac.d===1?String(e.frac.n):e.frac.n+'/'+e.frac.d; else v=e.accept[0];
   const i=q('#ans'); i.value=v; i.dispatchEvent(new Event('input',{bubbles:true})); q('#checkbtn').click(); }
 else if(e.type==='build'){ for(const w of words(e.accept[0])){ const b=qa('#bank .word').find(x=>!x.disabled&&(x.dataset.word||x.textContent)===w); if(!b) return 'tuile manquante '+w; b.click(); } q('#checkbtn').click(); }
 else if(e.type==='match'){ e.pairs.forEach((p,i)=>{ q(`.opt[data-s="l"][data-i="${i}"]`).click(); q(`.opt[data-s="r"][data-i="${i}"]`).click(); }); }
 else if(e.type==='board'){ const s=e.sol[0]; q(`button.sq[data-sq="${s.slice(0,2)}"]`).click(); q(`button.sq[data-sq="${s.slice(2)}"]`).click(); }
 else if(e.type==='moves'){ e.targets.forEach(t=>q(`button.sq[data-sq="${t}"]`).click()); q('#checkbtn').click(); }
 else if(e.type==='speak'){ __T.judge(e,['zzz qqq']); if(q('#lfoot').classList.contains('bad')) return 'prononciation fausse acceptée'; __T.judge(e,[e.target.toUpperCase()+' !']); }
 else if(e.type==='piano'){ e.want.forEach(pc=>{ const k=qa('.pk').find(x=>((+x.dataset.m)%12)===pc); if(!k) throw new Error('touche '+pc); k.click(); }); q('#checkbtn').click(); }
 const ok=q('#lfoot').classList.contains('good'); const info=e.type+' : '+(e.label||'')+' | '+(e.reveal||'');
 q('[data-act="next"]').click(); return ok?null:info;
}"""

WRONG = r"""() => { const L=__T.L(), e=L.queue[L.i]; const q=s=>document.querySelector(s);
 if(e.type==='choice'){ const k=(e.answer+1)%e.options.length; q(`.opt[data-k="${k}"]`).click(); q('#checkbtn').click(); }
 else { const s=q('[data-act="skip"]'); if(s) s.click(); else { const i=q('#ans'); if(i){i.value='zzz';i.dispatchEvent(new Event('input',{bubbles:true}));} else { q('#bank .word').click(); } q('#checkbtn').click(); } }
 const bad=q('#lfoot').classList.contains('bad'); q('[data-act="next"]').click(); return bad; }"""


async def run_lesson(pg, start_js, label, max_steps=60):
    await pg.evaluate(start_js)
    n = 0
    for _ in range(max_steps):
        if not await pg.evaluate("!!document.querySelector('.lesson')"):
            return n
        r = await pg.evaluate(ANSWER)
        n += 1
        if r:
            fail(f'{label} : bonne réponse refusée → {r}')
    fail(f'{label} : la leçon ne se termine pas')
    return n


async def run_engine(p, engine, base):
    if engine == 'webkit':
        # moteur de Safari, avec l'écran, le tactile et l'identité d'un iPhone 13
        browser = await p.webkit.launch()
        ctx = await browser.new_context(**p.devices['iPhone 13'])
    else:
        kw = {'executable_path': os.environ['CHROME_PATH']} if os.environ.get('CHROME_PATH') else {}
        browser = await p.chromium.launch(args=['--no-sandbox'], **kw)
        ctx = await browser.new_context(viewport={'width': 390, 'height': 844}, service_workers='allow')
    print(f'\n=== Navigateur : {engine} ===')
    await ctx.add_init_script("window.__csp=[];document.addEventListener('securitypolicyviolation',e=>window.__csp.push(e.violatedDirective+' '+e.blockedURI));window.__dialog=0;")
    external, errors = [], []
    ctx.on('request', lambda r: external.append(r.url) if not r.url.startswith(base) and not r.url.startswith('data:') and not r.url.startswith('blob:') else None)
    pg = await ctx.new_page()
    pg.on('pageerror', lambda e: errors.append(str(e)))
    pg.on('console', lambda m: errors.append(m.text) if m.type == 'error' else None)
    pg.on('dialog', lambda d: (errors.append('boîte de dialogue inattendue : ' + d.message), asyncio.ensure_future(d.dismiss())))
    await pg.goto(base + 'index.html?selftest')
    # Premier lancement : écran de bienvenue, chacun écrit son prénom (aucun prénom imposé)
    await pg.wait_for_selector('#nameform')
    await pg.click('#nameform button[type=submit]')
    if not await pg.evaluate("document.querySelector('#werr').textContent.length>0"):
        fail('bienvenue : un prénom vide doit être refusé')
    await pg.fill('#wname', 'Camille')
    await pg.click('#nameform button[type=submit]')
    await pg.wait_for_selector('.tile')
    if await pg.evaluate("__T.me().name") != 'Camille' or 'Camille' not in await pg.inner_text('#h-hello'):
        fail('bienvenue : le prénom saisi doit être utilisé')

    # 1. Toutes les leçons, tous les modes
    total = 0
    courses = await pg.evaluate("__T.C.map(c=>[c.id,c.units.length])")
    for cid, nu in courses:
        for ui in range(nu):
            for mode in (0, 1, 2, 'turbo'):
                total += await run_lesson(pg, f"__T.start(__T.byId('{cid}'),{ui},{json.dumps(mode)})", f'{cid} unité {ui+1} mode {mode}')
    for cid, nu in courses:
        lvls = await pg.evaluate(f"levelsOf(__T.byId('{cid}'))") if False else await pg.evaluate(f"[...new Set(__T.byId('{cid}').units.map(u=>u.lv||0))]")
        for lv in lvls:
            total += await run_lesson(pg, f"__T.start(__T.byId('{cid}'),{lv},'level')", f'{cid} test du niveau {lv}')
    total += await run_lesson(pg, "__T.start(null,0,'review')", 'révision')
    print('Exercices réussis automatiquement :', total)

    # 1 bis. v3 : 10 langues à 6 niveaux, ordre de déblocage, correction de la prononciation
    v3 = await pg.evaluate("""() => { const out=[]; const langs=__T.C.filter(c=>c.kind==='lang');
     if(langs.length!==13) out.push('nombre de langues : '+langs.length);
     ['pt-pt','ro','pt-br','en-gb','ru','zh','ja'].forEach(id=>{ if(!__T.byId(id)) out.push('cours absent '+id); });
     langs.forEach(c=>{ const lv=[...new Set(c.units.map(u=>u.lv||0))].sort(); if(lv.join()!=='0,1,2,3,4,5') out.push(c.id+' niveaux '+lv.join());
       if(c.units.filter(u=>u.kind==='vocab').length!==12) out.push(c.id+' vocabulaire'); if(c.units.filter(u=>u.kind==='gram').length!==4) out.push(c.id+' grammaire');
       const o=__T.order(c); for(let k=1;k<o.length;k++){ if((c.units[o[k]].lv||0)<(c.units[o[k-1]].lv||0)) out.push(c.id+' ordre'); } });
     langs.filter(c=>['el','ru','zh','ja'].includes(c.k)).forEach(c=>c.units.forEach((u,ui)=>u.items.forEach((it,ii)=>{ if(!it[3]) out.push(c.id+' sans lettres latines : '+it[1]); if((u.g||[])[ii]&&!(u.g[ii][3]&&u.g[ii][4])) out.push(c.id+' grammaire sans lettres latines '+ui); })));
     const z=__T.speechScore('我叫安娜','我叫安'); if(Math.abs(z.score-.75)>1e-9) out.push('score chinois '+z.score);
     const r=__T.speechScore('Je suis très contente','je suis contente'); if(Math.abs(r.score-.75)>1e-9||r.ok.join()!=='true,true,false,true') out.push('score '+r.score+' '+r.ok);
     const g=__T.speechScore('Μιλάω λίγα ελληνικά','μιλαω λιγα ελληνικα'); if(g.score!==1) out.push('score grec '+g.score);
     return out; }""")
    if v3:
        fail('v3 : ' + ' ; '.join(v3[:8]))
    cat = await pg.evaluate("__T.audioCatalog()")
    ref = json.loads(open(os.path.join(ROOT, 'tools', 'audio_texts.json'), encoding='utf-8').read())
    if cat != ref:
        fail('tools/audio_texts.json n\'est plus à jour : relancer la génération de la liste des voix')
    # Jamais une langue lue avec la voix d'une autre langue
    wrong = await pg.evaluate("""() => { const vs=[{lang:'fr-FR',name:'Microsoft Denise',localService:true},{lang:'en-US',name:'Microsoft David',localService:true}];
      return ['el-GR','ru-RU','zh-CN','ja-JP','ro-RO','en-GB'].map(l=>[l,(__T.pickVoice(vs,l)||{}).lang||null]); }""")
    if any(v and v[:2] != l[:2] for l, v in wrong):
        fail(f'voix d\'une autre langue choisie : {wrong}')
    # Déblocage : la 1re unité du niveau A2 ne s'ouvre qu'après tout le niveau A1 ; un test de niveau réussi valide les niveaux inférieurs
    unlock = await pg.evaluate("""() => { const c=__T.byId('ro'),p=__T.me(); p.prog[c.id]={}; const o=__T.order(c), a1=o.filter(i=>(c.units[i].lv||0)===0), a2=o.find(i=>c.units[i].lv===1);
      const before=__T.unitOpen(p,c,a2); a1.forEach(i=>p.prog[c.id][i]=3); const after=__T.unitOpen(p,c,a2); p.prog[c.id]={}; return [before,after]; }""")
    if unlock != [False, True]:
        fail(f'ordre de déblocage par niveau : {unlock}')
    await pg.evaluate("__T.start(__T.byId('de'),2,'level')")
    await pg.evaluate("__T.L().firstOk=__T.L().total; __T.finish();")
    low = await pg.evaluate("(()=>{const c=__T.byId('de'),p=__T.me();return c.units.every((u,i)=>(u.lv||0)>2||__T.unitDone(p,c,i));})()")
    if not low:
        fail('le test de niveau réussi doit valider aussi les niveaux inférieurs')
    await pg.evaluate("__T.me().prog={}")
    # Bouton « Je ne peux pas parler maintenant »
    sp = await pg.evaluate("""() => { const c=__T.byId('it'); __T.start(c,0,1); const L=__T.L(); const k=L.queue.findIndex(e=>e.type==='speak'); if(k<0) return 'aucun exercice de prononciation';
      L.i=k; __T.renderLesson(); document.querySelector('[data-act="nospeak"]').click(); return L.queue[L.i].type!=='speak'&&L.noSpeak?null:'remplacement absent'; }""")
    if sp:
        fail('prononciation : ' + sp)

    # 2. Mauvaise réponse : l'exercice doit revenir en fin de leçon
    await pg.evaluate("__T.start(__T.byId('it'),0,0)")
    n0 = await pg.evaluate("__T.L().queue.length")
    bad = await pg.evaluate(WRONG)
    n1 = await pg.evaluate("__T.L().queue.length")
    if not bad or n1 != n0 + 1:
        fail(f'reprise des erreurs : feedback={bad}, file {n0}→{n1}')
    # Bouton « retour » (Android) pendant une leçon : doit proposer de quitter, pas fermer l'application
    await pg.evaluate("history.back()")
    await pg.wait_for_timeout(300)
    if not await pg.evaluate("!!document.querySelector('.quitbox') && !!document.querySelector('.lesson')"):
        fail('bouton retour : la confirmation de sortie de leçon ne s\'affiche pas')
    await pg.evaluate("document.querySelector('[data-act=quitok]').click()")

    # 3. Code de sauvegarde piégé (XSS) et code trop long
    evil = {'profiles': [{'id': '"><img src=x onerror=window.__pwn=1>', 'name': '<img src=x onerror=window.__pwn=1>Eve',
                          'color': 'p1" onmouseover="window.__pwn=1', 'xp': 'NaN', 'prog': {'it': {'0': 99}}, 'srs': {'<b>|1|1': {'b': 9}}, 'last': 'javascript:alert(1)'}],
            'active': 'x', 'set': {'goal': '<svg onload=alert(1)>', 'size': 'xl" onclick="x'}}
    code = 'BIA1.' + base64.b64encode(json.dumps(evil).encode()).decode()
    await pg.click('[data-act=settings]')
    await pg.fill('#importbox', code)
    await pg.click('[data-act=import]')
    await pg.click('[data-act=family]')
    st = await pg.evaluate("__T.state()")
    prof = st['profiles'][0]
    pwn = await pg.evaluate("window.__pwn")
    imgs = await pg.evaluate("document.querySelectorAll('#app img').length")
    if pwn or imgs:
        fail('XSS : le code piégé a injecté du HTML ou du script')
    if '<' in prof['name'] or prof['color'] != 'p4' or not re.match(r'^p[a-z0-9]+$', prof['id']) or prof['prog'].get('it', {}).get('0') != 3 or prof['srs'] or prof['last'] is not None:
        fail('validation du code importé incomplète : ' + json.dumps(prof)[:200])
    if st['set'] != {'rate': 0.9, 'sfx': True, 'voice': True, 'size': 'm', 'goal': 50, 'vq': 'local', 'mic': 0}:
        fail('réglages importés non normalisés : ' + json.dumps(st['set']))
    await pg.click('[data-act=settings]')
    await pg.fill('#importbox', 'BIA1.' + 'A' * 500000)
    await pg.click('[data-act=import]')
    msg = await pg.text_content('#impmsg')
    if 'pas reconnu' not in (msg or ''):
        fail('un code trop long devrait être refusé')
    print('Test d’injection (XSS) et de validation : terminé')

    # 4. Mode hors ligne, manifeste, pages légales
    await pg.wait_for_timeout(800)
    if engine == 'chromium':  # l'automate de test WebKit ne gère pas les service workers
        regs = await pg.evaluate("navigator.serviceWorker.getRegistrations().then(r=>r.length)")
        if regs < 1:
            fail("le service worker (mode hors ligne) ne s'enregistre pas")
    man = json.loads((WEB / 'manifest.webmanifest').read_text(encoding='utf-8'))
    for key in ('id', 'name', 'short_name', 'start_url', 'display', 'icons', 'screenshots', 'lang'):
        if key not in man:
            fail('manifeste : champ manquant ' + key)
    for item in man['icons'] + man['screenshots']:
        if not (WEB / item['src']).exists():
            fail('fichier manquant : ' + item['src'])
    if not any(i.get('purpose') == 'maskable' for i in man['icons']):
        fail('manifeste : icône adaptative (maskable) manquante')
    for page, must in (('telecharger.html', 'APK'), ('confidentialite.html', 'aucune donnée personnelle'), ('mentions-legales.html', 'Hébergeur')):
        await pg.goto(base + page)
        if must not in await pg.content():
            fail(f'{page} : contenu attendu absent ({must})')
    sw = (WEB / 'sw.js').read_text(encoding='utf-8')
    for f in re.findall(r"'\./([^']+)'", sw):
        if not (WEB / f).exists():
            fail('sw.js référence un fichier absent : ' + f)

    csp = await pg.evaluate("window.__csp")
    if external:
        fail('requêtes vers des sites externes : ' + ', '.join(sorted(set(external))[:5]))
    if csp:
        fail('violations CSP : ' + ', '.join(csp[:5]))
    if errors:
        fail('erreurs JavaScript : ' + ' | '.join(errors[:5]))
    await browser.close()


async def main():
    check_contrast()
    srv = serve()
    base = f'http://localhost:{srv.server_address[1]}/'
    engines = [e.strip() for e in os.environ.get('BROWSERS', 'chromium').split(',') if e.strip()]
    async with async_playwright() as p:
        for engine in engines:
            await run_engine(p, engine, base)
    srv.shutdown()
    print('\nRÉSULTAT :', 'OK, aucun problème détecté' if not FAILS else f'{len(FAILS)} problème(s)')
    sys.exit(1 if FAILS else 0)


if __name__ == '__main__':
    asyncio.run(main())
