"""Auswertung der RFID-Karten und der laufenden Transaktion.

Der Wattpilot meldet zwei Werte, aus denen sich die Zuordnung einer
Ladung zu einem Fahrzeug ergibt:

cards
    Eine Liste der im Geraet gespeicherten Karten. Jeder Eintrag hat
    einen Namen, einen Energiezaehler und die Angabe, ob ueberhaupt
    eine Kartenkennung hinterlegt ist.

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
    MAX_RFID_CARDS,
    PROP_CARDS,
    PROP_ENERGY_SESSION,
    PROP_TRANSACTION,
)

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


def parse_cards(data: dict[str, Any] | None) -> list[CardInfo]:
    """Liest die Kartenliste aus den Geraetedaten.

    Liefert alle Eintraege, auch die ungenutzten. Welche davon eine
    Entitaet bekommen, entscheidet registered_cards.
    """
    roh = (data or {}).get(PROP_CARDS)
    if not isinstance(roh, list):
        return []

    karten: list[CardInfo] = []
    for index, eintrag in enumerate(roh[:MAX_RFID_CARDS]):
        if not isinstance(eintrag, dict):
            continue
        name = eintrag.get("name")
        karten.append(
            CardInfo(
                index=index,
                name=str(name).strip() if name is not None else "",
                energy=_to_float(eintrag.get("energy")),
                registered=bool(eintrag.get("cardId")),
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
