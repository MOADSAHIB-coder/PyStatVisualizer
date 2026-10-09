#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""

 Histogramme (classes d'amplitudes inégales) - Variable quantitative continue

 Nom complet : SAHIB MOAD
 Filière     : Génie Informatique

 Description :
   Ce script permet de saisir, dans le terminal, les classes d'intervalles
   [e_i, e_{i+1}[ d'une variable quantitative continue (ex. : revenu en
   ×100 DH) ainsi que, au choix, leurs effectifs n_i ou leurs fréquences f_i.
   Il calcule ensuite :
       - l'amplitude de chaque classe      a_i = e_{i+1} - e_i
       - la fréquence relative             f_i = n_i / N
       - la densité de fréquence           d_i = f_i / a_i
       - les totaux                        N = Σ n_i  et  Σ f_i = 1,00
   puis affiche un tableau récapitulatif et trace l'histogramme dont la
   HAUTEUR est la densité d_i : l'AIRE de chaque rectangle (d_i × a_i = f_i)
   est ainsi proportionnelle à la fréquence de la classe.

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
    """Représente une classe [borne_inf, borne_sup[ et ses grandeurs statistiques."""
    borne_inf: float                  # e_i
    borne_sup: float                  # e_{i+1}
    effectif: Optional[int] = None    # n_i (None si l'utilisateur a saisi les fréquences)
    amplitude: float = 0.0            # a_i = e_{i+1} - e_i
    frequence: float = 0.0            # f_i = n_i / N
    densite: float = 0.0              # d_i = f_i / a_i

    @property
    def libelle(self) -> str:
        """Écriture de la classe sous la forme [a, b[."""
        return f"[{fmt(self.borne_inf)}, {fmt(self.borne_sup)}["


# =============================================================================
# 2. Saisie et validation des entrées (terminal)
# =============================================================================
class SaisieUtilisateur:
    """Gère la saisie interactive et la validation des données dans le terminal."""

    # Tolérance pour comparer des bornes décimales (évite les erreurs de flottants)
    TOLERANCE = 1e-9
    # Écart toléré entre Σ f_i et 1 lors d'une saisie en fréquences (arrondis)
    TOLERANCE_SOMME_F = 0.01

    # Motif d'un nombre (entier ou décimal, virgule ou point)
    _NOMBRE = r"[-+]?\d+(?:[.,]\d+)?"

    @classmethod
    def analyser_classe(cls, texte: str) -> Optional[Tuple[float, float]]:
        """Extrait (borne_inf, borne_sup) d'une saisie comme '[0, 20[' ou '0 20'.
        Retourne None si le format est invalide."""
        nettoye = texte.replace("[", " ").replace("]", " ")
        # Le tiret est un séparateur seulement s'il suit un chiffre (ex. '0-20')
        nettoye = re.sub(r"(?<=\d)\s*-\s*(?=\d)", " ", nettoye)
        nettoye = nettoye.replace(";", " ")
        nombres = re.findall(cls._NOMBRE, nettoye)
        # Vérifie qu'il ne reste aucun caractère parasite
        reste = re.sub(cls._NOMBRE, "", nettoye).replace(",", " ").strip()
        if len(nombres) != 2 or reste:
            return None
        a, b = (float(n.replace(",", ".")) for n in nombres)
        return a, b

    @staticmethod
    def lire_choix(message: str, choix_valides: List[str]) -> str:
        """Demande un choix parmi une liste de réponses valides."""
        while True:
            reponse = input(message).strip()
            if reponse in choix_valides:
                return reponse
            print(f"  ⚠ Erreur : choix invalide ({' / '.join(choix_valides)}).")

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
    def lire_frequence(message: str) -> float:
        """Demande une fréquence f_i dans ]0 ; 1] (virgule ou point accepté)."""
        while True:
            texte = input(message).strip().replace(",", ".")
            try:
                valeur = float(texte)
            except ValueError:
                print("  ⚠ Erreur : la fréquence doit être un nombre (ex. 0.25).")
                continue
            if not (0 < valeur <= 1):
                print("  ⚠ Erreur : la fréquence doit être comprise entre 0 (exclu) et 1.")
                continue
            return valeur

    @classmethod
    def saisir_classes(cls, k: int) -> List[Classe]:
        """Saisit k classes contiguës (amplitudes quelconques mais strictement positives)."""
        classes: List[Classe] = []
        for i in range(1, k + 1):
            while True:
                bornes = cls.analyser_classe(input(f"  Classe {i} : "))
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
                    print(f"  ⚠ Erreur : la classe doit commencer à "
                          f"{fmt(classes[-1].borne_sup)} (classes contiguës).")
                    continue
                break
            classes.append(Classe(borne_inf=inf, borne_sup=sup))
        return classes

    @classmethod
    def saisir_donnees(cls) -> List[Classe]:
        """Saisie complète : classes, puis effectifs n_i ou fréquences f_i."""
        print("\n--- Saisie des données ---")
        print("Format d'une classe : [0, 20[   (ou : 0 20 / 0-20 / 0;20)")
        k = cls.lire_nombre_classes()

        print("\nClasses (contiguës, amplitudes libres) :")
        classes = cls.saisir_classes(k)

        mode = cls.lire_choix("\nSaisir les (1) effectifs n_i ou (2) fréquences f_i ? [1/2] : ",
                              ["1", "2"])

        if mode == "1":
            print("\nEffectifs :")
            for i, c in enumerate(classes, start=1):
                c.effectif = cls.lire_entier_positif(f"  Effectif n{i} de {c.libelle} : ")
        else:
            # Boucle jusqu'à ce que Σ f_i soit (à peu près) égale à 1
            while True:
                print("\nFréquences (décimales entre 0 et 1, ex. 0.25) :")
                freqs = [cls.lire_frequence(f"  Fréquence f{i} de {c.libelle} : ")
                         for i, c in enumerate(classes, start=1)]
                somme = math.fsum(freqs)
                if abs(somme - 1.0) <= cls.TOLERANCE_SOMME_F:
                    # Renormalisation légère pour que Σ f_i = 1 exactement
                    if not math.isclose(somme, 1.0, abs_tol=1e-12):
                        print(f"  ℹ Σ f_i = {somme:.4f} : fréquences renormalisées pour obtenir 1,00.")
                    for c, f in zip(classes, freqs):
                        c.frequence = f / somme
                    break
                print(f"  ⚠ Erreur : Σ f_i = {somme:.4f} ≠ 1. Veuillez ressaisir les fréquences.")
        return classes

    @staticmethod
    def donnees_exemple() -> List[Classe]:
        """Jeu de données d'exemple : revenus en ×100 DH (classes d'amplitudes inégales)."""
        exemple = [(0, 20, 12), (20, 40, 18), (40, 80, 30), (80, 160, 20)]
        return [Classe(borne_inf=a, borne_sup=b, effectif=n) for a, b, n in exemple]


# =============================================================================
# 3. Calculs statistiques
# =============================================================================
class StatistiquesContinues:
    """Calcule a_i, f_i, d_i et les totaux."""

    def __init__(self, classes: List[Classe]):
        if not classes:
            raise ValueError("La liste des classes est vide.")
        self.classes = classes
        # N n'existe que si les effectifs ont été saisis
        self.effectifs_connus = all(c.effectif is not None for c in classes)
        self.total_effectif: Optional[int] = None   # N = Σ n_i
        self.total_frequence = 0.0                  # Σ f_i
        self.aire_totale = 0.0                      # Σ d_i × a_i (doit valoir 1)
        self._calculer()

    def _calculer(self) -> None:
        """Calcule a_i, N, f_i, d_i puis les totaux."""
        for c in self.classes:
            c.amplitude = c.borne_sup - c.borne_inf        # a_i = e_{i+1} - e_i

        if self.effectifs_connus:
            self.total_effectif = sum(c.effectif for c in self.classes)
            if self.total_effectif <= 0:
                raise ValueError("L'effectif total N doit être strictement positif.")
            for c in self.classes:
                c.frequence = c.effectif / self.total_effectif   # f_i = n_i / N

        for c in self.classes:
            c.densite = c.frequence / c.amplitude          # d_i = f_i / a_i

        self.total_frequence = math.fsum(c.frequence for c in self.classes)
        self.aire_totale = math.fsum(c.densite * c.amplitude for c in self.classes)


# =============================================================================
# 4. Affichage du tableau récapitulatif
# =============================================================================
class AfficheurTableau:
    """Affiche le tableau (Classes, a_i, [n_i], f_i, d_i) avec la ligne des totaux."""

    @classmethod
    def afficher(cls, stats: StatistiquesContinues) -> None:
        avec_n = stats.effectifs_connus
        entetes = ["Classes", "a_i"] + (["n_i"] if avec_n else []) + ["f_i", "d_i = f_i / a_i"]

        lignes = []
        for c in stats.classes:
            ligne = [c.libelle, fmt(c.amplitude)]
            if avec_n:
                ligne.append(str(c.effectif))
            ligne += [f"{c.frequence:.4f}", f"{c.densite:.4g}"]
            lignes.append(ligne)

        # Ligne des totaux : N et Σ f_i (pas de total pour a_i ni d_i)
        total = ["Total", "-"]
        if avec_n:
            total.append(str(stats.total_effectif))
        total += [f"{stats.total_frequence:.2f}", "-"]
        lignes.append(total)

        print("\n--- Tableau récapitulatif ---")
        if TABULATE_DISPONIBLE:
            # disable_numparse=True conserve le format texte (ex. 0.1000)
            print(tabulate(lignes, headers=entetes, tablefmt="fancy_grid",
                           colalign=("left",) + ("right",) * (len(entetes) - 1),
                           disable_numparse=True))
        else:
            cls._afficher_manuel(entetes, lignes)

        resume = f"Σ f_i = {stats.total_frequence:.2f}   |   Σ d_i × a_i = {stats.aire_totale:.2f}"
        if avec_n:
            resume = f"N = Σ n_i = {stats.total_effectif}   |   " + resume
        print("\n" + resume)

    @staticmethod
    def _afficher_manuel(entetes: list, lignes: list) -> None:
        """Formatage textuel aligné (utilisé si `tabulate` n'est pas installé)."""
        largeurs = [
            max(len(ligne[j]) for ligne in [entetes] + lignes)
            for j in range(len(entetes))
        ]
        separateur = "+-" + "-+-".join("-" * w for w in largeurs) + "-+"

        def formater(ligne):
            return "| " + " | ".join(
                val.ljust(largeurs[j]) if j == 0 else val.rjust(largeurs[j])
                for j, val in enumerate(ligne)
            ) + " |"

        print(separateur)
        print(formater(entetes))
        print(separateur)
        for ligne in lignes[:-1]:
            print(formater(ligne))
        print(separateur)
        print(formater(lignes[-1]))   # ligne des totaux
        print(separateur)


# =============================================================================
# 5. Génération de l'histogramme
# =============================================================================
class HistogrammeInegal:
    """Trace l'histogramme à amplitudes inégales (hauteur = densité d_i)."""

    COULEUR_BARRES = "#5BA874"     # vert sobre
    COULEUR_CONTOUR = "#1E5B35"    # vert foncé pour des contours nets
    TITRE = "Histogramme (amplitudes inégales)"

    def __init__(self, stats: StatistiquesContinues):
        self.stats = stats

    def tracer(self) -> None:
        """Construit et affiche la figure."""
        gauches = np.array([c.borne_inf for c in self.stats.classes])
        largeurs = np.array([c.amplitude for c in self.stats.classes])
        densites = np.array([c.densite for c in self.stats.classes])

        plt.style.use("seaborn-v0_8-whitegrid")
        fig, ax = plt.subplots(figsize=(10, 6))

        # Rectangles contigus : largeur = a_i, hauteur = d_i => aire = f_i
        ax.bar(gauches, densites, width=largeurs, align="edge",
               color=self.COULEUR_BARRES, edgecolor=self.COULEUR_CONTOUR,
               linewidth=1.8, zorder=3)

        # Densité affichée au-dessus de chaque rectangle
        centres = gauches + largeurs / 2
        for xc, d in zip(centres, densites):
            ax.annotate(f"{d:.4g}", (xc, d), textcoords="offset points",
                        xytext=(0, 6), ha="center", fontsize=11,
                        fontweight="bold", color="#1E3D2B")

        # Titres
        ax.set_title(self.TITRE, fontsize=16, fontweight="bold", pad=15, color="#222222")
        ax.set_xlabel("Revenu (×100 DH)", fontsize=13)
        ax.set_ylabel(r"Densité $d_i$", fontsize=13)

        # Axe X : graduations sur les bornes des classes e_0, e_1, ..., e_k
        bornes = np.append(gauches, self.stats.classes[-1].borne_sup)
        ax.set_xticks(bornes)
        ax.set_xticklabels([fmt(b) for b in bornes])
        ax.set_xlim(bornes[0], bornes[-1])

        # Axe Y : démarre à 0, avec une marge pour les annotations
        ax.set_ylim(0, densites.max() * 1.15)

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
    print("  HISTOGRAMME (amplitudes inégales) - Variable continue")
    print("  Auteur : SAHIB MOAD - Génie Informatique")
    print("=" * 60)

    # Choix entre saisie manuelle et jeu de données d'exemple
    reponse = input("\nUtiliser l'exemple (revenus, 4 classes inégales) ? [o/N] : ").strip().lower()
    if reponse in ("o", "oui", "y", "yes"):
        classes = SaisieUtilisateur.donnees_exemple()
    else:
        classes = SaisieUtilisateur.saisir_donnees()

    stats = StatistiquesContinues(classes)
    AfficheurTableau.afficher(stats)

    print("\nGénération de l'histogramme...")
    HistogrammeInegal(stats).tracer()


if __name__ == "__main__":
    try:
        main()
    except (KeyboardInterrupt, EOFError):
        print("\n\nProgramme interrompu par l'utilisateur.")
    except ValueError as erreur:
        print(f"\nErreur : {erreur}")