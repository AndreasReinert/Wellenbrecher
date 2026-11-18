"""Startpunkt: python main.py (benötigt pygame)."""
import pygame

from assets import hintergrund
from entities import Spieler
from settings import FENSTERGROESSE, FPS, TITEL


def main():
    pygame.init()
    try:
        fenster = pygame.display.set_mode(FENSTERGROESSE)
        pygame.display.set_caption(TITEL)
        uhr = pygame.time.Clock()
        hintergrundbild = hintergrund(FENSTERGROESSE)
        spieler = Spieler(FENSTERGROESSE)
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

            spieler.aktualisieren(
                delta_time, pygame.key.get_pressed(), pygame.mouse.get_pos()
            )
            fenster.blit(hintergrundbild, (0, 0))
            spieler.zeichnen(fenster)
            pygame.display.flip()
    finally:
        pygame.quit()


if __name__ == "__main__":
    main()
