# Fronius Wattpilot by Lutarym

Home Assistant Integration für die lokale Kommunikation mit dem Fronius Wattpilot.

Es wird kein Fronius-Konto und keine Cloud-Verbindung benötigt.

## Funktionsumfang

Die Integration kennt **254 Entitäten**. Angelegt werden davon nur die, die Ihr Gerät tatsächlich meldet.

### Standardmäßig aktiv

Aktiv ist nur, was man täglich braucht. Acht feste Entitäten:

| Entität | Art | Bedeutung |
|---|---|---|
| Fahrzeugstatus | Sensor | Kein Fahrzeug, Lädt, Angesteckt wartet, Ladung abgeschlossen |
| Fahrzeug angesteckt | Ja/Nein | ob ein Auto am Kabel hängt |
| Lademodus | Auswahl | Standard, Eco Mode, Next Trip Mode |
| Ladestrom | Zahl | 6 bis 32 A |
| Gesamtleistung | Sensor | aktuelle Ladeleistung in W |
| Gesamtenergie | Sensor | Zählerstand, geeignet für das Energie-Dashboard |
| Energie seit Anstecken | Sensor | Energie der laufenden Ladung |
| Fehlerstatus | Sensor | Klartext, zum Beispiel Überstrom oder Übertemperatur |

Dazu kommen die Entitäten für die RFID-Chips: eine je Chip für den Gesamtzähler, die letzte Ladung und den Ladevorgang, sowie einmalig die aktive Karte. Diese entstehen nur, wenn Chips im Gerät hinterlegt sind. Ebenfalls ab Werk aktiv sind **Registrierte RFID-Karten** und **Aktive Transaktion**. Einzelheiten im Abschnitt zu den RFID-Chips.

Alle übrigen Entitäten sind vorhanden, aber deaktiviert. Einschalten geht unter Einstellungen, Geräte und Dienste, Entitäten: Entität suchen, anklicken, Zahnrad, Aktiviert einschalten.

### Verfügbar, aber deaktiviert

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
| Registrierte Karten | Sensor, Anzahl mit Liste in den Attributen, ab Werk aktiv. Nur bei Geräten, die die Liste `cards` melden | `cards` |
| Aktive Transaktion | Zahl, setzbar, ab Werk aktiv | `trx` |
| Chip-Entitäten | Je Chip Energie gesamt, Energie letzte Ladung und lädt | aus `cards` oder aus `c0n` bis `c9n`, `c0e` bis `c9e`, `c0i` bis `c9i` |

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

## Lademodi

Fronius nennt die drei Lademodi in seiner Dokumentation **Standard**, **Eco Mode** und **Next Trip Mode**. Genau so heißen sie auch in dieser Integration.

Die zugrunde liegende API-Definition verwendet dafür interne Bezeichnungen (Default, Awattar, AutomaticStop). Die werden hier auf die Namen aus der Fronius-App übersetzt, damit die Anzeige zu dem passt, was Sie vom Gerät kennen.

Für das sofortige Starten oder Stoppen unabhängig vom Modus gibt es zusätzlich die Entität **Ladefreigabe erzwingen**. Sie ist standardmäßig deaktiviert.

## RFID-Chips und Zuordnung zum Fahrzeug

Wer mehrere Autos lädt, kann jedem einen NFC-Chip zuordnen. Der Wattpilot führt dann je Chip einen eigenen Energiezähler, und die Integration macht daraus Entitäten.

### Was angelegt wird

Je angelerntem Chip entstehen drei Entitäten. Der Chipname aus der Wattpilot-App steht im Namen, sodass die Werte unmittelbar dem Fahrzeug zugeordnet sind. Heißt der Chip in der App "Zoe", lauten sie:

| Entität | Bedeutung |
|---|---|
| Zoe Energie gesamt | Zählerstand des Chips über alle Ladungen, vom Wattpilot geführt |
| Zoe Energie letzte Ladung | Energie der laufenden oder zuletzt mit diesem Chip gefahrenen Ladung |
| Zoe lädt | Ja, solange dieser Chip die Transaktion hält und tatsächlich Strom fließt |

Dazu kommt einmalig **Aktive RFID-Karte**. Sie zeigt den Namen des Chips, der gerade vorgehalten wurde. Wird ohne Chip geladen oder läuft keine Ladung, bleibt sie leer, die Einzelheiten stehen dann in den Attributen.

Alle diese Entitäten sind sofort aktiv.

### Fürs Energie-Dashboard

Geeignet ist **Energie gesamt** je Chip. Das ist der Zähler des Wattpilot selbst, er läuft über alle Ladungen weiter.

**Energie letzte Ladung** bekommt bewusst keine Zustandsklasse und taucht daher nicht im Energie-Dashboard auf. Der Wert fällt zu Beginn jeder Ladung auf null zurück und taugt deshalb nicht als Zählerstand für die Langzeitstatistik.

### Zwei Meldeformen der Chips

Je nach Firmware meldet der Wattpilot die Chips auf zwei Arten:

| Form | Schlüssel | Inhalt |
|---|---|---|
| Liste | `cards` | eine Liste mit Name, Energie und Kennung je Chip |
| Einzelschlüssel | `c0n` bis `c9n`, `c0e` bis `c9e`, `c0i` bis `c9i` | Name, Energie in Wh und ob eine Kennung hinterlegt ist, je Chip ein eigener Schlüssel |

Die Schlüsselliste der go-e-API v2 führt die Einzelschlüssel ab Firmware 60.0 und vermerkt `cards` dort als entfernt. Die Integration liest ab Version 2.9.0 beide Formen. Bis 2.8.0 wurde nur die Liste gelesen. Bei einem Gerät mit Einzelschlüsseln entstanden deshalb keine Chip-Entitäten.

Bei Geräten mit Einzelschlüsseln gibt es den Sensor **Registrierte RFID-Karten** nicht, weil das Gerät die Liste nicht meldet. Die Chips erscheinen dann direkt als eigene Entitäten.

### Wie die Zuordnung funktioniert

Der Wattpilot meldet nur zwei Dinge: die Liste der gespeicherten Chips und welcher davon gerade die Transaktion hält. Einen Zähler je Chip und Ladung gibt es nicht.

Die Integration merkt sich deshalb selbst, wie viel Energie geflossen ist, solange ein bestimmter Chip die Transaktion hält. Nach dem Abstecken bleibt der Wert stehen, bis mit demselben Chip wieder geladen wird. Über Neustarts von Home Assistant hinweg bleibt er erhalten.

Wird ohne Chip geladen, läuft die Energie in keinen Chipzähler. Das ist auch im Wattpilot so.

### Wenn keine Chip-Entitäten erscheinen

Der Wattpilot schickt seinen Zustand beim Verbinden in mehreren Teilnachrichten. Die zugrunde liegende Bibliothek meldet die Verbindung aber schon als fertig, sobald irgendeine Änderungsnachricht eintrifft, auch wenn noch Teilnachrichten unterwegs sind.

Die Integration wartet deshalb, bis sich die Liste der gemeldeten Werte über mehrere Durchläufe hinweg nicht mehr ändert, längstens zwanzig Sekunden. Nachzügler wie die Chipliste gehen so nicht mehr verloren.

Meldet der Wattpilot einen Wert erst später, etwa weil eine Funktion gerade erst eingeschaltet wurde, gilt er ab dann dauerhaft als vorhanden.

Falls dennoch Entitäten fehlen, hilft die Diagnose weiter: Unter Einstellungen, Geräte und Dienste beim Gerät auf **Diagnose herunterladen**. Die Datei zeigt, welche Werte das Gerät gemeldet hat, wie die Chipliste aussieht und welche Entitäten mangels Meldung übersprungen wurden. Unter `rfid` steht bei `kartenformat`, in welcher Form das Gerät die Chips meldet: `cards` für die Liste, `einzelschluessel` für `c0n` und folgende. Steht dort nichts, meldet das Gerät keine Chips.

### Neue Chips anlernen

Chips werden in der Wattpilot-App angelernt, nicht in Home Assistant.

Danach ist nichts weiter zu tun: Die Integration merkt, dass sich die Chipliste geändert hat, und lädt sich selbst neu, damit der neue Chip seine Entitäten bekommt. Dasselbe gilt beim Umbenennen und beim Löschen eines Chips.

Beim Umbenennen ändert sich nur der Anzeigename. Die eindeutige Kennung richtet sich nach der Position des Chips im Gerät, der bisherige Verlauf bleibt also erhalten.

### Freigeben ohne Chip

Die Entität **Aktive Transaktion** kann die Transaktion auch ohne physisches Vorhalten setzen. Null bedeutet ohne Chip, eins steht für den ersten Chip, zwei für den zweiten. Sie ist ab Werk aktiv.

### Ab Werk aktiv

**Aktive Transaktion** und **Registrierte RFID-Karten** sind ab Version 2.9.0 ab Werk aktiv. Waren sie aus einer früheren Fassung noch deaktiviert, schaltet die Integration sie beim ersten Start ein. Home Assistant lädt die Integration danach einmal neu. Hat jemand eine der beiden Entitäten selbst deaktiviert, bleibt sie aus.

### Einheit der Chipzähler

Die API-Definition nennt für den Zähler je Chip keine Einheit. Für die Einzelschlüssel `c0e` bis `c9e` nennt die Schlüsselliste der go-e-API v2 ausdrücklich Wh. Für die Liste `cards` wird dieselbe Einheit angenommen.

Bitte einmal mit der Anzeige in der Wattpilot-App vergleichen. Falls es nicht passt, ist `CARD_ENERGY_UNIT` in `const.py` die Stelle zum Ändern.

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

### Aufräumen alter Entitäten

Home Assistant löscht Entitäten nicht von selbst, wenn eine Integration sie nicht mehr anlegt. Sie bleiben als **Nicht verfügbar** in der Liste stehen.

Die Integration räumt diese Reste beim Start automatisch weg. Betroffen sind zwei Fälle: Entitäten aus älteren Fassungen dieser Integration und Werte, die Ihr Gerät nicht liefert.

Aus Vorsicht wird nichts gelöscht, wenn die Verfügbarkeitsprüfung abgeschaltet ist, wenn das Gerät beim Verbinden gar nichts gemeldet hat oder wenn überhaupt keine Entität angelegt wurde. Ein einmaliger Aussetzer beim Verbinden soll nicht den Verlauf einer Entität vernichten.

Was entfernt wurde, steht im Protokoll.

### Warum manche Werte fehlen

Nicht jeder Wert existiert auf jedem Gerät. Drei Beispiele, die die API-Definition ausdrücklich als gerätespezifisch führt: Stromabweichung, Leistungsabweichung und Alter der Wechselrichterdaten gibt es nur bei einer anderen Gerätevariante, nicht beim Fronius Wattpilot.

Welche Werte Ihr Gerät meldet, zeigt das Protokoll bei eingeschalteter Fehlersuche.

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

Lehnt der Wattpilot das gespeicherte Passwort ab, erkennt die Integration das als Anmeldefehler und nicht als Verbindungsproblem. Home Assistant fragt dann von selbst nach dem neuen Passwort. Die Adresse bleibt unverändert.

Auch bei der Einrichtung wird unterschieden: Ein abgelehntes Passwort wird als solches gemeldet, nicht als nicht erreichbares Gerät.

### Einstellungen

Über **Konfigurieren** bei der Integration lässt sich einstellen, ob nur vorhandene Entitäten angelegt werden. Siehe den Abschnitt weiter oben.

## Aktualisierung der Werte

Die Werte kommen per WebSocket-Push, also unmittelbar bei jeder Änderung im Gerät. Ein fester Abrufzyklus ist dafür nicht nötig.

Zusätzlich läuft alle 60 Sekunden eine Prüfung, ob die Verbindung noch steht. Bricht sie ab, wird automatisch neu verbunden, mit wachsender Wartezeit von 10 bis maximal 300 Sekunden.

## Verhalten beim Start

Die Bibliothek `wattpilot-api` liest beim ersten Zugriff eine Beschreibungsdatei von der Festplatte. Home Assistant meldet solche Zugriffe als Fehler, wenn sie den laufenden Betrieb kurzzeitig anhalten.

Die Integration lädt diese Datei deshalb in einem Hintergrund-Thread und behält sie danach im Speicher. Sie wird nur einmal geladen, auch wenn mehrere Wattpilot eingerichtet sind.

Eine Sache bleibt: Bei jeder Anmeldung berechnet die Bibliothek das Passwort neu, was etwa 300 Millisekunden dauert. Das geschieht innerhalb der Bibliothek und lässt sich von der Integration aus nicht verlagern. Es fällt nur beim Verbindungsaufbau an, nicht im laufenden Betrieb, und wird von Home Assistant nicht als Fehler gemeldet.

## Neuladen der Integration

Ändert sich etwas an der Konfiguration, muss die Integration neu geladen werden. Das geschieht an genau einer Stelle, nämlich über den Update-Listener.

Die Dialoge selbst laden bewusst nicht zusätzlich neu. Seit Home Assistant 2026.6 wird die Kombination aus beidem beanstandet, weil sonst zweimal hintereinander neu geladen wird. Ab Fassung 2026.12 wäre das ein Fehler.

## Zu den Energiezählern

Der Wattpilot liefert zwei Gesamtzähler. **Gesamtenergie** ist ein hochgerechneter Live-Wert, **Gesamtenergie gespeichert** der tatsächlich gespeicherte Wert ohne diese Hochrechnung.

Der Live-Wert kann deshalb gelegentlich um wenige Wattstunden zurückspringen, wenn der gespeicherte Wert nachzieht. Alle Energiezähler sind daher als **total** geführt und nicht als streng steigend. Genau das empfiehlt auch die API-Definition.

Für das Energie-Dashboard ist das geeignet. Wer den ruhigeren Verlauf möchte, kann stattdessen **Gesamtenergie gespeichert** aktivieren.

## Hinweis zu den Leistungswerten

Die Leistungswerte je Phase stammen aus dem Messwerte-Array `nrg` und werden unverändert in Watt angezeigt. Bitte einmal mit der Anzeige in der Wattpilot-App vergleichen. Die Bibliothek `wattpilot-api` skaliert diese Werte für ihre eigenen Eigenschaften mit dem Faktor 0,001, was auf eine abweichende Einheit hindeuten könnte. Die API-Definition macht dazu keine eindeutige Angabe.

## Wichtig

Das lokale Wattpilot-Protokoll ist keine offizielle öffentliche Fronius-Schnittstelle. Dieses Projekt nutzt die quelloffene Umsetzung `wattpilot-api`.

Der WebSocket-Zugang des Wattpilot sollte nicht aus dem Internet erreichbar sein.

## Diagnose

Unter Einstellungen, Geräte und Dienste beim Gerät gibt es **Diagnose herunterladen**. Die Datei enthält:

- alle vom Wattpilot gemeldeten Werte samt der daraus abgeleiteten Einzelwerte
- die vollständige Chipliste mit Namen, Zählerständen und der Angabe, ob eine Kennung hinterlegt ist
- in welcher Form das Gerät die Chips meldet (`kartenformat`)
- die laufende Transaktion und die Zugangsfreigabe
- welche Entitäten mangels Meldung übersprungen wurden

Zugangsdaten und Angaben, die das Gerät im Netz auffindbar machen, sind darin durch einen Platzhalter ersetzt.

## Verhalten unter Last

Die Bibliothek meldet jede geänderte Property einzeln. Eine Vollstatus-Nachricht des Wattpilot enthält rund 300 davon. Würde jede einzeln verarbeitet, schriebe jede Entität bei einer einzigen Nachricht dreihundertmal ihren Zustand neu.

Die Integration sammelt deshalb die Änderungen und verarbeitet sie einmal am Ende des laufenden Durchlaufs. Aus einer Nachricht wird genau eine Aktualisierung, ohne spürbare Verzögerung.

Die vollständigen Inhalte zusammengesetzter Werte, etwa die Chipliste oder die Liste gefundener WLAN-Netze, stehen in den Attributen, werden aber nicht in die Verlaufsdatenbank geschrieben.

## Fehlersuche

```yaml
logger:
  default: warning
  logs:
    custom_components.fronius_wattpilot_lutarym: debug
    wattpilot_api: debug
```
