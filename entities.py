"""Spielobjekte für Wellenbrecher."""
import math

import pygame

import assets
from settings import (
    SPIELER_FARBE, SPIELER_GROESSE, SPIELER_TEMPO,
    SCHUSS_PAUSE, SCHUSS_TEMPO, SCHUSS_GROESSE, SCHUSS_FARBE,
)


class Spieler:
    """WASD bewegt das Schiff; das Originalbild zeigt mit seiner Spitze nach oben."""

    def __init__(self, fenstergroesse):
        self.grenzen = pygame.Rect((0, 0), fenstergroesse)
        self.position = pygame.Vector2(self.grenzen.center)
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

    def zeichnen(self, fenster):
        fenster.blit(self.bild, self.rect)


class Schuss:
    """Fliegt geradlinig in die beim Abfeuern gewählte Richtung."""

    def __init__(self, position, richtung):
        self.position = pygame.Vector2(position)
        self.geschwindigkeit = pygame.Vector2(richtung).normalize() * SCHUSS_TEMPO
        self.bild = assets.bild("schuss", SCHUSS_GROESSE, SCHUSS_FARBE)
        self.rect = self.bild.get_rect(center=(round(self.position.x), round(self.position.y)))

    def aktualisieren(self, delta_time):
        self.position += self.geschwindigkeit * delta_time
        self.rect.center = (round(self.position.x), round(self.position.y))

    def im_fenster(self, grenzen):
        """Erst entfernen, wenn das gesamte Bild außerhalb liegt."""
        return self.rect.colliderect(grenzen)

    def zeichnen(self, fenster):
        fenster.blit(self.bild, self.rect)
