from __future__ import annotations

from dataclasses import dataclass

import requests
from http.cookies import SimpleCookie


class DaeClient:
    """Client for dae API."""

    def __init__(self, username: str, password: str) -> None:
        """Initialize with credentials."""
        self.username = username
        self.password = password

        self.base_url = "https://meter.iotems.net/ws/home-owner.php"
        self.auth_cookies = SimpleCookie()

    def get_channel_meters(self) -> dict:
        """Get channel and meter data."""
        self.login()
        channels = self.list_circuits()
        meters = self.read_meters()

        channel_meters = {}
        for meter in meters.data:
            channel_for_meter = next(filter(lambda x: x.channel_id == meter.channel_id, channels.data))
            channel_meters[meter.channel_id] = MeterDevice(channel_for_meter, meter)

        return channel_meters

    def login(self) -> LoginResponse:
        """Login and set auth cookie."""
        action_type = "login"
        data = {'d': action_type, 'username': self.username, 'password': self.password}

        r = requests.post(self.base_url, data=data)
        self.auth_cookies.load(r.headers['Set-Cookie'])

        rj = r.json()
        return LoginResponse(rj['result'], rj['message'], rj.get('data'))

    def list_circuits(self) -> ListCircuitsResponse:
        """List circuits."""
        action_type = "channel"
        operation_type = "list"
        data = {'d': action_type, 'm': operation_type, 'username': self.username}

        r = requests.post(self.base_url, data=data, cookies={'PHPSESSID': self.auth_cookies['PHPSESSID'].value})
        rj = r.json()

        channels = []
        for channel in rj.get('data')[0]:
            channels.append(Channel(channel['channel-id'],
                                    channel['channel-name'],
                                    channel['email'],
                                    channel['device-type'],
                                    channel['model'],
                                    channel['project-name'],
                                    channel['mac-address']))
        return ListCircuitsResponse(rj['result'], rj['message'], channels)

    def read_meters(self, channel_id: int = None) -> ReadMetersResponse:
        """Read meter data."""
        action_type = "data"
        data = {'d': action_type, 'username': self.username}
        if channel_id:
            data['channel-id'] = channel_id

        r = requests.post(self.base_url, data=data, cookies={'PHPSESSID': self.auth_cookies['PHPSESSID'].value})
        rj = r.json()

        meters = []
        for meter in rj.get('data'):
            meters.append(Meter(meter['unit'],
                                meter['value'],
                                meter['channel-id'],
                                meter['timestamp'],
                                meter['disconnected']))
        return ReadMetersResponse(rj['result'], rj['message'], meters)


@dataclass
class LoginResponse:
    result: bool
    message: str
    data: dict[str] | None


@dataclass
class ListCircuitsResponse:
    result: bool
    message: str
    data: list[Channel]


@dataclass
class Channel:
    channel_id: int
    channel_name: str
    email: str
    device_type: int
    model: str
    project_name: str
    mac_address: str


@dataclass
class ReadMetersResponse:
    result: bool
    message: str
    data: list[Meter]


@dataclass
class Meter:
    unit: str
    value: int
    channel_id: int
    timestamp: str
    disconnected: bool


@dataclass
class MeterDevice:
    channel: Channel
    meter: Meter
