"""

 Diagramme en bâtons - Variable statistique quantitative discrète

 Nom complet : SAHIB MOAD
 Filière     : Génie Informatique

 Description :
   Ce script permet de saisir, dans le terminal, les valeurs discrètes (x_i)
   d'une variable quantitative (ex. : nombre d'enfants) et leurs effectifs (n_i).
   Il calcule ensuite :
       - la fréquence relative  f_i = n_i / N
       - les totaux             N = Σ n_i  et  Σ f_i = 1,00
   puis affiche un tableau récapitulatif et trace le diagramme en bâtons.

"""

import math
from dataclasses import dataclass
from typing import List

import matplotlib.pyplot as plt
import numpy as np

# `tabulate` est facultatif : en son absence, un formatage textuel aligné
# est utilisé à la place.
try:
    from tabulate import tabulate
    TABULATE_DISPONIBLE = True
except ImportError:
    TABULATE_DISPONIBLE = False


# =============================================================================
# 1. Modèle de données
# =============================================================================
@dataclass
class Valeur:
    """Représente une valeur discrète x_i avec son effectif n_i et sa fréquence f_i."""
    x: int                  # x_i : valeur de la variable
    effectif: int           # n_i : effectif
    frequence: float = 0.0  # f_i : fréquence relative


# =============================================================================
# 2. Saisie et validation des entrées (terminal)
# =============================================================================
class SaisieUtilisateur:
    """Gère la saisie interactive et la validation des données dans le terminal."""

    @staticmethod
    def lire_entier(message: str, minimum: int) -> int:
        """Demande un entier >= minimum ; recommence tant que la saisie est invalide."""
        while True:
            texte = input(message).strip()
            try:
                nombre = int(texte)
            except ValueError:
                print("  ⚠ Erreur : veuillez entrer un nombre entier valide.")
                continue
            if nombre < minimum:
                print(f"  ⚠ Erreur : la valeur doit être supérieure ou égale à {minimum}.")
                continue
            return nombre

    @classmethod
    def saisir_donnees(cls) -> List[Valeur]:
        """Saisie complète : nombre de valeurs, puis (x_i, n_i) pour chacune."""
        print("\n--- Saisie des données ---")
        k = cls.lire_entier("Nombre de valeurs distinctes (au moins 2) : ", minimum=2)

        valeurs: List[Valeur] = []
        deja_saisies: List[int] = []
        for i in range(1, k + 1):
            # x_i : entier positif ou nul (0 enfant est une valeur légitime), sans doublon
            while True:
                x = cls.lire_entier(f"  Valeur x{i} : ", minimum=0)
                if x in deja_saisies:
                    print(f"  ⚠ Erreur : la valeur {x} a déjà été saisie.")
                else:
                    break
            # n_i : entier strictement positif
            n = cls.lire_entier(f"  Effectif n{i} de x = {x} : ", minimum=1)
            deja_saisies.append(x)
            valeurs.append(Valeur(x=x, effectif=n))

        # Tri par ordre croissant des x_i (nécessaire pour un tableau lisible)
        valeurs.sort(key=lambda v: v.x)
        return valeurs

    @staticmethod
    def donnees_exemple() -> List[Valeur]:
        """Jeu de données d'exemple : nombre d'enfants par famille."""
        exemple = [(0, 4), (1, 9), (2, 14), (3, 8), (4, 4), (5, 1)]
        return [Valeur(x=x, effectif=n) for x, n in exemple]


# =============================================================================
# 3. Calculs statistiques
# =============================================================================
class StatistiquesDiscretes:
    """Calcule les fréquences relatives et les totaux d'une série discrète."""

    def __init__(self, valeurs: List[Valeur]):
        if not valeurs:
            raise ValueError("La liste des valeurs est vide.")
        self.valeurs = valeurs
        self.total_effectif = 0       # N = Σ n_i
        self.total_frequence = 0.0    # Σ f_i
        self._calculer()

    def _calculer(self) -> None:
        """Calcule N, puis f_i pour chaque valeur, puis Σ f_i."""
        self.total_effectif = sum(v.effectif for v in self.valeurs)
        if self.total_effectif <= 0:
            raise ValueError("L'effectif total N doit être strictement positif.")

        for v in self.valeurs:
            v.frequence = v.effectif / self.total_effectif   # f_i = n_i / N

        # math.fsum limite les erreurs d'arrondi lors de la somme de flottants
        self.total_frequence = math.fsum(v.frequence for v in self.valeurs)


# =============================================================================
# 4. Affichage du tableau récapitulatif
# =============================================================================
class AfficheurTableau:
    """Affiche le tableau (x_i, n_i, f_i) avec la ligne des totaux."""

    ENTETES = ["x_i", "n_i", "f_i"]

    @classmethod
    def afficher(cls, stats: StatistiquesDiscretes) -> None:
        lignes = [
            [str(v.x), str(v.effectif), f"{v.frequence:.4f}"]
            for v in stats.valeurs
        ]
        # Ligne des totaux : N = Σ n_i et Σ f_i = 1,00
        lignes.append(["Total", str(stats.total_effectif), f"{stats.total_frequence:.2f}"])

        print("\n--- Tableau récapitulatif ---")
        if TABULATE_DISPONIBLE:
            # disable_numparse=True conserve le format texte (ex. 0.1000)
            print(tabulate(lignes, headers=cls.ENTETES, tablefmt="fancy_grid",
                           colalign=("left", "right", "right"),
                           disable_numparse=True))
        else:
            cls._afficher_manuel(lignes)

        print(f"\nN = Σ n_i = {stats.total_effectif}   |   "
              f"Σ f_i = {stats.total_frequence:.2f}")

    @classmethod
    def _afficher_manuel(cls, lignes: list) -> None:
        """Formatage textuel aligné (utilisé si `tabulate` n'est pas installé)."""
        # Largeur de chaque colonne = longueur maximale (en-tête ou données)
        largeurs = [
            max(len(ligne[j]) for ligne in [cls.ENTETES] + lignes)
            for j in range(len(cls.ENTETES))
        ]
        separateur = "+-" + "-+-".join("-" * w for w in largeurs) + "-+"

        def formater(ligne):
            return "| " + " | ".join(
                val.ljust(largeurs[j]) if j == 0 else val.rjust(largeurs[j])
                for j, val in enumerate(ligne)
            ) + " |"

        print(separateur)
        print(formater(cls.ENTETES))
        print(separateur)
        for ligne in lignes[:-1]:
            print(formater(ligne))
        print(separateur)
        print(formater(lignes[-1]))   # ligne des totaux
        print(separateur)


# =============================================================================
# 5. Génération du diagramme en bâtons
# =============================================================================
class DiagrammeBatons:
    """Trace le diagramme en bâtons (stem plot) avec matplotlib."""

    COULEUR_BATON = "#4C78A8"      # bleu sobre
    COULEUR_MARQUEUR = "#E45756"   # rouge corail pour contraster
    TITRE = "Diagramme en bâtons"

    def __init__(self, stats: StatistiquesDiscretes):
        self.stats = stats

    def tracer(self) -> None:
        """Construit et affiche la figure."""
        x = np.array([v.x for v in self.stats.valeurs])
        n = np.array([v.effectif for v in self.stats.valeurs])

        plt.style.use("seaborn-v0_8-whitegrid")
        fig, ax = plt.subplots(figsize=(9, 6))

        # Bâtons verticaux terminés par un marqueur circulaire
        marqueurs, batons, base = ax.stem(x, n, basefmt=" ")
        plt.setp(batons, color=self.COULEUR_BATON, linewidth=3)
        plt.setp(marqueurs, color=self.COULEUR_MARQUEUR, markersize=12,
                 markeredgecolor="white", markeredgewidth=1.5)

        # Affichage de l'effectif au-dessus de chaque marqueur
        for xi, ni in zip(x, n):
            ax.annotate(str(ni), (xi, ni), textcoords="offset points",
                        xytext=(0, 12), ha="center", fontsize=11,
                        fontweight="bold", color="#333333")

        # Titres
        ax.set_title(self.TITRE, fontsize=16, fontweight="bold", pad=15, color="#222222")
        ax.set_xlabel(r"Nombre d'enfants $x_i$", fontsize=13)
        ax.set_ylabel(r"Effectif $n_i$", fontsize=13)

        # Axes : x_i entiers uniquement, marge pour l'annotation, début à 0
        ax.set_xticks(x)
        ax.set_xlim(x.min() - 0.7, x.max() + 0.7)
        ax.set_ylim(0, n.max() * 1.15)
        ax.yaxis.get_major_locator().set_params(integer=True)

        # Grille légère, horizontale uniquement
        ax.grid(axis="y", linestyle="--", alpha=0.5)
        ax.grid(axis="x", visible=False)
        for cote in ("top", "right"):
            ax.spines[cote].set_visible(False)

        plt.tight_layout()
        plt.show()


# =============================================================================
# 6. Programme principal
# =============================================================================
def main() -> None:
    """Point d'entrée : saisie -> calculs -> tableau -> graphique."""
    print("=" * 60)
    print("  DIAGRAMME EN BÂTONS - Variable quantitative discrète")
    print("  Auteur : SAHIB MOAD - Génie Informatique")
    print("=" * 60)

    # Choix entre saisie manuelle et jeu de données d'exemple
    reponse = input("\nUtiliser l'exemple (nombre d'enfants) ? [o/N] : ").strip().lower()
    if reponse in ("o", "oui", "y", "yes"):
        valeurs = SaisieUtilisateur.donnees_exemple()
    else:
        valeurs = SaisieUtilisateur.saisir_donnees()

    stats = StatistiquesDiscretes(valeurs)
    AfficheurTableau.afficher(stats)

    print("\nGénération du diagramme en bâtons...")
    DiagrammeBatons(stats).tracer()


if __name__ == "__main__":
    try:
        main()
    except (KeyboardInterrupt, EOFError):
        print("\n\nProgramme interrompu par l'utilisateur.")
    except ValueError as erreur:
        print(f"\nErreur : {erreur}")