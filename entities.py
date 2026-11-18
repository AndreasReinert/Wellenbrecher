"""Spielobjekte für Wellenbrecher."""
import math

import pygame

import assets
from settings import SPIELER_FARBE, SPIELER_GROESSE, SPIELER_TEMPO


class Spieler:
    """WASD bewegt das Schiff; das Originalbild zeigt mit seiner Spitze nach oben."""

    def __init__(self, fenstergroesse):
        self.grenzen = pygame.Rect((0, 0), fenstergroesse)
        self.position = pygame.Vector2(self.grenzen.center)
        self.tempo = SPIELER_TEMPO
        self.originalbild = assets.bild(
            "spieler", SPIELER_GROESSE, SPIELER_FARBE
        )
        self.bild = self.originalbild
        self.rect = self.bild.get_rect(center=self.grenzen.center)
        self.winkel = 0.0
        # Halbe Bilddiagonale: Auch gedrehte Bildecken bleiben im Fenster.
        self.rand = math.ceil(math.hypot(*self.originalbild.get_size()) / 2)

    def aktualisieren(self, delta_time, tasten, mausposition):
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

    def zeichnen(self, fenster):
        fenster.blit(self.bild, self.rect)
