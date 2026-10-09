"""
Diagramme en barres - Statistiques descriptives (variable qualitative)

Nom complet : SAHIB MOAD
Filière     : Génie Informatique

Description :
    Le programme demande à l'utilisateur de saisir, dans le terminal, les
    modalités d'une variable qualitative (ex : M, P, AB, B, TB) ainsi que
    leurs effectifs n_i. Il calcule ensuite les fréquences relatives
    f_i = n_i / N, affiche le tableau statistique récapitulatif, puis trace
    le diagramme en barres correspondant avec Matplotlib.

Organisation du code :
    Saisie  ->  Calculs  ->  Affichage terminal  ->  Graphique

Dépendances :
    pip install matplotlib tabulate
"""

from dataclasses import dataclass, field
from typing import List

import matplotlib.pyplot as plt

import calculs_stats as cs

try:
    from tabulate import tabulate
except ImportError:  # Repli si tabulate n'est pas installé
    tabulate = None


# ----------------------------------------------------------------------------
# 1. Modèle de données
# ----------------------------------------------------------------------------
@dataclass
class SerieStatistique:
    """Série statistique qualitative : modalités, effectifs et fréquences."""

    modalites: List[str] = field(default_factory=list)
    effectifs: List[int] = field(default_factory=list)
    frequences: List[float] = field(default_factory=list)

    def calculer(self) -> None:
        """Calcule les fréquences relatives à partir des effectifs."""
        self.frequences = cs.frequences_relatives(self.effectifs)

    @property
    def n_total(self) -> int:
        return cs.effectif_total(self.effectifs)

    @property
    def f_total(self) -> float:
        return cs.somme_frequences(self.frequences)


# ----------------------------------------------------------------------------
# 2. Saisie utilisateur (avec validations)
# ----------------------------------------------------------------------------
class SaisieDonnees:
    """Gère la saisie et la validation des données dans le terminal."""

    @staticmethod
    def lire_entier_positif(message: str) -> int:
        """Demande un entier strictement positif, jusqu'à saisie valide."""
        while True:
            texte = input(message).strip()
            try:
                valeur = int(texte)
            except ValueError:
                print("  ✗ Erreur : veuillez saisir un nombre entier.")
                continue
            if valeur <= 0:
                print("  ✗ Erreur : l'effectif doit être un entier strictement positif.")
                continue
            return valeur

    @staticmethod
    def lire_modalite(deja_saisies: List[str]) -> str:
        """Demande une modalité non vide et unique."""
        while True:
            nom = input("  Modalité : ").strip()
            if not nom:
                print("  ✗ Erreur : la modalité ne peut pas être vide.")
            elif nom.upper() in (m.upper() for m in deja_saisies):
                print(f"  ✗ Erreur : la modalité « {nom} » a déjà été saisie.")
            else:
                return nom

    def saisir_serie(self) -> SerieStatistique:
        """Saisie complète de la série statistique."""
        print("\n=== SAISIE DES DONNÉES ===")
        nb = self.lire_entier_positif("Nombre de modalités : ")

        serie = SerieStatistique()
        for i in range(1, nb + 1):
            print(f"\nModalité n°{i}/{nb}")
            nom = self.lire_modalite(serie.modalites)
            effectif = self.lire_entier_positif(f"  Effectif n_i de « {nom} » : ")
            serie.modalites.append(nom)
            serie.effectifs.append(effectif)
        return serie


# ----------------------------------------------------------------------------
# 3. Affichage dans le terminal
# ----------------------------------------------------------------------------
class AffichageTerminal:
    """Affiche le tableau statistique récapitulatif."""

    @staticmethod
    def afficher_tableau(serie: SerieStatistique) -> None:
        entetes = ["Modalité", "Effectif n_i", "Fréquence f_i"]
        lignes = [
            [m, n, cs.formater_decimal(f)]
            for m, n, f in zip(serie.modalites, serie.effectifs, serie.frequences)
        ]
        # Ligne des totaux : N = Σ n_i et Σ f_i = 1,00
        lignes.append(["TOTAL", serie.n_total, cs.formater_decimal(serie.f_total)])

        print("\n=== TABLEAU STATISTIQUE ===")
        if tabulate is not None:
            print(tabulate(lignes, headers=entetes, tablefmt="grid",
                           colalign=("center", "center", "center")))
        else:
            AffichageTerminal._tableau_secours(entetes, lignes)

        print(f"\n  N  = Σ n_i = {serie.n_total}")
        print(f"  Σ f_i = {cs.formater_decimal(serie.f_total)}")

    @staticmethod
    def _tableau_secours(entetes: List[str], lignes: List[list]) -> None:
        """Tableau textuel simple utilisé si `tabulate` n'est pas disponible."""
        largeurs = [
            max(len(str(x)) for x in [entetes[j]] + [l[j] for l in lignes]) + 2
            for j in range(len(entetes))
        ]
        separateur = "+" + "+".join("-" * w for w in largeurs) + "+"
        print(separateur)
        print("|" + "|".join(str(e).center(w) for e, w in zip(entetes, largeurs)) + "|")
        print(separateur)
        for ligne in lignes:
            print("|" + "|".join(str(c).center(w) for c, w in zip(ligne, largeurs)) + "|")
        print(separateur)


# ----------------------------------------------------------------------------
# 4. Génération du graphique
# ----------------------------------------------------------------------------
class GenerateurGraphique:
    """Trace le diagramme en barres vertical avec Matplotlib."""

    COULEUR_BARRES = "#4C72B0"   # bleu sobre
    COULEUR_BORDURE = "#1F2D3D"  # bordure nette
    COULEUR_TEXTE = "#222222"

    @classmethod
    def tracer(cls, serie: SerieStatistique) -> None:
        fig, ax = plt.subplots(figsize=(8, 5.5))

        barres = ax.bar(
            serie.modalites,
            serie.effectifs,
            color=cls.COULEUR_BARRES,
            edgecolor=cls.COULEUR_BORDURE,
            linewidth=1.2,
            width=0.6,
            zorder=3,
        )

        # Valeurs exactes affichées au-dessus de chaque barre
        for barre, valeur in zip(barres, serie.effectifs):
            ax.text(
                barre.get_x() + barre.get_width() / 2,
                barre.get_height() + max(serie.effectifs) * 0.015,
                str(valeur),
                ha="center", va="bottom",
                fontsize=12, fontweight="bold", color=cls.COULEUR_TEXTE,
            )

        # Titres et étiquettes
        ax.set_title("Diagramme en barres - Distribution de l'opinion",
                     fontsize=14, fontweight="bold", pad=15)
        ax.set_xlabel("Modalité", fontsize=12, labelpad=8)
        ax.set_ylabel("Effectif $n_i$", fontsize=12, labelpad=8)

        # Axe Y : graduations entières, marge pour les étiquettes
        ax.set_ylim(0, max(serie.effectifs) * 1.15)
        ax.yaxis.get_major_locator().set_params(integer=True)

        # Style épuré : grille horizontale légère, bordures haut/droite retirées
        ax.grid(axis="y", linestyle="--", alpha=0.4, zorder=0)
        for cote in ("top", "right"):
            ax.spines[cote].set_visible(False)

        fig.tight_layout()
        plt.show()


# ----------------------------------------------------------------------------
# 5. Programme principal
# ----------------------------------------------------------------------------
def main() -> None:
    print("=" * 60)
    print("  DIAGRAMME EN BARRES - STATISTIQUES DESCRIPTIVES")
    print("  SAHIB MOAD - Génie Informatique")
    print("=" * 60)

    serie = SaisieDonnees().saisir_serie()   # Saisie
    serie.calculer()                         # Calculs
    AffichageTerminal.afficher_tableau(serie)  # Affichage terminal
    GenerateurGraphique.tracer(serie)        # Graphique


if __name__ == "__main__":
    try:
        main()
    except (KeyboardInterrupt, EOFError):
        print("\nProgramme interrompu par l'utilisateur.")