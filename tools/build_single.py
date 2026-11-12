# -*- coding: utf-8 -*-
"""Fabrique Bialingo en UN SEUL fichier HTML (tout inclus, fonctionne hors ligne en double-cliquant).

Usage : python3 tools/build_single.py SORTIE.html [--fragment]
  --fragment : sans <html>/<head> (page publiée telle quelle comme « artefact »).
  --desktop  : version pour l'application Windows / Linux (desktop/app/index.html).
Le fichier unique n'a pas de manifeste : il s'ouvre dans le navigateur, sans installation.
"""
import base64, pathlib, re, sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
WEB = ROOT / 'web'


def build(out, fragment=False, desktop=False):
    css = (WEB / 'app.css').read_text(encoding='utf-8')
    js = (WEB / 'glyphs.js').read_text(encoding='utf-8') + '\n</script>\n<script>\n' + (WEB / 'app.js').read_text(encoding='utf-8')
    assert '</script' not in (WEB / 'app.js').read_text(encoding='utf-8').lower()
    icon = base64.b64encode((WEB / 'icons/icon-192.png').read_bytes()).decode()
    # Application de bureau (Electron) : la reconnaissance vocale en ligne n'y existe pas ; on utilise l'enregistrement local.
    idx = WEB / 'audio/index.json'
    idx_js = idx.read_text(encoding='utf-8').strip() if idx.exists() else '{}'
    pre = ('<script>window.BIA_NO_SR=true;window.BIA_DESKTOP=true;window.BIA_AUDIO_IDX=' + idx_js + ';</script>\n') if desktop else ''
    body = f'<div id="app"></div>\n{pre}<script>\n{js}\n</script>\n'
    if fragment:
        html = f'<title>Bialingo</title>\n<meta name="claude:viewport-fit-sides" content="cover">\n<style>\n{css}\n</style>\n\n{body}'
    else:
        html = ('<!doctype html>\n<html lang="fr">\n<head>\n<meta charset="utf-8">\n'
                '<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">\n'
                '<meta name="referrer" content="no-referrer">\n<title>Bialingo</title>\n'
                f'<link rel="icon" href="data:image/png;base64,{icon}">\n<meta name="color-scheme" content="light dark">\n'
                f'<style>\n{css}\n</style>\n</head>\n<body>\n{body}</body>\n</html>\n')
    pathlib.Path(out).write_text(html, encoding='utf-8')
    print(out, round(len(html.encode()) / 1024), 'Ko')


if __name__ == '__main__':
    if len(sys.argv) < 2:
        sys.exit(__doc__)
    build(sys.argv[1], '--fragment' in sys.argv, '--desktop' in sys.argv)
