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
WELLEN_SPAWN_PAUSE = 2.0  # Pause zwischen Gruppen
WELLEN_GRUPPENGROESSE = 3
WELLEN_PAUSE = 2.0
WELLEN_TEXT_DAUER = 2.0
GEGNER_AB_WELLE = {"jaeger": 1, "flitzer": 2, "panzer": 3}

# Treffer und Schutzzeit; Radien unabhängig von der Bilddrehung.
SPIELER_RADIUS = SPIELER_GROESSE / 2
SPIELER_MAXLEBEN = 10
SPIELER_STARTLEBEN = SPIELER_MAXLEBEN
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

# Gegnerfeuer: Sekunden, Pixel/Sekunde, Radien in Pixeln, Winkel in Grad.
GEGNER_SCHUSS_TEMPO = 320.0
GEGNER_SCHUSS_LEBENSDAUER = 5.0
GEGNER_SCHUSS_SCHADEN = 1
GEGNER_WAFFEN = {
    "jaeger": {"pause": 1.5, "radius": 10, "winkel": (0,),
               "bildname": "schuss_jaeger", "farbe": (255, 110, 80)},
    "panzer": {"pause": 2.0, "radius": 12, "winkel": (-20, 0, 20),
               "bildname": "schuss_panzer", "farbe": (220, 130, 255)},
}

# Kristalle und Erfahrung: Schwellen werden je Level auf ganze Punkte aufgerundet.
KRISTALL_RADIUS = 8
KRISTALL_FARBE = (80, 255, 210)
KRISTALL_MAGNETRADIUS = 160.0
KRISTALL_TEMPO = 450.0
KRISTALL_ERFAHRUNG = 1
ERFAHRUNG_STARTBEDARF = 5
ERFAHRUNG_WACHSTUM = 1.25
ERFAHRUNGSLEISTE_HOEHE = 10
ERFAHRUNGSLEISTE_FARBE = (70, 210, 255)
ERFAHRUNGSLEISTE_TEXTABSTAND = 6


# Upgrades verändern ausschließlich Werte der aktuellen Spielerinstanz.
UPGRADES = [
    {"id": "schaden", "name": "Schaden", "wirkung": "+1 Schaden pro Schuss", "icon": "icon_schaden", "wert": 1},
    {"id": "feuerrate", "name": "Feuerrate", "wirkung": "Feuerpause -25 %", "icon": "icon_feuerrate", "wert": 0.75},
    {"id": "tempo", "name": "Tempo", "wirkung": "Bewegungstempo +12 %", "icon": "icon_tempo", "wert": 1.12},
    {"id": "mehrfach", "name": "Mehrfachschuss", "wirkung": "+1 Schuss (maximal 5)", "icon": "icon_mehrfach", "wert": 1, "maximum": 5},
    {"id": "leben", "name": "Reparatur", "wirkung": "+1 Leben (maximal 10)", "icon": "icon_leben", "wert": 1, "maximum": SPIELER_MAXLEBEN},
    {"id": "magnet", "name": "Magnet", "wirkung": "Magnetradius +40 %", "icon": "icon_magnet", "wert": 1.4},
]
MEHRFACHSCHUSS_START = 1
MEHRFACHSCHUSS_WINKEL = 12.0
UPGRADE_KARTENANZAHL = 3
UPGRADE_KARTENGROESSE = (300, 320)
UPGRADE_KARTENABSTAND = 28
UPGRADE_ANHEBUNG = 12
UPGRADE_ECKRADIUS = 18
UPGRADE_RAHMEN = 2
UPGRADE_ICON_GROESSE = 80
UPGRADE_ICON_Y = 88
UPGRADE_NAME_Y = 176
UPGRADE_WIRKUNG_Y = 226
UPGRADE_TITEL_Y = 112
UPGRADE_HINWEIS_Y = 610
UPGRADE_TITELGROESSE = 54
UPGRADE_NAMEGROESSE = 34
UPGRADE_TEXTGROESSE = 24
UPGRADE_FARBE = (22, 40, 65)
UPGRADE_AKTIVFARBE = (34, 72, 99)
UPGRADE_LEUCHTFARBE = (100, 235, 255)
UPGRADE_ICONFARBE = (90, 215, 235)
UPGRADE_LEUCHTSCHICHTEN = ((12, 18), (8, 28), (4, 48))

# Explosionen besiegter Gegner
PARTIKEL_ANZAHL_MIN = 12
PARTIKEL_ANZAHL_MAX = 20
PARTIKEL_MAXIMUM = 300
PARTIKEL_LEBENSDAUER = 0.5
PARTIKEL_TEMPO_MIN = 80.0
PARTIKEL_TEMPO_MAX = 260.0
PARTIKEL_BREMSUNG = 5.0
PARTIKEL_RADIUS_MIN = 2
PARTIKEL_RADIUS_MAX = 4
PARTIKEL_LEUCHTSCHICHTEN = ((3, 24), (2, 65), (1, 255))

# Trefferfeedback
GEGNER_BLITZ_DAUER = 0.08
BILDSCHIRM_WACKEL_DAUER = 0.25
BILDSCHIRM_WACKEL_STAERKE = 5.0  # Maximale Verschiebung je Achse in Pixeln

# Retro-Sounds: Lautstärken zwischen 0 (stumm) und 1.
SOUNDORDNER = BASISORDNER / "assets" / "sounds"
SOUND_LAUTSTAERKEN = {
    "schuss": 0.12, "treffer": 0.35, "explosion": 0.45,
    "kristall": 0.30, "levelup": 0.50, "gameover": 0.50,
}
SOUND_ABTASTRATE = 22050
SOUND_AMPLITUDE = 0.65
SOUND_EINBLENDZEIT = 0.004
# Dauer, Start-/Endfrequenz, Rauschanteil, Tonfolge (Hz).
SOUND_REZEPTE = {
    "schuss": (0.10, 1100, 180, 0.05, ()),
    "treffer": (0.12, 220, 65, 0.55, ()),
    "explosion": (0.38, 110, 25, 0.85, ()),
    "kristall": (0.18, 1000, 1700, 0.0, ()),
    "levelup": (0.48, 0, 0, 0.0, (523.25, 659.25, 783.99, 1046.50)),
    "gameover": (0.72, 0, 0, 0.12, (392, 329.63, 261.63, 130.81)),
}

# Startmenü
MENUE_TITEL_GROESSE = 88
MENUE_TEXT_GROESSE = 30
MENUE_TITEL_Y = 155
MENUE_KNOPF_GROESSE = (340, 62)
MENUE_KNOPF_START_Y = 320
MENUE_KNOPF_ABSTAND = 82
MENUE_RADIUS = 12
MENUE_RAND = 2
MENUE_FARBE = (12, 26, 48)
MENUE_HOVER_FARBE = (23, 65, 88)
MENUE_AKZENT = (95, 230, 255)
MENUE_TEXT_FARBE = (235, 248, 255)
MENUE_HILFE_Y = 290
MENUE_HILFE_ABSTAND = 48
MENUE_ZURUECK_Y = 600
MENUE_ABDUNKLUNG = 175

# Spielmodi und Classic-Finale
CLASSIC_BOSS_WELLE = 5
BOSS_LEBEN = 1200
BOSS_RADIUS = 60
BOSS_TEMPO = 70.0
BOSS_Y = 145
BOSS_RAND = 35
BOSS_RING_PAUSE = 3.0
BOSS_HILFE_PAUSE = 8.0
BOSS_RING_ANZAHL = 16
BOSS_HILFE_ANZAHL = 4
BOSS_SCHUSS_TEMPO = 130.0
BOSS_SCHUSS_RADIUS = 12
BOSS_FARBE = (235, 65, 150)
BOSS_EXPLOSIONEN = 10
BOSS_EXPLOSIONSRADIUS = 80
BOSS_LEISTE_BREITE = 540
BOSS_LEISTE_HOEHE = 22
BOSS_LEISTE_Y = 56
BOSS_NAME_Y = 30
SIEG_ZEILEN_Y = (230, 325, 380, 470)
MODUS_KARTEN = [
    {"id": "classic", "name": "Classic", "wirkung": "5 Wellen • Besiege den Boss", "icon": "panzer"},
    {"id": "endless", "name": "Endless", "wirkung": "Endlose Wellen • Überlebe!", "icon": "jaeger"},
]
GEGNER_TYPEN["boss"] = {"tempo": BOSS_TEMPO, "leben": BOSS_LEBEN,
    "radius": BOSS_RADIUS, "bildname": "mutterschiff", "ersatzfarbe": BOSS_FARBE}

# Dauerhafte Rekorde liegen außerhalb des temporären PyInstaller-Ordners.
HIGHSCORE_DATEI = Path.home() / ".wellenbrecher" / "highscore.json"
HIGHSCORE_TEXT_Y = 267
HIGHSCORE_ZEILENABSTAND = 25

# Anzeige: F11 schaltet jederzeit zwischen Fenster und Vollbild um.
VOLLBILD_START = False

# Freischaltungen beziehen sich auf Wellen, nicht auf das Spielerlevel.
GEGNER_AB_WELLE_MODUS = {
    "classic": {"jaeger": 1, "flitzer": 2, "panzer": 3, "circle": 4},
    "endless": {"jaeger": 1, "flitzer": 2, "panzer": 5, "circle": 8},
}
CIRCLE_LEBEN = 12
CIRCLE_RADIUS = 34
CIRCLE_FARBE = (255, 100, 195)
CIRCLE_SCHUSS_PAUSE = 5.0
CIRCLE_RING_ANZAHL = 16
CIRCLE_SCHUSS_RADIUS = 10
GEGNER_TYPEN["circle"] = {
    "tempo": GEGNER_TYPEN["panzer"]["tempo"], "leben": CIRCLE_LEBEN,
    "radius": CIRCLE_RADIUS, "bildname": "circle", "ersatzfarbe": CIRCLE_FARBE,
}
GEGNER_WAFFEN["circle"] = {
    "pause": CIRCLE_SCHUSS_PAUSE, "radius": CIRCLE_SCHUSS_RADIUS,
    "winkel": tuple(i * 360 / CIRCLE_RING_ANZAHL for i in range(CIRCLE_RING_ANZAHL)),
    "bildname": "schuss_circle", "farbe": CIRCLE_FARBE,
}

# Begleitdrohne: unabhängig von den Waffen-Upgrades des Spielers.
DROHNE_RADIUS = 6
DROHNE_FARBE = (90, 255, 220)
DROHNE_ORBITRADIUS = 58.0
DROHNE_WINKELTEMPO = 100.0  # Grad pro Sekunde
DROHNE_STARTWINKEL = -90.0
DROHNE_SCHUSS_PAUSE = 0.8
DROHNE_STARTSCHADEN = 1
UPGRADES.extend([
    {"id": "drohne", "name": "Begleitdrohne", "wirkung": "Feuert automatisch auf Gegner", "icon": "icon_drohne", "wert": 1},
    {"id": "drohne_schaden", "name": "Drohnen-Schaden", "wirkung": "+1 Schaden pro Drohnenschuss", "icon": "icon_drohne_upgrade", "wert": 1},
])

# Endless-Bosswellen und direkte Levelbelohnung (keine Erfahrungspunkte).
ENDLESS_BOSS_INTERVALL = 15
ENDLESS_BOSS_LEVELBONUS = 3
UPGRADES.append({"id": "drohne_feuerrate", "name": "Drohnen-Feuerrate",
                 "wirkung": "Drohnen-Feuerpause -40 %",
                 "icon": "icon_drohne_feuerrate", "wert": 0.60})
