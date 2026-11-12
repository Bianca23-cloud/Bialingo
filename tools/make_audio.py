# -*- coding: utf-8 -*-
"""Enregistre chaque mot et chaque phrase de Bialingo avec une VOIX NATIVE de sa langue
(voix neuronales gratuites de Microsoft Edge, via l'outil libre edge-tts : https://github.com/rany2/edge-tts).

Entrée : tools/audio_texts.json (tout ce que l'application prononce, par langue ; vérifié par les tests).
Sortie : web/audio/<langue>/<empreinte>.mp3 + web/audio/index.json (liste des fichiers présents).
L'empreinte est FNV-1a 32 bits du texte (même calcul que fnv() dans web/app.js).
Usage (sur GitHub Actions) : pip install edge-tts && python tools/make_audio.py
"""
import asyncio, json, os, pathlib, sys
import edge_tts

for _f in (sys.stdout, sys.stderr):      # Windows : sortie en UTF-8 (sinon les messages accentués plantent)
    try:
        _f.reconfigure(encoding='utf-8', errors='replace')
    except Exception:
        pass

ROOT = pathlib.Path(__file__).resolve().parent.parent
OUT = ROOT / 'web' / 'audio'
# Une voix native par langue et par pays (2e voix = secours, même langue et même pays)
VOICES = {
    'en-GB': ['en-GB-SoniaNeural', 'en-GB-LibbyNeural'],
    'pt-BR': ['pt-BR-FranciscaNeural', 'pt-BR-AntonioNeural'],
    'pt-PT': ['pt-PT-RaquelNeural', 'pt-PT-DuarteNeural'],
    'it-IT': ['it-IT-ElsaNeural', 'it-IT-IsabellaNeural'],
    'es-ES': ['es-ES-ElviraNeural', 'es-ES-AlvaroNeural'],
    'es-MX': ['es-MX-DaliaNeural', 'es-MX-JorgeNeural'],
    'es-AR': ['es-AR-ElenaNeural', 'es-AR-TomasNeural'],
    'de-DE': ['de-DE-KatjaNeural', 'de-DE-AmalaNeural'],
    'el-GR': ['el-GR-AthinaNeural', 'el-GR-NestorasNeural'],
    'ro-RO': ['ro-RO-AlinaNeural', 'ro-RO-EmilNeural'],
    'ru-RU': ['ru-RU-SvetlanaNeural', 'ru-RU-DmitryNeural'],
    'zh-CN': ['zh-CN-XiaoxiaoNeural', 'zh-CN-XiaoyiNeural'],
    'ja-JP': ['ja-JP-NanamiNeural', 'ja-JP-KeitaNeural'],
    'fr-FR': ['fr-FR-EloiseNeural', 'fr-FR-DeniseNeural'],   # la mascotte : voix jeune et joyeuse
}
RATE = {'fr-FR': '+5%'}


def fnv(s):
    h = 0x811c9dc5
    b = s.encode('utf-16-le')
    for i in range(0, len(b), 2):          # unités UTF-16, comme charCodeAt en JavaScript
        h ^= b[i] | (b[i + 1] << 8)
        h = (h * 16777619) & 0xffffffff
    return f'{h:08x}'


async def main():
    texts = json.loads((ROOT / 'tools' / 'audio_texts.json').read_text(encoding='utf-8'))
    todo = [(lang, t.strip(), OUT / lang / f'{fnv(t.strip())}.mp3') for lang, items in texts.items() for t in items]
    sem, failed, done = asyncio.Semaphore(8), [], [0]

    async def one(lang, text, path):
        if path.exists() and path.stat().st_size > 500:
            return
        path.parent.mkdir(parents=True, exist_ok=True)
        async with sem:
            for attempt in range(4):
                voice = VOICES[lang][0 if attempt < 2 else 1]
                try:
                    await asyncio.wait_for(edge_tts.Communicate(text, voice, rate=RATE.get(lang, '-8%'),
                                                                pitch='+8Hz' if lang == 'fr-FR' else '+0Hz').save(str(path)), 40)
                    if path.stat().st_size > 500:
                        done[0] += 1
                        if done[0] % 200 == 0:
                            print(done[0], 'enregistrements', flush=True)
                        return
                except Exception as e:
                    print(f'nouvel essai {lang} ({voice}) « {text[:30]} » : {type(e).__name__}', flush=True)
                await asyncio.sleep(2 + attempt * 3)
            failed.append(f'{lang} : {text}')
            if path.exists():
                path.unlink()

    await asyncio.gather(*(one(*x) for x in todo))
    index = {}
    for lang, t, path in todo:
        if path.exists() and path.stat().st_size > 500:
            index.setdefault(lang, []).append(path.stem)
    index = {k: sorted(set(v)) for k, v in sorted(index.items())}
    (OUT / 'index.json').write_text(json.dumps(index, separators=(',', ':')), encoding='utf-8')
    total = sum(len(v) for v in index.values())
    for lang in sorted(texts):
        print(f'{lang:6} {VOICES[lang][0]:24} {len(index.get(lang, []))}/{len(set(texts[lang]))}')
    print('TOTAL', total, 'enregistrements natifs sur', len({(l, t) for l, t, _ in todo}))
    if failed:
        print('::warning::' + str(len(failed)) + " phrases sans enregistrement (l'appareil prendra le relais, même langue uniquement) : " + ' | '.join(failed[:10]))
    if total < 0.9 * len({(l, t) for l, t, _ in todo}):
        sys.exit('Trop d\'enregistrements manquants')

asyncio.run(main())
