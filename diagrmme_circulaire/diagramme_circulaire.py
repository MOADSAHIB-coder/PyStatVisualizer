"""

 Diagramme circulaire (secteurs angulaires) - Variable statistique qualitative

 Nom complet : SAHIB MOAD
 Filière     : Génie Informatique

 Description :
   Ce script permet de saisir, dans le terminal, les modalités (x_i) d'une
   variable qualitative ainsi que leurs effectifs (n_i). Il calcule ensuite :
       - la fréquence relative      f_i     = n_i / N
       - l'angle du secteur (en °)  theta_i = 360 * f_i = 360 * n_i / N
       - les totaux                 N = Σ n_i ,  Σ f_i = 1,00 ,  Σ theta_i = 360°
   puis affiche un tableau récapitulatif et trace le diagramme circulaire.

"""

import math
from dataclasses import dataclass
from typing import List

import matplotlib.pyplot as plt

try:
    from tabulate import tabulate
    TABULATE_DISPONIBLE = True
except ImportError:
    TABULATE_DISPONIBLE = False


# =============================================================================
# 1. Modèle de données
# =============================================================================
@dataclass
class Modalite:
    """Représente une modalité x_i avec son effectif n_i et ses grandeurs calculées."""
    nom: str                      # x_i : libellé de la modalité
    effectif: int                 # n_i : effectif
    frequence: float = 0.0        # f_i : fréquence relative
    angle: float = 0.0            # theta_i : angle du secteur en degrés


# =============================================================================
# 2. Saisie et validation des entrées (terminal)
# =============================================================================
class SaisieUtilisateur:
    """Gère la saisie interactive et la validation des données dans le terminal."""

    @staticmethod
    def lire_entier_positif(message: str, minimum: int = 1) -> int:
        """Demande un entier >= minimum et recommence tant que la saisie est invalide."""
        while True:
            valeur = input(message).strip()
            try:
                nombre = int(valeur)
            except ValueError:
                print("  ⚠ Erreur : veuillez entrer un nombre entier valide.")
                continue
            if nombre < minimum:
                print(f"  ⚠ Erreur : la valeur doit être supérieure ou égale à {minimum}.")
                continue
            return nombre

    @staticmethod
    def lire_nom_modalite(numero: int, deja_saisies: List[str]) -> str:
        """Demande un libellé de modalité non vide et unique."""
        while True:
            nom = input(f"  Modalité x{numero} : ").strip()
            if not nom:
                print("  ⚠ Erreur : le nom de la modalité ne peut pas être vide.")
            elif nom.lower() in (n.lower() for n in deja_saisies):
                print(f"  ⚠ Erreur : la modalité « {nom} » a déjà été saisie.")
            else:
                return nom

    @classmethod
    def saisir_donnees(cls) -> List[Modalite]:
        """Saisie complète : nombre de modalités, puis (x_i, n_i) pour chacune."""
        print("\n--- Saisie des données ---")
        k = cls.lire_entier_positif("Nombre de modalités (au moins 2) : ", minimum=2)

        modalites: List[Modalite] = []
        noms: List[str] = []
        for i in range(1, k + 1):
            nom = cls.lire_nom_modalite(i, noms)
            effectif = cls.lire_entier_positif(f"  Effectif n{i} de « {nom} » : ", minimum=1)
            noms.append(nom)
            modalites.append(Modalite(nom=nom, effectif=effectif))
        return modalites

    @staticmethod
    def donnees_exemple() -> List[Modalite]:
        """Jeu de données d'exemple (mentions : M, P, AB, B, TB)."""
        exemple = [("M", 5), ("P", 10), ("AB", 15), ("B", 12), ("TB", 8)]
        return [Modalite(nom=n, effectif=e) for n, e in exemple]


# =============================================================================
# 3. Calculs statistiques
# =============================================================================
class StatistiquesQualitatives:
    """Calcule les fréquences, les angles et les totaux d'une série qualitative."""

    def __init__(self, modalites: List[Modalite]):
        if not modalites:
            raise ValueError("La liste des modalités est vide.")
        self.modalites = modalites
        self.total_effectif = 0      # N = Σ n_i
        self.total_frequence = 0.0   # Σ f_i
        self.total_angle = 0.0       # Σ theta_i
        self._calculer()

    def _calculer(self) -> None:
        """Calcule N, puis f_i et theta_i pour chaque modalité, puis les totaux."""
        self.total_effectif = sum(m.effectif for m in self.modalites)
        if self.total_effectif <= 0:
            raise ValueError("L'effectif total N doit être strictement positif.")

        for m in self.modalites:
            m.frequence = m.effectif / self.total_effectif   # f_i = n_i / N
            m.angle = 360.0 * m.frequence                    # theta_i = 360 * f_i

        # math.fsum limite les erreurs d'arrondi lors des sommes de flottants
        self.total_frequence = math.fsum(m.frequence for m in self.modalites)
        self.total_angle = math.fsum(m.angle for m in self.modalites)


# =============================================================================
# 4. Affichage du tableau récapitulatif
# =============================================================================
class AfficheurTableau:
    """Affiche le tableau (x_i, n_i, f_i, theta_i) avec la ligne des totaux."""

    ENTETES = ["x_i", "n_i", "f_i", "θ_i (°)"]

    @classmethod
    def afficher(cls, stats: StatistiquesQualitatives) -> None:
        lignes = [
            [m.nom, str(m.effectif), f"{m.frequence:.4f}", f"{m.angle:.2f}"]
            for m in stats.modalites
        ]
        # Ligne des totaux : N, Σ f_i = 1,00 et Σ θ_i = 360°
        lignes.append([
            "Total",
            str(stats.total_effectif),
            f"{stats.total_frequence:.2f}",
            f"{stats.total_angle:.2f}",
        ])

        print("\n--- Tableau récapitulatif ---")
        if TABULATE_DISPONIBLE:
            print(tabulate(lignes, headers=cls.ENTETES, tablefmt="fancy_grid",
                           colalign=("left", "right", "right", "right"),
                           disable_numparse=True))   # conserve le format 0.1000 / 36.00
        else:
            cls._afficher_manuel(lignes)

        print(f"\nN = Σ n_i = {stats.total_effectif}   |   "
              f"Σ f_i = {stats.total_frequence:.2f}   |   "
              f"Σ θ_i = {stats.total_angle:.2f}°")

    @classmethod
    def _afficher_manuel(cls, lignes: list) -> None:
        """Formatage textuel aligné (utilisé si `tabulate` n'est pas installé)."""
        # Largeur de chaque colonne = longueur maximale (en-tête ou données)
        largeurs = [
            max(len(str(ligne[j])) for ligne in [cls.ENTETES] + lignes)
            for j in range(len(cls.ENTETES))
        ]
        separateur = "+-" + "-+-".join("-" * w for w in largeurs) + "-+"

        def formater(ligne):
            return "| " + " | ".join(
                str(val).ljust(largeurs[j]) if j == 0 else str(val).rjust(largeurs[j])
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
# 5. Génération du diagramme circulaire
# =============================================================================
class DiagrammeCirculaire:
    """Trace le diagramme circulaire (secteurs angulaires) avec matplotlib."""

    # Palette moderne et harmonieuse (tons doux et contrastés)
    PALETTE = ["#4C78A8", "#F58518", "#54A24B", "#E45756", "#B279A2",
               "#72B7B2", "#EECA3B", "#9D755D", "#BAB0AC", "#FF9DA6"]

    TITRE = "Diagramme circulaire - Secteurs angulaires"

    def __init__(self, stats: StatistiquesQualitatives):
        self.stats = stats

    def _couleurs(self) -> List[str]:
        """Retourne autant de couleurs que de modalités (palette répétée si besoin)."""
        k = len(self.stats.modalites)
        return [self.PALETTE[i % len(self.PALETTE)] for i in range(k)]

    @staticmethod
    def _format_texte_secteur(pourcentage: float) -> str:
        """Texte affiché sur chaque secteur : pourcentage (f_i × 100 %) et angle θ_i."""
        angle = pourcentage * 3.6          # 360° × (pourcentage / 100)
        return f"{pourcentage:.1f} %\n{angle:.1f}°"

    def tracer(self) -> None:
        """Construit et affiche la figure."""
        etiquettes = [m.nom for m in self.stats.modalites]
        effectifs = [m.effectif for m in self.stats.modalites]

        plt.style.use("seaborn-v0_8-whitegrid")
        fig, ax = plt.subplots(figsize=(8, 8))

        _, textes_etiquettes, textes_valeurs = ax.pie(
            effectifs,
            labels=etiquettes,                      # modalités autour du cercle
            colors=self._couleurs(),
            autopct=self._format_texte_secteur,     # % et angle sur chaque secteur
            pctdistance=0.68,
            labeldistance=1.08,
            startangle=90,                          # premier secteur en haut
            counterclock=False,                     # sens horaire
            wedgeprops={"edgecolor": "white", "linewidth": 2},
        )

        # Mise en forme du texte
        for t in textes_etiquettes:
            t.set_fontsize(14)
            t.set_fontweight("bold")
            t.set_color("#333333")
        for t in textes_valeurs:
            t.set_fontsize(11)
            t.set_color("white")
            t.set_fontweight("bold")

        ax.set_title(self.TITRE, fontsize=17, fontweight="bold", pad=22, color="#222222")
        ax.axis("equal")   # garantit un cercle parfait

        # Note de bas de figure avec l'effectif total
        fig.text(0.5, 0.04, f"N = {self.stats.total_effectif}",
                 ha="center", fontsize=12, color="#555555")

        plt.tight_layout()
        plt.show()


# =============================================================================
# 6. Programme principal
# =============================================================================
def main() -> None:
    """Point d'entrée : saisie -> calculs -> tableau -> graphique."""
    print("=" * 60)
    print("  DIAGRAMME CIRCULAIRE - Variable statistique qualitative")
    print("  Auteur : SAHIB MOAD - Génie Informatique")
    print("=" * 60)

    # Choix entre saisie manuelle et jeu de données d'exemple
    reponse = input("\nUtiliser l'exemple (M, P, AB, B, TB) ? [o/N] : ").strip().lower()
    if reponse in ("o", "oui", "y", "yes"):
        modalites = SaisieUtilisateur.donnees_exemple()
    else:
        modalites = SaisieUtilisateur.saisir_donnees()

    stats = StatistiquesQualitatives(modalites)
    AfficheurTableau.afficher(stats)

    print("\nGénération du diagramme circulaire...")
    DiagrammeCirculaire(stats).tracer()


if __name__ == "__main__":
    try:
        main()
    except (KeyboardInterrupt, EOFError):
        print("\n\nProgramme interrompu par l'utilisateur.")
    except ValueError as erreur:
        print(f"\nErreur : {erreur}")