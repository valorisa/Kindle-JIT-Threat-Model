# Threat Model — Amazon Kindle (2026) — Chaîne d'exploitation navigateur → système

> **Statut :** Documentaire uniquement. Ce document décrit une menace publiquement
> divulguée, à des fins de sensibilisation et de remédiation. Il ne contient
> aucun code d'exploitation, aucun payload, ni aucune étape technique
> suffisante pour reproduire l'attaque. Pour les détails techniques complets,
> se référer aux publications originales de Synacktiv (voir Sources).

## 1. Résumé exécutif

En juin 2026, le chercheur Tanguy Dubroca (Synacktiv) a présenté à leHACK 2026
une chaîne de compromission permettant de prendre le contrôle total d'un
Kindle Paperwhite 5 (firmwares 5.18.4 / 5.18.6) à partir d'un simple site web
malveillant ouvert dans le navigateur embarqué. Le signalement a été transmis
à Amazon Devices VRP le 1er décembre 2025, classé critique, primé 20 000 $, et
corrigé dans le firmware **5.19.2** (janvier 2026), déployé automatiquement
dès que l'appareil se connecte au Wi-Fi.

Point clé : la vulnérabilité mémoire exploitée (dérivée de CVE-2022-1364,
faille de confusion de type dans le moteur V8/Turbofan de Chrome, corrigée par
Google en 2022) *aurait dû* être neutralisée sur le Kindle, le composant
vulnérable étant censé être désactivé. Une erreur de configuration dans le
firmware (documentée publiquement comme un oubli d'options de désactivation)
a laissé le composant actif.

## 2. Architecture cible

Le Kindle n'est pas une simple liseuse mais un objet connecté complexe :

- **Système** : Linux embarqué (architecture ARM)
- **Runtime applicatif** : composants Java + code natif, interface React Native
- **Navigateurs embarqués** : Chrome (base ≈2019) et WebKit (base ≈2011-2012),
  tous deux nettement obsolètes par rapport aux versions courantes
- **Services internes** : gestionnaire d'applications (`appmgr`), stockage de
  configuration applicative (`appreg.db`), compte Amazon lié (achats,
  bibliothèque, Wi-Fi domestique)

Modèle simplifié de la chaîne de confiance :

```
Site web distant (non fiable)
        │
        ▼
Navigateur embarqué (Chrome/WebKit obsolètes) ── frontière de sandbox
        │
        ▼
Composant applicatif système (appmgr / appreg.db) ── frontière de privilège
        │
        ▼
Système Linux embarqué (accès complet à l'appareil et au compte lié)
```

## 3. Vecteurs d'entrée

| Vecteur | Type | Interaction utilisateur requise |
|---|---|---|
| Navigation web via le navigateur embarqué | Distant | Ouvrir un lien / site piégé |
| Manipulation de configuration locale (`appreg.db`) | Local | Accès physique préalable à l'appareil (scénario secondaire) |

Le vecteur principal démontré publiquement est **distant** : l'utilisateur n'a
qu'à visiter une page web depuis son Kindle.

## 4. Impact

En cas de compromission complète, un attaquant pourrait potentiellement :

- Exécuter du code arbitraire sur l'appareil
- Élever ses privilèges au-delà du bac à sable du navigateur
- Accéder aux données de session / cookies du navigateur embarqué
- Détourner ou espionner le compte Amazon associé à l'appareil
- Utiliser l'appareil comme point de pivot sur le réseau Wi-Fi domestique

Il est important de noter, comme le souligne Synacktiv lui-même, qu'il s'agit
d'une démonstration de recherche en laboratoire — **aucune exploitation en
conditions réelles n'a été observée**.

## 5. Prérequis pour qu'un appareil soit vulnérable

- Firmware Kindle **antérieur à la version 5.19.2**
- Modèle testé publiquement : Kindle Paperwhite 5 (2021), firmwares 5.18.4 et
  5.18.6 — d'autres modèles/versions n'ont pas été confirmés publiquement
- Appareil ayant navigué (ou navigable) vers un site web arbitraire depuis le
  navigateur embarqué

## 6. Chronologie publique

| Date | Événement |
|---|---|
| 2022 | Google corrige CVE-2022-1364 dans Chrome (upstream) |
| 1er décembre 2025 | Signalement transmis à Amazon Devices VRP |
| — | Amazon classe la faille en critique, prime de 20 000 $ |
| Janvier 2026 | Correctif déployé dans le firmware Kindle 5.19.2 |
| 27 juin 2026 | Présentation publique « Bootstrapping Kindle research for the lazy attacker » à leHACK 2026 |
| 8 juillet 2026 | Communiqué public de Synacktiv |

## 7. Recommandations générales

Voir `SECURITY_POLICY.md` pour le détail des mesures de remédiation
(vérification de version, procédure de mise à jour, segmentation réseau).

## 8. Sources

- Communiqué Synacktiv, 8 juillet 2026 — « Bootstrapping Kindle research for the lazy attacker » (leHACK 2026, 27 juin 2026)
- Korben.info — « Un Kindle rooté à cause d'une faute de frappe d'Amazon »
- ActuaLitté — « Votre Kindle peut intéresser les pirates : un chercheur français l'a prouvé »
- NVD — CVE-2022-1364 (Google Chrome, confusion de type V8/Turbofan)

---

*Ce document a une vocation exclusivement pédagogique et défensive. Il ne
décrit ni ne fournit d'étapes techniques d'exploitation.*
