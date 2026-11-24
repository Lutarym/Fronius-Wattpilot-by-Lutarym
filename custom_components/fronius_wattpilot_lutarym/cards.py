"""Auswertung der RFID-Karten und der laufenden Transaktion.

Der Wattpilot meldet zwei Werte, aus denen sich die Zuordnung einer
Ladung zu einem Fahrzeug ergibt:

cards
    Eine Liste der im Geraet gespeicherten Karten. Jeder Eintrag hat
    einen Namen, einen Energiezaehler und die Angabe, ob ueberhaupt
    eine Kartenkennung hinterlegt ist.

c0n, c0e, c0i bis c9n, c9e, c9i
    Neuere Firmware meldet statt der Liste je Karte eigene Schluessel
    fuer Name, Energie und Kartenkennung. Die go-e-Schluesselliste
    fuehrt sie ab Firmware 60.0 und vermerkt "cards" dort als entfernt.
    Gelesen wird beides, je nachdem, was das Geraet liefert.

trx
    Die laufende Transaktion. Leer bedeutet, dass keine Transaktion
    laeuft. Null bedeutet, dass ohne Karte geladen wird. Jeder andere
    Wert ist der Kartenindex plus eins, eine Eins steht also fuer die
    erste Karte.

Quelle: API-Definition der Bibliothek wattpilot-api 1.4.0 sowie die
Schluesselliste der go-e-API v2, die dasselbe Protokoll beschreibt.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from .const import (
    CARD_KEY_ENERGY,
    CARD_KEY_ID,
    CARD_KEY_NAME,
    MAX_RFID_CARDS,
    PROP_CARDS,
    PROP_ENERGY_SESSION,
    PROP_TRANSACTION,
)

# Kennzeichnung, in welcher Form das Geraet die Karten meldet
FORMAT_LIST = "cards"
FORMAT_KEYS = "einzelschluessel"

# Wert von trx, wenn ohne Karte geladen wird
TRANSACTION_WITHOUT_CARD = 0


@dataclass(frozen=True)
class CardInfo:
    """Eine einzelne im Wattpilot gespeicherte RFID-Karte."""

    index: int
    name: str
    energy: float | None
    registered: bool

    @property
    def display_name(self) -> str:
        """Name fuer die Anzeige, mit Rueckfall auf die Kartennummer."""
        return self.name or f"Karte {self.index + 1}"


def _to_float(value: Any) -> float | None:
    try:
        return float(value) if value is not None else None
    except (TypeError, ValueError):
        return None


def _ist_hinterlegt(value: Any) -> bool:
    """Ob eine Kartenkennung hinterlegt ist.

    Gemeldet wird true oder false. Ein Text wird vorsichtshalber auch
    verstanden, eine echte Kennung als Text zaehlt als hinterlegt.
    """
    if isinstance(value, str):
        return value.strip().lower() not in ("", "0", "false", "no", "off", "none", "null")
    return bool(value)


def _hat_einzelschluessel(daten: dict[str, Any], index: int) -> bool:
    """Ob das Geraet fuer diese Karte eigene Schluessel meldet."""
    return any(
        vorlage.format(index) in daten
        for vorlage in (CARD_KEY_NAME, CARD_KEY_ENERGY, CARD_KEY_ID)
    )


def card_format(data: dict[str, Any] | None) -> str | None:
    """In welcher Form das Geraet die Karten meldet, oder None."""
    daten = data or {}
    roh = daten.get(PROP_CARDS)
    if isinstance(roh, list) and roh:
        return FORMAT_LIST
    if any(_hat_einzelschluessel(daten, i) for i in range(MAX_RFID_CARDS)):
        return FORMAT_KEYS
    if isinstance(roh, list):
        return FORMAT_LIST
    return None


def parse_cards(data: dict[str, Any] | None) -> list[CardInfo]:
    """Liest die Karten aus den Geraetedaten.

    Verstanden wird die Liste "cards" und die Einzelschluessel c0n bis
    c9n, c0e bis c9e und c0i bis c9i. Liefert alle Eintraege, auch die
    ungenutzten. Welche davon eine Entitaet bekommen, entscheidet
    registered_cards.
    """
    daten = data or {}
    format_ = card_format(daten)

    karten: list[CardInfo] = []
    if format_ == FORMAT_LIST:
        for index, eintrag in enumerate(daten[PROP_CARDS][:MAX_RFID_CARDS]):
            if not isinstance(eintrag, dict):
                continue
            name = eintrag.get("name")
            karten.append(
                CardInfo(
                    index=index,
                    name=str(name).strip() if name is not None else "",
                    energy=_to_float(eintrag.get("energy")),
                    registered=_ist_hinterlegt(eintrag.get("cardId")),
                )
            )
        return karten

    if format_ == FORMAT_KEYS:
        for index in range(MAX_RFID_CARDS):
            if not _hat_einzelschluessel(daten, index):
                continue
            name = daten.get(CARD_KEY_NAME.format(index))
            karten.append(
                CardInfo(
                    index=index,
                    name=str(name).strip() if name is not None else "",
                    energy=_to_float(daten.get(CARD_KEY_ENERGY.format(index))),
                    registered=_ist_hinterlegt(daten.get(CARD_KEY_ID.format(index))),
                )
            )
    return karten


def registered_cards(data: dict[str, Any] | None) -> list[CardInfo]:
    """Nur die Karten, die tatsaechlich benutzt werden.

    Eine Karte zaehlt als benutzt, wenn eine Kartenkennung hinterlegt
    ist oder wenn bereits Energie darauf gebucht wurde. Der zweite Fall
    faengt Karten ab, deren Kennung spaeter geloescht wurde, deren
    Zaehlerstand aber erhalten bleiben soll.
    """
    return [
        karte
        for karte in parse_cards(data)
        if karte.registered or (karte.energy or 0) > 0
    ]


def card_by_index(data: dict[str, Any] | None, index: int) -> CardInfo | None:
    """Eine einzelne Karte anhand ihres Index."""
    for karte in parse_cards(data):
        if karte.index == index:
            return karte
    return None


def transaction(data: dict[str, Any] | None) -> int | None:
    """Der Rohwert der laufenden Transaktion, oder None."""
    wert = (data or {}).get(PROP_TRANSACTION)
    if wert is None:
        return None
    try:
        return int(wert)
    except (TypeError, ValueError):
        return None


def active_card_index(data: dict[str, Any] | None) -> int | None:
    """Index der Karte, die gerade vorgehalten wurde.

    Liefert None, wenn keine Transaktion laeuft oder ohne Karte
    geladen wird.
    """
    wert = transaction(data)
    if wert is None or wert <= TRANSACTION_WITHOUT_CARD:
        return None
    return wert - 1


def charging_without_card(data: dict[str, Any] | None) -> bool:
    """Ob gerade eine Ladung ohne Karte laeuft."""
    return transaction(data) == TRANSACTION_WITHOUT_CARD


def session_energy(
    previous: float | None,
    data: dict[str, Any] | None,
    index: int,
) -> float | None:
    """Fortgeschriebene Ladeenergie einer Karte.

    Haelt die Karte die laufende Transaktion, wird die Energie seit dem
    Anstecken uebernommen. Andernfalls bleibt der zuletzt gemerkte Wert
    stehen, damit nach dem Abstecken sichtbar bleibt, wie viel das
    Fahrzeug zuletzt geladen hat.

    Ein unbrauchbarer oder fehlender Messwert aendert nichts am bisher
    gemerkten Stand.
    """
    if active_card_index(data) != index:
        return previous

    wert = _to_float((data or {}).get(PROP_ENERGY_SESSION))
    return previous if wert is None else wert
