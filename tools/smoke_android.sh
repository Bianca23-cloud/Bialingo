#!/usr/bin/env bash
# Test de démarrage réel : installe l'APK sur l'émulateur, lance Bialingo et vérifie que l'accueil s'affiche.
set -euo pipefail
mkdir -p smoke
APK=$(ls dist/*.apk | head -n 1)
adb install -r "$APK"
adb shell monkey -p fr.bialingo.app -c android.intent.category.LAUNCHER 1 > /dev/null
ok=0
for i in $(seq 1 12); do
  sleep 5
  adb shell uiautomator dump /sdcard/ui.xml > /dev/null 2>&1 || continue
  adb pull /sdcard/ui.xml smoke/ui.xml > /dev/null 2>&1 || continue
  if grep -Eq "Bonjour|Bonsoir|Langues|Bialingo" smoke/ui.xml; then ok=1; break; fi
done
adb exec-out screencap -p > smoke/accueil.png || true
adb logcat -d -s chromium Capacitor Console > smoke/logcat.txt 2>&1 || true
if [ "$ok" != "1" ]; then
  echo "::error::L'accueil de Bialingo ne s'affiche pas sur l'émulateur (voir la capture et logcat)."
  exit 1
fi
echo "Bialingo démarre et affiche l'accueil sur Android : OK"
