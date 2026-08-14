DOMAIN = "fronius_wattpilot_lutarym"
CONF_HOST = "host"
CONF_PASSWORD = "password"

DEFAULT_NAME = "Fronius Wattpilot"

# Known property aliases. The API has used short property names in different
# releases; entity code checks aliases instead of assuming one spelling.
PROP_ALIASES = {
    "power_total": ("power", "power_total", "total_power"),
    "energy_total": ("energy", "energy_total", "total_energy"),
    "current_total": ("amp", "amps", "current"),
    "vehicle_connected": ("car_connected", "carConnected"),
    "charging": ("charging", "car_charging"),
    "mode": ("mode",),
    "max_current": ("amp", "max_current", "max_amps"),
    "voltage1": ("voltage1", "volt1"),
    "voltage2": ("voltage2", "volt2"),
    "voltage3": ("voltage3", "volt3"),
    "current1": ("amps1", "amp1", "current1"),
    "current2": ("amps2", "amp2", "current2"),
    "current3": ("amps3", "amp3", "current3"),
    "power1": ("power1",),
    "power2": ("power2",),
    "power3": ("power3",),
}
