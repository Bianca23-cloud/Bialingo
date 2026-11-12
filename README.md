# Bialingo

Application libre pour apprendre vite et bien, seul ou en famille : **13 langues et variantes (6 niveaux, de A1 à C2, dont russe, chinois et japonais avec lettres latines), maths et économie, échecs, musique et solfège**.
Gratuite et illimitée, sans compte, sans publicité, sans collecte de données. Fonctionne hors ligne.

**Téléchargements directs** (toujours la dernière version) :

| Appareil | Lien |
|---|---|
| 🪟 Windows 11 (installation en un clic) | https://github.com/Bianca23-cloud/Bialingo/releases/latest/download/Bialingo-Windows-Setup.exe |
| 🪟 Windows 11 (sans installation) | https://github.com/Bianca23-cloud/Bialingo/releases/latest/download/Bialingo-Windows-portable.exe |
| 🤖 Android | https://github.com/Bianca23-cloud/Bialingo/releases/latest/download/Bialingo.apk |
| 🐧 Linux | https://github.com/Bianca23-cloud/Bialingo/releases/latest/download/Bialingo-Linux.AppImage |
| 🍎 iPhone / iPad | https://bianca23-cloud.github.io/Bialingo/ › Safari › Partager › Sur l'écran d'accueil |

Page de téléchargement : https://bianca23-cloud.github.io/Bialingo/telecharger.html

## Contenu
- **Langues** (6 niveaux A1 → C2, vocabulaire illustré, grammaire, prononciation corrigée) : anglais britannique, portugais du Brésil et du Portugal, italien, allemand, roumain, grec moderne, russe, chinois, japonais, espagnol d'Espagne, du Mexique et d'Argentine. Grec, russe, chinois et japonais : écriture d'origine + lettres latines.
- **Maths et économie** : calcul mental, pourcentages, fractions, équations, TVA, intérêts simples et composés (exercices générés à l'infini, corrections expliquées).
- **Échecs** : pièces et règles, coordonnées, mats en un coup sur échiquier interactif.
- **Musique** : clé de sol, clé de fa, rythme, intervalles à l'oreille, gammes et altérations.
- **Méthode** : test Turbo pour valider une unité d'un coup, répétition espacée, reprise des erreurs, jusqu'à 8 profils.

## Vie privée et sécurité
Aucune donnée ne quitte l'appareil. Aucun script ni ressource externe, CSP stricte, données importées validées.
L'application Android n'a **aucun accès à Internet** ; sa seule autorisation possible est le **micro**, demandée uniquement pour les exercices de prononciation. Détails : [SECURITY.md](SECURITY.md), [store/AUDIT.md](store/AUDIT.md),
[politique de confidentialité](web/confidentialite.html).

## Structure
```
web/                 application (HTML, CSS, JavaScript sans dépendance), pages légales, page de téléchargement
tests/test_app.py    tests automatiques (toutes les leçons, XSS, CSP, requêtes externes, contrastes)
tools/               préparation Android, captures d'écran, test de démarrage sur émulateur
.github/workflows/   tests + site (GitHub Pages), application Android (APK/AAB), analyse CodeQL
fastlane/            textes et images de la fiche Google Play / F-Droid
store/               guide de publication (PUBLIER.md) et rapport d'audit (AUDIT.md)
```

## Développer
```
python -m pip install playwright && python -m playwright install chromium
python tests/test_app.py          # tests complets
python -m http.server -d web 8000 # puis http://localhost:8000
```
Application Android (Node 22, JDK 21, SDK Android 36) :
```
npm install && python tools/prepare_android.py web && npx cap add android
python tools/prepare_android.py native && npx cap sync android && cd android && ./gradlew assembleDebug
```

## Publier
Voir [store/PUBLIER.md](store/PUBLIER.md) : site, signature, APK en téléchargement direct, Google Play, F-Droid.

## Licence
[MIT](LICENSE) © 2026 Bianca C. et les contributeurs. Composants tiers : [NOTICE.md](NOTICE.md).
Bialingo est une application indépendante, non affiliée à d'autres applications d'apprentissage.
