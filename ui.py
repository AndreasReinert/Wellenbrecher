"""Anzeigen und Zielhilfe für Wellenbrecher."""
import random

import assets
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


    def erfahrung(self, fenster, spieler):
        """Schmale Fortschrittsleiste am unteren Rand mit aktueller Levelzahl."""
        rand = settings.UI_RAND
        hoehe = settings.ERFAHRUNGSLEISTE_HOEHE
        rahmen = pygame.Rect(rand, fenster.get_height() - rand - hoehe,
                             fenster.get_width() - rand * 2, hoehe)
        pygame.draw.rect(fenster, settings.LEISTE_HINTERGRUND, rahmen)
        fuellung = rahmen.copy()
        fuellung.width = round(rahmen.width * min(
            1.0, spieler.erfahrung / spieler.erfahrung_bedarf))
        pygame.draw.rect(fenster, settings.ERFAHRUNGSLEISTE_FARBE, fuellung)
        text = self.schrift.render(f"Level {spieler.level}", True, settings.UI_TEXTFARBE)
        fenster.blit(text, text.get_rect(
            bottomleft=(rand, rahmen.top - settings.ERFAHRUNGSLEISTE_TEXTABSTAND)))


class UpgradeKarten:
    """Zufällige, verschiedene Angebote; Trefferflächen folgen der Anhebung."""

    def __init__(self):
        self.karten = []
        self.titel = pygame.font.Font(None, settings.UPGRADE_TITELGROESSE)
        self.name = pygame.font.Font(None, settings.UPGRADE_NAMEGROESSE)
        self.text = pygame.font.Font(None, settings.UPGRADE_TEXTGROESSE)
        self.schleier = pygame.Surface(settings.FENSTERGROESSE, pygame.SRCALPHA)
        self.schleier.fill((0, 0, 0, settings.GAME_OVER_ABDUNKLUNG))

    def leeren(self):
        self.karten = []

    def oeffnen(self, spieler):
        verfuegbar = [u for u in settings.UPGRADES if spieler.upgrade_verfuegbar(u)]
        self.karten = random.sample(verfuegbar, min(settings.UPGRADE_KARTENANZAHL, len(verfuegbar)))

    def rechtecke(self, mausposition):
        breite, hoehe = settings.UPGRADE_KARTENGROESSE
        abstand = settings.UPGRADE_KARTENABSTAND
        gesamt = len(self.karten) * breite + max(0, len(self.karten) - 1) * abstand
        links = (settings.BREITE - gesamt) // 2
        oben = (settings.HOEHE - hoehe) // 2
        ergebnis = []
        for index in range(len(self.karten)):
            rect = pygame.Rect(links + index * (breite + abstand), oben, breite, hoehe)
            # Erweiterte Hoverzone verhindert Flackern am angehobenen Rand.
            zone = rect.union(rect.move(0, -settings.UPGRADE_ANHEBUNG))
            aktiv = zone.collidepoint(mausposition)
            if aktiv:
                rect.y -= settings.UPGRADE_ANHEBUNG
            ergebnis.append((rect, aktiv))
        return ergebnis

    def auswahl(self, mausposition):
        for upgrade, (rect, _) in zip(self.karten, self.rechtecke(mausposition)):
            if rect.collidepoint(mausposition):
                return upgrade
        return None

    def zeichnen(self, fenster, mausposition):
        fenster.blit(self.schleier, (0, 0))
        titel = self.titel.render(getattr(self, "ueberschrift", "Level aufgestiegen!"), True, settings.UI_TEXTFARBE)
        fenster.blit(titel, titel.get_rect(center=(settings.BREITE // 2, settings.UPGRADE_TITEL_Y)))
        for upgrade, (rect, aktiv) in zip(self.karten, self.rechtecke(mausposition)):
            if aktiv:
                leuchten = pygame.Surface(settings.FENSTERGROESSE, pygame.SRCALPHA)
                for rand, alpha in settings.UPGRADE_LEUCHTSCHICHTEN:
                    pygame.draw.rect(leuchten, (*settings.UPGRADE_LEUCHTFARBE, alpha),
                                     rect.inflate(rand * 2, rand * 2), border_radius=settings.UPGRADE_ECKRADIUS)
                fenster.blit(leuchten, (0, 0))
            pygame.draw.rect(fenster, settings.UPGRADE_AKTIVFARBE if aktiv else settings.UPGRADE_FARBE,
                             rect, border_radius=settings.UPGRADE_ECKRADIUS)
            pygame.draw.rect(fenster, settings.UPGRADE_LEUCHTFARBE if aktiv else settings.LEISTE_HINTERGRUND,
                             rect, settings.UPGRADE_RAHMEN, border_radius=settings.UPGRADE_ECKRADIUS)
            icon = assets.bild(upgrade["icon"], settings.UPGRADE_ICON_GROESSE, settings.UPGRADE_ICONFARBE)
            fenster.blit(icon, icon.get_rect(center=(rect.centerx, rect.top + settings.UPGRADE_ICON_Y)))
            for schrift, inhalt, y in ((self.name, upgrade["name"], settings.UPGRADE_NAME_Y),
                                      (self.text, upgrade["wirkung"], settings.UPGRADE_WIRKUNG_Y)):
                text = schrift.render(inhalt, True, settings.UI_TEXTFARBE)
                fenster.blit(text, text.get_rect(center=(rect.centerx, rect.top + y)))
        hinweis = self.text.render(getattr(self, "hinweis", "Wähle ein Upgrade mit Linksklick – die Spielwelt pausiert."), True, settings.UI_TEXTFARBE)
        fenster.blit(hinweis, hinweis.get_rect(center=(settings.BREITE // 2, settings.UPGRADE_HINWEIS_Y)))


class Startmenue:
    """Startseite und kurze Steuerungshilfe ohne laufende Spielwelt."""

    def __init__(self):
        self.hintergrund = assets.titelbild(settings.FENSTERGROESSE)
        self.titel = pygame.font.Font(None, settings.MENUE_TITEL_GROESSE)
        self.schrift = pygame.font.Font(None, settings.MENUE_TEXT_GROESSE)
        self.knoepfe = []
        for index, text in enumerate(("Spielen", "Steuerung", "Beenden")):
            rect = pygame.Rect((0, 0), settings.MENUE_KNOPF_GROESSE)
            rect.center = (settings.BREITE // 2,
                           settings.MENUE_KNOPF_START_Y + index * settings.MENUE_KNOPF_ABSTAND)
            self.knoepfe.append((text, rect))
        self.zurueck = pygame.Rect((0, 0), settings.MENUE_KNOPF_GROESSE)
        self.zurueck.center = (settings.BREITE // 2, settings.MENUE_ZURUECK_Y)
        self.schleier = pygame.Surface(settings.FENSTERGROESSE, pygame.SRCALPHA)
        self.schleier.fill((*settings.DUNKELBLAU, settings.MENUE_ABDUNKLUNG))

    def auswahl(self, position, zustand):
        knoepfe = [("Zurück", self.zurueck)] if zustand == "steuerung" else self.knoepfe
        for text, rect in knoepfe:
            if rect.collidepoint(position):
                return text
        return None

    def _text(self, fenster, text, y, schrift):
        bild = schrift.render(text, True, settings.MENUE_TEXT_FARBE)
        fenster.blit(bild, bild.get_rect(center=(settings.BREITE // 2, y)))

    def zeichnen(self, fenster, position, zustand):
        fenster.blit(self.hintergrund, (0, 0))
        if zustand == "steuerung":
            fenster.blit(self.schleier, (0, 0))
        self._text(fenster, "WELLENBRECHER", settings.MENUE_TITEL_Y, self.titel)
        if zustand == "steuerung":
            zeilen = ("WASD – Schiff bewegen", "Maus – Zielen  |  Linke Maustaste halten – Schießen",
                      "Kristalle sammeln – Level aufsteigen und Upgrade wählen",
                      "R – Neustart nach Game Over  |  Esc – Spiel beenden")
            for index, text in enumerate(zeilen):
                self._text(fenster, text, settings.MENUE_HILFE_Y + index * settings.MENUE_HILFE_ABSTAND, self.schrift)
            knoepfe = [("Zurück", self.zurueck)]
        else:
            knoepfe = self.knoepfe
        for text, rect in knoepfe:
            aktiv = rect.collidepoint(position)
            farbe = settings.MENUE_HOVER_FARBE if aktiv else settings.MENUE_FARBE
            pygame.draw.rect(fenster, farbe, rect, border_radius=settings.MENUE_RADIUS)
            pygame.draw.rect(fenster, settings.MENUE_AKZENT if aktiv else settings.MENUE_TEXT_FARBE,
                             rect, settings.MENUE_RAND, border_radius=settings.MENUE_RADIUS)
            self._text(fenster, text, rect.centery, self.schrift)


class ModusKarten(UpgradeKarten):
    """Moduskarten mit unabhängigen, dauerhaft gespeicherten Endless-Rekorden."""

    def __init__(self, rekord=None):
        super().__init__()
        self.rekord = rekord if rekord is not None else {"besiegte_gegner": 0, "geschaffte_wellen": 0}
        self.karten = settings.MODUS_KARTEN
        self.ueberschrift = "Wähle deinen Spielmodus"
        self.hinweis = "Linksklick auf eine Karte startet eine neue Runde."

    def zeichnen(self, fenster, mausposition):
        super().zeichnen(fenster, mausposition)
        for karte, (rect, aktiv) in zip(self.karten, self.rechtecke(mausposition)):
            if karte["id"] != "endless":
                continue
            zeilen = (f"Rekord: {self.rekord['besiegte_gegner']} besiegte Gegner",
                      f"Geschaffte Wellen: {self.rekord['geschaffte_wellen']}")
            for index, inhalt in enumerate(zeilen):
                text = self.text.render(inhalt, True, settings.MENUE_AKZENT)
                fenster.blit(text, text.get_rect(center=(rect.centerx,
                    rect.top + settings.HIGHSCORE_TEXT_Y + index * settings.HIGHSCORE_ZEILENABSTAND)))


def bossleiste(fenster, boss):
    schrift = pygame.font.Font(None, settings.UPGRADE_NAMEGROESSE)
    text = schrift.render("Mutterschiff", True, settings.UI_TEXTFARBE)
    fenster.blit(text, text.get_rect(center=(settings.BREITE // 2, settings.BOSS_NAME_Y)))
    rect = pygame.Rect(0, settings.BOSS_LEISTE_Y, settings.BOSS_LEISTE_BREITE, settings.BOSS_LEISTE_HOEHE)
    rect.centerx = settings.BREITE // 2
    pygame.draw.rect(fenster, settings.LEISTE_HINTERGRUND, rect)
    fuellung = rect.copy()
    fuellung.width = round(rect.width * max(0, boss.leben) / settings.BOSS_LEBEN)
    pygame.draw.rect(fenster, settings.BOSS_FARBE, fuellung)


def sieganzeige(fenster, spielzeit, besiegt):
    schleier = pygame.Surface(settings.FENSTERGROESSE, pygame.SRCALPHA)
    schleier.fill((0, 0, 0, settings.GAME_OVER_ABDUNKLUNG))
    fenster.blit(schleier, (0, 0))
    minuten, sekunden = divmod(int(spielzeit), 60)
    texte = ("SIEG!", f"Spielzeit: {minuten:02d}:{sekunden:02d}",
             f"Besiegte Gegner: {besiegt}", "R = neue Runde")
    for index, (text, y) in enumerate(zip(texte, settings.SIEG_ZEILEN_Y)):
        schrift = pygame.font.Font(None, settings.MENUE_TITEL_GROESSE if index == 0 else settings.UPGRADE_NAMEGROESSE)
        bild = schrift.render(text, True, settings.UI_TEXTFARBE)
        fenster.blit(bild, bild.get_rect(center=(settings.BREITE // 2, y)))
