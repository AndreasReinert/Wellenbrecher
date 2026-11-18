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
        self.schaden = settings.SCHUSS_SCHADEN
        self.schuss_pause = SCHUSS_PAUSE
        self.schuss_anzahl = settings.MEHRFACHSCHUSS_START
        self.magnetradius = settings.KRISTALL_MAGNETRADIUS
        self.drohne = None
        self.upgrades_offen = 0
        self.level = 1
        self.erfahrung = 0
        self.erfahrung_bedarf = settings.ERFAHRUNG_STARTBEDARF
        self.unverwundbar_rest = 0.0
        self.wackel_rest = 0.0
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

    def erfahrung_sammeln(self, menge):
        """Restpunkte behalten; jede neue Schwelle auf ganze Punkte aufrunden."""
        self.erfahrung += menge
        while self.erfahrung >= self.erfahrung_bedarf:
            self.erfahrung -= self.erfahrung_bedarf
            self.level += 1
            self.upgrades_offen += 1
            assets.sound_spielen("levelup")
            self.erfahrung_bedarf = math.ceil(
                self.erfahrung_bedarf * settings.ERFAHRUNG_WACHSTUM
            )

    def bonuslevel_erhalten(self, anzahl):
        """Direkte Level samt Karten; vorhandene Erfahrung bleibt erhalten."""
        for _ in range(anzahl):
            self.level += 1
            self.upgrades_offen += 1
            assets.sound_spielen("levelup")
            self.erfahrung_bedarf = math.ceil(
                self.erfahrung_bedarf * settings.ERFAHRUNG_WACHSTUM)

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

    def upgrade_verfuegbar(self, upgrade):
        if upgrade["id"] == "drohne":
            return self.drohne is None
        if upgrade["id"] in ("drohne_schaden", "drohne_feuerrate"):
            return self.drohne is not None
        if upgrade["id"] == "mehrfach":
            return self.schuss_anzahl < upgrade["maximum"]
        if upgrade["id"] == "leben":
            return self.leben < upgrade["maximum"]
        return True

    def upgrade_anwenden(self, upgrade):
        if not self.upgrade_verfuegbar(upgrade):
            return False
        art, wert = upgrade["id"], upgrade["wert"]
        if art == "drohne":
            self.drohne = Drohne(self.position)
        elif art == "drohne_schaden":
            self.drohne.schaden += wert
        elif art == "drohne_feuerrate":
            self.drohne.schuss_pause *= wert
            self.drohne.schuss_wartezeit = min(self.drohne.schuss_wartezeit, self.drohne.schuss_pause)
        elif art == "schaden":
            self.schaden += wert
        elif art == "feuerrate":
            self.schuss_pause *= wert
            self.schuss_wartezeit = min(self.schuss_wartezeit, self.schuss_pause)
        elif art == "tempo":
            self.tempo *= wert
        elif art == "mehrfach":
            self.schuss_anzahl = min(upgrade["maximum"], self.schuss_anzahl + wert)
        elif art == "leben":
            self.leben = min(upgrade["maximum"], self.leben + wert)
        elif art == "magnet":
            self.magnetradius *= wert
        assets.sound_spielen("reparatur" if art == "leben" else "drohne_aktiv" if art == "drohne" else "upgrade")
        return True

    def feuern(self, mausposition):
        """Eine symmetrische Salve mit beim Abschuss gespeicherten Schadenswerten."""
        if self.schuss_wartezeit > 0:
            return []
        richtung = pygame.Vector2(mausposition) - self.position
        if richtung.length_squared() == 0:
            return []
        self.schuss_wartezeit = self.schuss_pause
        assets.sound_spielen("schuss")
        return [Schuss(self.position, richtung.rotate(
            (index - (self.schuss_anzahl - 1) / 2) * settings.MEHRFACHSCHUSS_WINKEL
        ), self.schaden) for index in range(self.schuss_anzahl)]

    def schaden_nehmen(self, schaden):
        """Nur ein Treffer pro Schutzzeit; Lebenspunkte fallen nicht unter null."""
        if self.leben <= 0 or self.unverwundbar_rest > 0:
            return False
        self.leben = max(0, self.leben - schaden)
        self.unverwundbar_rest = SPIELER_UNVERWUNDBAR_DAUER
        self.wackel_rest = settings.BILDSCHIRM_WACKEL_DAUER
        assets.sound_spielen("spieler_treffer")
        return True

    def zeichnen(self, fenster):
        if self.unverwundbar_rest > 0:
            vergangen = SPIELER_UNVERWUNDBAR_DAUER - self.unverwundbar_rest
            if int(vergangen / SPIELER_BLINK_PAUSE) % 2 == 0:
                return
        fenster.blit(self.bild, self.rect)


class Schuss:
    """Fliegt geradlinig in die beim Abfeuern gewählte Richtung."""

    def __init__(self, position, richtung, schaden=settings.SCHUSS_SCHADEN):
        self.schaden = schaden
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
        self.blitz_rest = 0.0
        # Eigene Kopie: transparente Pixel und das gecachte Original bleiben erhalten.
        self.weissbild = self.originalbild.copy()
        self.weissbild.fill((255, 255, 255, 0), special_flags=pygame.BLEND_RGBA_ADD)
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
        self.blitz_rest = max(0.0, self.blitz_rest - delta_time)
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
        assets.sound_spielen("gegner_schuss")
        return [GegnerSchuss(self.position, richtung.rotate(winkel), self.waffe)
                for winkel in self.waffe["winkel"]]

    def schaden_nehmen(self, schaden):
        self.leben = max(0, self.leben - schaden)
        self.blitz_rest = settings.GEGNER_BLITZ_DAUER
        assets.sound_spielen("treffer")

    def zeichnen(self, fenster):
        # Erst beim Zeichnen auswählen: ein neuer Treffer ist sofort sichtbar.
        bild = (pygame.transform.rotate(self.weissbild, self.winkel)
                if self.blitz_rest > 0 else self.bild)
        fenster.blit(bild, self.rect)


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


class Kristall:
    """Bleibt liegen, bis der Magnet greift; folgt danach bis zur Aufnahme."""

    def __init__(self, position):
        self.position = pygame.Vector2(position)
        self.radius = settings.KRISTALL_RADIUS
        self.angezogen = False
        self.bild = assets.bild(
            "kristall", self.radius * 2, settings.KRISTALL_FARBE
        )

    def aktualisieren(self, delta_time, spieler):
        """True bedeutet aufgenommen; der Aufrufer entfernt den Kristall."""
        richtung = spieler.position - self.position
        abstand = richtung.length()
        if abstand <= spieler.magnetradius:
            self.angezogen = True
        if self.angezogen and abstand > 0:
            weg = min(settings.KRISTALL_TEMPO * delta_time, abstand)
            self.position += richtung / abstand * weg
        if beruehren(self, spieler):
            assets.sound_spielen("kristall")
            spieler.erfahrung_sammeln(settings.KRISTALL_ERFAHRUNG)
            return True
        return False

    def zeichnen(self, fenster):
        fenster.blit(self.bild, self.bild.get_rect(
            center=(round(self.position.x), round(self.position.y))
        ))


class Partikel:
    """Ein leuchtender Punkt mit zeitunabhängiger exponentieller Bremsung."""

    def __init__(self, position, farbe):
        self.position = pygame.Vector2(position)
        self.alter = 0.0
        self.geschwindigkeit = pygame.Vector2(1, 0).rotate(
            random.uniform(0, 360)
        ) * random.uniform(settings.PARTIKEL_TEMPO_MIN, settings.PARTIKEL_TEMPO_MAX)
        radius = random.randint(settings.PARTIKEL_RADIUS_MIN, settings.PARTIKEL_RADIUS_MAX)
        aussenradius = math.ceil(radius * max(
            faktor for faktor, _ in settings.PARTIKEL_LEUCHTSCHICHTEN))
        self.bild = pygame.Surface((aussenradius * 2 + 1,) * 2, pygame.SRCALPHA)
        for faktor, alpha in settings.PARTIKEL_LEUCHTSCHICHTEN:
            pygame.draw.circle(self.bild, (*farbe, alpha),
                               (aussenradius, aussenradius), round(radius * faktor))

    def aktualisieren(self, delta_time):
        zeit = min(delta_time, max(0.0, settings.PARTIKEL_LEBENSDAUER - self.alter))
        bremsung = settings.PARTIKEL_BREMSUNG
        faktor = math.exp(-bremsung * zeit)
        wegzeit = (1 - faktor) / bremsung if bremsung > 0 else zeit
        self.position += self.geschwindigkeit * wegzeit
        self.geschwindigkeit *= faktor
        self.alter += delta_time
        return self.alter < settings.PARTIKEL_LEBENSDAUER

    def zeichnen(self, fenster):
        rest = max(0.0, 1 - self.alter / settings.PARTIKEL_LEBENSDAUER)
        self.bild.set_alpha(round(255 * rest))
        fenster.blit(self.bild, self.bild.get_rect(
            center=(round(self.position.x), round(self.position.y))))


class Partikelsystem:
    """Begrenzt Explosionen; bei Platzmangel weichen die ältesten Punkte."""

    def __init__(self):
        self.partikel = []

    def explosion(self, position, gegner_typ):
        farbe = GEGNER_TYPEN[gegner_typ]["ersatzfarbe"]
        anzahl = random.randint(settings.PARTIKEL_ANZAHL_MIN, settings.PARTIKEL_ANZAHL_MAX)
        self.partikel.extend(Partikel(position, farbe) for _ in range(anzahl))
        del self.partikel[:max(0, len(self.partikel) - settings.PARTIKEL_MAXIMUM)]

    def aktualisieren(self, delta_time):
        self.partikel[:] = [punkt for punkt in self.partikel
                           if punkt.aktualisieren(delta_time)]

    def zeichnen(self, fenster):
        for punkt in self.partikel:
            punkt.zeichnen(fenster)


class Boss(Gegner):
    """Mutterschiff: oben pendeln, Ring und Verstärkung abwechseln."""

    def __init__(self, fenstergroesse):
        super().__init__("boss", fenstergroesse)
        self.position = pygame.Vector2(fenstergroesse[0] / 2, settings.BOSS_Y)
        self.richtung = 1
        self.angriff = "ring"
        self.angriffszeit = settings.BOSS_RING_PAUSE
        self.hilfe_offen = False
        self.waffe = {"radius": settings.BOSS_SCHUSS_RADIUS,
                      "bildname": "schuss_boss", "farbe": settings.BOSS_FARBE}
        self.aktualisieren(0.0, self.position)

    def aktualisieren(self, delta_time, spielerposition):
        self.blitz_rest = max(0.0, self.blitz_rest - delta_time)
        self.angriffszeit -= delta_time
        self.position.x += self.richtung * self.tempo * delta_time
        links = self.radius + settings.BOSS_RAND
        rechts = settings.BREITE - links
        if self.position.x >= rechts:
            self.position.x, self.richtung = rechts, -1
        elif self.position.x <= links:
            self.position.x, self.richtung = links, 1
        self.rect = self.bild.get_rect(center=self.position)

    def feuern(self, spielerposition, grenzen):
        if self.angriffszeit > 0:
            return []
        if self.angriff == "ring":
            assets.sound_spielen("boss_ring")
            schuesse = []
            for index in range(settings.BOSS_RING_ANZAHL):
                richtung = pygame.Vector2(0, 1).rotate(360 * index / settings.BOSS_RING_ANZAHL)
                schuss = GegnerSchuss(self.position, richtung, self.waffe)
                schuss.geschwindigkeit = richtung * settings.BOSS_SCHUSS_TEMPO
                schuesse.append(schuss)
            self.angriff = "hilfe"
            self.angriffszeit = settings.BOSS_HILFE_PAUSE
            return schuesse
        self.hilfe_offen = True
        self.angriff = "ring"
        self.angriffszeit = settings.BOSS_RING_PAUSE
        return []

    def verstaerkung(self):
        if not self.hilfe_offen:
            return []
        self.hilfe_offen = False
        assets.sound_spielen("boss_hilfe")
        return [Gegner("jaeger", settings.FENSTERGROESSE)
                for _ in range(settings.BOSS_HILFE_ANZAHL)]


class Drohne:
    """Umläuft den Spieler und zielt vom eigenen Mittelpunkt auf den nächsten Gegner."""

    def __init__(self, spielerposition):
        self.radius = settings.DROHNE_RADIUS
        self.schaden = settings.DROHNE_STARTSCHADEN
        self.schuss_pause = settings.DROHNE_SCHUSS_PAUSE
        self.orbitwinkel = settings.DROHNE_STARTWINKEL
        self.schuss_wartezeit = 0.0
        self.position = pygame.Vector2(spielerposition) + pygame.Vector2(
            settings.DROHNE_ORBITRADIUS, 0).rotate(self.orbitwinkel)
        self.originalbild = assets.bild("drohne", self.radius * 2, settings.DROHNE_FARBE)
        self.bild = self.originalbild

    def aktualisieren(self, delta_time, spielerposition, gegner):
        self.orbitwinkel = (self.orbitwinkel + settings.DROHNE_WINKELTEMPO * delta_time) % 360
        self.position = pygame.Vector2(spielerposition) + pygame.Vector2(
            settings.DROHNE_ORBITRADIUS, 0).rotate(self.orbitwinkel)
        self.schuss_wartezeit = max(0.0, self.schuss_wartezeit - delta_time)
        lebende = [feind for feind in gegner if feind.leben > 0]
        if not lebende:
            return []
        ziel = min(lebende, key=lambda feind: self.position.distance_squared_to(feind.position))
        richtung = ziel.position - self.position
        if richtung.length_squared() == 0:
            return []
        winkel = math.degrees(math.atan2(-richtung.x, -richtung.y))
        self.bild = pygame.transform.rotate(self.originalbild, winkel)
        if self.schuss_wartezeit > 0:
            return []
        self.schuss_wartezeit = self.schuss_pause
        assets.sound_spielen("drohne_schuss")
        return [Schuss(self.position, richtung, self.schaden)]

    def zeichnen(self, fenster):
        fenster.blit(self.bild, self.bild.get_rect(
            center=(round(self.position.x), round(self.position.y))))
