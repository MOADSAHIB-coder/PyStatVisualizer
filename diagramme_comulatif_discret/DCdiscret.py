"""

 Diagramme cumulatif discret - Fonction de répartition empirique

 Nom complet : SAHIB MOAD
 Filière     : Génie Informatique

 Description :
   Ce script permet de saisir, dans le terminal, les valeurs discrètes (x_i)
   d'une variable quantitative et leurs effectifs (n_i). Il calcule ensuite :
       - la fréquence relative              f_i = n_i / N
       - la fréquence cumulée croissante    F_i = f_1 + f_2 + ... + f_i
       - l'effectif total                   N = Σ n_i
   et vérifie que le dernier F_i vaut bien 1,00.
   Il affiche un tableau récapitulatif puis trace la fonction de répartition
   empirique sous forme d'escalier (segments horizontaux avec points fermés
   et ouverts pour marquer les discontinuités).

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
    """Représente une valeur discrète x_i avec n_i, f_i et F_i."""
    x: int                          # x_i : valeur de la variable
    effectif: int                   # n_i : effectif
    frequence: float = 0.0          # f_i : fréquence relative
    frequence_cumulee: float = 0.0  # F_i : fréquence cumulée croissante


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
            # x_i : entier positif ou nul, sans doublon
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

        # Tri par ordre croissant des x_i (indispensable pour les cumuls)
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
class StatistiquesCumulees:
    """Calcule N, les fréquences f_i et les fréquences cumulées croissantes F_i."""

    def __init__(self, valeurs: List[Valeur]):
        if not valeurs:
            raise ValueError("La liste des valeurs est vide.")
        self.valeurs = valeurs
        self.total_effectif = 0     # N = Σ n_i
        self.verification_ok = False
        self._calculer()

    def _calculer(self) -> None:
        """Calcule N, f_i = n_i / N puis F_i = Σ_{k<=i} f_k."""
        self.total_effectif = sum(v.effectif for v in self.valeurs)
        if self.total_effectif <= 0:
            raise ValueError("L'effectif total N doit être strictement positif.")

        cumul = 0.0
        for v in self.valeurs:
            v.frequence = v.effectif / self.total_effectif   # f_i = n_i / N
            cumul += v.frequence
            v.frequence_cumulee = cumul                      # F_i

        # Vérification : le dernier F_i doit valoir 1,00 (tolérance numérique)
        self.verification_ok = math.isclose(
            self.valeurs[-1].frequence_cumulee, 1.0, abs_tol=1e-9
        )
        if self.verification_ok:
            # Élimine l'éventuel écart d'arrondi (ex. 0.9999999999999999)
            self.valeurs[-1].frequence_cumulee = 1.0


# =============================================================================
# 4. Affichage du tableau récapitulatif
# =============================================================================
class AfficheurTableau:
    """Affiche le tableau (x_i, n_i, f_i, F_i) avec la ligne des totaux."""

    ENTETES = ["x_i", "n_i", "f_i", "F_i"]

    @classmethod
    def afficher(cls, stats: StatistiquesCumulees) -> None:
        lignes = [
            [str(v.x), str(v.effectif), f"{v.frequence:.4f}", f"{v.frequence_cumulee:.4f}"]
            for v in stats.valeurs
        ]
        # Ligne des totaux : N et Σ f_i (la colonne F_i n'a pas de total)
        somme_f = math.fsum(v.frequence for v in stats.valeurs)
        lignes.append(["Total", str(stats.total_effectif), f"{somme_f:.2f}", "-"])

        print("\n--- Tableau récapitulatif ---")
        if TABULATE_DISPONIBLE:
            # disable_numparse=True conserve le format texte (ex. 0.1000)
            print(tabulate(lignes, headers=cls.ENTETES, tablefmt="fancy_grid",
                           colalign=("left", "right", "right", "right"),
                           disable_numparse=True))
        else:
            cls._afficher_manuel(lignes)

        # Vérification de cohérence
        dernier = stats.valeurs[-1].frequence_cumulee
        etat = "✔ OK" if stats.verification_ok else "✘ ERREUR"
        print(f"\nN = Σ n_i = {stats.total_effectif}   |   "
              f"Dernier F_i = {dernier:.2f}   [{etat}]")

    @classmethod
    def _afficher_manuel(cls, lignes: list) -> None:
        """Formatage textuel aligné (utilisé si `tabulate` n'est pas installé)."""
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
# 5. Génération du diagramme cumulatif en escalier
# =============================================================================
class DiagrammeCumulatif:
    """Trace la fonction de répartition empirique F(x) en escalier."""

    COULEUR_MARCHE = "#4C78A8"   # bleu sobre pour les segments
    COULEUR_POINT = "#E45756"    # rouge corail pour les points
    TITRE = "Diagramme cumulatif discret - Fonction de répartition empirique"

    def __init__(self, stats: StatistiquesCumulees):
        self.stats = stats

    def tracer(self) -> None:
        """Construit et affiche la figure."""
        x = np.array([v.x for v in self.stats.valeurs], dtype=float)
        F = np.array([v.frequence_cumulee for v in self.stats.valeurs])

        # Marge horizontale pour prolonger l'escalier avant x_1 et après x_k
        marge = 1.0
        x_min, x_max = x[0] - marge, x[-1] + marge

        plt.style.use("seaborn-v0_8-whitegrid")
        fig, ax = plt.subplots(figsize=(10, 6))

        # --- Segment F(x) = 0 pour x < x_1 (point ouvert en x_1) ---
        ax.hlines(0.0, x_min, x[0], colors=self.COULEUR_MARCHE, linewidth=2.5)

        # --- Marches : F(x) = F_i pour x_i <= x < x_{i+1} ---
        # Dernière marche : F(x) = 1 pour x >= x_k (prolongée jusqu'à x_max)
        droites = np.append(x[1:], x_max)
        ax.hlines(F, x, droites, colors=self.COULEUR_MARCHE, linewidth=2.5)

        # --- Points fermés (début de chaque marche : la valeur est incluse) ---
        ax.plot(x, F, "o", color=self.COULEUR_POINT, markersize=9, zorder=5,
                label=r"Point fermé : $F(x_i) = F_i$")

        # --- Points ouverts (fin de chaque marche : valeur exclue) ---
        # En x_1 le niveau précédent est 0, puis F_{i-1} en x_i pour i >= 2
        niveaux_precedents = np.concatenate(([0.0], F[:-1]))
        ax.plot(x, niveaux_precedents, "o", markerfacecolor="white",
                markeredgecolor=self.COULEUR_POINT, markeredgewidth=2,
                markersize=9, zorder=4, label="Point ouvert (discontinuité)")

        # --- Pointillés verticaux pour visualiser les sauts ---
        ax.vlines(x, niveaux_precedents, F, colors="#999999",
                  linestyles=":", linewidth=1.2)

        # --- Titres et axes ---
        ax.set_title(self.TITRE, fontsize=15, fontweight="bold", pad=15, color="#222222")
        ax.set_xlabel(r"$x_i$", fontsize=14)
        ax.set_ylabel(r"$F_i$", fontsize=14)

        # Axe X : graduations sur les x_i (entiers), Axe Y : de 0 à 1,05
        ax.set_xticks(x)
        ax.set_xlim(x_min, x_max)
        ax.set_ylim(0, 1.05)
        ax.set_yticks(np.arange(0, 1.01, 0.1))

        # Grille légère et épurée
        ax.grid(True, linestyle="--", alpha=0.4)
        for cote in ("top", "right"):
            ax.spines[cote].set_visible(False)

        ax.legend(loc="lower right", frameon=True, fontsize=10)
        plt.tight_layout()
        plt.show()


# =============================================================================
# 6. Programme principal
# =============================================================================
def main() -> None:
    """Point d'entrée : saisie -> calculs -> tableau -> graphique."""
    print("=" * 60)
    print("  DIAGRAMME CUMULATIF DISCRET - Fonction de répartition")
    print("  Auteur : SAHIB MOAD - Génie Informatique")
    print("=" * 60)

    # Choix entre saisie manuelle et jeu de données d'exemple
    reponse = input("\nUtiliser l'exemple (nombre d'enfants) ? [o/N] : ").strip().lower()
    if reponse in ("o", "oui", "y", "yes"):
        valeurs = SaisieUtilisateur.donnees_exemple()
    else:
        valeurs = SaisieUtilisateur.saisir_donnees()

    stats = StatistiquesCumulees(valeurs)
    AfficheurTableau.afficher(stats)

    print("\nGénération du diagramme cumulatif...")
    DiagrammeCumulatif(stats).tracer()


if __name__ == "__main__":
    try:
        main()
    except (KeyboardInterrupt, EOFError):
        print("\n\nProgramme interrompu par l'utilisateur.")
    except ValueError as erreur:
        print(f"\nErreur : {erreur}")