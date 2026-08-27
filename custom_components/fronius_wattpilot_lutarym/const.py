"""Konstanten und Entitaets-Beschreibungen fuer die Wattpilot-Integration.

Diese Datei wurde aus der API-Definition der Bibliothek wattpilot-api
erzeugt (wattpilot_api/resources/wattpilot.yaml, Version 1.4.0).

Jeder Eintrag beschreibt genau eine Property des Wattpilot:
  key           Property-Schluessel im Wattpilot-Protokoll
  name          Anzeigename
  unit          Masseinheit oder None
  device_class  Home-Assistant-Geraeteklasse oder None
  value_map     Zuordnung Zahlenwert -> Klartext oder None
  enabled       ob die Entitaet standardmaessig aktiv ist
  category      None, "config" oder "diagnostic"
  range         (min, max, schrittweite) fuer Number-Entitaeten
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

DOMAIN = "fronius_wattpilot_lutarym"

CONF_HOST = "host"
CONF_PASSWORD = "password"

DEFAULT_NAME = "Fronius Wattpilot"

# Dienst zum Setzen beliebiger Properties
SERVICE_SET_PROPERTY = "set_property"
ATTR_PROPERTY = "property"
ATTR_VALUE = "value"

# Property, die einen Neustart des Geraets ausloest
PROP_REBOOT = "rst"

# Property mit der Liste der registrierten RFID-Karten
PROP_CARDS = "cards"

# Hoechstzahl an RFID-Karten, fuer die Entitaeten angelegt werden
MAX_RFID_CARDS = 10


@dataclass(frozen=True)
class WattpilotDescription:
    """Beschreibung einer einzelnen Wattpilot-Property."""

    key: str
    name: str
    unit: str | None = None
    device_class: str | None = None
    value_map: dict[str, str] | None = None
    enabled: bool = False
    category: str | None = None
    range: tuple[float, float, float] | None = None
    state_class: str | None = None



SENSORS: tuple[WattpilotDescription, ...] = (
    WattpilotDescription(
        key="acu",
        name="Allowed Current",
        unit="A",
        device_class="current",
        enabled=True,
        state_class="measurement",
    ),
    WattpilotDescription(
        key="al1",
        name="Adapter Limit 1",
        unit="A",
        device_class="current",
        category="diagnostic",
        state_class="measurement",
    ),
    WattpilotDescription(
        key="al2",
        name="Adapter Limit 2",
        unit="A",
        device_class="current",
        category="diagnostic",
        state_class="measurement",
    ),
    WattpilotDescription(
        key="al3",
        name="Adapter Limit 3",
        unit="A",
        device_class="current",
        category="diagnostic",
        state_class="measurement",
    ),
    WattpilotDescription(
        key="al4",
        name="Adapter Limit 4",
        unit="A",
        device_class="current",
        category="diagnostic",
        state_class="measurement",
    ),
    WattpilotDescription(
        key="al5",
        name="Adapter Limit 5",
        unit="A",
        device_class="current",
        category="diagnostic",
        state_class="measurement",
    ),
    WattpilotDescription(
        key="amt",
        name="Temperature Current Limit",
        unit="A",
        device_class="current",
        enabled=True,
        state_class="measurement",
    ),
    WattpilotDescription(
        key="apd",
        name="Firmware Description",
        category="diagnostic",
    ),
    WattpilotDescription(
        key="apd_idf_ver",
        name="Firmware Description Idf Ver",
        category="diagnostic",
    ),
    WattpilotDescription(
        key="apd_project_name",
        name="Firmware Description Project Name",
        category="diagnostic",
    ),
    WattpilotDescription(
        key="apd_secure_version",
        name="Firmware Description Secure Version",
        category="diagnostic",
    ),
    WattpilotDescription(
        key="apd_sha256",
        name="Firmware Description Sha256",
        category="diagnostic",
    ),
    WattpilotDescription(
        key="apd_timestamp",
        name="Firmware Description Timestamp",
        category="diagnostic",
    ),
    WattpilotDescription(
        key="apd_version",
        name="Firmware Description Version",
        category="diagnostic",
    ),
    WattpilotDescription(
        key="arv",
        name="App Recommended Version",
        category="diagnostic",
    ),
    WattpilotDescription(
        key="awcp",
        name="Awattar Current Price",
        category="diagnostic",
    ),
    WattpilotDescription(
        key="awcp_end",
        name="Awattar Current Price End",
        enabled=True,
    ),
    WattpilotDescription(
        key="awcp_marketprice",
        name="Awattar Current Price Marketprice",
        enabled=True,
    ),
    WattpilotDescription(
        key="awcp_start",
        name="Awattar Current Price Start",
        enabled=True,
    ),
    WattpilotDescription(
        key="awpl",
        name="Awattar Price List",
        enabled=True,
    ),
    WattpilotDescription(
        key="car",
        name="Car State",
        value_map={"0": "Unknown/Error", "1": "Idle", "2": "Charging", "3": "WaitCar", "4": "Complete", "5": "Error"},
        enabled=True,
    ),
    WattpilotDescription(
        key="cards",
        name="Registered Cards",
        enabled=True,
    ),
    WattpilotDescription(
        key="cbl",
        name="Cable Current Limit",
        unit="A",
        device_class="current",
        enabled=True,
        state_class="measurement",
    ),
    WattpilotDescription(
        key="ccrv",
        name="Charge Controller Recommended Version",
        category="diagnostic",
    ),
    WattpilotDescription(
        key="ccu",
        name="Charge Controller Update Progress",
        category="diagnostic",
    ),
    WattpilotDescription(
        key="ccw",
        name="Currently Connected Wifi",
        category="diagnostic",
    ),
    WattpilotDescription(
        key="cdi",
        name="Charging Duration Info",
        category="diagnostic",
    ),
    WattpilotDescription(
        key="cdi_type",
        name="Charging Duration Type",
        value_map={"0": "Counter", "1": "Duration"},
        enabled=True,
    ),
    WattpilotDescription(
        key="cdi_value",
        name="Charging Duration Value",
        enabled=True,
    ),
    WattpilotDescription(
        key="clp",
        name="Current Limit Presets",
        category="diagnostic",
    ),
    WattpilotDescription(
        key="cus",
        name="Cable Unlock Status",
        value_map={"0": "Unknown", "1": "Unlocked", "2": "UnlockFailed", "3": "Locked", "4": "LockFailed", "5": "LockUnlockPowerout"},
        enabled=True,
    ),
    WattpilotDescription(
        key="cwsca",
        name="Cloud WS Connected Age",
        unit="ms",
        category="diagnostic",
    ),
    WattpilotDescription(
        key="deltaa",
        name="deltaCurrent",
        enabled=True,
    ),
    WattpilotDescription(
        key="deltap",
        name="Delta Power",
        unit="W",
        device_class="power",
        enabled=True,
        state_class="measurement",
    ),
    WattpilotDescription(
        key="dns",
        name="DNS Server",
        category="diagnostic",
    ),
    WattpilotDescription(
        key="ecf",
        name="ESP CPU Frequency",
        category="diagnostic",
    ),
    WattpilotDescription(
        key="ecf_div",
        name="ESP CPU Frequency Div",
        category="diagnostic",
    ),
    WattpilotDescription(
        key="ecf_freq_mhz",
        name="ESP CPU Frequency Freq Mhz",
        category="diagnostic",
    ),
    WattpilotDescription(
        key="ecf_source",
        name="ESP CPU Frequency Source",
        value_map={"0": "XTAL", "1": "PLL", "2": "8M", "3": "APLL"},
        category="diagnostic",
    ),
    WattpilotDescription(
        key="ecf_source_freq_mhz",
        name="ESP CPU Frequency Source Freq Mhz",
        category="diagnostic",
    ),
    WattpilotDescription(
        key="eci",
        name="ESP Chip Info",
        category="diagnostic",
    ),
    WattpilotDescription(
        key="eci_cores",
        name="ESP Chip Info Cores",
        category="diagnostic",
    ),
    WattpilotDescription(
        key="eci_features",
        name="ESP Chip Info Features",
        category="diagnostic",
    ),
    WattpilotDescription(
        key="eci_model",
        name="ESP Chip Info Model",
        value_map={"1": "ESP32", "2": "ESP32S2", "4": "ESP32S3", "5": "ESP32C3"},
        category="diagnostic",
    ),
    WattpilotDescription(
        key="eci_revision",
        name="ESP Chip Info Revision",
        category="diagnostic",
    ),
    WattpilotDescription(
        key="efh",
        name="ESP Free Heap",
        unit="B",
        device_class="data_size",
        category="diagnostic",
        state_class="measurement",
    ),
    WattpilotDescription(
        key="efh32",
        name="ESP Free Heap 32",
        unit="B",
        device_class="data_size",
        category="diagnostic",
        state_class="measurement",
    ),
    WattpilotDescription(
        key="efh8",
        name="ESP Free Heap 8",
        unit="B",
        device_class="data_size",
        category="diagnostic",
        state_class="measurement",
    ),
    WattpilotDescription(
        key="efi",
        name="ESP Flash Info",
        category="diagnostic",
    ),
    WattpilotDescription(
        key="efi_spi_mode",
        name="ESP Flash Info Spi Mode",
        value_map={"0": "QIO", "1": "QOUT", "2": "DIO", "3": "DOUT", "4": "FAST_READ", "5": "SLOW_READ"},
        category="diagnostic",
    ),
    WattpilotDescription(
        key="efi_spi_size",
        name="ESP Flash Info Spi Size",
        value_map={"0": "1MB", "1": "2MB", "2": "4MB", "3": "8MB", "4": "16MB", "5": "MAX"},
        category="diagnostic",
    ),
    WattpilotDescription(
        key="efi_spi_speed",
        name="ESP Flash Info Spi Speed",
        value_map={"0": "40M", "1": "26M", "2": "20M", "15": "80M"},
        category="diagnostic",
    ),
    WattpilotDescription(
        key="ehs",
        name="ESP Heap Size",
        unit="B",
        device_class="data_size",
        category="diagnostic",
        state_class="measurement",
    ),
    WattpilotDescription(
        key="emfh",
        name="ESP Min Free Heap",
        unit="B",
        device_class="data_size",
        category="diagnostic",
        state_class="measurement",
    ),
    WattpilotDescription(
        key="emhb",
        name="ESP Max Heap",
        unit="B",
        device_class="data_size",
        category="diagnostic",
        state_class="measurement",
    ),
    WattpilotDescription(
        key="err",
        name="Error State",
        value_map={"0": "None", "1": "FiAc", "2": "FiDc", "3": "Phase", "4": "Overvolt", "5": "Overamp", "6": "Diode", "7": "PpInvalid", "8": "GndInvalid", "9": "ContactorStuck", "10": "ContactorMiss", "11": "FiUnknown", "12": "Unknown", "13": "Overtemp", "14": "NoComm", "15": "StatusLockStuckOpen", "16": "StatusLockStuckLocked", "20": "Reserved20", "21": "Reserved21", "22": "Reserved22", "23": "Reserved23", "24": "Reserved24"},
        enabled=True,
    ),
    WattpilotDescription(
        key="esr",
        name="RTC Reset Reasons",
        value_map={"0": "NO_MEAN", "1": "POWERON_RESET", "3": "SW_RESET", "4": "OWDT_RESET", "5": "DEEPSLEEP_RESET", "6": "SDIO_RESET", "7": "TG0WDT_SYS_RESET", "8": "TG1WDT_SYS_RESET", "9": "RTCWDT_SYS_RESET", "10": "INTRUSION_RESET", "11": "TGWDT_CPU_RESET", "12": "SW_CPU_RESET", "13": "RTCWDT_CPU_RESET", "14": "EXT_CPU_RESET", "15": "RTCWDT_BROWN_OUT_RESET", "16": "RTCWDT_RTC_RESET"},
        category="diagnostic",
    ),
    WattpilotDescription(
        key="eto",
        name="Energy Counter Total",
        unit="Wh",
        device_class="energy",
        enabled=True,
        state_class="total_increasing",
    ),
    WattpilotDescription(
        key="etop",
        name="Energy Total Persisted",
        unit="Wh",
        device_class="energy",
        enabled=True,
        state_class="total_increasing",
    ),
    WattpilotDescription(
        key="fam",
        name="PV Battery Limit",
        enabled=True,
        range=(0, 100, 1),
    ),
    WattpilotDescription(
        key="fbuf_age",
        name="Fronius Age",
        enabled=True,
    ),
    WattpilotDescription(
        key="fbuf_akkuMode",
        name="Battery Mode",
        enabled=True,
    ),
    WattpilotDescription(
        key="fbuf_akkuSOC",
        name="Battery SoC",
        unit="%",
        enabled=True,
    ),
    WattpilotDescription(
        key="fbuf_ohmpilotState",
        name="Ohmpilot State",
        category="diagnostic",
    ),
    WattpilotDescription(
        key="fbuf_ohmpilotTemperature",
        name="Ohmpilot Temperature",
        category="diagnostic",
    ),
    WattpilotDescription(
        key="fbuf_pAcTotal",
        name="Power AC Total",
        unit="W",
        device_class="power",
        enabled=True,
        state_class="measurement",
    ),
    WattpilotDescription(
        key="fbuf_pAkku",
        name="Power Akku",
        unit="W",
        device_class="power",
        enabled=True,
        state_class="measurement",
    ),
    WattpilotDescription(
        key="fbuf_pGrid",
        name="Power Grid",
        unit="W",
        device_class="power",
        enabled=True,
        state_class="measurement",
    ),
    WattpilotDescription(
        key="fbuf_pPv",
        name="Power PV",
        unit="W",
        device_class="power",
        enabled=True,
        state_class="measurement",
    ),
    WattpilotDescription(
        key="fem",
        name="Flash Encryption Mode",
        value_map={"0": "Disabled", "1": "Development", "2": "Release"},
        category="diagnostic",
    ),
    WattpilotDescription(
        key="ferm",
        name="Effective Rounding Mode",
        category="diagnostic",
    ),
    WattpilotDescription(
        key="ffb",
        name="Lock Feedback",
        value_map={"0": "NoProblem", "1": "ProblemLock", "2": "ProblemUnlock"},
        enabled=True,
    ),
    WattpilotDescription(
        key="ffba",
        name="Lock Feedback Age",
        unit="ms",
        category="diagnostic",
    ),
    WattpilotDescription(
        key="ffna",
        name="Factory Friendly Name",
        category="diagnostic",
    ),
    WattpilotDescription(
        key="fhz",
        name="Frequency",
        unit="Hz",
        device_class="frequency",
        enabled=True,
        state_class="measurement",
    ),
    WattpilotDescription(
        key="fot",
        name="Ohmpilot Temperature Limit",
        unit="°C",
        device_class="temperature",
        category="config",
        range=(0, 100, 1),
        state_class="measurement",
    ),
    WattpilotDescription(
        key="frm",
        name="Rounding Mode",
        value_map={"0": "PreferPowerFromGrid", "1": "Default", "2": "PreferPowerToGrid"},
        category="diagnostic",
    ),
    WattpilotDescription(
        key="fsptws",
        name="Force Single Phase Toggle Wished Since",
        unit="ms",
        category="diagnostic",
    ),
    WattpilotDescription(
        key="fwan",
        name="Factory WiFi AP Name",
        category="diagnostic",
    ),
    WattpilotDescription(
        key="fwc",
        name="Firmware Car Control",
        category="diagnostic",
    ),
    WattpilotDescription(
        key="fwv",
        name="Firmware Version",
        enabled=True,
    ),
    WattpilotDescription(
        key="host",
        name="Hostname",
        category="diagnostic",
    ),
    WattpilotDescription(
        key="ido",
        name="Inverter Data Override",
        category="diagnostic",
    ),
    WattpilotDescription(
        key="inva",
        name="Inverter Data Age",
        unit="ms",
        enabled=True,
    ),
    WattpilotDescription(
        key="lbp",
        name="Last Button Press",
        unit="ms",
        category="diagnostic",
    ),
    WattpilotDescription(
        key="lccfc",
        name="Last Car State Changed From Charging",
        unit="ms",
        category="diagnostic",
    ),
    WattpilotDescription(
        key="lccfi",
        name="Last Car State Changed From Idle",
        unit="ms",
        category="diagnostic",
    ),
    WattpilotDescription(
        key="lcctc",
        name="Last Car State Changed To Charging",
        unit="ms",
        category="diagnostic",
    ),
    WattpilotDescription(
        key="lck",
        name="Effective Lock Setting",
        value_map={"0": "Normal", "1": "AutoUnlock", "2": "AlwaysLock", "3": "ForceUnlock"},
        category="diagnostic",
    ),
    WattpilotDescription(
        key="led",
        name="LED Info",
        category="diagnostic",
    ),
    WattpilotDescription(
        key="lfspt",
        name="Last Force Single Phase Toggle",
        unit="ms",
        category="diagnostic",
    ),
    WattpilotDescription(
        key="lmsc",
        name="Last Model Status Change",
        unit="ms",
        category="diagnostic",
    ),
    WattpilotDescription(
        key="loa",
        name="Load Balancing Current",
        category="diagnostic",
    ),
    WattpilotDescription(
        key="loc",
        name="Local Time",
        enabled=True,
    ),
    WattpilotDescription(
        key="lom",
        name="Load Balancing Members",
        category="diagnostic",
    ),
    WattpilotDescription(
        key="los",
        name="Load Balancing Status",
        category="diagnostic",
    ),
    WattpilotDescription(
        key="lpsc",
        name="Last PV Surplus Calculation",
        unit="ms",
        category="diagnostic",
    ),
    WattpilotDescription(
        key="lssfc",
        name="Last STA Switched From Connected",
        unit="ms",
        category="diagnostic",
    ),
    WattpilotDescription(
        key="lsstc",
        name="Last STA Switched To Connected",
        unit="ms",
        category="diagnostic",
    ),
    WattpilotDescription(
        key="map",
        name="Load Mapping",
        enabled=True,
    ),
    WattpilotDescription(
        key="mcpea",
        name="Min Charge Pause End",
        unit="ms",
        category="diagnostic",
    ),
    WattpilotDescription(
        key="mod",
        name="Module HW PCB Version",
        category="diagnostic",
    ),
    WattpilotDescription(
        key="modelStatus",
        name="Model Status",
        value_map={"0": "NotChargingBecauseNoChargeCtrlData", "1": "NotChargingBecauseOvertemperature", "2": "NotChargingBecauseAccessControlWait", "3": "ChargingBecauseForceStateOn", "4": "NotChargingBecauseForceStateOff", "5": "NotChargingBecauseScheduler", "6": "NotChargingBecauseEnergyLimit", "7": "ChargingBecauseAwattarPriceLow", "8": "ChargingBecauseAutomaticStopTestLadung", "9": "ChargingBecauseAutomaticStopNotEnoughTime", "10": "ChargingBecauseAutomaticStop", "11": "ChargingBecauseAutomaticStopNoClock", "12": "ChargingBecausePvSurplus", "13": "ChargingBecauseFallbackGoEDefault", "14": "ChargingBecauseFallbackGoEScheduler", "15": "ChargingBecauseFallbackDefault", "16": "NotChargingBecauseFallbackGoEAwattar", "17": "NotChargingBecauseFallbackAwattar", "18": "NotChargingBecauseFallbackAutomaticStop", "19": "ChargingBecauseCarCompatibilityKeepAlive", "20": "ChargingBecauseChargePauseNotAllowed", "22": "NotChargingBecauseSimulateUnplugging", "23": "NotChargingBecausePhaseSwitch", "24": "NotChargingBecauseMinPauseDuration"},
        enabled=True,
    ),
    WattpilotDescription(
        key="msi",
        name="Model Status Internal",
        value_map={"0": "NotChargingBecauseNoChargeCtrlData", "1": "NotChargingBecauseOvertemperature", "2": "NotChargingBecauseAccessControlWait", "3": "ChargingBecauseForceStateOn", "4": "NotChargingBecauseForceStateOff", "5": "NotChargingBecauseScheduler", "6": "NotChargingBecauseEnergyLimit", "7": "ChargingBecauseAwattarPriceLow", "8": "ChargingBecauseAutomaticStopTestLadung", "9": "ChargingBecauseAutomaticStopNotEnoughTime", "10": "ChargingBecauseAutomaticStop", "11": "ChargingBecauseAutomaticStopNoClock", "12": "ChargingBecausePvSurplus", "13": "ChargingBecauseFallbackGoEDefault", "14": "ChargingBecauseFallbackGoEScheduler", "15": "ChargingBecauseFallbackDefault", "16": "NotChargingBecauseFallbackGoEAwattar", "17": "NotChargingBecauseFallbackAwattar", "18": "NotChargingBecauseFallbackAutomaticStop", "19": "ChargingBecauseCarCompatibilityKeepAlive", "20": "ChargingBecauseChargePauseNotAllowed", "22": "NotChargingBecauseSimulateUnplugging", "23": "NotChargingBecausePhaseSwitch", "24": "NotChargingBecauseMinPauseDuration"},
        category="diagnostic",
    ),
    WattpilotDescription(
        key="nif",
        name="Default Route",
        category="diagnostic",
    ),
    WattpilotDescription(
        key="nrg",
        name="Charging Energy",
        category="diagnostic",
    ),
    WattpilotDescription(
        key="nrg_il1",
        name="Charging Current L1",
        unit="A",
        device_class="current",
        enabled=True,
        state_class="measurement",
    ),
    WattpilotDescription(
        key="nrg_il2",
        name="Charging Current L2",
        unit="A",
        device_class="current",
        enabled=True,
        state_class="measurement",
    ),
    WattpilotDescription(
        key="nrg_il3",
        name="Charging Current L3",
        unit="A",
        device_class="current",
        enabled=True,
        state_class="measurement",
    ),
    WattpilotDescription(
        key="nrg_pfl1",
        name="Charging Power Factor L1",
        unit="%",
        enabled=True,
    ),
    WattpilotDescription(
        key="nrg_pfl2",
        name="Charging Power Factor L2",
        unit="%",
        enabled=True,
    ),
    WattpilotDescription(
        key="nrg_pfl3",
        name="Charging Power Factor L3",
        unit="%",
        enabled=True,
    ),
    WattpilotDescription(
        key="nrg_pfn",
        name="Charging Power Factor N",
        unit="%",
        enabled=True,
    ),
    WattpilotDescription(
        key="nrg_pl1",
        name="Charging Power L1",
        unit="W",
        device_class="power",
        enabled=True,
        state_class="measurement",
    ),
    WattpilotDescription(
        key="nrg_pl2",
        name="Charging Power L2",
        unit="W",
        device_class="power",
        enabled=True,
        state_class="measurement",
    ),
    WattpilotDescription(
        key="nrg_pl3",
        name="Charging Power L3",
        unit="W",
        device_class="power",
        enabled=True,
        state_class="measurement",
    ),
    WattpilotDescription(
        key="nrg_pn",
        name="Charging Power N",
        unit="W",
        device_class="power",
        enabled=True,
        state_class="measurement",
    ),
    WattpilotDescription(
        key="nrg_ptotal",
        name="Charging Power Total",
        unit="W",
        device_class="power",
        enabled=True,
        state_class="measurement",
    ),
    WattpilotDescription(
        key="nrg_ul1",
        name="Charging Voltage L1",
        unit="V",
        device_class="voltage",
        enabled=True,
        state_class="measurement",
    ),
    WattpilotDescription(
        key="nrg_ul2",
        name="Charging Voltage L2",
        unit="V",
        device_class="voltage",
        enabled=True,
        state_class="measurement",
    ),
    WattpilotDescription(
        key="nrg_ul3",
        name="Charging Voltage L3",
        unit="V",
        device_class="voltage",
        enabled=True,
        state_class="measurement",
    ),
    WattpilotDescription(
        key="nrg_un",
        name="Charging Voltage N",
        unit="V",
        device_class="voltage",
        enabled=True,
        state_class="measurement",
    ),
    WattpilotDescription(
        key="oca",
        name="OTA Cloud App",
        category="diagnostic",
    ),
    WattpilotDescription(
        key="ocl",
        name="OTA Cloud Length",
        category="diagnostic",
    ),
    WattpilotDescription(
        key="ocm",
        name="OTA Cloud Message",
        category="diagnostic",
    ),
    WattpilotDescription(
        key="ocp",
        name="OTA Cloud Progress",
        category="diagnostic",
    ),
    WattpilotDescription(
        key="ocs",
        name="OTA Cloud Status",
        value_map={"0": "Idle", "1": "Updating", "2": "Failed", "3": "Succeeded"},
        category="diagnostic",
    ),
    WattpilotDescription(
        key="ocu",
        name="OTA Cloud Branches",
        category="diagnostic",
    ),
    WattpilotDescription(
        key="oem",
        name="OEM Manufacturer",
        category="diagnostic",
    ),
    WattpilotDescription(
        key="onv",
        name="OTA Newest Version",
        category="diagnostic",
    ),
    WattpilotDescription(
        key="otap",
        name="OTA Partition",
        category="diagnostic",
    ),
    WattpilotDescription(
        key="pakku",
        name="Power Akku",
        category="diagnostic",
    ),
    WattpilotDescription(
        key="part",
        name="Partition Table",
        category="diagnostic",
    ),
    WattpilotDescription(
        key="pgrid",
        name="Power Grid",
        category="diagnostic",
    ),
    WattpilotDescription(
        key="pha",
        name="Phases",
        category="diagnostic",
    ),
    WattpilotDescription(
        key="pnp",
        name="Number of Phases",
        category="diagnostic",
    ),
    WattpilotDescription(
        key="ppv",
        name="Power PV",
        category="diagnostic",
    ),
    WattpilotDescription(
        key="pto",
        name="Partition Table Offset",
        category="diagnostic",
    ),
    WattpilotDescription(
        key="pvopt_averagePAkku",
        name="Average Power Akku",
        unit="W",
        device_class="power",
        enabled=True,
        state_class="measurement",
    ),
    WattpilotDescription(
        key="pvopt_averagePGrid",
        name="Average Power Grid",
        unit="W",
        device_class="power",
        enabled=True,
        state_class="measurement",
    ),
    WattpilotDescription(
        key="pvopt_averagePOhmpilot",
        name="Average Power Ohmpilot",
        unit="W",
        device_class="power",
        category="diagnostic",
        state_class="measurement",
    ),
    WattpilotDescription(
        key="pvopt_averagePPv",
        name="Average Power PV",
        unit="W",
        device_class="power",
        enabled=True,
        state_class="measurement",
    ),
    WattpilotDescription(
        key="pvopt_deltaA",
        name="Delta Current",
        unit="A",
        device_class="current",
        enabled=True,
        state_class="measurement",
    ),
    WattpilotDescription(
        key="pvopt_deltaP",
        name="Delta Power",
        unit="W",
        device_class="power",
        enabled=True,
        state_class="measurement",
    ),
    WattpilotDescription(
        key="pvopt_specialCase",
        name="PVOpt Special Case",
        category="diagnostic",
    ),
    WattpilotDescription(
        key="pwm",
        name="Phase Wish Mode",
        value_map={"0": "Force_3", "1": "Wish_1", "2": "Wish_3"},
        category="diagnostic",
    ),
    WattpilotDescription(
        key="qsc",
        name="Queue Size Cloud",
        category="diagnostic",
    ),
    WattpilotDescription(
        key="qsw",
        name="Queue Size WS",
        category="diagnostic",
    ),
    WattpilotDescription(
        key="rbc",
        name="Reboot Counter",
        category="diagnostic",
    ),
    WattpilotDescription(
        key="rbt",
        name="Time Since Boot",
        unit="ms",
        category="diagnostic",
    ),
    WattpilotDescription(
        key="rcd",
        name="Residual Current Detection",
        unit="us",
        category="diagnostic",
    ),
    WattpilotDescription(
        key="rfb",
        name="Relay Feedback",
        category="diagnostic",
    ),
    WattpilotDescription(
        key="rr",
        name="ESP Reset Reason",
        value_map={"0": "UNKNOWN", "1": "POWERON", "2": "EXT", "3": "SW", "4": "PANIC", "5": "INT_WDT", "6": "TASK_WDT", "7": "WDT", "8": "DEEPSLEEP", "9": "BROWNOUT", "10": "SDIO"},
        category="diagnostic",
    ),
    WattpilotDescription(
        key="rssi",
        name="WIFI Signal Strength",
        unit="dBm",
        device_class="signal_strength",
        enabled=True,
        state_class="measurement",
    ),
    WattpilotDescription(
        key="scaa",
        name="WiFi Scan Age",
        unit="ms",
        category="diagnostic",
    ),
    WattpilotDescription(
        key="scan",
        name="Scanned WIFI Hotspots",
        category="diagnostic",
    ),
    WattpilotDescription(
        key="scas",
        name="WIFI Scan Status",
        value_map={"0": "None", "1": "Scanning", "2": "Finished", "3": "Failed"},
        category="diagnostic",
    ),
    WattpilotDescription(
        key="sch_satur",
        name="Charging Schedule Saturday",
        enabled=True,
    ),
    WattpilotDescription(
        key="sch_satur_control",
        name="Charging Schedule Saturday Control",
        value_map={"0": "Disabled", "1": "Inside", "2": "Outside"},
        enabled=True,
    ),
    WattpilotDescription(
        key="sch_sund",
        name="Charging Schedule Sunday",
        enabled=True,
    ),
    WattpilotDescription(
        key="sch_sund_control",
        name="Charging Schedule Sunday Control",
        value_map={"0": "Disabled", "1": "Inside", "2": "Outside"},
        enabled=True,
    ),
    WattpilotDescription(
        key="sch_week",
        name="Charging Schedule Weekday",
        enabled=True,
    ),
    WattpilotDescription(
        key="sch_week_control",
        name="Charging Schedule Weekday Control",
        value_map={"0": "Disabled", "1": "Inside", "2": "Outside"},
        enabled=True,
    ),
    WattpilotDescription(
        key="sse",
        name="Serial Number",
        enabled=True,
    ),
    WattpilotDescription(
        key="tma",
        name="Temperature Sensors",
        category="diagnostic",
    ),
    WattpilotDescription(
        key="tma_1",
        name="Temperature Sensor 1",
        unit="°C",
        device_class="temperature",
        enabled=True,
        state_class="measurement",
    ),
    WattpilotDescription(
        key="tma_2",
        name="Temperature Sensor 2",
        unit="°C",
        device_class="temperature",
        enabled=True,
        state_class="measurement",
    ),
    WattpilotDescription(
        key="tpa",
        name="Total Power Average",
        category="diagnostic",
    ),
    WattpilotDescription(
        key="ts",
        name="Time Server",
        category="diagnostic",
    ),
    WattpilotDescription(
        key="tsom",
        name="Time Server Operating Mode",
        value_map={"0": "POLL", "1": "LISTENONLY"},
        category="diagnostic",
    ),
    WattpilotDescription(
        key="tssi",
        name="Time Server Sync Interval",
        unit="ms",
        category="diagnostic",
    ),
    WattpilotDescription(
        key="tssm",
        name="Time Server Sync Mode",
        value_map={"0": "IMMED", "1": "SMOOTH"},
        category="diagnostic",
    ),
    WattpilotDescription(
        key="tsss",
        name="Time Server Sync Status",
        value_map={"0": "RESET", "1": "COMPLETED", "2": "IN_PROGRESS"},
        category="diagnostic",
    ),
    WattpilotDescription(
        key="typ",
        name="Device Type",
        enabled=True,
    ),
    WattpilotDescription(
        key="var",
        name="Variant",
        value_map={"11": "11kW/16A", "22": "22kW/32A"},
        enabled=True,
    ),
    WattpilotDescription(
        key="wcb",
        name="WiFi Current MAC Address",
        category="diagnostic",
    ),
    WattpilotDescription(
        key="wcch",
        name="HTTP Connected Clients",
        category="diagnostic",
    ),
    WattpilotDescription(
        key="wccw",
        name="WS Connected Clients",
        category="diagnostic",
    ),
    WattpilotDescription(
        key="wfb",
        name="WiFi Failed MAC Address",
        category="diagnostic",
    ),
    WattpilotDescription(
        key="wh",
        name="Energy Counter Since Start",
        unit="Wh",
        device_class="energy",
        enabled=True,
        state_class="total_increasing",
    ),
    WattpilotDescription(
        key="wpb",
        name="WiFi Planned MAC",
        category="diagnostic",
    ),
    WattpilotDescription(
        key="wsc",
        name="WiFi STA Error Count",
        category="diagnostic",
    ),
    WattpilotDescription(
        key="wsm",
        name="Wifi STA Error Message",
        category="diagnostic",
    ),
    WattpilotDescription(
        key="wsms",
        name="WIFI State Machine State",
        value_map={"0": "None", "1": "Scanning", "2": "Connecting", "3": "Connected"},
        category="diagnostic",
    ),
    WattpilotDescription(
        key="wss",
        name="WIFI SSID",
        category="diagnostic",
    ),
    WattpilotDescription(
        key="wst",
        name="WIFI STA Status",
        value_map={"0": "IDLE_STATUS", "1": "NO_SSID_AVAIL", "2": "SCAN_COMPLETED", "3": "CONNECTED", "4": "CONNECT_FAILED", "5": "CONNECTION_LOST", "6": "DISCONNECTED", "8": "CONNECTING", "9": "DISCONNECTING", "10": "NO_SHIELD"},
        category="diagnostic",
    ),
)


BINARY_SENSORS: tuple[WattpilotDescription, ...] = (
    WattpilotDescription(
        key="adi",
        name="Adapter (16A) Limit",
        enabled=True,
    ),
    WattpilotDescription(
        key="alw",
        name="Allow Charging",
        enabled=True,
    ),
    WattpilotDescription(
        key="cca",
        name="Cloud Client Auth",
        category="diagnostic",
    ),
    WattpilotDescription(
        key="cpe",
        name="CP Enable",
        category="diagnostic",
    ),
    WattpilotDescription(
        key="cpr",
        name="CP Enable Request",
        category="diagnostic",
    ),
    WattpilotDescription(
        key="cws",
        name="Cloud WS Started",
        category="diagnostic",
    ),
    WattpilotDescription(
        key="cwsc",
        name="Cloud WS Connected",
        category="diagnostic",
    ),
    WattpilotDescription(
        key="ful",
        name="useDynamicPricing",
        enabled=True,
    ),
    WattpilotDescription(
        key="ocuca",
        name="OTA Cloud Use Client Auth",
        category="diagnostic",
    ),
    WattpilotDescription(
        key="sbe",
        name="Secure Boot Enabled",
        category="diagnostic",
    ),
)


NUMBERS: tuple[WattpilotDescription, ...] = (
    WattpilotDescription(
        key="ama",
        name="Max Current Limit",
        unit="A",
        device_class="current",
        enabled=True,
        range=(6, 32, 1),
    ),
    WattpilotDescription(
        key="amp",
        name="Charging Current",
        unit="A",
        device_class="current",
        enabled=True,
        range=(6, 32, 1),
    ),
    WattpilotDescription(
        key="awp",
        name="Awattar Max Price",
        enabled=True,
        range=(-100, 100, 0.1),
    ),
    WattpilotDescription(
        key="cco",
        name="Car Consumption",
        enabled=True,
        category="config",
        range=(0, 100, 0.1),
    ),
    WattpilotDescription(
        key="dwo",
        name="Charging Energy Limit",
        unit="Wh",
        device_class="energy",
        enabled=True,
        range=(0, 100000, 100),
    ),
    WattpilotDescription(
        key="fmt",
        name="Min Charge Time",
        unit="ms",
        enabled=True,
        range=(0, 7200000, 60000),
    ),
    WattpilotDescription(
        key="fst",
        name="Starting Power",
        unit="W",
        device_class="power",
        enabled=True,
        range=(-10000, 10000, 100),
    ),
    WattpilotDescription(
        key="lbr",
        name="LED Brightness",
        enabled=True,
        category="config",
        range=(0, 255, 1),
    ),
    WattpilotDescription(
        key="lof",
        name="Load Fallback",
        unit="A",
        device_class="current",
        enabled=True,
        range=(0, 32, 1),
    ),
    WattpilotDescription(
        key="lop",
        name="Load Priority",
        enabled=True,
        category="config",
        range=(0, 100, 1),
    ),
    WattpilotDescription(
        key="lot",
        name="Load Balancing Current Total",
        unit="A",
        device_class="current",
        enabled=True,
        range=(6, 200, 1),
    ),
    WattpilotDescription(
        key="mca",
        name="Min Charging Current",
        unit="A",
        device_class="current",
        enabled=True,
        range=(6, 32, 1),
    ),
    WattpilotDescription(
        key="mci",
        name="Minimum Charging Interval",
        unit="ms",
        enabled=True,
        range=(0, 3600000, 60000),
    ),
    WattpilotDescription(
        key="mcpd",
        name="Min Charge Pause Duration",
        unit="ms",
        category="config",
        range=(0, 3600000, 60000),
    ),
    WattpilotDescription(
        key="mptwt",
        name="Min Phase Toggle Wait Time",
        unit="ms",
        category="config",
        range=(0, 600000, 10000),
    ),
    WattpilotDescription(
        key="mpwst",
        name="Min Phase Wish Switch Time",
        unit="ms",
        category="config",
        range=(0, 600000, 10000),
    ),
    WattpilotDescription(
        key="po",
        name="Prio Offset",
        unit="W",
        device_class="power",
        enabled=True,
        range=(-5000, 5000, 50),
    ),
    WattpilotDescription(
        key="psh",
        name="Phase Switch Hysteresis",
        unit="W",
        device_class="power",
        enabled=True,
        range=(0, 5000, 50),
    ),
    WattpilotDescription(
        key="psmd",
        name="Force Single Phase Duration",
        unit="ms",
        category="config",
        range=(0, 3600000, 60000),
    ),
    WattpilotDescription(
        key="sh",
        name="Stop Hysteresis",
        unit="W",
        device_class="power",
        enabled=True,
        range=(0, 5000, 50),
    ),
    WattpilotDescription(
        key="spl3",
        name="Three Phase Switch Level",
        unit="W",
        device_class="power",
        enabled=True,
        range=(0, 20000, 100),
    ),
    WattpilotDescription(
        key="sumd",
        name="Simulate Unplugging Duration",
        unit="ms",
        category="config",
        range=(0, 600000, 10000),
    ),
    WattpilotDescription(
        key="tof",
        name="Timezone Offset",
        unit="min",
        category="config",
        range=(-720, 840, 15),
    ),
    WattpilotDescription(
        key="trx",
        name="Transaction",
        enabled=True,
        range=(0, 10, 1),
    ),
    WattpilotDescription(
        key="zfo",
        name="Zero Feedin Offset",
        unit="W",
        device_class="power",
        enabled=True,
        range=(-5000, 5000, 50),
    ),
)


SELECTS: tuple[WattpilotDescription, ...] = (
    WattpilotDescription(
        key="acs",
        name="Access State",
        value_map={"0": "Open", "1": "Wait"},
        enabled=True,
        category="config",
    ),
    WattpilotDescription(
        key="awc",
        name="Awattar Country",
        value_map={"0": "Austria", "1": "Germany"},
        enabled=True,
        category="config",
    ),
    WattpilotDescription(
        key="frc",
        name="Force State",
        value_map={"0": "Neutral", "1": "Off", "2": "On"},
        enabled=True,
    ),
    WattpilotDescription(
        key="lmo",
        name="Logic Mode",
        value_map={"3": "Default", "4": "Awattar", "5": "AutomaticStop"},
        enabled=True,
    ),
    WattpilotDescription(
        key="loty",
        name="Load Balancing Type",
        value_map={"0": "Static", "1": "Dynamic"},
        enabled=True,
        category="config",
    ),
    WattpilotDescription(
        key="psm",
        name="Phase Switch Mode",
        value_map={"0": "Auto", "1": "Force_1", "2": "Force_3"},
        enabled=True,
        category="config",
    ),
    WattpilotDescription(
        key="tds",
        name="Timezone Daylight Saving Mode",
        value_map={"0": "None", "1": "EuropeanSummerTime", "2": "UsDaylightTime"},
        category="config",
    ),
    WattpilotDescription(
        key="ust",
        name="Unlock Setting",
        value_map={"0": "Normal", "1": "AutoUnlock", "2": "AlwaysLock"},
        enabled=True,
        category="config",
    ),
)


SWITCHS: tuple[WattpilotDescription, ...] = (
    WattpilotDescription(
        key="bac",
        name="Button Allow Current Change",
        enabled=True,
        category="config",
    ),
    WattpilotDescription(
        key="cwe",
        name="Cloud WS Enabled",
        category="config",
    ),
    WattpilotDescription(
        key="esk",
        name="Energy Set kWh",
        enabled=True,
        category="config",
    ),
    WattpilotDescription(
        key="fsp",
        name="Force Single Phase",
        enabled=True,
    ),
    WattpilotDescription(
        key="fup",
        name="PV Surplus",
        enabled=True,
    ),
    WattpilotDescription(
        key="fzf",
        name="Zero Feedin",
        enabled=True,
    ),
    WattpilotDescription(
        key="hsa",
        name="HTTP STA Authentication",
        category="config",
    ),
    WattpilotDescription(
        key="hws",
        name="HTTP STA Reachable",
        category="config",
    ),
    WattpilotDescription(
        key="loe",
        name="Load Balancing Enabled",
        enabled=True,
    ),
    WattpilotDescription(
        key="lse",
        name="LED Save Energy",
        category="config",
    ),
    WattpilotDescription(
        key="nmo",
        name="Norway Mode",
        category="config",
    ),
    WattpilotDescription(
        key="su",
        name="Simulate Unplugging",
        category="config",
    ),
    WattpilotDescription(
        key="sua",
        name="Simulate Unplugging Always",
        category="config",
    ),
    WattpilotDescription(
        key="tse",
        name="Time Server Enabled",
        category="config",
    ),
    WattpilotDescription(
        key="upo",
        name="Unlock Power Outage",
        category="config",
    ),
    WattpilotDescription(
        key="wen",
        name="WiFi Enabled",
        category="config",
    ),
)


TEXTS: tuple[WattpilotDescription, ...] = (
    WattpilotDescription(
        key="cch",
        name="Color Charging",
        category="config",
    ),
    WattpilotDescription(
        key="cfi",
        name="Color Finished",
        category="config",
    ),
    WattpilotDescription(
        key="cid",
        name="Color Idle",
        category="config",
    ),
    WattpilotDescription(
        key="ct",
        name="Car Type",
        enabled=True,
        category="config",
    ),
    WattpilotDescription(
        key="cwc",
        name="Color Wait Car",
        category="config",
    ),
    WattpilotDescription(
        key="fna",
        name="Friendly Name",
        enabled=True,
        category="config",
    ),
    WattpilotDescription(
        key="log",
        name="Load Group ID",
        enabled=True,
        category="config",
    ),
    WattpilotDescription(
        key="utc",
        name="UTC Time",
        enabled=True,
    ),
    WattpilotDescription(
        key="wan",
        name="WiFi AP Name",
        category="config",
    ),
)

