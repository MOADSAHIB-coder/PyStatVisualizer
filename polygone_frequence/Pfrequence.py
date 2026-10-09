"""
Polygone des fréquences d'une variable quantitative continue.

Nom complet : SAHIB MOAD
Filière : Génie Informatique

"""

import re
import sys
from typing import List, Sequence, Tuple

try:
    import matplotlib.pyplot as plt
    import numpy as np
    from tabulate import tabulate
except ImportError as exc:
    print(
        "Une dépendance est manquante. Installez-les avec :\n"
        "python -m pip install matplotlib numpy tabulate",
        file=sys.stderr,
    )
    raise SystemExit(1) from exc


Intervalle = Tuple[float, float]

# Accepte notamment [0, 20[, [0; 20[ ou [0.5; 2.5[.
NOMBRE = r"[+-]?(?:\d+(?:[.,]\d+)?|[.,]\d+)"
MOTIF_INTERVALLE = re.compile(
    rf"^\s*[\[(]\s*({NOMBRE})\s*[,;]\s*({NOMBRE})\s*(?:\[|\))?\s*$"
)


def convertir_nombre(texte: str) -> float:
    """Convertit un nombre saisi avec un point ou une virgule décimale."""
    return float(texte.strip().replace(",", "."))


def saisir_nombre_classes() -> int:
    """Demande le nombre de classes et valide la saisie."""
    while True:
        saisie = input("Nombre de classes : ").strip()
        try:
            nombre = int(saisie)
            if nombre > 0:
                return nombre
        except ValueError:
            pass
        print("Veuillez saisir un entier strictement positif.")


def saisir_intervalle(numero: int, precedent: Intervalle | None) -> Intervalle:
    """Demande un intervalle [borne inférieure, borne supérieure[ valide."""
    while True:
        saisie = input(
            f"Classe {numero} (ex. [0, 20[ ou [0.5; 2.5[) : "
        )
        correspondance = MOTIF_INTERVALLE.match(saisie)
        if not correspondance:
            print("Format invalide. Utilisez par exemple [0, 20[.")
            continue

        try:
            borne_inf = convertir_nombre(correspondance.group(1))
            borne_sup = convertir_nombre(correspondance.group(2))
        except ValueError:
            print("Les bornes doivent être des nombres valides.")
            continue

        if not borne_inf < borne_sup:
            print("La borne supérieure doit être strictement plus grande.")
            continue
        if precedent is not None and borne_inf < precedent[1]:
            print(
                "Les classes doivent être saisies dans l'ordre et ne pas "
                "se chevaucher."
            )
            continue
        return borne_inf, borne_sup


def saisir_effectif(numero: int) -> int:
    """Demande un effectif entier positif ou nul."""
    while True:
        saisie = input(f"Effectif n{numero} : ").strip()
        try:
            effectif = int(saisie)
            if effectif >= 0:
                return effectif
        except ValueError:
            pass
        print("L'effectif doit être un entier positif ou nul.")


def saisir_donnees() -> Tuple[List[Intervalle], List[int]]:
    """Collecte les classes et leurs effectifs."""
    nombre_classes = saisir_nombre_classes()
    classes: List[Intervalle] = []
    effectifs: List[int] = []

    for numero in range(1, nombre_classes + 1):
        precedent = classes[-1] if classes else None
        classe = saisir_intervalle(numero, precedent)
        classes.append(classe)
        effectifs.append(saisir_effectif(numero))

    if sum(effectifs) == 0:
        raise ValueError(
            "La somme des effectifs doit être supérieure à zéro."
        )
    return classes, effectifs


def calculer_statistiques(
    classes: Sequence[Intervalle], effectifs: Sequence[int]
) -> Tuple[List[float], List[float], int]:
    """Calcule les centres, les fréquences relatives et l'effectif total."""
    total = sum(effectifs)
    centres = [(borne_inf + borne_sup) / 2 for borne_inf, borne_sup in classes]
    frequences = [effectif / total for effectif in effectifs]
    return centres, frequences, total


def formater_nombre(valeur: float) -> str:
    """Formate un nombre avec une virgule décimale."""
    return f"{valeur:g}".replace(".", ",")


def afficher_tableau(
    classes: Sequence[Intervalle],
    centres: Sequence[float],
    effectifs: Sequence[int],
    frequences: Sequence[float],
    total: int,
) -> None:
    """Affiche un tableau aligné avec la ligne des totaux."""
    lignes = []
    for classe, centre, effectif, frequence in zip(
        classes, centres, effectifs, frequences
    ):
        borne_inf, borne_sup = classe
        libelle = f"[{formater_nombre(borne_inf)}, {formater_nombre(borne_sup)}["
        lignes.append(
            [libelle, formater_nombre(centre), effectif, f"{frequence:.2f}"]
        )

    lignes.append(["Total", "—", total, f"{sum(frequences):.2f}"])
    print()
    print(
        tabulate(
            lignes,
            headers=["Classes", "Centre c_i", "n_i", "f_i"],
            tablefmt="rounded_outline",
            stralign="center",
            numalign="center",
        )
    )
    print(f"\nSomme des effectifs : N = {total}")
    print(f"Somme des fréquences : Σ f_i = {sum(frequences):.2f}")


def tracer_graphique(
    classes: Sequence[Intervalle],
    centres: Sequence[float],
    frequences: Sequence[float],
) -> None:
    """Trace l'histogramme des fréquences et le polygone fermé à zéro."""
    bornes_inf = np.array([classe[0] for classe in classes], dtype=float)
    largeurs = np.array(
        [borne_sup - borne_inf for borne_inf, borne_sup in classes],
        dtype=float,
    )
    centres_array = np.asarray(centres, dtype=float)
    frequences_array = np.asarray(frequences, dtype=float)

    # Le centre fictif extérieur est placé à une largeur de classe du centre
    # réel le plus proche ; sa fréquence est nulle.
    x_polygone = np.concatenate(
        (
            [centres_array[0] - largeurs[0]],
            centres_array,
            [centres_array[-1] + largeurs[-1]],
        )
    )
    y_polygone = np.concatenate(([0.0], frequences_array, [0.0]))

    fig, ax = plt.subplots(figsize=(10, 6))
    ax.bar(
        bornes_inf,
        frequences_array,
        width=largeurs,
        align="edge",
        color="steelblue",
        edgecolor="navy",
        alpha=0.3,
        label="Histogramme des fréquences",
    )
    ax.plot(
        x_polygone,
        y_polygone,
        color="red",
        marker="o",
        linewidth=2,
        markersize=6,
        label="Polygone des fréquences",
    )

    ax.set_title("Polygone des fréquences")
    ax.set_xlabel("Revenu (×100 DH)")
    ax.set_ylabel("Fréquence $f_i$")
    ax.set_xticks(centres_array)
    ax.set_xticklabels([formater_nombre(c) for c in centres_array])
    ax.set_ylim(bottom=0)
    ax.grid(axis="y", linestyle="--", alpha=0.45)
    ax.legend()
    fig.tight_layout()
    plt.show()


def main() -> None:
    """Orchestre la saisie, les calculs, l'affichage et le graphique."""
    print("Calcul et représentation d'un polygone des fréquences\n")
    try:
        classes, effectifs = saisir_donnees()
        centres, frequences, total = calculer_statistiques(classes, effectifs)
        afficher_tableau(classes, centres, effectifs, frequences, total)
        tracer_graphique(classes, centres, frequences)
    except (ValueError, KeyboardInterrupt) as exc:
        if isinstance(exc, KeyboardInterrupt):
            print("\nSaisie interrompue.")
        else:
            print(f"\nErreur : {exc}")


if __name__ == "__main__":
    main()