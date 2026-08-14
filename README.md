# Fronius Wattpilot by Lutarym

A Home Assistant custom integration for local Fronius Wattpilot communication.

## Features

- Local Wattpilot communication
- WebSocket push updates
- Automatic reconnect
- Connection diagnostics
- Charging power/current
- Per-phase voltage/current/power when supplied by the API
- Total energy
- Vehicle connected / charging state
- Maximum current control
- Charging mode selection
- Device/firmware/serial information
- Config Flow
- HACS compatible

The integration does not require a Fronius cloud account.

## Installation

### HACS

Add this GitHub repository as a custom repository with category `Integration`, then install it.

### Manual

Copy `custom_components/fronius_wattpilot_lutarym` to `/config/custom_components/`.

Restart Home Assistant and add **Fronius Wattpilot by Lutarym** from Settings → Devices & services.

## Configuration

Only the local IP address and Wattpilot password are required.

The underlying `wattpilot-api` library handles the supported Wattpilot authentication variants.

## Important

The local Wattpilot protocol is not an official public Fronius API. This project uses the open-source `wattpilot-api` implementation.

Do not expose the Wattpilot WebSocket endpoint to the Internet.

## Debug logging

```yaml
logger:
  default: warning
  logs:
    custom_components.fronius_wattpilot_lutarym: debug
    wattpilot_api: debug
```
