"""Mit python tools/sounds_erzeugen.py alle Retro-WAVs erzeugen.

Nur Standardbibliothek; unabhängig vom aktuellen Arbeitsordner.
Die Klangparameter stehen zentral in settings.py. Vorhandene WAVs werden ersetzt.
"""
import math
import random
import wave
from pathlib import Path
import sys

BASISORDNER = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASISORDNER))
import settings


def erzeugen():
    ziel = BASISORDNER / "assets" / "sounds"
    ziel.mkdir(parents=True, exist_ok=True)
    zufall = random.Random(0)
    for name, rezept in settings.SOUND_REZEPTE.items():
        dauer, start, ende, rauschen, tonfolge = rezept
        daten = bytearray()
        phase = 0.0
        anzahl = round(dauer * settings.SOUND_ABTASTRATE)
        for index in range(anzahl):
            zeit = index / settings.SOUND_ABTASTRATE
            fortschritt = index / max(1, anzahl - 1)
            frequenz = start + (ende - start) * fortschritt
            if tonfolge:
                frequenz = tonfolge[min(int(fortschritt * len(tonfolge)), len(tonfolge) - 1)]
            phase += frequenz / settings.SOUND_ABTASTRATE
            # Weiches Rechteck mit Sinusanteil für kurze Retro-Klänge.
            sinus = math.sin(2 * math.pi * phase)
            ton = 0.65 * (1 if sinus >= 0 else -1) + 0.35 * sinus
            huelle = min(1.0, zeit / settings.SOUND_EINBLENDZEIT) * (1 - fortschritt) ** 1.5
            wert = ((1 - rauschen) * ton + rauschen * zufall.uniform(-1, 1))
            wert *= huelle * settings.SOUND_AMPLITUDE
            pcm = round(max(-1.0, min(1.0, wert)) * 32767)
            daten.extend(pcm.to_bytes(2, "little", signed=True))
        with wave.open(str(ziel / f"{name}.wav"), "wb") as datei:
            datei.setnchannels(1)
            datei.setsampwidth(2)
            datei.setframerate(settings.SOUND_ABTASTRATE)
            datei.writeframes(daten)
        print(f"Erzeugt: {name}.wav")


if __name__ == "__main__":
    erzeugen()
