# ha-dae

DAE integration for Home Assistant.

## Features
- Sensors for raw meter values

## Installation
First add this repository [as a custom repository](https://hacs.xyz/docs/faq/custom_repositories/).

## Setup
[![Open your Home Assistant instance and start setting up a new integration.](https://my.home-assistant.io/badges/config_flow_start.svg)](https://my.home-assistant.io/redirect/config_flow_start/?domain=dae)

## Development
Run the following to set up your development environment
```shell
python3 -m venv venv
source venv/bin/activate
pip3 install -r requirements_test.txt
```
To run Home Assistant with this integration loaded:
```shell
hass -c config
```
### Testing
To run unit tests with coverage:
```shell
pytest tests --cov=custom_components.dae --cov-report term-missing
```

### Releasing
[Create a new GitHub release](https://github.com/ScottG489/ha-dae/releases/new). The [release workflow](https://github.com/ScottG489/ha-dae/blob/master/.github/workflows/release.yaml) takes care of the rest.
When finished, it will be available to download via HACS.
