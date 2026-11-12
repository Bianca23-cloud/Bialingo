# Composants tiers

| Composant | Utilisation | Licence |
|---|---|---|
| GNU FreeFont (FreeSerif) | Contours non modifiés des clés de sol (U+1D11E) et de fa (U+1D122), dans `web/glyphs.js` | GNU GPL v3 avec exception pour les polices : intégrer des portions non modifiées de la police dans un document ne soumet pas ce document à la GPL. https://www.gnu.org/software/freefont/ |
| DejaVu Sans | Contours non modifiés des pièces d'échecs (U+265A à U+265F), dans `web/glyphs.js` | Licence Bitstream Vera (permissive) ; modifications DejaVu dans le domaine public. https://dejavu-fonts.github.io/License.html |
| Capacitor (`@capacitor/core`, `@capacitor/android`, `@capacitor/cli`) | Emballage de l'application Android, installé au moment de la compilation | MIT |
| Capacitor Community Text-to-Speech | Voix du téléphone dans l'application Android, installé au moment de la compilation | MIT |

Aucun de ces composants n'est chargé depuis Internet par l'application : tout est inclus dans le paquet.
