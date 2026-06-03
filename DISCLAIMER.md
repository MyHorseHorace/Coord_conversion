# DISCLAIMER — CoordQC

---

## FRANÇAIS

### Avis de non-responsabilité et conditions d'utilisation

**CoordQC — Convertisseur de coordonnées géodésiques**
Application web progressive (PWA) et script Python

---

#### 1. Nature du projet

CoordQC est un projet réalisé dans un **cadre scolaire**, par un étudiant au baccalauréat en génie géologique de l'école Polytechnique de Montréal. Le développement de ce projet a été **assisté par intelligence artificielle** (Claude, développé par Anthropic), tant pour la conception du code Python que pour l'application web. Ce projet n'a pas fait l'objet d'une validation professionnelle indépendante et ne constitue pas un outil certifié ou homologué à des fins professionnelles, légales ou réglementaires.

---

#### 2. Utilisation des données

**Application web (PWA) :**
Toutes les conversions de coordonnées sont effectuées **localement dans le navigateur de l'utilisateur**, côté client. Aucune donnée saisie n'est transmise à un serveur distant, enregistrée, stockée ou partagée avec quelque tiers que ce soit. L'application ne collecte aucune information personnelle. Les ressources statiques (bibliothèques, polices) peuvent être mises en cache localement par le navigateur ou le service worker à des fins de fonctionnement hors ligne.

**Script Python :**
Le script Python s'exécute entièrement en **environnement local**, sur la machine de l'utilisateur. Aucune donnée n'est transmise vers l'extérieur. Les fichiers CSV traités et les fichiers de sortie générés demeurent sur le système de fichiers local de l'utilisateur. L'auteur n'a aucun accès aux données traitées par le script.

---

#### 3. Précision et fiabilité

CoordQC repose sur des bibliothèques de projection géodésique reconnues (`pyproj` / `proj4js`, basées sur la bibliothèque PROJ). Les résultats sont fournis à titre **indicatif** uniquement. Malgré le soin apporté au développement, des erreurs de calcul, d'arrondi, de détection de zone ou d'interprétation des paramètres de projection peuvent subsister. L'utilisateur est seul responsable de la vérification et de la validation des résultats avant toute utilisation dans un contexte professionnel, technique ou légal.

---

#### 4. Limitation de responsabilité

L'auteur de CoordQC **décline toute responsabilité**, directe ou indirecte, pour tout préjudice, perte, dommage ou conséquence fortuite découlant de l'utilisation correcte ou incorrecte de l'application web ou du script Python, incluant sans s'y limiter :

- les erreurs de conversion ou de projection ;
- les décisions techniques, professionnelles ou financières prises sur la base des résultats fournis ;
- la perte ou la corruption de données ;
- tout problème de compatibilité logicielle ou matérielle ;
- toute interruption de service ou indisponibilité de l'application.

Cette limitation de responsabilité s'applique dans toute la mesure permise par la loi applicable.

---

#### 5. Renonciation aux recours juridiques

**En utilisant CoordQC, l'utilisateur reconnaît et accepte expressément qu'aucune action en justice, réclamation, poursuite civile ou autre recours juridique ne pourra être intenté à l'encontre de l'auteur en lien avec l'utilisation, la mauvaise utilisation, ou les résultats produits par l'application web ou le script Python, quelles qu'en soient les circonstances.**

---

#### 6. Obligation de lecture du README

Avant toute utilisation de l'application ou du script Python, l'utilisateur **s'engage à lire attentivement le fichier `README.md`** fourni avec le projet. Ce document contient les informations essentielles relatives au fonctionnement, à la nomenclature des systèmes de coordonnées, aux formats d'entrée attendus et aux procédures d'installation. Toute utilisation sans lecture préalable du README est effectuée sous l'entière responsabilité de l'utilisateur.

---

#### 7. Absence de garantie

CoordQC est fourni **« tel quel »**, sans garantie d'aucune sorte, expresse ou implicite, incluant notamment l'absence de garantie de qualité marchande, d'adéquation à un usage particulier ou d'absence de contrefaçon.

---

---

## ENGLISH

### Disclaimer and Terms of Use

**CoordQC — Geodetic Coordinate Converter**
Progressive Web Application (PWA) and Python Script

---

#### 1. Nature of the Project

CoordQC is a project developed in an **academic context**, by a student in geological enginnering at Polytechnique Montréal. The development of this project was **assisted by artificial intelligence** (Claude, developed by Anthropic), both for the Python script and the web application. This project has not been subject to independent professional validation and does not constitute a certified or approved tool for professional, legal, or regulatory purposes.

---

#### 2. Data Usage and Storage

**Web Application (PWA):**
All coordinate conversions are performed **locally within the user's browser**, on the client side. No data entered by the user is transmitted to a remote server, recorded, stored, or shared with any third party. The application does not collect any personal information. Static resources (libraries, fonts) may be cached locally by the browser or service worker to enable offline functionality.

**Python Script:**
The Python script runs entirely in a **local environment**, on the user's own machine. No data is transmitted externally. CSV files processed and output files generated remain on the user's local file system. The author has no access to any data processed by the script.

---

#### 3. Accuracy and Reliability

CoordQC relies on established geodetic projection libraries (`pyproj` / `proj4js`, based on the PROJ library). Results are provided for **informational purposes only**. Despite care taken during development, errors in calculation, rounding, zone detection, or projection parameter interpretation may exist. The user bears sole responsibility for verifying and validating results before any use in a professional, technical, or legal context.

---

#### 4. Limitation of Liability

The author of CoordQC **disclaims all liability**, direct or indirect, for any harm, loss, damage, or incidental consequence arising from the correct or incorrect use of the web application or the Python script, including but not limited to:

- conversion or projection errors;
- technical, professional, or financial decisions made based on the results provided;
- loss or corruption of data;
- software or hardware compatibility issues;
- service interruptions or application unavailability.

This limitation of liability applies to the fullest extent permitted by applicable law.

---

#### 5. Waiver of Legal Action

**By using CoordQC, the user expressly acknowledges and agrees that no lawsuit, claim, civil proceeding, or other legal action may be brought against the author in connection with the use, misuse, or results produced by the web application or the Python script, under any circumstances.**

---

#### 6. Obligation to Read the README

Prior to any use of the application or the Python script, the user **agrees to carefully read the `README.md` file** provided with the project. This document contains essential information regarding the operation of the tool, the nomenclature of coordinate systems, expected input formats, and installation procedures. Any use without prior reading of the README is undertaken entirely at the user's own risk.

---

#### 7. No Warranty

CoordQC is provided **"as is"**, without warranty of any kind, express or implied, including but not limited to warranties of merchantability, fitness for a particular purpose, or non-infringement.

---

*CoordQC — Academic project, École Polytechnique de Montréal. AI-assisted development (Claude, Anthropic).*
