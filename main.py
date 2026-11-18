"""Startpunkt: python main.py (benötigt pygame-ce)."""
import pygame

from assets import hintergrund
from entities import Spieler
from ui import Fadenkreuz
from settings import FENSTERGROESSE, FPS, TITEL


def main():
    pygame.init()
    maus_war_sichtbar = pygame.mouse.get_visible()
    try:
        fenster = pygame.display.set_mode(FENSTERGROESSE)
        pygame.display.set_caption(TITEL)
        pygame.mouse.set_visible(False)
        fadenkreuz = Fadenkreuz()
        uhr = pygame.time.Clock()
        hintergrundbild = hintergrund(FENSTERGROESSE)
        spieler = Spieler(FENSTERGROESSE)
        schuesse = []
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

            if not laeuft:
                break

            mausposition = pygame.mouse.get_pos()
            spieler.aktualisieren(
                delta_time, pygame.key.get_pressed(), mausposition
            )
            for schuss in schuesse:
                schuss.aktualisieren(delta_time)
            schuesse = [schuss for schuss in schuesse if schuss.im_fenster(grenzen)]

            if pygame.mouse.get_pressed()[0]:
                schuss = spieler.feuern(mausposition)
                if schuss is not None:
                    schuesse.append(schuss)

            fenster.blit(hintergrundbild, (0, 0))
            for schuss in schuesse:
                schuss.zeichnen(fenster)
            spieler.zeichnen(fenster)
            if pygame.mouse.get_focused():
                fadenkreuz.zeichnen(fenster, mausposition)
            pygame.display.flip()
    finally:
        pygame.mouse.set_visible(maus_war_sichtbar)
        pygame.quit()


if __name__ == "__main__":
    main()
