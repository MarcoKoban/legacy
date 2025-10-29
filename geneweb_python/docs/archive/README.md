# Archive - Documentation Obsolète

Ce dossier contient la documentation qui n'est plus d'actualité mais conservée pour référence historique.

## Fichiers archivés

### Bcrypt Implementation (2024-2025)
- **BCRYPT_FIX.md** - Documentation du fix bcrypt initial
- **BCRYPT_FIX_SUMMARY.md** - Résumé du fix bcrypt
- **BCRYPT_MONKEY_PATCH.md** - Documentation du monkey patch bcrypt

**Raison de l'archivage** : Ces fonctionnalités ont été intégrées nativement dans le système d'authentification JWT (`src/geneweb/api/routers/auth.py`). Le bcrypt est maintenant utilisé directement via la bibliothèque `passlib` avec un cost factor de 12.

**Date d'archivage** : 2025-01-10

**Remplacement** : Voir `AUTHENTICATION_GUIDE.md` pour la documentation actuelle du système d'authentification.

## Quand archiver un document ?

Un document doit être archivé quand :
1. ✅ La fonctionnalité est complètement intégrée dans le système principal
2. ✅ La documentation est remplacée par une documentation plus complète
3. ✅ Le document contient des informations temporaires ou de transition
4. ✅ Le document décrit une approche abandonnée ou obsolète

## Restauration

Si vous avez besoin de restaurer un document archivé :
```bash
# Déplacer le fichier vers docs/
mv docs/archive/FICHIER.md docs/FICHIER.md

# Mettre à jour DOCUMENTATION_STATUS.md
```

## Suppression définitive

Les fichiers archivés peuvent être supprimés définitivement après :
- 6 mois minimum d'archivage
- Vérification qu'aucune référence n'existe dans le code
- Validation par l'équipe de développement
