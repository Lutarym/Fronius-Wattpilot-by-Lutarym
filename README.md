# Fronius Wattpilot by Lutarym

Home Assistant Integration für die lokale Kommunikation mit dem Fronius Wattpilot.

Es wird kein Fronius-Konto und keine Cloud-Verbindung benötigt.

## Funktionsumfang

Die Integration legt **254 Entitäten** an. Davon sind **105 standardmäßig aktiv**, die übrigen 149 sind angelegt, aber deaktiviert. Sie lassen sich jederzeit unter Einstellungen, Geräte und Dienste, Entitäten einschalten.

Grundlage ist die API-Definition der Bibliothek `wattpilot-api` in Version 1.4.0.

### Laden und Steuerung

| Funktion | Typ | Property |
|---|---|---|
| Ladestrom | Zahl, 6 bis 32 A | `amp` |
| Maximaler Stromgrenzwert | Zahl | `ama` |
| Minimaler Ladestrom | Zahl | `mca` |
| Lademodus | Auswahl: Default, Awattar, AutomaticStop | `lmo` |
| Force State | Auswahl: Neutral, Off, On | `frc` |
| Phasenumschaltung | Auswahl: Auto, 1-phasig, 3-phasig | `psm` |
| Einphasig erzwingen | Schalter | `fsp` |
| Zugriffsfreigabe | Auswahl: Open, Wait | `acs` |
| Kabelverriegelung | Auswahl: Normal, AutoUnlock, AlwaysLock | `ust` |
| Ladeenergie-Grenze | Zahl in Wh | `dwo` |
| Fahrzeugstatus | Sensor: Idle, Charging, WaitCar, Complete, Error | `car` |
| Ladegrund | Sensor mit 25 Klartext-Zuständen | `modelStatus` |
| Fehlerstatus | Sensor mit Klartext | `err` |
| Erlaubter Strom des Fahrzeugs | Sensor in A | `acu` |
| Laden erlaubt | Binärsensor | `alw` |

Der **Force State** ist der Weg, um das Laden sofort zu starten oder zu stoppen. `On` erzwingt das Laden, `Off` unterbindet es, `Neutral` überlässt die Entscheidung dem eingestellten Lademodus.

### Messwerte

Spannung, Strom, Leistung und Leistungsfaktor für alle drei Phasen und den Neutralleiter, dazu Frequenz, Temperatursensoren, Gesamtenergie, gespeicherte Gesamtenergie und Energie seit dem Anstecken.

### RFID und Transponder

| Funktion | Typ | Property |
|---|---|---|
| Registrierte Karten | Sensor, Anzahl mit Liste in den Attributen | `cards` |
| Aktive Transaktion | Zahl, setzbar | `trx` |
| Energie je Karte | Ein Sensor pro Karte | aus `cards` |
| Name je Karte | Ein Sensor pro Karte | aus `cards` |

Über `trx` lässt sich eine Ladung auch ohne physisches Vorhalten der Karte freigeben. `0` bedeutet ohne Karte, `1` steht für die erste Karte, `2` für die zweite und so weiter.

Die Entitäten für die einzelnen Karten werden beim Start anhand der tatsächlich vorhandenen Karten angelegt. Nach dem Anlegen oder Löschen einer Karte muss die Integration neu geladen werden.

### PV-Überschuss und Wechselrichter

Überschussladen ein und aus, Startleistung, Stopp-Hysterese, Umschaltschwelle auf drei Phasen, Phasen-Hysterese, Nulleinspeisung mit Offset und Batteriegrenze.

Vom Fronius-Wechselrichter kommen zusätzlich PV-Leistung, Netzbezug, Speicherleistung, Speicherladestand und die jeweiligen Mittelwerte.

### Awattar und dynamische Preise

Land, Höchstpreis, aktueller Marktpreis mit Start- und Endzeit, vollständige Preisliste in den Attributen und die Anzeige, ob dynamische Preise verwendet werden.

### Lastmanagement

Lastmanagement ein und aus, Typ statisch oder dynamisch, Gesamtstrom der Gruppe, Gruppenkennung, Priorität, Prioritäts-Offset, Rückfallstrom und Lastzuordnung.

### Zeitpläne

Die Ladezeitpläne für Wochentag, Samstag und Sonntag werden mit ihrem Steuerungsmodus und den vollständigen Zeitbereichen in den Attributen angezeigt.

### Gerät und Diagnose

Firmware, Seriennummer, Modell, Anzeigename, WLAN-Signalstärke, Uhrzeit, Betriebsdauer, Neustartzähler und eine Schaltfläche zum Neustart.

## Was der Wattpilot nicht liefert

Der Wattpilot liest **keine Daten aus dem Fahrzeug** aus. Es gibt keinen Ladestand und keine Reichweite des Autos.

Die Felder Fahrzeugtyp (`ct`) und Fahrzeugverbrauch (`cco`) sind Freitextangaben, die Sie selbst eintragen. Laut API-Definition werden sie ausschließlich für die App gespeichert.

Der Wert `fbuf_akkuSOC` ist der Ladestand des **PV-Hausspeichers** am Fronius-Wechselrichter, nicht der des Fahrzeugs.

Abrufbar sind vom Fahrzeug nur der Anschlusszustand (`car`), der Strom, den das Fahrzeug ziehen darf (`acu`), und die Strombelastbarkeit des Kabels (`cbl`).

## Dienst: Parameter setzen

Für Parameter ohne eigene Entität gibt es den Dienst `fronius_wattpilot_lutarym.set_property`.

```yaml
action: fronius_wattpilot_lutarym.set_property
data:
  device_id: <Ihr Wattpilot>
  property: amp
  value: 16
```

## Installation

### HACS

Dieses GitHub-Repository als benutzerdefiniertes Repository mit der Kategorie `Integration` hinzufügen und installieren.

### Manuell

Den Ordner `custom_components/fronius_wattpilot_lutarym` nach `/config/custom_components/` kopieren.

Danach Home Assistant neu starten und unter Einstellungen, Geräte und Dienste die Integration **Fronius Wattpilot by Lutarym** hinzufügen.

## Einrichtung

Benötigt werden nur die lokale IP-Adresse und das Wattpilot-Passwort. Das Passwort ist dasselbe, das in der Wattpilot-App vergeben wurde.

## Aktualisierung der Werte

Die Werte kommen per WebSocket-Push, also unmittelbar bei jeder Änderung im Gerät. Ein fester Abrufzyklus ist dafür nicht nötig.

Zusätzlich läuft alle 60 Sekunden eine Prüfung, ob die Verbindung noch steht. Bricht sie ab, wird automatisch neu verbunden, mit wachsender Wartezeit von 10 bis maximal 300 Sekunden.

## Hinweis zu den Leistungswerten

Die Leistungswerte je Phase stammen aus dem Messwerte-Array `nrg` und werden unverändert in Watt angezeigt. Bitte einmal mit der Anzeige in der Wattpilot-App vergleichen. Die Bibliothek `wattpilot-api` skaliert diese Werte für ihre eigenen Eigenschaften mit dem Faktor 0,001, was auf eine abweichende Einheit hindeuten könnte. Die API-Definition macht dazu keine eindeutige Angabe.

## Wichtig

Das lokale Wattpilot-Protokoll ist keine offizielle öffentliche Fronius-Schnittstelle. Dieses Projekt nutzt die quelloffene Umsetzung `wattpilot-api`.

Der WebSocket-Zugang des Wattpilot sollte nicht aus dem Internet erreichbar sein.

## Fehlersuche

```yaml
logger:
  default: warning
  logs:
    custom_components.fronius_wattpilot_lutarym: debug
    wattpilot_api: debug
```
