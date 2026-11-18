"""Spielobjekte für Wellenbrecher."""
import math
import random

import pygame

import assets
import settings
from settings import (
    SPIELER_FARBE, SPIELER_GROESSE, SPIELER_TEMPO,
    SCHUSS_PAUSE, SCHUSS_TEMPO, SCHUSS_GROESSE, SCHUSS_FARBE,
    SCHUSS_LEBENSDAUER, GEGNER_TYPEN,
    SPIELER_RADIUS, SPIELER_STARTLEBEN, SPIELER_UNVERWUNDBAR_DAUER,
    SPIELER_BLINK_PAUSE, SCHUSS_RADIUS,

)


class Spieler:
    """WASD bewegt das Schiff; das Originalbild zeigt mit seiner Spitze nach oben."""

    def __init__(self, fenstergroesse):
        self.grenzen = pygame.Rect((0, 0), fenstergroesse)
        self.position = pygame.Vector2(self.grenzen.center)
        self.radius = SPIELER_RADIUS
        self.leben = SPIELER_STARTLEBEN
        self.unverwundbar_rest = 0.0
        self.tempo = SPIELER_TEMPO
        self.schuss_wartezeit = 0.0
        self.originalbild = assets.bild(
            "spieler", SPIELER_GROESSE, SPIELER_FARBE
        )
        self.bild = self.originalbild
        self.rect = self.bild.get_rect(center=self.grenzen.center)
        self.winkel = 0.0
        # Halbe Bilddiagonale: Auch gedrehte Bildecken bleiben im Fenster.
        self.rand = math.ceil(math.hypot(*self.originalbild.get_size()) / 2)

    def aktualisieren(self, delta_time, tasten, mausposition):
        self.unverwundbar_rest = max(0.0, self.unverwundbar_rest - delta_time)
        self.schuss_wartezeit = max(0.0, self.schuss_wartezeit - delta_time)
        richtung = pygame.Vector2(
            int(tasten[pygame.K_d]) - int(tasten[pygame.K_a]),
            int(tasten[pygame.K_s]) - int(tasten[pygame.K_w]),
        )
        if richtung.length_squared() > 0:
            richtung.normalize_ip()
            self.position += richtung * self.tempo * delta_time

        self.position.x = max(
            self.rand, min(self.grenzen.width - self.rand, self.position.x)
        )
        self.position.y = max(
            self.rand, min(self.grenzen.height - self.rand, self.position.y)
        )

        zur_maus = pygame.Vector2(mausposition) - self.position
        if zur_maus.length_squared() > 0:
            self.winkel = math.degrees(math.atan2(-zur_maus.x, -zur_maus.y))
        # Immer das Original drehen, um Qualitätsverlust zu vermeiden.
        self.bild = pygame.transform.rotate(self.originalbild, self.winkel)
        self.rect = self.bild.get_rect(
            center=(round(self.position.x), round(self.position.y))
        )

    def feuern(self, mausposition):
        """Gibt einen neuen Schuss zurück, sobald die Feuerpause vorbei ist."""
        if self.schuss_wartezeit > 0:
            return None
        richtung = pygame.Vector2(mausposition) - self.position
        # Direkt auf dem Schiff gibt es keine eindeutige Zielrichtung.
        if richtung.length_squared() == 0:
            return None
        self.schuss_wartezeit = SCHUSS_PAUSE
        return Schuss(self.position, richtung)

    def schaden_nehmen(self, schaden):
        """Nur ein Treffer pro Schutzzeit; Lebenspunkte fallen nicht unter null."""
        if self.leben <= 0 or self.unverwundbar_rest > 0:
            return False
        self.leben = max(0, self.leben - schaden)
        self.unverwundbar_rest = SPIELER_UNVERWUNDBAR_DAUER
        return True

    def zeichnen(self, fenster):
        if self.unverwundbar_rest > 0:
            vergangen = SPIELER_UNVERWUNDBAR_DAUER - self.unverwundbar_rest
            if int(vergangen / SPIELER_BLINK_PAUSE) % 2 == 0:
                return
        fenster.blit(self.bild, self.rect)


class Schuss:
    """Fliegt geradlinig in die beim Abfeuern gewählte Richtung."""

    def __init__(self, position, richtung):
        self.position = pygame.Vector2(position)
        self.alter = 0.0
        self.radius = SCHUSS_RADIUS
        self.geschwindigkeit = pygame.Vector2(richtung).normalize() * SCHUSS_TEMPO
        self.bild = assets.bild("schuss", SCHUSS_GROESSE, SCHUSS_FARBE)
        self.rect = self.bild.get_rect(center=(round(self.position.x), round(self.position.y)))

    def aktualisieren(self, delta_time):
        self.alter += delta_time
        self.position += self.geschwindigkeit * delta_time
        self.rect.center = (round(self.position.x), round(self.position.y))

    def abgelaufen(self):
        """Die Lebensdauer beginnt für jeden Schuss beim Abfeuern."""
        return self.alter >= SCHUSS_LEBENSDAUER

    def im_fenster(self, grenzen):
        """Erst entfernen, wenn das gesamte Bild außerhalb liegt."""
        return self.rect.colliderect(grenzen)

    def zeichnen(self, fenster):
        fenster.blit(self.bild, self.rect)


class Gegner:
    """Erscheint außerhalb eines zufälligen Randes und verfolgt den Spieler."""

    def __init__(self, typ, fenstergroesse):
        daten = GEGNER_TYPEN[typ]
        self.typ = typ
        self.waffe = settings.GEGNER_WAFFEN.get(typ)
        self.schuss_wartezeit = self.waffe["pause"] if self.waffe else 0.0
        self.tempo = daten["tempo"]
        self.leben = daten["leben"]
        self.radius = daten["radius"]
        self.originalbild = assets.bild(
            daten["bildname"], self.radius * 2, daten["ersatzfarbe"]
        )
        # Auch die gedrehten Bildecken starten vollständig außerhalb.
        abstand = math.ceil(math.hypot(*self.originalbild.get_size()) / 2)
        breite, hoehe = fenstergroesse
        rand = random.choice(("links", "rechts", "oben", "unten"))
        if rand == "links":
            position = (-abstand, random.uniform(0, hoehe))
        elif rand == "rechts":
            position = (breite + abstand, random.uniform(0, hoehe))
        elif rand == "oben":
            position = (random.uniform(0, breite), -abstand)
        else:
            position = (random.uniform(0, breite), hoehe + abstand)
        self.position = pygame.Vector2(position)
        self.winkel = 0.0
        self.bild = self.originalbild
        self.rect = self.bild.get_rect(
            center=(round(self.position.x), round(self.position.y))
        )

    def aktualisieren(self, delta_time, spielerposition):
        self.schuss_wartezeit = max(0.0, self.schuss_wartezeit - delta_time)
        zum_spieler = pygame.Vector2(spielerposition) - self.position
        entfernung = zum_spieler.length()
        if entfernung > 0:
            self.winkel = math.degrees(math.atan2(-zum_spieler.x, -zum_spieler.y))
            # Am Ziel stoppen, statt bei großen Zeitschritten darüber zu springen.
            self.position += zum_spieler / entfernung * min(
                self.tempo * delta_time, entfernung
            )
        self.bild = pygame.transform.rotate(self.originalbild, self.winkel)
        self.rect = self.bild.get_rect(
            center=(round(self.position.x), round(self.position.y))
        )

    def feuern(self, spielerposition, grenzen):
        """Nur sichtbare Gegner feuern; die erste Salve folgt nach einer Pause."""
        if not self.waffe or self.schuss_wartezeit > 0:
            return []
        if not grenzen.collidepoint(self.position):
            return []
        richtung = pygame.Vector2(spielerposition) - self.position
        if richtung.length_squared() == 0:
            return []
        self.schuss_wartezeit = self.waffe["pause"]
        return [GegnerSchuss(self.position, richtung.rotate(winkel), self.waffe)
                for winkel in self.waffe["winkel"]]

    def zeichnen(self, fenster):
        fenster.blit(self.bild, self.rect)


class GegnerSchuss(Schuss):
    """Feindliches Projektil mit eigener Größe und gerader Flugbahn."""

    def __init__(self, position, richtung, waffe):
        self.position = pygame.Vector2(position)
        self.alter = 0.0
        self.radius = waffe["radius"]
        self.geschwindigkeit = (pygame.Vector2(richtung).normalize()
                                * settings.GEGNER_SCHUSS_TEMPO)
        self.bild = assets.bild(waffe["bildname"], self.radius * 2, waffe["farbe"])
        self.rect = self.bild.get_rect(center=(round(self.position.x), round(self.position.y)))

    def abgelaufen(self):
        return self.alter >= settings.GEGNER_SCHUSS_LEBENSDAUER


def beruehren(erstes, zweites):
    """Kreiskollision: Mittelpunktabstand höchstens Summe der Radien.

    Quadrierte Abstände sparen die Quadratwurzel; Berührung zählt als Treffer.
    """
    return erstes.position.distance_squared_to(zweites.position) <= (
        erstes.radius + zweites.radius
    ) ** 2
