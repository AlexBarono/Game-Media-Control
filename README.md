# Valorant Media Guard

Kleines Windows-Tool: Wenn im gewaehlten Bildschirmbereich **Rot** erkannt wird, sendet es `Play`. Wenn dort kein Rot erkannt wird, sendet es `Pause`.

Das Tool liest nur den Bildschirm und sendet normale Windows-Medientasten. Es greift nicht in Valorant-Speicher, Dateien, Netzwerk oder Anti-Cheat ein.

## Start

1. `start_valorant_media_guard.bat` doppelklicken.
2. In Valorant am besten `Fenster-Vollbild` oder `Randlos` nutzen, falls Screenshots bei exklusivem Vollbild schwarz bleiben.
3. `Bereich waehlen` klicken und den Bereich markieren, in dem die rote Anzeige erscheinen soll.
4. `Test Play` und `Test Pause` pruefen.
5. `Start` klicken.

## Tipps

- `Rot %`: So viel Prozent des gewaehlten Bereichs muessen rot sein. Standard: `1.0`.
- `Rot min`: Der rote Farbkanal muss mindestens so hell sein. Standard: `140`.
- `Rot Abstand`: Rot muss so viel staerker sein als Gruen und Blau. Standard: `45`.
- Wenn die Erkennung wackelt, waehle einen kleineren, klareren Bereich.
- Wenn dein Mediaplayer direkte `Play`/`Pause`-Befehle ignoriert, stelle in der App auf `Fallback: Medien-Toggle bei jedem Wechsel`.
- `Rot %` hoeher machen, wenn zu oft Play ausgelöst wird. `Rot %` niedriger machen, wenn Rot nicht erkannt wird. `Stabil` hoeher machen, wenn kurze Bildschirmwechsel stoeren.
- Die Einstellungen werden in `config.json` neben dem Tool gespeichert.
