"""Unabhängige Endless-Bestwerte; Standardbibliothek, atomare Speicherung."""
import json
import settings


def laden():
    rekord = {"besiegte_gegner": 0, "geschaffte_wellen": 0}
    try:
        daten = json.loads(settings.HIGHSCORE_DATEI.read_text(encoding="utf-8"))
        if isinstance(daten, dict):
            for name in rekord:
                wert = daten.get(name)
                if type(wert) is int and wert >= 0:
                    rekord[name] = wert
    except (OSError, ValueError):
        pass
    return rekord


def aktualisieren(rekord, besiegt, wellen):
    neu = {"besiegte_gegner": max(rekord["besiegte_gegner"], besiegt),
           "geschaffte_wellen": max(rekord["geschaffte_wellen"], wellen)}
    if neu == rekord:
        return
    rekord.update(neu)
    pfad = settings.HIGHSCORE_DATEI
    try:
        pfad.parent.mkdir(parents=True, exist_ok=True)
        temporaer = pfad.with_suffix(".tmp")
        temporaer.write_text(json.dumps(neu, indent=2), encoding="utf-8")
        temporaer.replace(pfad)
    except OSError:
        # Bei fehlenden Schreibrechten bleibt die Runde trotzdem spielbar.
        pass
