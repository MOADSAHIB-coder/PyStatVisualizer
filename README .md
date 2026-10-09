# 📊 MATH_IMP_SAHIB — Visualisation & Analyse Statistique Descriptive

Une suite complète de scripts Python dédiés au calcul des indicateurs de statistiques descriptives et à la génération automatique de graphiques interactifs (variables qualitatives, quantitatives discrètes et continues).

Projet conçu et implémenté par **SAHIB MOAD** dans le cadre du cursus **Génie Informatique**.

---

## 📌 Présentation du Projet

**MATH_IMP_SAHIB** offre une interface en ligne de commande (CLI) permettant de :
- Saisir dynamiquement des séries statistiques brutes (modalités, effectifs, intervalles).
- Calculer automatiquement les tableaux statistiques complets :
  - Fréquences relatives ($f_i = \frac{n_i}{N}$)
  - Fréquences cumulées ($F_i$)
  - Angles des secteurs angulaires ($\theta_i = 360^\circ \times f_i$)
  - Densités de fréquence pour classes d'amplitudes inégales ($d_i = \frac{f_i}{a_i}$)
- Afficher les données sous forme de tableaux structurés et lisibles dans le terminal.
- Générer des rendus graphiques de haute qualité avec `Matplotlib`.

---

## 📂 Structure du Projet

L'arborescence du projet est organisée par type de représentation graphique :

```text
MATH_IMP_SAHIB/
│
├── diagramme_barre/
│   ├── calculs_stats.py          # Module réutilisable pour les calculs statistiques de base
│   └── Dbarre.py                 # Script du diagramme en barres (variable qualitative)
│
├── diagramme_batons/
│   └── Dbatons.py                # Script du diagramme en bâtons (variable quantitative discrète)
│
├── diagramme_commulatif_continu/
│   └── DCcontinu.py              # Script de la fonction de répartition empirique continue (ogive)
│
├── diagramme_comulatif_discret/
│   └── DCdiscret.py              # Script du diagramme cumulatif discret (fonction en escalier)
│
├── diagrmme_circulaire/
│   └── diagramme_circulaire.py   # Script du diagramme circulaire (secteurs angulaires)
│
├── HISTOGRAME/
│   └── histogramme.py            # Script de l'histogramme pour classes d'amplitudes égales
│
├── histogramme_inegal/
│   └── Hinegal.py                # Script de l'histogramme pour classes d'amplitudes inégales
│
├── polygone_frequence/
│   └── Pfrequence.py             # Script du polygone des fréquences (lissage d'histogramme)
│
└── README.md                     # Documentation du projet
```

---

## 📈 Modules & Représentations Graphiques

| Répertoire | Script principal | Description Statistique |
| :--- | :--- | :--- |
| `diagramme_barre/` | `Dbarre.py` | Représentation en barres verticales des effectifs pour variables qualitatives. |
| `diagrmme_circulaire/` | `diagramme_circulaire.py` | Camembert où chaque secteur correspond à un angle $\theta_i = 360^\circ \times f_i$. |
| `diagramme_batons/` | `Dbatons.py` | Bâtons verticaux sur axes cartésiens pour variables quantitatives discrètes. |
| `diagramme_comulatif_discret/` | `DCdiscret.py` | Courbe en escalier de la fonction de répartition empirique $F_i$. |
| `HISTOGRAME/` | `histogramme.py` | Rectangles contigus de même largeur pour variables continues. |
| `histogramme_inegal/` | `Hinegal.py` | Rectangles dont la hauteur est égale à la densité $d_i = f_i / a_i$. |
| `polygone_frequence/` | `Pfrequence.py` | Ligne brisée reliant les centres des classes $(c_i, f_i)$, refermée à zéro aux extrémités. |
| `diagramme_commulatif_continu/` | `DCcontinu.py` | Courbe continue reliant les points $(x_i, F_i)$ aux bornes supérieures des classes. |

---

## 🛠️ Installation & Prérequis

### 1. Prérequis
Assurez-vous de disposer de **Python 3.8+** sur votre système.

### 2. Dépendances requises
Le projet utilise les bibliothèques Python suivantes :
- `matplotlib` (Génération des graphiques)
- `numpy` / `math` (Calculs mathématiques)
- `tabulate` (Affichage propre dans le terminal)

Pour installer toutes les dépendances :
```bash
pip install matplotlib numpy tabulate
```

---

## 🚀 Utilisation

Chaque module s'exécute de manière indépendante depuis le dossier racine du projet.

### Exemples d'exécution :

1. **Diagramme en barres :**
   ```bash
   python diagramme_barre/Dbarre.py
   ```

2. **Diagramme circulaire :**
   ```bash
   python diagrmme_circulaire/diagramme_circulaire.py
   ```

3. **Diagramme en bâtons :**
   ```bash
   python diagramme_batons/Dbatons.py
   ```

4. **Histogramme (amplitudes inégales) :**
   ```bash
   python histogramme_inegal/Hinegal.py
   ```

5. **Polygone des fréquences :**
   ```bash
   python polygone_frequence/Pfrequence.py
   ```

---

## 👨‍💻 Auteur

- **Nom & Prénom :** SAHIB MOAD
- **Filière :** Génie Informatique
- **Domaine :** Mathématiques pour l'ingénieur & Statistique Descriptive