"""Anzeigen und Zielhilfe für Wellenbrecher."""
import pygame
import settings


class Fadenkreuz:
    """Einmal gezeichnete Zielhilfe aus zwei Kreisen und vier Linien."""

    def __init__(self):
        aussen = settings.FADENKREUZ_LINIENSTART + settings.FADENKREUZ_LINIENLAENGE
        rand = max(breite for breite, _ in settings.FADENKREUZ_SCHICHTEN)
        mitte = aussen + rand
        groesse = (mitte * 2 + 1, mitte * 2 + 1)
        self.bild = pygame.Surface(groesse, pygame.SRCALPHA)
        for breite, deckkraft in settings.FADENKREUZ_SCHICHTEN:
            schicht = pygame.Surface(groesse, pygame.SRCALPHA)
            self._formen(schicht, mitte,
                         (*settings.FADENKREUZ_LEUCHTFARBE, deckkraft), breite)
            self.bild.blit(schicht, (0, 0))
        kern = pygame.Surface(groesse, pygame.SRCALPHA)
        self._formen(kern, mitte, settings.FADENKREUZ_FARBE,
                     settings.FADENKREUZ_KERNBREITE)
        self.bild.blit(kern, (0, 0))

    @staticmethod
    def _formen(flaeche, mitte, farbe, breite):
        for radius in settings.FADENKREUZ_RADIEN:
            pygame.draw.circle(flaeche, farbe, (mitte, mitte), radius, breite)
        for x, y in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            innen = settings.FADENKREUZ_LINIENSTART
            aussen = innen + settings.FADENKREUZ_LINIENLAENGE
            pygame.draw.line(flaeche, farbe,
                             (mitte + x * innen, mitte + y * innen),
                             (mitte + x * aussen, mitte + y * aussen), breite)

    def zeichnen(self, fenster, mausposition):
        fenster.blit(self.bild, self.bild.get_rect(center=mausposition))
