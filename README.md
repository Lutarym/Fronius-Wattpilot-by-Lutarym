# Fronius Wattpilot by Lutarym

Home Assistant Integration für die lokale Kommunikation mit dem Fronius Wattpilot.

Es wird kein Fronius-Konto und keine Cloud-Verbindung benötigt.

## Funktionsumfang

Die Integration kennt **254 Entitäten**. Angelegt werden davon nur diejenigen, die Ihr Gerät tatsächlich meldet. Siehe den Abschnitt zu den vorhandenen Entitäten weiter unten.

Von den angelegten Entitäten sind die wichtigsten sofort aktiv, seltener benötigte sind angelegt aber deaktiviert. Sie lassen sich jederzeit unter Einstellungen, Geräte und Dienste, Entitäten einschalten.

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

## Nur vorhandene Entitäten

Beim Verbinden prüft die Integration, welche Werte Ihr Wattpilot tatsächlich meldet. Es werden nur dafür Entitäten angelegt.

Das ist sinnvoll, weil nicht jedes Gerät alle Werte liefert. Ohne angeschlossenen Fronius-Wechselrichter gibt es keine PV-Werte, ohne eingerichtetes Lastmanagement keine Gruppenwerte, und je nach Firmware fehlen einzelne Angaben ganz.

So bleibt die Entitätenliste auf das beschränkt, was bei Ihnen wirklich existiert.

### Wie die Prüfung abläuft

Der Wattpilot meldet seinen Zustand manchmal in mehreren Teilnachrichten. Die Integration wartet deshalb nach dem Verbinden, bis keine neuen Werte mehr eintreffen, längstens acht Sekunden. Erst danach wird entschieden, welche Entitäten angelegt werden.

Bei zusammengesetzten Werten wird zusätzlich geprüft, ob der Einzelwert wirklich vorhanden ist. Meldet Ihr Gerät im Messwerte-Array nur die drei Spannungen, entstehen auch nur diese drei Entitäten und nicht die übrigen dreizehn.

Werte, die gemeldet werden aber gerade leer sind, gelten als vorhanden. Die aktive Transaktion ist zum Beispiel leer, solange keine Karte verwendet wird. Die Entität wird trotzdem angelegt.

Meldet das Gerät wider Erwarten gar nichts, werden vorsorglich alle Entitäten angelegt und eine Warnung ins Protokoll geschrieben.

### Abschalten

Unter Einstellungen, Geräte und Dienste, bei der Integration auf **Konfigurieren** lässt sich die Prüfung abschalten. Dann werden wieder alle 254 möglichen Entitäten angelegt.

Nach dem Umschalten lädt die Integration automatisch neu.

### Nach dem Umstieg

Wenn Sie von einer früheren Fassung kommen, bleiben nicht mehr angelegte Entitäten zunächst als nicht verfügbar in der Liste stehen. Sie lassen sich unter Einstellungen, Geräte und Dienste, Entitäten löschen.

## Sprachen

Die Integration ist vollständig übersetzt in **Deutsch, Englisch und Französisch**.

Übersetzt sind alle 254 Entitätsnamen, die Zustandswerte der Auswahllisten und Statussensoren, der Einrichtungsdialog und die Beschreibung des Dienstes.

Die Sprache richtet sich nach der Spracheinstellung Ihres Home-Assistant-Benutzerkontos. Sie lässt sich unter dem Benutzerprofil unten links ändern.

Rein technische Kennungen bleiben unübersetzt, etwa die Neustartgründe des Mikrocontrollers oder die Flash-Betriebsarten. Diese stehen ausschließlich auf Diagnose-Entitäten, die standardmäßig deaktiviert sind.

Die Übersetzungen liegen in `custom_components/fronius_wattpilot_lutarym/translations/` und können dort angepasst werden.

## Installation

### HACS

Dieses GitHub-Repository als benutzerdefiniertes Repository mit der Kategorie `Integration` hinzufügen und installieren.

### Manuell

Den Ordner `custom_components/fronius_wattpilot_lutarym` nach `/config/custom_components/` kopieren.

Danach Home Assistant neu starten und unter Einstellungen, Geräte und Dienste die Integration **Fronius Wattpilot by Lutarym** hinzufügen.

## Einrichtung

Benötigt werden nur die lokale IP-Adresse und das Wattpilot-Passwort. Das Passwort ist dasselbe, das in der Wattpilot-App vergeben wurde.

### Verbindung nachträglich ändern

Hat der Wattpilot eine neue IP-Adresse bekommen oder wurde das Passwort in der App geändert, muss die Integration nicht entfernt werden.

Unter Einstellungen, Geräte und Dienste bei der Integration auf die drei Punkte klicken und **Neu konfigurieren** wählen. Dort lassen sich Adresse und Passwort ändern. Die bisherige Adresse ist bereits eingetragen.

Die Integration prüft dabei, ob unter der neuen Adresse noch derselbe Wattpilot antwortet. Ist es ein anderes Gerät, wird abgebrochen. So bleiben Entitäten und Verläufe eindeutig einem Gerät zugeordnet. Ein zweiter Wattpilot wird stattdessen als eigene Integration hinzugefügt.

### Passwort erneut abfragen

Nimmt der Wattpilot das gespeicherte Passwort nicht mehr an, meldet Home Assistant das von selbst und fragt nur nach dem neuen Passwort. Die Adresse bleibt dabei unverändert.

### Einstellungen

Über **Konfigurieren** bei der Integration lässt sich einstellen, ob nur vorhandene Entitäten angelegt werden. Siehe den Abschnitt weiter oben.

## Aktualisierung der Werte

Die Werte kommen per WebSocket-Push, also unmittelbar bei jeder Änderung im Gerät. Ein fester Abrufzyklus ist dafür nicht nötig.

Zusätzlich läuft alle 60 Sekunden eine Prüfung, ob die Verbindung noch steht. Bricht sie ab, wird automatisch neu verbunden, mit wachsender Wartezeit von 10 bis maximal 300 Sekunden.

## Verhalten beim Start

Die Bibliothek `wattpilot-api` liest beim ersten Zugriff eine Beschreibungsdatei von der Festplatte. Home Assistant meldet solche Zugriffe als Fehler, wenn sie den laufenden Betrieb kurzzeitig anhalten.

Die Integration lädt diese Datei deshalb in einem Hintergrund-Thread und behält sie danach im Speicher. Sie wird nur einmal geladen, auch wenn mehrere Wattpilot eingerichtet sind.

Eine Sache bleibt: Bei jeder Anmeldung berechnet die Bibliothek das Passwort neu, was etwa 300 Millisekunden dauert. Das geschieht innerhalb der Bibliothek und lässt sich von der Integration aus nicht verlagern. Es fällt nur beim Verbindungsaufbau an, nicht im laufenden Betrieb, und wird von Home Assistant nicht als Fehler gemeldet.

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
