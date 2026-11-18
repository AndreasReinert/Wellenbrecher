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


@lru_cache(maxsize=None)
def sound(name):
    """Einmal laden; fehlende Datei oder fehlendes Audiogerät bedeutet Stille."""
    import settings
    if not pygame.mixer.get_init():
        return None
    try:
        klang = pygame.mixer.Sound(str(settings.SOUNDORDNER / f"{name}.wav"))
        klang.set_volume(settings.SOUND_LAUTSTAERKEN.get(name, 0.0) * settings.SOUND_GESAMTLAUTSTAERKE)
        return klang
    except (pygame.error, OSError):
        return None


def sounds_laden():
    """Nach pygame.init() vorladen; keine Soundhardware erforderlich."""
    import settings
    _letzte_toene.clear()
    if pygame.mixer.get_init():
        pygame.mixer.set_num_channels(settings.SOUND_KANAELE)
        pygame.mixer.set_reserved(settings.SOUND_WICHTIGE_KANAELE)
    sound.cache_clear()
    for name in settings.SOUND_LAUTSTAERKEN:
        sound(name)


_letzte_toene = {}


def sound_spielen(name):
    """Effekte drosseln; Hinweise nicht durch viele Schüsse verdrängen lassen."""
    import settings
    try:
        if not pygame.mixer.get_init():
            return
        jetzt = pygame.time.get_ticks() / 1000.0
        pause = settings.SOUND_PAUSEN.get(name, settings.SOUND_MINDESTABSTAND)
        if jetzt - _letzte_toene.get(name, -float("inf")) < pause:
            return
        klang = sound(name)
        if klang is None:
            return
        if name in settings.SOUND_PRIORITAET:
            kanaele = [pygame.mixer.Channel(i) for i in range(settings.SOUND_WICHTIGE_KANAELE)]
            kanal = next((k for k in kanaele if not k.get_busy()), kanaele[0])
            kanal.play(klang)
        else:
            klang.play()
        _letzte_toene[name] = jetzt
    except (pygame.error, OSError):
        pass


@lru_cache(maxsize=None)
def titelbild(groesse):
    """Titelhintergrund einmal laden; ohne Datei dunkelblau bleiben."""
    quelle = _laden(BILDERORDNER / "titelbild.png")
    if quelle is not None:
        return pygame.transform.smoothscale(quelle, groesse)
    flaeche = pygame.Surface(groesse)
    flaeche.fill(DUNKELBLAU)
    return flaeche
