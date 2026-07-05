# Game Media Guard

Kleines Windows-Tool mit drei Tabs:

- **Valorant**: Rot im gewaehlten Bildschirmbereich gilt als `tot`, kein Rot als `nicht tot`.
- **LoL**: Eine Zahl oder ein Countdown im gewaehlten Bildschirmbereich gilt als `tot`, keine Zahl als `nicht tot`.

Pro Tab kannst du getrennt einstellen, ob das Tool `Play/Pause` sendet oder nur die Lautstaerke einer ausgewaehlten Medienwiedergabe aendert.

Der dritte Tab zeigt diese README direkt im Programm.

Das Tool liest nur den Bildschirm und sendet normale Windows-Medientasten. Es greift nicht in Spiel-Speicher, Dateien, Netzwerk oder Anti-Cheat ein.

## Start

1. `start_valorant_media_guard.bat` doppelklicken.
2. Den passenden Tab auswaehlen: `Valorant` oder `LoL`.
3. Im Spiel am besten `Fenster-Vollbild` oder `Randlos` nutzen, falls Screenshots bei exklusivem Vollbild schwarz bleiben.
4. `Bereich waehlen` klicken und den Bereich markieren, in dem die rote Anzeige oder die LoL-Zahl erscheinen soll.
5. Unter `Medienwiedergabe` auf `Aktualisieren` klicken und z. B. Spotify, Browser oder Player auswaehlen.
6. Entweder `Play/Pause steuern` oder `Nur Lautstaerke anpassen` waehlen.
7. Bei Lautstaerke-Modus `Tot %` und `Nicht tot %` eintragen und mit `Test Tot` / `Test Nicht tot` pruefen.
8. `Start` klicken.

## Valorant-Tipps

- `Rot %`: So viel Prozent des gewaehlten Bereichs muessen rot sein. Standard: `1.0`.
- `Rot min`: Der rote Farbkanal muss mindestens so hell sein. Standard: `140`.
- `Rot Abstand`: Rot muss so viel staerker sein als Gruen und Blau. Standard: `45`.

## LoL-Tipps

- Markiere nur den kleinen Bereich, in dem die Zahl herunterzaehlt. Je kleiner und klarer der Bereich ist, desto besser.
- `Hell %`: So viel Prozent des Bereichs muessen helle Pixel enthalten. Standard: `0.25`.
- `Hell min`: Ab welchem Farbwert ein Pixel als hell gilt. Standard: `150`.
- `Ziffer Hoehe` und `Ziffer Flaeche`: Mindestgroesse fuer ziffernartige Formen.
- `Komponenten`: Wie viele ziffernartige Formen mindestens gefunden werden muessen. Standard: `1`.

## Allgemein

- Oben im Programm steht die installierte Version und die neueste Version auf GitHub.
- Wenn GitHub neuer ist, erscheint der Button `Jetzt aktualisieren`.
- Das Update laeuft ueber `git pull --ff-only`; danach die App neu starten.
- Das GIF `Gangcord.gif` wird im Fenster sichtbar angezeigt, `logo der app.png` wird als App-Logo genutzt.
- Valorant und LoL speichern Bereich, Ziel, Modus und Lautstaerke getrennt.
- Wenn die Erkennung wackelt, waehle einen kleineren, klareren Bereich.
- Wenn dein Mediaplayer direkte `Play`/`Pause`-Befehle ignoriert, stelle in der App auf `Fallback: Medien-Toggle bei jedem Wechsel`.
- Die Medienziel-Auswahl wirkt auf die Lautstaerke der ausgewaehlten Windows-Audio-Sitzung.
- `Stabil` hoeher machen, wenn kurze Bildschirmwechsel stoeren.
- Die Einstellungen werden in `config.json` neben dem Tool gespeichert.
