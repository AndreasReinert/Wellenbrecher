"""Startpunkt: python main.py (benötigt pygame-ce)."""
import random

import pygame
import settings

from assets import hintergrund
from entities import Spieler, Gegner, Kristall, Partikelsystem, beruehren
from ui import Fadenkreuz, Anzeigen, UpgradeKarten
from settings import (
    FENSTERGROESSE, FPS, TITEL,
    WELLEN_STARTANZAHL, WELLEN_ZUWACHS, WELLEN_SPAWN_PAUSE,
    WELLEN_GRUPPENGROESSE,
    WELLEN_PAUSE, WELLEN_TEXT_DAUER, GEGNER_AB_WELLE,
    SCHUSS_SCHADEN, GEGNER_KONTAKTSCHADEN, GEGNER_SCHUSS_SCHADEN,
)


def kollisionen_pruefen(spieler, schuesse, gegner, gegnerschuesse, kristalle, partikel):
    """Listen vor Ort bereinigen und die Anzahl neu besiegter Gegner liefern."""
    verbleibende_schuesse = []
    besiegt = 0
    for schuss in schuesse:
        for feind in gegner:
            if feind.leben > 0 and beruehren(schuss, feind):
                feind.schaden_nehmen(schuss.schaden)
                if feind.leben == 0:
                    besiegt += 1
                    kristalle.append(Kristall(feind.position))
                    partikel.explosion(feind.position, feind.typ)
                # Jeder Schuss trifft höchstens einen Gegner und verschwindet.
                break
        else:
            verbleibende_schuesse.append(schuss)
    schuesse[:] = verbleibende_schuesse
    gegner[:] = [feind for feind in gegner if feind.leben > 0]

    for feind in gegner:
        if beruehren(feind, spieler):
            spieler.schaden_nehmen(GEGNER_KONTAKTSCHADEN)
    verbleibend = []
    for schuss in gegnerschuesse:
        if beruehren(schuss, spieler):
            spieler.schaden_nehmen(GEGNER_SCHUSS_SCHADEN)
        else:
            verbleibend.append(schuss)
    gegnerschuesse[:] = verbleibend
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
                # Eine Gruppe gleichzeitig; eine Restgruppe bleibt kleiner.
                for _ in range(min(WELLEN_GRUPPENGROESSE, len(self.wartend))):
                    feind = Gegner(self.wartend.pop(), FENSTERGROESSE)
                    feind.aktualisieren(0.0, spielerposition)
                    gegner.append(feind)
                self.spawn_zeit = WELLEN_SPAWN_PAUSE

    def abschluss_pruefen(self, gegner):
        if not self.wartend and not gegner and self.pause is None:
            self.pause = WELLEN_PAUSE


def neues_spiel():
    """Alle veränderlichen Rundendaten frisch anlegen, Bildcache behalten."""
    return Spieler(FENSTERGROESSE), [], [], [], [], Partikelsystem(), Wellen(), 0, "spiel"


def main():
    pygame.init()
    maus_war_sichtbar = pygame.mouse.get_visible()
    try:
        fenster = pygame.display.set_mode(FENSTERGROESSE)
        pygame.display.set_caption(TITEL)
        pygame.mouse.set_visible(False)
        fadenkreuz = Fadenkreuz()
        anzeigen = Anzeigen()
        upgrade_karten = UpgradeKarten()
        uhr = pygame.time.Clock()
        hintergrundbild = hintergrund(FENSTERGROESSE)
        spieler, schuesse, gegner, gegnerschuesse, kristalle, partikel, wellen, besiegte_gegner, zustand = neues_spiel()
        welt = pygame.Surface(FENSTERGROESSE)
        versatz = (0, 0)
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
                    spieler, schuesse, gegner, gegnerschuesse, kristalle, partikel, wellen, besiegte_gegner, zustand = neues_spiel()
                    versatz = (0, 0)
                    upgrade_karten.leeren()
                    # Keine Zeit der alten Runde auf die neue Runde übertragen.
                    delta_time = 0.0

                elif (ereignis.type == pygame.MOUSEBUTTONDOWN
                      and ereignis.button == 1 and zustand == "upgrade"):
                    upgrade = upgrade_karten.auswahl(ereignis.pos)
                    if upgrade is not None and spieler.upgrade_anwenden(upgrade):
                        spieler.upgrades_offen -= 1
                        if spieler.upgrades_offen > 0:
                            upgrade_karten.oeffnen(spieler)
                        else:
                            upgrade_karten.leeren()
                            zustand = "spiel"
                        # Auswahlklick nicht als Schuss verwenden, keine Pausenzeit übernehmen.
                        delta_time = 0.0
                        spieler.schuss_wartezeit = spieler.schuss_pause
                        break

            if not laeuft:
                break

            mausposition = pygame.mouse.get_pos()
            if zustand != "upgrade":
                # Auch beim letzten Leben läuft das kurze Wackeln noch aus.
                spieler.wackel_rest = max(0.0, spieler.wackel_rest - delta_time)
            if zustand == "spiel":
                partikel.aktualisieren(delta_time)
                spieler.aktualisieren(
                    delta_time, pygame.key.get_pressed(), mausposition
                )
                for feind in gegner:
                    feind.aktualisieren(delta_time, spieler.position)
                wellen.aktualisieren(delta_time, gegner, spieler.position)

                for schuss in gegnerschuesse:
                    schuss.aktualisieren(delta_time)
                gegnerschuesse = [
                    schuss for schuss in gegnerschuesse
                    if not schuss.abgelaufen() and schuss.im_fenster(grenzen)
                ]
                for feind in gegner:
                    gegnerschuesse.extend(feind.feuern(spieler.position, grenzen))

                for schuss in schuesse:
                    schuss.aktualisieren(delta_time)
                schuesse = [
                    schuss for schuss in schuesse
                    if not schuss.abgelaufen() and schuss.im_fenster(grenzen)
                ]

                if pygame.mouse.get_pressed()[0]:
                    schuesse.extend(spieler.feuern(mausposition))

                besiegte_gegner += kollisionen_pruefen(spieler, schuesse, gegner, gegnerschuesse, kristalle, partikel)
                if spieler.leben > 0:
                    kristalle[:] = [kristall for kristall in kristalle
                                   if not kristall.aktualisieren(delta_time, spieler)]
                wellen.abschluss_pruefen(gegner)
                if spieler.leben <= 0:
                    zustand = "game_over"
                elif spieler.upgrades_offen > 0:
                    zustand = "upgrade"
                    upgrade_karten.oeffnen(spieler)
            # Werte zum Testen im Fenstertitel, ohne zusätzliche Spielgrafik.
            pygame.display.set_caption(
                f"{TITEL} | Welle: {wellen.nummer} | Besiegt: {besiegte_gegner}"
            )

            if zustand != "upgrade":
                if spieler.wackel_rest > 0:
                    staerke = (settings.BILDSCHIRM_WACKEL_STAERKE
                               * spieler.wackel_rest / settings.BILDSCHIRM_WACKEL_DAUER)
                    versatz = (round(random.uniform(-staerke, staerke)),
                               round(random.uniform(-staerke, staerke)))
                else:
                    versatz = (0, 0)
            # Nur die Welt wackelt; Anzeigen und Mausziel bleiben ruhig.
            welt.blit(hintergrundbild, (0, 0))
            for kristall in kristalle:
                kristall.zeichnen(welt)
            for feind in gegner:
                feind.zeichnen(welt)
            for schuss in schuesse:
                schuss.zeichnen(welt)
            for schuss in gegnerschuesse:
                schuss.zeichnen(welt)
            partikel.zeichnen(welt)
            spieler.zeichnen(welt)
            fenster.fill(settings.DUNKELBLAU)
            fenster.blit(welt, versatz)
            anzeigen.spielstand(fenster, spieler.leben, wellen.nummer, besiegte_gegner)
            if zustand == "game_over":
                anzeigen.game_over(fenster, wellen.nummer, besiegte_gegner)
            elif zustand == "spiel" and wellen.anzeige_zeit > 0:
                anzeigen.welle(fenster, wellen.nummer)
            anzeigen.erfahrung(fenster, spieler)
            if zustand == "upgrade":
                upgrade_karten.zeichnen(fenster, mausposition)
            if pygame.mouse.get_focused():
                fadenkreuz.zeichnen(fenster, mausposition)
            pygame.display.flip()
    finally:
        pygame.mouse.set_visible(maus_war_sichtbar)
        pygame.quit()


if __name__ == "__main__":
    main()
