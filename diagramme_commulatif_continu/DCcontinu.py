"""
Diagramme cumulatif continu (fonction de répartition empirique)
pour une variable quantitative continue.

Nom complet : SAHIB MOAD
Filière : Génie Informatique

"""

import re
import sys
from math import isclose
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

# Accepte par exemple [0, 20[, [0; 20[ ou [0.5; 2.5[.
NOMBRE = r"[+-]?(?:\d+(?:[.,]\d+)?|[.,]\d+)"
MOTIF_INTERVALLE = re.compile(
    rf"^\s*[\[(]\s*({NOMBRE})\s*[,;]\s*({NOMBRE})\s*(?:\[|\))?\s*$"
)


def convertir_nombre(texte: str) -> float:
    """Convertit un nombre saisi avec un point ou une virgule décimale."""
    return float(texte.strip().replace(",", "."))


def saisir_nombre_classes() -> int:
    """Demande un nombre de classes entier strictement positif."""
    while True:
        try:
            nombre = int(input("Nombre de classes : ").strip())
            if nombre > 0:
                return nombre
        except ValueError:
            pass
        print("Veuillez saisir un entier strictement positif.")


def saisir_intervalle(numero: int, precedent: Intervalle | None) -> Intervalle:
    """Demande un intervalle valide et contigu avec la classe précédente."""
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

        if precedent is not None:
            borne_precedente = precedent[1]
            if borne_inf < borne_precedente and not isclose(
                borne_inf, borne_precedente, rel_tol=1e-9, abs_tol=1e-9
            ):
                print("Cette classe chevauche la classe précédente.")
                continue
            if not isclose(
                borne_inf, borne_precedente, rel_tol=1e-9, abs_tol=1e-9
            ):
                print(
                    "Les classes doivent être contiguës : la borne inférieure "
                    "doit correspondre à la borne supérieure précédente."
                )
                continue

        return borne_inf, borne_sup


def saisir_effectif(numero: int) -> int:
    """Demande un effectif entier positif ou nul."""
    while True:
        try:
            effectif = int(input(f"Effectif n{numero} : ").strip())
            if effectif >= 0:
                return effectif
        except ValueError:
            pass
        print("L'effectif doit être un entier positif ou nul.")


def saisir_donnees() -> Tuple[List[Intervalle], List[int]]:
    """Collecte les classes contiguës et leurs effectifs."""
    nombre_classes = saisir_nombre_classes()
    classes: List[Intervalle] = []
    effectifs: List[int] = []

    for numero in range(1, nombre_classes + 1):
        precedent = classes[-1] if classes else None
        classes.append(saisir_intervalle(numero, precedent))
        effectifs.append(saisir_effectif(numero))

    if sum(effectifs) == 0:
        raise ValueError(
            "La somme des effectifs doit être supérieure à zéro."
        )
    return classes, effectifs


def calculer_statistiques(
    effectifs: Sequence[int],
) -> Tuple[List[float], List[float], int]:
    """Calcule les fréquences relatives, cumulées et l'effectif total."""
    total = sum(effectifs)
    frequences = [effectif / total for effectif in effectifs]
    frequences_cumulees = np.cumsum(frequences).tolist()

    # La dernière fréquence cumulée vaut mathématiquement exactement 1.
    frequences_cumulees[-1] = 1.0
    return frequences, frequences_cumulees, total


def formater_nombre(valeur: float) -> str:
    """Formate un nombre avec une virgule décimale."""
    return f"{valeur:g}".replace(".", ",")


def afficher_tableau(
    classes: Sequence[Intervalle],
    effectifs: Sequence[int],
    frequences: Sequence[float],
    frequences_cumulees: Sequence[float],
    total: int,
) -> None:
    """Affiche les fréquences par classe et la ligne des totaux."""
    lignes = []
    for classe, effectif, frequence, cumulee in zip(
        classes, effectifs, frequences, frequences_cumulees
    ):
        borne_inf, borne_sup = classe
        libelle = (
            f"[{formater_nombre(borne_inf)}, "
            f"{formater_nombre(borne_sup)}["
        )
        lignes.append(
            [libelle, effectif, f"{frequence:.2f}", f"{cumulee:.2f}"]
        )

    lignes.append(
        [
            "Total",
            total,
            f"{sum(frequences):.2f}",
            f"{frequences_cumulees[-1]:.2f}",
        ]
    )
    print()
    print(
        tabulate(
            lignes,
            headers=["Classes", "n_i", "f_i", "F_i"],
            tablefmt="rounded_outline",
            stralign="center",
            numalign="center",
        )
    )
    print(f"\nSomme des effectifs : N = {total}")
    print(f"Dernière fréquence cumulée : F_n = {frequences_cumulees[-1]:.2f}")


def tracer_diagramme(
    classes: Sequence[Intervalle],
    frequences_cumulees: Sequence[float],
) -> None:
    """Trace l'ogive avec F=0 à la borne inférieure de la première classe."""
    bornes = [classes[0][0]] + [borne_sup for _, borne_sup in classes]
    frequences_trace = [0.0] + list(frequences_cumulees)

    x = np.asarray(bornes, dtype=float)
    y = np.asarray(frequences_trace, dtype=float)

    fig, ax = plt.subplots(figsize=(10, 6))
    ax.plot(
        x,
        y,
        color="royalblue",
        marker="o",
        linewidth=2.5,
        markersize=7,
        label="Fréquence cumulée croissante",
    )

    # Guides verticaux entre l'axe horizontal et les points des bornes supérieures.
    for borne_sup, frequence_cumulee in zip(bornes[1:], frequences_cumulees):
        ax.vlines(
            borne_sup,
            0,
            frequence_cumulee,
            color="gray",
            linestyle=":",
            linewidth=1.2,
            alpha=0.8,
        )

    ax.set_title(
        "Diagramme cumulatif continu - Fonction de répartition empirique"
    )
    ax.set_xlabel("Revenu (×100 DH)")
    ax.set_ylabel("$F_i$")
    ax.set_xticks(x)
    ax.set_xticklabels([formater_nombre(borne) for borne in bornes])
    ax.set_ylim(0.0, 1.05)
    ax.set_xlim(bornes[0], bornes[-1])
    ax.grid(axis="both", linestyle="--", alpha=0.35)
    ax.legend()
    fig.tight_layout()
    plt.show()


def main() -> None:
    """Orchestre la saisie, les calculs, le tableau et le graphique."""
    print("Diagramme cumulatif continu (ogive)\n")
    try:
        classes, effectifs = saisir_donnees()
        frequences, frequences_cumulees, total = calculer_statistiques(
            effectifs
        )

        # Vérification de la fréquence cumulée finale.
        if not isclose(
            frequences_cumulees[-1], 1.0, rel_tol=1e-9, abs_tol=1e-9
        ):
            raise ArithmeticError(
                "La dernière fréquence cumulée doit être égale à 1."
            )

        afficher_tableau(
            classes,
            effectifs,
            frequences,
            frequences_cumulees,
            total,
        )
        tracer_diagramme(classes, frequences_cumulees)
    except (ValueError, ArithmeticError) as exc:
        print(f"\nErreur : {exc}")
    except KeyboardInterrupt:
        print("\nSaisie interrompue.")


if __name__ == "__main__":
    main()