"""Startpunkt: python main.py (benötigt pygame-ce)."""
import random

import pygame

from assets import hintergrund
from entities import Spieler, Gegner, beruehren
from ui import Fadenkreuz, Anzeigen
from settings import (
    FENSTERGROESSE, FPS, TITEL,
    WELLEN_STARTANZAHL, WELLEN_ZUWACHS, WELLEN_SPAWN_PAUSE,
    WELLEN_PAUSE, WELLEN_TEXT_DAUER, GEGNER_AB_WELLE,
    SCHUSS_SCHADEN, GEGNER_KONTAKTSCHADEN,
)


def kollisionen_pruefen(spieler, schuesse, gegner):
    """Listen vor Ort bereinigen und die Anzahl neu besiegter Gegner liefern."""
    verbleibende_schuesse = []
    besiegt = 0
    for schuss in schuesse:
        for feind in gegner:
            if feind.leben > 0 and beruehren(schuss, feind):
                feind.leben = max(0, feind.leben - SCHUSS_SCHADEN)
                if feind.leben == 0:
                    besiegt += 1
                # Jeder Schuss trifft höchstens einen Gegner und verschwindet.
                break
        else:
            verbleibende_schuesse.append(schuss)
    schuesse[:] = verbleibende_schuesse
    gegner[:] = [feind for feind in gegner if feind.leben > 0]

    for feind in gegner:
        if beruehren(feind, spieler):
            spieler.schaden_nehmen(GEGNER_KONTAKTSCHADEN)
    return besiegt


class Wellen:
    """Erst nach allen Spawns und besiegten Gegnern beginnt die Wellenpause."""

    def __init__(self):
        self.nummer = 0
        self.pause = None
        self.starten()

    def starten(self):
        self.nummer += 1
        anzahl = WELLEN_STARTANZAHL + (self.nummer - 1) * WELLEN_ZUWACHS
        typen = [typ for typ, ab in GEGNER_AB_WELLE.items() if self.nummer >= ab]
        # Gleichmäßig mischen: freigeschaltete Typen sind sicher vertreten.
        self.wartend = [typen[index % len(typen)] for index in range(anzahl)]
        random.shuffle(self.wartend)
        self.spawn_zeit = 0.0
        self.anzeige_zeit = WELLEN_TEXT_DAUER
        self.pause = None

    def aktualisieren(self, delta_time, gegner, spielerposition):
        self.anzeige_zeit = max(0.0, self.anzeige_zeit - delta_time)
        if self.pause is not None:
            self.pause -= delta_time
            if self.pause <= 0:
                self.starten()
            return
        if self.wartend:
            self.spawn_zeit -= delta_time
            if self.spawn_zeit <= 0:
                feind = Gegner(self.wartend.pop(), FENSTERGROESSE)
                feind.aktualisieren(0.0, spielerposition)
                gegner.append(feind)
                self.spawn_zeit = WELLEN_SPAWN_PAUSE

    def abschluss_pruefen(self, gegner):
        if not self.wartend and not gegner and self.pause is None:
            self.pause = WELLEN_PAUSE


def neues_spiel():
    """Alle veränderlichen Rundendaten frisch anlegen, Bildcache behalten."""
    return Spieler(FENSTERGROESSE), [], [], Wellen(), 0, "spiel"


def main():
    pygame.init()
    maus_war_sichtbar = pygame.mouse.get_visible()
    try:
        fenster = pygame.display.set_mode(FENSTERGROESSE)
        pygame.display.set_caption(TITEL)
        pygame.mouse.set_visible(False)
        fadenkreuz = Fadenkreuz()
        anzeigen = Anzeigen()
        uhr = pygame.time.Clock()
        hintergrundbild = hintergrund(FENSTERGROESSE)
        spieler, schuesse, gegner, wellen, besiegte_gegner, zustand = neues_spiel()
        grenzen = fenster.get_rect()
        laeuft = True

        while laeuft:
            # Millisekunden in Sekunden umrechnen; begrenzt auf maximal 60 FPS.
            delta_time = uhr.tick(FPS) / 1000.0

            for ereignis in pygame.event.get():
                if ereignis.type == pygame.QUIT:
                    laeuft = False
                elif ereignis.type == pygame.KEYDOWN and ereignis.key == pygame.K_ESCAPE:
                    laeuft = False
                elif (ereignis.type == pygame.KEYDOWN
                      and ereignis.key == pygame.K_r and zustand == "game_over"):
                    spieler, schuesse, gegner, wellen, besiegte_gegner, zustand = neues_spiel()
                    # Keine Zeit der alten Runde auf die neue Runde übertragen.
                    delta_time = 0.0

            if not laeuft:
                break

            mausposition = pygame.mouse.get_pos()
            if zustand == "spiel":
                spieler.aktualisieren(
                    delta_time, pygame.key.get_pressed(), mausposition
                )
                for feind in gegner:
                    feind.aktualisieren(delta_time, spieler.position)
                wellen.aktualisieren(delta_time, gegner, spieler.position)

                for schuss in schuesse:
                    schuss.aktualisieren(delta_time)
                schuesse = [
                    schuss for schuss in schuesse
                    if not schuss.abgelaufen() and schuss.im_fenster(grenzen)
                ]

                if pygame.mouse.get_pressed()[0]:
                    schuss = spieler.feuern(mausposition)
                    if schuss is not None:
                        schuesse.append(schuss)

                besiegte_gegner += kollisionen_pruefen(spieler, schuesse, gegner)
                wellen.abschluss_pruefen(gegner)
                if spieler.leben <= 0:
                    zustand = "game_over"
            # Werte zum Testen im Fenstertitel, ohne zusätzliche Spielgrafik.
            pygame.display.set_caption(
                f"{TITEL} | Welle: {wellen.nummer} | Leben: {spieler.leben} | Besiegt: {besiegte_gegner}"
            )

            fenster.blit(hintergrundbild, (0, 0))
            for feind in gegner:
                feind.zeichnen(fenster)
            for schuss in schuesse:
                schuss.zeichnen(fenster)
            spieler.zeichnen(fenster)
            anzeigen.spielstand(fenster, spieler.leben, wellen.nummer, besiegte_gegner)
            if zustand == "game_over":
                anzeigen.game_over(fenster, wellen.nummer, besiegte_gegner)
            elif wellen.anzeige_zeit > 0:
                anzeigen.welle(fenster, wellen.nummer)
            if pygame.mouse.get_focused():
                fadenkreuz.zeichnen(fenster, mausposition)
            pygame.display.flip()
    finally:
        pygame.mouse.set_visible(maus_war_sichtbar)
        pygame.quit()


if __name__ == "__main__":
    main()
