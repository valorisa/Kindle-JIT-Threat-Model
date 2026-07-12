# Kindle-JIT-Threat-Model

Recherche défensive et documentation autour de la chaîne d'exploitation
publiquement divulguée par Synacktiv (leHACK 2026) affectant le Kindle
Paperwhite 5 : compromission via le navigateur embarqué (faille V8/Turbofan,
dérivée de CVE-2022-1364), corrigée dans le firmware **5.19.2** (janvier 2026).

Ce dépôt ne contient **aucun code d'exploitation ni PoC fonctionnel**. Il
regroupe uniquement de la documentation, une modélisation de menace, et des
outils de détection passifs.

## Structure

- [`docs/THREAT_MODEL.md`](docs/THREAT_MODEL.md) — modélisation de la menace,
  chronologie publique, sources
- [`SECURITY_POLICY.md`](SECURITY_POLICY.md) — checklist de remédiation,
  procédure de mise à jour, hardening réseau IoT
- [`src/detector/`](src/detector/) — scripts de détection défensive
  (vérification de version de firmware, contrôle d'intégrité de `appreg.db`,
  gabarit YARA)

## Avertissement

Ce projet a une vocation exclusivement pédagogique et défensive (Blue Team).
La vulnérabilité documentée est déjà publique et corrigée. Toute nouvelle
découverte de vulnérabilité sur un appareil Amazon doit être signalée via le
programme officiel Amazon Devices VRP, pas par divulgation publique directe.

## Sources

Voir `docs/THREAT_MODEL.md`, section 8.
