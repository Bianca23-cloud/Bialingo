"""Prépare l'application Android (Capacitor) à partir de la version web.

  python tools/prepare_android.py web      → crée build-android/ (copie de web/ adaptée à Android)
  python tools/prepare_android.py native   → durcit le projet android/ généré par « npx cap add android »

Durcissement appliqué :
  - aucune autorisation : la permission INTERNET est retirée (l'application fonctionne entièrement hors ligne) ;
  - pas de sauvegarde automatique vers le cloud (allowBackup=false), pas de trafic en clair ;
  - débogage de la WebView désactivé (capacitor.config.json) ;
  - icônes et écran de démarrage Bialingo, numéro de version issu de la publication.
"""
import os, re, shutil, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
WEB, OUT, ANDROID, RES = ROOT / 'web', ROOT / 'build-android', ROOT / 'android', ROOT / 'android-res'


def sub(path, pattern, repl, count=1, flags=0, required=True):
    text = path.read_text(encoding='utf-8')
    new, n = re.subn(pattern, repl, text, count=count, flags=flags)
    if required and n == 0:
        sys.exit(f'Motif introuvable dans {path}: {pattern}')
    path.write_text(new, encoding='utf-8')


def prepare_web():
    if OUT.exists():
        shutil.rmtree(OUT)
    shutil.copytree(WEB, OUT, ignore=shutil.ignore_patterns('screenshots', 'sw.js', 'telecharger.html', 'dl.js'))
    # Capacitor injecte son pont natif sous forme de script en ligne : on l'autorise uniquement dans l'application Android,
    # qui ne charge jamais de contenu distant (aucune permission Internet).
    sub(OUT / 'index.html', r"script-src 'self'", "script-src 'self' 'unsafe-inline'")

    # Voix du téléphone : on inclut le moteur Capacitor et l'extension Text-to-Speech (versions « navigateur » sans outil
    # d'assemblage), puis native.js expose l'extension à l'application sous le nom window.BIA_TTS.
    nm = ROOT / 'node_modules'
    core = nm / '@capacitor/core/dist/capacitor.js'
    # (fichier « navigateur » de l'extension, nom de la classe exposée, nom donné à Bialingo)
    plugins = [(nm / '@capacitor-community/text-to-speech/dist/plugin.js', 'TextToSpeech', 'BIA_TTS', 'tts-plugin.js'),
               (nm / '@capacitor-community/speech-recognition/dist/plugin.js', 'SpeechRecognition', 'BIA_SR', 'sr-plugin.js')]
    tags, lines = [], []
    if core.exists():
        shutil.copy(core, OUT / 'capacitor.js')
        tags.append('capacitor.js')
        for path, cls, name, dest in plugins:
            if not path.exists():
                print(f'Avertissement : extension {cls} absente ({name} désactivé, l\'application garde une solution de repli)')
                continue
            src = path.read_text(encoding='utf-8')
            m = re.search(r'var\s+(\w+)\s*=\s*\(function', src)
            if not m:
                print(f'Avertissement : nom global de l\'extension {cls} introuvable')
                continue
            shutil.copy(path, OUT / dest)
            tags.append(dest)
            lines.append(f"window.{name} = (window.{m.group(1)} && window.{m.group(1)}.{cls}) || null;")
        if lines:
            (OUT / 'native.js').write_text("'use strict';\n/* Expose les extensions natives (voix du téléphone, reconnaissance vocale) à Bialingo. */\n"
                                           + '\n'.join(lines) + '\n', encoding='utf-8')
            tags.append('native.js')
    else:
        print('Avertissement : @capacitor/core absent (lancer npm install d\'abord)')
    if tags:
        sub(OUT / 'index.html', r'<script src="glyphs.js"></script>',
            ''.join(f'<script src="{t}"></script>\n' for t in tags) + '<script src="glyphs.js"></script>')
    print('build-android/ prêt :', ', '.join(tags) or 'sans moteur natif')


def prepare_native():
    manifest = ANDROID / 'app/src/main/AndroidManifest.xml'
    text = manifest.read_text(encoding='utf-8')
    if 'xmlns:tools' not in text:
        text = text.replace('xmlns:android="http://schemas.android.com/apk/res/android"',
                            'xmlns:android="http://schemas.android.com/apk/res/android"\n    xmlns:tools="http://schemas.android.com/tools"', 1)
    text = re.sub(r'\s*<uses-permission android:name="android.permission.INTERNET"\s*/>', '', text)
    text = text.replace('</manifest>', '    <uses-permission android:name="android.permission.INTERNET" tools:node="remove" />\n</manifest>')
    text = re.sub(r'android:allowBackup="true"', 'android:allowBackup="false"', text)
    # Reconnaissance vocale (exercices de prononciation) : seul le micro est autorisé, demandé au moment où l'on appuie dessus.
    # La transcription est faite par le service vocal du téléphone ; Bialingo reste sans accès Internet.
    if 'android.speech.RecognitionService' not in text:
        text = text.replace('</manifest>', '    <queries>\n        <intent>\n            <action android:name="android.speech.RecognitionService" />\n        </intent>\n    </queries>\n</manifest>')
    if 'usesCleartextTraffic' not in text:
        text = text.replace('<application', '<application\n        android:usesCleartextTraffic="false"', 1)
    manifest.write_text(text, encoding='utf-8')

    # Version : code = numéro de compilation, nom = étiquette de publication (v1.2.0 → 1.2.0)
    code = os.environ.get('VERSION_CODE', '1')
    name = os.environ.get('VERSION_NAME', '3.0.0').lstrip('v')
    gradle = ANDROID / 'app/build.gradle'
    sub(gradle, r'versionCode \d+', f'versionCode {int(code)}')
    sub(gradle, r'versionName "[^"]*"', f'versionName "{name}"')

    # Icônes
    res = ANDROID / 'app/src/main/res'
    for d in RES.glob('mipmap-*'):
        for f in d.iterdir():
            shutil.copy(f, res / d.name / f.name)
    shutil.copy(RES / 'values/ic_launcher_background.xml', res / 'values/ic_launcher_background.xml')
    # Écrans de démarrage : on remplace chaque image du modèle par la nôtre, à la même taille
    from PIL import Image
    src = Image.open(RES / 'splash-source.png').convert('RGB')
    n = 0
    for f in res.glob('drawable*/splash.png'):
        w, h = Image.open(f).size
        side = max(w, h)
        img = src.resize((side, side), Image.LANCZOS)
        left, top = (side - w) // 2, (side - h) // 2
        img.crop((left, top, left + w, top + h)).save(f)
        n += 1
    print(f'android/ durci : permissions retirées, version {name} ({code}), {n} écrans de démarrage')


if __name__ == '__main__':
    {'web': prepare_web, 'native': prepare_native}.get(sys.argv[1] if len(sys.argv) > 1 else '', lambda: sys.exit(__doc__))()
