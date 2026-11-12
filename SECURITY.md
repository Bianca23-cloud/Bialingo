# Sécurité de Bialingo

## Signaler une faille
Merci de **ne pas** ouvrir de ticket public. Utilisez le signalement privé de GitHub :
onglet **Security** du dépôt › **Report a vulnerability**. Réponse visée sous 7 jours.

## Versions suivies
Seule la dernière version publiée (site et APK) reçoit des correctifs.

## Principes de conception
- **Aucune donnée collectée** : pas de serveur, pas de compte, pas de traceur. Les données restent sur l'appareil.
- **Aucun script ni ressource tiers** : polices, icônes et tracés sont inclus ; aucune requête vers un autre site.
- **Politique CSP stricte** (`script-src 'self'`, `style-src 'self'`, `default-src 'none'`). L'application Android autorise
  en plus le script en ligne du pont Capacitor ; elle ne charge jamais de contenu distant.
- **Validation de toutes les données** lues depuis le stockage ou importées (code ou fichier de sauvegarde) :
  types, longueurs, listes autorisées, taille maximale. Les textes affichés sont échappés.
- **Android** : aucun accès Internet (la permission INTERNET est retirée) ; seule autorisation : le micro, demandée au moment d'un exercice de prononciation ; sauvegarde cloud désactivée, débogage désactivé,
  trafic en clair interdit. Le contrôle est automatique à chaque compilation.
- **Chaîne de fabrication** : compilation publique par GitHub Actions avec droits minimaux, empreintes SHA-256,
  attestation de provenance, analyse CodeQL, mises à jour Dependabot.

## Vérifier un APK
```
gh attestation verify Bialingo.apk -R <propriétaire>/bialingo
```
ou comparez `Get-FileHash Bialingo.apk` (Windows) / `sha256sum Bialingo.apk` avec `SHA256SUMS.txt`.
