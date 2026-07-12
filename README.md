# src/detector — Outils de détection défensive

Ce dossier contient uniquement des outils **passifs et défensifs** liés au
threat model décrit dans `docs/THREAT_MODEL.md`. Aucun script ici ne modifie,
n'exploite, ni ne contourne un mécanisme de sécurité : ils lisent, comparent
et signalent.

| Script | Rôle |
|---|---|
| `check_firmware_version.py` | Compare une version de firmware au seuil de sécurité connu (5.19.2) |
| `appreg_integrity_check.py` | Contrôle d'intégrité de `appreg.db` par comparaison à une baseline (hash + inventaire de tables) |
| `kindle_jit_exploit_indicators.yar` | Gabarit YARA à compléter avec des IOC officiels si publiés par Synacktiv |

## Utilisation type

```bash
# 1. Vérifier la version de firmware
python3 check_firmware_version.py --version 5.18.6

# 2. Sur un appareil sain (post-5.19.2), enregistrer une baseline
python3 appreg_integrity_check.py appreg.db --save-baseline baseline.json

# 3. Sur un appareil à auditer, comparer à la baseline
python3 appreg_integrity_check.py appreg.db --baseline-file baseline.json
```

## Ce que ces outils NE font PAS

- Ils ne reproduisent aucune étape de la chaîne d'exploitation (pas de
  corruption mémoire, pas de bypass ASLR, pas d'injection).
- Ils ne fournissent pas de payload.
- La règle YARA est un gabarit vide de toute signature réelle d'exploit tant
  qu'aucun IOC officiel n'est publié.

Pour la remédiation, voir `SECURITY_POLICY.md` à la racine du dépôt.
