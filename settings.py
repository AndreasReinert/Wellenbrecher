"""Zentrale Einstellungen für Wellenbrecher."""
from pathlib import Path
import sys

BREITE = 1280
HOEHE = 720
FENSTERGROESSE = (BREITE, HOEHE)
TITEL = "Wellenbrecher"
FPS = 60
DUNKELBLAU = (10, 24, 48)

# PyInstaller entpackt gebündelte Ressourcen nach sys._MEIPASS.
BASISORDNER = Path(getattr(sys, "_MEIPASS", Path(__file__).resolve().parent))
BILDERORDNER = BASISORDNER / "assets" / "bilder"

# Bewegung in Pixeln pro Sekunde; Bildgröße in Pixeln.
SPIELER_TEMPO = 300.0
SPIELER_GROESSE = 48
SPIELER_FARBE = (80, 210, 255)

# Schüsse: Pause in Sekunden, Tempo in Pixeln pro Sekunde.
SCHUSS_PAUSE = 0.18
SCHUSS_TEMPO = 700.0
SCHUSS_GROESSE = 12
SCHUSS_FARBE = (255, 220, 90)
