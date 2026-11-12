# Publier Bialingo : guide pas à pas

Ce guide suppose que le code est sur GitHub, dans un dépôt public nommé `bialingo`.

## 1. Mettre en ligne le site (Windows 11, iPhone, Android) : gratuit

1. Sur GitHub, ouvrez le dépôt › **Settings** › **Pages**.
2. Dans **Build and deployment › Source**, choisissez **GitHub Actions**.
3. Onglet **Actions** › **Tests et site** › **Run workflow**.
4. Après 3 à 5 minutes, le site est en ligne à l'adresse `https://<votre-pseudo>.github.io/bialingo/`.
5. La page de téléchargement est `https://<votre-pseudo>.github.io/bialingo/telecharger.html`.

## 2. Configurer la signature Android (une seule fois)

La signature prouve que chaque mise à jour vient bien de vous. Le fichier `bialingo-release.jks` et son mot de passe
vous sont fournis séparément.

1. **Gardez deux copies du fichier `.jks` et de son mot de passe**, par exemple sur une clé USB et dans un gestionnaire de mots de passe.
   Sans eux, vous ne pourrez plus jamais mettre à jour l'application.
2. Dépôt › **Settings** › **Secrets and variables** › **Actions** › **New repository secret** :
   - `ANDROID_KEYSTORE_BASE64` : le contenu du fichier `bialingo-release.jks.base64.txt` ;
   - `ANDROID_KEYSTORE_PASSWORD` : le mot de passe.

## 3. Publier une version Android téléchargeable directement

1. Dépôt › **Releases** › **Draft a new release**.
2. **Choose a tag** › tapez `v1.1.0` › **Create new tag**, puis **Publish release**.
3. L'onglet **Actions** compile, vérifie (signature, au plus l'autorisation du micro, jamais Internet, démarrage réel sur un émulateur) et ajoute à la publication :
   - `Bialingo.apk` : le téléchargement direct ;
   - `Bialingo.aab` : le paquet pour Google Play ;
   - `SHA256SUMS.txt` : les empreintes pour vérifier les fichiers.
4. Le lien direct, toujours valable pour la dernière version :
   `https://github.com/<votre-pseudo>/bialingo/releases/latest/download/Bialingo.apk`

Pour les versions suivantes, incrémentez l'étiquette : `v1.1.1`, `v1.2.0`…

## 4. Google Play (compte personnel)

### 4.1 Créer le compte
1. https://play.google.com/console › créez un compte **Personnel**.
2. Frais uniques : 25 $. Vérification d'identité par pièce d'identité et vérification du téléphone.

3. **Adresse e-mail de contact** : elle est affichée publiquement sur la fiche Google Play. Créez une adresse dédiée
   (par exemple `bialingo.contact@gmail.com`) plutôt que votre adresse personnelle.
4. **Statut de « professionnel » (règlement européen DSA)** : la Play Console demande si vous êtes un professionnel (trader).
   Une application gratuite, sans revenu, publiée par une particulière : répondez **non professionnel**.

### 4.2 Créer l'application
1. **Créer une application** › nom « Bialingo » › langue par défaut **Français (France)** › **Application** › **Gratuite**.
2. Le nom du paquet est `fr.bialingo.app`. Il est **définitif** : ne le modifiez plus après le premier envoi.

### 4.3 Fiche du Play Store
Copiez les textes du dossier `fastlane/metadata/android/fr-FR/` :
- titre : `title.txt` ;
- description courte : `short_description.txt` ;
- description complète : `full_description.txt` ;
- icône 512 × 512 : `images/icon.png` ;
- captures de téléphone (6 images 1080 × 1920) : `images/phoneScreenshots/`.

- image de présentation 1024 × 500 : `images/featureGraphic.png`.

### 4.4 Contenu de l'application (questionnaires)
| Rubrique | Réponse |
|---|---|
| Règles de confidentialité | `https://<votre-pseudo>.github.io/bialingo/confidentialite.html` |
| Accès à l'application | Toutes les fonctionnalités sont accessibles sans restriction |
| Annonces | Non, l'application ne contient pas d'annonces |
| Sécurité des données | Aucune donnée collectée ; aucune donnée partagée (l'application n'a pas Internet ; la reconnaissance vocale est faite par le service vocal d'Android, hors de Bialingo) |
| Classification du contenu | Catégorie « Éducation » ; répondre **Non** à toutes les questions (violence, contenu sexuel, langage, jeux d'argent, achats…) |
| Public cible | **13 ans et plus** (le plus simple). Si vous ajoutez les enfants de moins de 13 ans, Google applique le programme Familles : Bialingo le respecte déjà (ni publicité, ni données), mais l'examen est plus long |
| Application d'actualités, santé, finance, VPN… | Non |
| Gouvernement | Non |

### 4.5 Test fermé obligatoire
Pour un compte personnel créé après novembre 2023, Google impose un **test fermé avec au moins 12 testeurs
pendant au moins 14 jours d'affilée** avant l'accès à la production.

1. **Tester › Test fermé** › créer un canal › importez `Bialingo.aab`.
2. Ajoutez au moins 12 adresses Gmail (famille, amis, collègues). Chaque testeur accepte l'invitation, installe l'application
   et la garde 14 jours.
3. Activez **Signature d'application par Google Play** (proposée au premier envoi) : Google conserve la clé de distribution,
   votre fichier `.jks` sert de clé d'importation.
4. Au bout de 14 jours : **Tableau de bord › Demander l'accès à la production**, puis répondez aux questions sur le test.

### 4.6 Production
**Production › Créer une version** › importez le même `.aab` (ou un plus récent) › **Envoyer pour examen**.
L'examen prend généralement de quelques jours à une semaine.

## 5. Autres boutiques gratuites et open source
- **F-Droid** (catalogue d'applications libres) : les textes `fastlane/` sont déjà au bon format. Demande d'inclusion sur
  https://gitlab.com/fdroid/rfp/-/issues.
- **Microsoft Store** (Windows 11) : pwabuilder.com › adresse du site › *Package for stores* › Windows.
  Un compte développeur Microsoft est nécessaire.
- **App Store** (iPhone) : un compte Apple Developer est payant chaque année et un Mac est requis.
  L'installation gratuite par Safari reste disponible.
