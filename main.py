"""Startpunkt: python main.py (benötigt pygame)."""
import pygame

from assets import hintergrund
from settings import FENSTERGROESSE, FPS, TITEL


def main():
    pygame.init()
    try:
        fenster = pygame.display.set_mode(FENSTERGROESSE)
        pygame.display.set_caption(TITEL)
        uhr = pygame.time.Clock()
        hintergrundbild = hintergrund(FENSTERGROESSE)
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

            # Spiellogik hier ergänzen, z. B. x += tempo * delta_time.
            # delta_time ist die tatsächlich vergangene Zeit in Sekunden.
            fenster.blit(hintergrundbild, (0, 0))
            pygame.display.flip()
    finally:
        pygame.quit()


if __name__ == "__main__":
    main()
