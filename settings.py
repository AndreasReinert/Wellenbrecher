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
SCHUSS_LEBENSDAUER = 5.0  # Sekunden ab dem Abfeuern
SCHUSS_TEMPO = 700.0
SCHUSS_GROESSE = 12
SCHUSS_FARBE = (255, 220, 90)

# Fadenkreuz: Radien, Linienmaße und Leuchtschichten in Pixeln.
FADENKREUZ_RADIEN = (4, 11)
FADENKREUZ_LINIENSTART = 15
FADENKREUZ_LINIENLAENGE = 7
FADENKREUZ_FARBE = (155, 240, 255)
FADENKREUZ_LEUCHTFARBE = (40, 190, 255)
FADENKREUZ_SCHICHTEN = ((7, 22), (5, 45), (3, 85))
FADENKREUZ_KERNBREITE = 1

# Gegner: Tempo in Pixeln/Sekunde, Radius in Pixeln; Bilder zeigen nach oben.
GEGNER_TYPEN = {
    "jaeger": {"tempo": 120, "leben": 2, "radius": 26,
               "bildname": "jaeger", "ersatzfarbe": (255, 100, 90)},
    "flitzer": {"tempo": 220, "leben": 1, "radius": 20,
                "bildname": "flitzer", "ersatzfarbe": (255, 210, 70)},
    "panzer": {"tempo": 70, "leben": 6, "radius": 40,
               "bildname": "panzer", "ersatzfarbe": (170, 120, 230)},
}
# Wellen: Anzahl, Freischaltungen und Zeiten in Sekunden.
WELLEN_STARTANZAHL = 6
WELLEN_ZUWACHS = 3
WELLEN_SPAWN_PAUSE = 2.0
WELLEN_PAUSE = 2.0
WELLEN_TEXT_DAUER = 2.0
GEGNER_AB_WELLE = {"jaeger": 1, "flitzer": 2, "panzer": 3}

# Treffer und Schutzzeit; Radien unabhängig von der Bilddrehung.
SPIELER_RADIUS = SPIELER_GROESSE / 2
SPIELER_STARTLEBEN = 5
SPIELER_UNVERWUNDBAR_DAUER = 1.0
SPIELER_BLINK_PAUSE = 0.1  # Sekunden pro sichtbarer/unsichtbarer Phase
SCHUSS_RADIUS = SCHUSS_GROESSE / 2
SCHUSS_SCHADEN = 1
GEGNER_KONTAKTSCHADEN = 1

# Anzeigen: Maße in Pixeln, Farben als RGB.
UI_RAND = 24
LEISTE_GROESSE = (240, 22)
LEISTE_RAHMEN = 2
LEISTE_TEXT_ABSTAND = 8
LEISTE_HINTERGRUND = (35, 48, 65)
LEISTE_FARBE = (70, 220, 150)
UI_TEXTFARBE = (220, 240, 255)
UI_SCHRIFTGROESSE = 26
WELLEN_SCHRIFTGROESSE = 76
GAME_OVER_SCHRIFTGROESSE = 80
GAME_OVER_ABSTAND = 64
GAME_OVER_FARBE = (255, 100, 100)
GAME_OVER_ABDUNKLUNG = 190

# Abstand der Statistikzeilen und zusätzlicher Hinweis beim Spielende.
UI_ZEILENABSTAND = 8
GAME_OVER_ENDE_VERSATZ = 112
