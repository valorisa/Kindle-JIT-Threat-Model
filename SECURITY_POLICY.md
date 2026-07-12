# Security Policy — Kindle-JIT-Threat-Model

## Portée

Ce document couvre les recommandations de remédiation et de hardening pour
les appareils Kindle potentiellement exposés à la vulnérabilité documentée
dans `docs/THREAT_MODEL.md` (chaîne d'exploitation V8/Turbofan → escalade de
privilèges, divulguée par Synacktiv, corrigée dans le firmware 5.19.2).

## 1. Checklist de conformité

- [ ] **Version de firmware** : vérifier que l'appareil est en version
      `5.19.2` ou supérieure (voir `src/detector/check_firmware_version.py`)
- [ ] **Mise à jour automatique** : s'assurer que le Wi-Fi de l'appareil a été
      activé au moins une fois depuis janvier 2026, pour déclencher l'OTA
- [ ] **Appareils dormants** : pour tout Kindle resté longtemps sans connexion
      (tiroir, cadeau non déballé, appareil de collection), forcer une
      connexion Wi-Fi contrôlée avant toute utilisation normale
- [ ] **Intégrité de `appreg.db`** : sur les appareils sensibles, établir une
      baseline post-mise à jour et la revérifier périodiquement (voir
      `src/detector/appreg_integrity_check.py`)
- [ ] **Compte Amazon** : vérifier l'activité récente du compte lié
      (achats, appareils enregistrés) si un appareil a navigué sur des sites
      non fiables avant mise à jour

## 2. Procédure de mise à jour du firmware

### Option A — OTA (recommandée, cas général)

1. Connecter le Kindle à un réseau Wi-Fi de confiance
2. Menu **Réglages → Options avancées → Mise à jour du logiciel**
3. Vérifier après mise à jour que la version affichée est ≥ `5.19.2`

### Option B — Mise à jour hors-ligne (offline)

Utile pour les appareils qu'on ne souhaite pas connecter directement à un
réseau, ou en environnement contrôlé (parc d'appareils géré) :

1. Télécharger le package de mise à jour officiel signé depuis le portail
   support Amazon Kindle, correspondant précisément au modèle de l'appareil
2. Transférer le fichier `.bin` sur l'appareil via USB, à la racine du volume
3. Lancer la mise à jour depuis le menu **Réglages → Mise à jour du logiciel**
4. Revalider la version installée

> Ne jamais utiliser de firmware provenant d'une source tierce non officielle.

## 3. Segmentation réseau (recommandation IoT générale)

Indépendamment du correctif, les bonnes pratiques suivantes réduisent
l'impact d'une éventuelle compromission future d'un appareil IoT/liseuse :

- Placer les appareils de lecture / IoT sur un **VLAN ou SSID dédié**, séparé
  du réseau principal (postes de travail, NAS, domotique sensible)
- Bloquer par défaut le trafic **est-ouest** entre le VLAN IoT et le reste du
  réseau local ; n'autoriser que les flux strictement nécessaires (ex : sortie
  Internet pour synchronisation)
- Activer la journalisation du pare-feu local sur ce segment pour détecter
  tout trafic sortant anormal (balises, exfiltration)
- Pour les foyers/organisations disposant d'un pare-feu applicatif, envisager
  un filtrage DNS pour bloquer les domaines de réputation faible ou
  nouvellement enregistrés

## 4. Réponse en cas de suspicion de compromission

1. Déconnecter l'appareil du Wi-Fi immédiatement
2. Ne pas effectuer de réinitialisation immédiate (préserver les preuves si
   une investigation est envisagée)
3. Exécuter `src/detector/appreg_integrity_check.py` si une baseline
   antérieure existe
4. Changer le mot de passe du compte Amazon associé et vérifier l'historique
   des connexions/appareils
5. En dernier recours : réinitialisation usine, puis mise à jour vers
   `5.19.2+` avant toute réutilisation

## 5. Divulgation responsable

Cette politique documente une vulnérabilité déjà publiquement divulguée et
corrigée. Pour toute nouvelle découverte concernant un appareil Amazon,
suivre le programme officiel **Amazon Devices VRP** (Vulnerability Research
Program) plutôt qu'une divulgation publique directe.

## 6. Références

Voir `docs/THREAT_MODEL.md`, section 8 (Sources).
