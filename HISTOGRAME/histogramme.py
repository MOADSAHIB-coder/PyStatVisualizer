"""

 Histogramme (classes de même amplitude) - Variable quantitative continue

 Nom complet : SAHIB MOAD
 Filière     : Génie Informatique

 Description :
   Ce script permet de saisir, dans le terminal, les classes d'intervalles
   [e_i, e_{i+1}[ d'une variable quantitative continue (ex. : revenu en
   ×100 DH) ainsi que leurs effectifs n_i. Il calcule ensuite :
       - l'amplitude de chaque classe   a_i = e_{i+1} - e_i
       - la fréquence relative          f_i = n_i / N
       - les totaux                     N = Σ n_i  et  Σ f_i = 1,00
   puis affiche un tableau récapitulatif et trace l'histogramme (rectangles
   contigus, amplitudes égales).

 Format de saisie d'une classe (au choix) :
       [0, 20[      ou      0 20      ou      0-20      ou      0;20

"""

import math
import re
from dataclasses import dataclass
from typing import List, Optional, Tuple

import matplotlib.pyplot as plt
import numpy as np

# `tabulate` est facultatif : en son absence, un formatage textuel aligné
# est utilisé à la place.
try:
    from tabulate import tabulate
    TABULATE_DISPONIBLE = True
except ImportError:
    TABULATE_DISPONIBLE = False


def fmt(nombre: float) -> str:
    """Formate un nombre sans zéros inutiles (20.0 -> '20', 2.50 -> '2.5')."""
    return f"{nombre:g}"


# =============================================================================
# 1. Modèle de données
# =============================================================================
@dataclass
class Classe:
    """Représente une classe [borne_inf, borne_sup[ avec son effectif et ses grandeurs."""
    borne_inf: float            # e_i
    borne_sup: float            # e_{i+1}
    effectif: int               # n_i
    amplitude: float = 0.0      # a_i = e_{i+1} - e_i
    frequence: float = 0.0      # f_i = n_i / N

    @property
    def libelle(self) -> str:
        """Écriture de la classe sous la forme [a, b[."""
        return f"[{fmt(self.borne_inf)}, {fmt(self.borne_sup)}["


# =============================================================================
# 2. Saisie et validation des entrées (terminal)
# =============================================================================
class SaisieUtilisateur:
    """Gère la saisie interactive et la validation des données dans le terminal."""

    # Tolérance pour comparer des amplitudes décimales (évite les erreurs de flottants)
    TOLERANCE = 1e-9

    # Motif d'un nombre (entier ou décimal, virgule ou point)
    _NOMBRE = r"[-+]?\d+(?:[.,]\d+)?"

    @classmethod
    def analyser_classe(cls, texte: str) -> Optional[Tuple[float, float]]:
        """Extrait (borne_inf, borne_sup) d'une saisie comme '[0, 20[' ou '0 20'.
        Retourne None si le format est invalide."""
        # On retire les crochets éventuels, puis on cherche exactement deux nombres
        nettoye = texte.replace("[", " ").replace("]", " ")
        # Le tiret est un séparateur seulement s'il suit un chiffre (ex. '0-20')
        nettoye = re.sub(r"(?<=\d)\s*-\s*(?=\d)", " ", nettoye)
        nettoye = nettoye.replace(";", " ")
        nombres = re.findall(cls._NOMBRE, nettoye)
        # Vérifie qu'il ne reste aucun caractère parasite
        reste = re.sub(cls._NOMBRE, "", nettoye)
        reste = reste.replace(",", " ").strip()
        if len(nombres) != 2 or reste:
            return None
        a, b = (float(n.replace(",", ".")) for n in nombres)
        return a, b

    @staticmethod
    def lire_entier_positif(message: str) -> int:
        """Demande un entier strictement positif ; recommence si la saisie est invalide."""
        while True:
            texte = input(message).strip()
            try:
                nombre = int(texte)
            except ValueError:
                print("  ⚠ Erreur : l'effectif doit être un nombre entier.")
                continue
            if nombre <= 0:
                print("  ⚠ Erreur : l'effectif doit être strictement positif.")
                continue
            return nombre

    @staticmethod
    def lire_nombre_classes() -> int:
        """Demande le nombre de classes (au moins 2)."""
        while True:
            texte = input("Nombre de classes (au moins 2) : ").strip()
            try:
                k = int(texte)
            except ValueError:
                print("  ⚠ Erreur : veuillez entrer un nombre entier valide.")
                continue
            if k < 2:
                print("  ⚠ Erreur : il faut au moins 2 classes.")
                continue
            return k

    @classmethod
    def saisir_donnees(cls) -> List[Classe]:
        """Saisie complète des classes contiguës d'amplitudes égales et de leurs effectifs."""
        print("\n--- Saisie des données ---")
        print("Format d'une classe : [0, 20[   (ou : 0 20 / 0-20 / 0;20)")
        k = cls.lire_nombre_classes()

        classes: List[Classe] = []
        for i in range(1, k + 1):
            while True:
                texte = input(f"  Classe {i} : ")
                bornes = cls.analyser_classe(texte)
                if bornes is None:
                    print("  ⚠ Erreur : format invalide. Exemple : [0, 20[")
                    continue
                inf, sup = bornes
                if sup <= inf:
                    print("  ⚠ Erreur : la borne supérieure doit être > à la borne inférieure.")
                    continue
                # Continuité : la borne inf. doit égaler la borne sup. de la classe précédente
                if classes and not math.isclose(inf, classes[-1].borne_sup,
                                                abs_tol=cls.TOLERANCE):
                    print(f"  ⚠ Erreur : la classe doit commencer à {fmt(classes[-1].borne_sup)} "
                          "(classes contiguës).")
                    continue
                # Amplitudes égales : même amplitude que la première classe
                if classes and not math.isclose(sup - inf, classes[0].borne_sup - classes[0].borne_inf,
                                                abs_tol=cls.TOLERANCE):
                    amp0 = classes[0].borne_sup - classes[0].borne_inf
                    print(f"  ⚠ Erreur : l'amplitude doit être égale à {fmt(amp0)} "
                          "(classes de même amplitude).")
                    continue
                break
            n = cls.lire_entier_positif(f"  Effectif n{i} de {Classe(inf, sup, 0).libelle} : ")
            classes.append(Classe(borne_inf=inf, borne_sup=sup, effectif=n))
        return classes

    @staticmethod
    def donnees_exemple() -> List[Classe]:
        """Jeu de données d'exemple : revenus en ×100 DH."""
        exemple = [(0, 20, 8), (20, 40, 15), (40, 60, 22), (60, 80, 10)]
        return [Classe(borne_inf=a, borne_sup=b, effectif=n) for a, b, n in exemple]


# =============================================================================
# 3. Calculs statistiques
# =============================================================================
class StatistiquesContinues:
    """Calcule les amplitudes a_i, les fréquences f_i et les totaux."""

    def __init__(self, classes: List[Classe]):
        if not classes:
            raise ValueError("La liste des classes est vide.")
        self.classes = classes
        self.total_effectif = 0     # N = Σ n_i
        self.total_frequence = 0.0  # Σ f_i
        self._calculer()

    def _calculer(self) -> None:
        """Calcule a_i, N, f_i puis Σ f_i."""
        self.total_effectif = sum(c.effectif for c in self.classes)
        if self.total_effectif <= 0:
            raise ValueError("L'effectif total N doit être strictement positif.")

        for c in self.classes:
            c.amplitude = c.borne_sup - c.borne_inf          # a_i = e_{i+1} - e_i
            c.frequence = c.effectif / self.total_effectif   # f_i = n_i / N

        self.total_frequence = math.fsum(c.frequence for c in self.classes)


# =============================================================================
# 4. Affichage du tableau récapitulatif
# =============================================================================
class AfficheurTableau:
    """Affiche le tableau (Classes, a_i, n_i, f_i) avec la ligne des totaux."""

    ENTETES = ["Classes", "a_i", "n_i", "f_i"]

    @classmethod
    def afficher(cls, stats: StatistiquesContinues) -> None:
        lignes = [
            [c.libelle, fmt(c.amplitude), str(c.effectif), f"{c.frequence:.4f}"]
            for c in stats.classes
        ]
        # Ligne des totaux : N et Σ f_i (pas de total pour l'amplitude)
        lignes.append(["Total", "-", str(stats.total_effectif), f"{stats.total_frequence:.2f}"])

        print("\n--- Tableau récapitulatif ---")
        if TABULATE_DISPONIBLE:
            # disable_numparse=True conserve le format texte (ex. 0.1000)
            print(tabulate(lignes, headers=cls.ENTETES, tablefmt="fancy_grid",
                           colalign=("left", "right", "right", "right"),
                           disable_numparse=True))
        else:
            cls._afficher_manuel(lignes)

        print(f"\nN = Σ n_i = {stats.total_effectif}   |   Σ f_i = {stats.total_frequence:.2f}")

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
# 5. Génération de l'histogramme
# =============================================================================
class Histogramme:
    """Trace l'histogramme à classes de même amplitude avec matplotlib."""

    COULEUR_BARRES = "#2E5AAC"    # bleu roi sobre
    COULEUR_CONTOUR = "#FFFFFF"   # contours blancs
    TITRE = "Histogramme (amplitudes égales)"

    def __init__(self, stats: StatistiquesContinues):
        self.stats = stats

    def tracer(self) -> None:
        """Construit et affiche la figure."""
        gauches = np.array([c.borne_inf for c in self.stats.classes])
        largeurs = np.array([c.amplitude for c in self.stats.classes])
        effectifs = np.array([c.effectif for c in self.stats.classes])

        plt.style.use("seaborn-v0_8-whitegrid")
        fig, ax = plt.subplots(figsize=(9, 6))

        # Rectangles contigus : alignés sur leur bord gauche, largeur = amplitude
        ax.bar(gauches, effectifs, width=largeurs, align="edge",
               color=self.COULEUR_BARRES, edgecolor=self.COULEUR_CONTOUR,
               linewidth=1.8, zorder=3)

        # Effectif affiché au-dessus de chaque rectangle
        centres = gauches + largeurs / 2
        for xc, n in zip(centres, effectifs):
            ax.annotate(str(n), (xc, n), textcoords="offset points",
                        xytext=(0, 6), ha="center", fontsize=11,
                        fontweight="bold", color="#333333")

        # Titres
        ax.set_title(self.TITRE, fontsize=16, fontweight="bold", pad=15, color="#222222")
        ax.set_xlabel("Revenu (×100 DH)", fontsize=13)
        ax.set_ylabel(r"Effectif $n_i$", fontsize=13)

        # Axe X : graduations sur les bornes des classes e_0, e_1, ..., e_k
        bornes = np.append(gauches, self.stats.classes[-1].borne_sup)
        ax.set_xticks(bornes)
        ax.set_xticklabels([fmt(b) for b in bornes])
        ax.set_xlim(bornes[0], bornes[-1])

        # Axe Y : démarre à 0, avec une marge pour les annotations, graduations entières
        ax.set_ylim(0, effectifs.max() * 1.15)
        ax.yaxis.get_major_locator().set_params(integer=True)

        # Grille légère horizontale uniquement
        ax.grid(axis="y", linestyle="--", alpha=0.5, zorder=0)
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
    print("  HISTOGRAMME - Variable quantitative continue")
    print("  Auteur : SAHIB MOAD - Génie Informatique")
    print("=" * 60)

    # Choix entre saisie manuelle et jeu de données d'exemple
    reponse = input("\nUtiliser l'exemple (revenus, 4 classes de 20) ? [o/N] : ").strip().lower()
    if reponse in ("o", "oui", "y", "yes"):
        classes = SaisieUtilisateur.donnees_exemple()
    else:
        classes = SaisieUtilisateur.saisir_donnees()

    stats = StatistiquesContinues(classes)
    AfficheurTableau.afficher(stats)

    print("\nGénération de l'histogramme...")
    Histogramme(stats).tracer()


if __name__ == "__main__":
    try:
        main()
    except (KeyboardInterrupt, EOFError):
        print("\n\nProgramme interrompu par l'utilisateur.")
    except ValueError as erreur:
        print(f"\nErreur : {erreur}")