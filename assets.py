"""Bilder laden und wiederverwenden; fehlende Dateien ersetzen.

Aufrufe nach pygame.init() und dem Erstellen des Fensters verwenden.
Zurückgegebene Surfaces sind gemeinsam genutzt: vor Änderungen .copy() nutzen.
Auch fehlende Dateien werden zwischengespeichert; neue Bilder erfordern Neustart.
"""
from functools import lru_cache
from pathlib import Path

import pygame

from settings import BILDERORDNER, DUNKELBLAU


@lru_cache(maxsize=None)
def _laden(pfad: Path):
    """Jede Quelldatei höchstens einmal laden, auch bei mehreren Größen."""
    try:
        return pygame.image.load(str(pfad))
    except FileNotFoundError:
        return None


def bild(name, durchmesser, farbe):
    """assets/bilder/<name>.png quadratisch skalieren, sonst Kreis zeichnen.

    name wird ohne Dateiendung übergeben; farbe ist eine Pygame-Farbe.
    """
    if not isinstance(durchmesser, int) or durchmesser <= 0:
        raise ValueError("durchmesser muss eine positive ganze Zahl sein")
    return _bild(str(name), durchmesser, tuple(pygame.Color(farbe)))


@lru_cache(maxsize=None)
def _bild(name, durchmesser, farbe):
    quelle = _laden(BILDERORDNER / f"{name}.png")
    if quelle is not None:
        return pygame.transform.smoothscale(quelle, (durchmesser, durchmesser))
    flaeche = pygame.Surface((durchmesser, durchmesser), pygame.SRCALPHA)
    pygame.draw.circle(
        flaeche, farbe,
        (durchmesser // 2, durchmesser // 2),
        max(1, durchmesser // 2),
    )
    return flaeche


def hintergrund(groesse):
    """assets/bilder/hintergrund.png laden, sonst dunkelblaue Fläche."""
    groesse = tuple(groesse)
    if len(groesse) != 2 or any(not isinstance(x, int) or x <= 0 for x in groesse):
        raise ValueError("groesse muss zwei positive ganze Zahlen enthalten")
    return _hintergrund(groesse)


@lru_cache(maxsize=None)
def _hintergrund(groesse):
    quelle = _laden(BILDERORDNER / "hintergrund.png")
    if quelle is not None:
        return pygame.transform.smoothscale(quelle, groesse)
    flaeche = pygame.Surface(groesse)
    flaeche.fill(DUNKELBLAU)
    return flaeche
