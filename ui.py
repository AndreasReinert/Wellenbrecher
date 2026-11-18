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


class Anzeigen:
    """Lebensleiste, Wellenhinweis und Spielende ohne erneutes Laden."""

    def __init__(self):
        self.schrift = pygame.font.Font(None, settings.UI_SCHRIFTGROESSE)
        self.wellenschrift = pygame.font.Font(None, settings.WELLEN_SCHRIFTGROESSE)
        self.endschrift = pygame.font.Font(None, settings.GAME_OVER_SCHRIFTGROESSE)
        self.schleier = pygame.Surface(settings.FENSTERGROESSE, pygame.SRCALPHA)
        self.schleier.fill((0, 0, 0, settings.GAME_OVER_ABDUNKLUNG))

    def lebensleiste(self, fenster, leben):
        rand = settings.UI_RAND
        text = self.schrift.render(
            "Leben", True, settings.UI_TEXTFARBE
        )
        fenster.blit(text, (rand, rand))
        rahmen = pygame.Rect((rand, rand + text.get_height() +
                              settings.LEISTE_TEXT_ABSTAND), settings.LEISTE_GROESSE)
        pygame.draw.rect(fenster, settings.LEISTE_HINTERGRUND, rahmen)
        fuellung = rahmen.copy()
        fuellung.width = round(rahmen.width * max(0, leben) / settings.SPIELER_STARTLEBEN)
        pygame.draw.rect(fenster, settings.LEISTE_FARBE, fuellung)
        pygame.draw.rect(fenster, settings.UI_TEXTFARBE, rahmen, settings.LEISTE_RAHMEN)

    def spielstand(self, fenster, leben, welle, besiegt):
        self.lebensleiste(fenster, leben)
        y = (settings.UI_RAND + self.schrift.get_height()
             + settings.LEISTE_TEXT_ABSTAND + settings.LEISTE_GROESSE[1]
             + settings.UI_ZEILENABSTAND)
        for inhalt in (f"Welle: {welle}", f"Besiegte Gegner: {besiegt}"):
            text = self.schrift.render(inhalt, True, settings.UI_TEXTFARBE)
            fenster.blit(text, (settings.UI_RAND, y))
            y += self.schrift.get_linesize() + settings.UI_ZEILENABSTAND

    def welle(self, fenster, nummer):
        text = self.wellenschrift.render(f"Welle {nummer}", True, settings.UI_TEXTFARBE)
        fenster.blit(text, text.get_rect(center=fenster.get_rect().center))

    def game_over(self, fenster, welle, besiegt):
        fenster.blit(self.schleier, (0, 0))
        x, y = fenster.get_rect().center
        zeilen = (
            ("GAME OVER", self.endschrift, settings.GAME_OVER_FARBE, -settings.GAME_OVER_ABSTAND),
            (f"Welle {welle}  |  Besiegt: {besiegt}", self.schrift, settings.UI_TEXTFARBE, 0),
            ("R = Restart", self.schrift, settings.UI_TEXTFARBE, settings.GAME_OVER_ABSTAND),
            ("Esc oder X zum Beenden", self.schrift, settings.UI_TEXTFARBE, settings.GAME_OVER_ENDE_VERSATZ),
        )
        for inhalt, schrift, farbe, versatz in zeilen:
            text = schrift.render(inhalt, True, farbe)
            fenster.blit(text, text.get_rect(center=(x, y + versatz)))
        # Auch beim Spielende bleibt der leere Lebensbalken sichtbar.
        self.spielstand(fenster, 0, welle, besiegt)
