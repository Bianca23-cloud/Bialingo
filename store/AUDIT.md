# Audit sécurité et conformité de Bialingo 1.1.0

Date : 3 novembre 2026 (2e vérification). Périmètre : application web installable (Windows 11, iPhone, Android), application Android (Capacitor),
chaîne de fabrication GitHub, textes légaux.

## 1. Sécurité : problèmes trouvés dans la version 1.0 et corrections

| # | Gravité | Problème | Correction en 1.1 | Vérifié par |
|---|---|---|---|---|
| S1 | Élevée | Injection de code (XSS) : un « code de sauvegarde » piégé pouvait insérer du HTML et du JavaScript (couleur et identifiant de profil non échappés). | Validation stricte de toutes les données lues ou importées (types, longueurs, listes autorisées), échappement des attributs, limite de 400 Ko. | Test automatique avec un code piégé |
| S2 | Moyenne | Polices chargées depuis Google Fonts : l'adresse IP de chaque visiteur était transmise à Google (jugé contraire au RGPD : tribunal régional de Munich, 20 janvier 2022, 3 O 17493/20). | Plus aucune ressource externe : polices du système, clés de musique et pièces d'échecs en tracés vectoriels inclus. | Test : aucune requête hors du site |
| S3 | Moyenne | Pas de politique de sécurité du contenu (CSP) ; scripts et styles en ligne. | Code séparé en fichiers ; CSP stricte : `default-src 'none'`, `script-src 'self'`, `style-src 'self'`, `base-uri 'none'`, `form-action 'none'`. | Test : zéro violation CSP |
| S4 | Moyenne | Le service worker mettait en cache des réponses tierces et ne livrait jamais les mises à jour. | Uniquement la même origine, cache versionné à chaque publication, réseau d'abord pour les pages. | Test d'enregistrement hors ligne |
| S5 | Faible | Les voix de synthèse pouvaient être des voix en ligne (texte envoyé à l'éditeur du navigateur). | Choix prioritaire des voix locales ; voix native du téléphone sur Android. | Revue de code |
| S6 | Faible | Encodage de sauvegarde avec des fonctions obsolètes (`escape`/`unescape`). | Encodage UTF-8 standard (TextEncoder/TextDecoder), format versionné `BIA1.`. | Test d'import |
| S7 | Info | Le navigateur pouvait effacer la progression en cas de manque d'espace. | Demande de stockage persistant, sauvegarde par fichier. | Revue de code |
| F1 | Moyenne | iPhone : Safari bloque le son et la voix lancés après un délai (première note, première phrase muettes). | Déverrouillage du son et de la voix au premier toucher. | Revue de code ; test WebKit sur GitHub |
| F2 | Moyenne | Android : la voix native n'était pas reliée (sans outil d'assemblage, l'extension Capacitor n'est pas exposée). | Le moteur Capacitor et l'extension vocale sont inclus ; `native.js` les relie à l'application. | Simulation de l'application Android |
| F3 | Faible | Android : le bouton « retour » fermait l'application en pleine leçon. | Il propose maintenant de quitter la leçon. | Test automatique |
| F4 | Faible | Vérification des autorisations de l'APK : fausse alerte possible (permission interne AndroidX). | Seules les autorisations système demandées sont contrôlées. | Revue de code |
| S6 | Moyenne | v3 : les exercices de prononciation utilisent la reconnaissance vocale du navigateur ou du téléphone, qui peut envoyer le son à son éditeur. | Explication et accord avant la première utilisation ; micro activé seulement à l'appui sur le bouton ; aucun son ni texte conservé ; repli 100 % local (enregistrement et réécoute) ; désactivable dans Réglages ; politique de confidentialité à jour. | Revue de code ; test automatique |
| S7 | Faible | v3 : option « voix les plus naturelles, même en ligne ». | Désactivée par défaut (voix installées sur l'appareil uniquement) ; avertissement dans Réglages et dans la politique de confidentialité. | Revue de code |

**Application Android** (contrôlé automatiquement à chaque compilation) :
- aucun accès Internet (INTERNET retirée) ; seule autorisation : le micro (RECORD_AUDIO), demandée au moment d'un exercice de prononciation ;
- sauvegarde cloud désactivée ;
- débogage de la WebView désactivé, trafic en clair interdit ;
- signature vérifiée (`apksigner`), empreintes SHA-256 et attestation de provenance publiées ;
- démarrage réel testé sur un émulateur Android 14.

**Chaîne de fabrication** :
- aucune dépendance chargée par l'application ;
- workflows à droits minimaux, sans identifiants persistants ;
- analyse CodeQL (JavaScript, Python, workflows) ;
- mises à jour Dependabot.

Amélioration possible : épingler les actions GitHub par empreinte (SHA) plutôt que par version ; Dependabot peut ensuite les tenir à jour.

## 2. Conformité légale (France / Union européenne)

| Sujet | Situation | Statut |
|---|---|---|
| RGPD | Aucune donnée personnelle collectée ni transmise ; données uniquement sur l'appareil, effaçables et exportables par l'utilisateur. Politique de confidentialité publiée. | Conforme |
| Cookies et traceurs (art. 82 loi Informatique et Libertés) | Aucun cookie ni traceur ; stockage local strictement nécessaire au service demandé, donc exempté de consentement. | Conforme, pas de bandeau requis |
| Mentions légales (LCEN, art. 6) | Page publiée ; éditrice non professionnelle (identité communiquée à l'hébergeur), hébergeur identifié. | Conforme |
| Droit d'auteur | Contenus et code originaux ; aucun élément graphique, texte ou nom d'une autre application ; licences des composants tiers documentées (NOTICE.md). | Conforme |
| Marques | Mention de non-affiliation présente. **À faire** avant Google Play : vérifier que « Bialingo » n'est pas déjà déposé (data.inpi.fr, tmsearch EUIPO, WIPO Global Brand Database). | Vérification à faire |
| Mineurs | Ni compte, ni âge, ni publicité, ni achat intégré. | Conforme |
| Accessibilité | WCAG 2.1 AA visé : 54 paires de couleurs ≥ 4,5:1 vérifiées en clair et en sombre, clavier, lecteur d'écran, réduction des animations. Le RGAA n'est pas obligatoire pour une particulière. | Conforme au niveau visé |
| Google Play | Cible SDK 36 (obligatoire depuis le 31 août 2026), politique de confidentialité, sécurité des données « aucune donnée », test fermé 12 testeurs × 14 jours (voir PUBLIER.md). | Prêt, démarches à faire par l'éditrice |
| Licence libre | MIT pour le code et les contenus ; glyphes sous leurs licences d'origine, compatibles. | Conforme |

## 3. Limites de cet audit
- Les tests tournent dans Chromium (moteur de Chrome, Edge et Android) ; sur GitHub, ils tournent aussi dans WebKit (moteur de Safari) avec le profil iPhone 13. Aucun vrai iPhone n'a été utilisé.
- La compilation Android sera vérifiée à la première exécution sur GitHub, car elle a besoin du SDK Android.
- Un scan dynamique externe (DAST, par exemple StackHawk) demande un compte et une clé d'API.
- Ce document ne remplace pas l'avis d'un avocat.

## 4. À surveiller en 2027
Google va exiger une **vérification d'identité des développeurs** même pour les APK installés hors Google Play :
d'abord au Brésil, en Indonésie, à Singapour et en Thaïlande (30 septembre 2026), puis dans le monde entier en 2027.
Avec un compte Google Play vérifié, l'APK en téléchargement direct restera installable.
