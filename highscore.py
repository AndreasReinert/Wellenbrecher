"""Unabhängige Endless-Bestwerte; Standardbibliothek, atomare Speicherung."""
import json
import math
import settings


def laden():
    rekord = {"besiegte_gegner": 0, "geschaffte_wellen": 0, "classic_bestzeit": None}
    try:
        daten = json.loads(settings.HIGHSCORE_DATEI.read_text(encoding="utf-8"))
        if isinstance(daten, dict):
            for name in ("besiegte_gegner", "geschaffte_wellen"):
                wert = daten.get(name)
                if type(wert) is int and wert >= 0:
                    rekord[name] = wert
            zeit = daten.get("classic_bestzeit")
            if type(zeit) in (int, float) and math.isfinite(zeit) and zeit > 0:
                rekord["classic_bestzeit"] = zeit
    except (OSError, ValueError):
        pass
    return rekord


def aktualisieren(rekord, besiegt, wellen):
    neu = {**rekord, "besiegte_gegner": max(rekord["besiegte_gegner"], besiegt),
           "geschaffte_wellen": max(rekord["geschaffte_wellen"], wellen)}
    if neu == rekord:
        return
    rekord.update(neu)
    _speichern(rekord)


def classic_aktualisieren(rekord, spielzeit):
    """Nur gewonnene Classic-Runden zählen; die kürzeste aktive Zeit gewinnt."""
    if not math.isfinite(spielzeit) or spielzeit <= 0:
        return
    bisher = rekord.get("classic_bestzeit")
    if bisher is None or spielzeit < bisher:
        rekord["classic_bestzeit"] = spielzeit
        _speichern(rekord)


def _speichern(rekord):
    pfad = settings.HIGHSCORE_DATEI
    try:
        pfad.parent.mkdir(parents=True, exist_ok=True)
        temporaer = pfad.with_suffix(".tmp")
        temporaer.write_text(json.dumps(rekord, indent=2), encoding="utf-8")
        temporaer.replace(pfad)
    except OSError:
        # Bei fehlenden Schreibrechten bleibt die Runde trotzdem spielbar.
        pass
