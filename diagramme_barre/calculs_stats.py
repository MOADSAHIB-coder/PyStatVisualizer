"""
Calculs statistiques (variables qualitatives).

Nom complet : SAHIB MOAD
Filière     : Génie Informatique

Ce module regroupe les fonctions mathématiques utilisées par le script
principal `diagramme_barres.py` :
    - effectif total   : N = Σ n_i
    - fréquence        : f_i = n_i / N
    - somme des fréquences : Σ f_i = 1
"""

from typing import List


def effectif_total(effectifs: List[int]) -> int:
    """Retourne l'effectif total N = Σ n_i."""
    return sum(effectifs)


def frequences_relatives(effectifs: List[int]) -> List[float]:
    """Retourne la liste des fréquences relatives f_i = n_i / N."""
    n_total = effectif_total(effectifs)
    if n_total == 0:
        raise ValueError("L'effectif total est nul : calcul des fréquences impossible.")
    return [n_i / n_total for n_i in effectifs]


def somme_frequences(frequences: List[float]) -> float:
    """Retourne la somme des fréquences Σ f_i (doit valoir 1,00)."""
    return sum(frequences)


def formater_decimal(valeur: float, decimales: int = 2) -> str:
    """Formate un nombre avec la virgule décimale française (ex : 0,25)."""
    return f"{valeur:.{decimales}f}".replace(".", ",")