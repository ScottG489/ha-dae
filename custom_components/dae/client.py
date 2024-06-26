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
        self.auth_cookie = {}

    def get_channel_meters(self) -> dict:
        """Get channel and meter data."""
        channels = self.list_channels()
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

        self.auth_cookie = {}
        r = self._request(data)
        auth_cookie = SimpleCookie()
        auth_cookie.load(r.headers['Set-Cookie'])
        self.auth_cookie = {'PHPSESSID': auth_cookie['PHPSESSID'].value}

        return LoginResponse.from_response(r.json())

    def list_channels(self) -> ListChannelsResponse:
        """List channels."""
        action_type = "channel"
        operation_type = "list"
        data = {'d': action_type, 'm': operation_type, 'username': self.username}

        r = self._request(data)

        return ListChannelsResponse.from_response(r.json())

    def read_meters(self, channel_id: int = None) -> ReadMetersResponse:
        """Read meter data."""
        action_type = "data"
        data = {'d': action_type, 'username': self.username}
        if channel_id:
            data['channel-id'] = channel_id

        r = self._request(data)

        return ReadMetersResponse.from_response(r.json())

    def _request(self, data: dict):
        resp = self._do_request(data)
        dae_resp = DaeResponse.from_response(resp.json())

        if dae_resp.result:
            return resp
        else:
            self.login()
            resp = self._do_request(data)
            dae_resp = DaeResponse.from_response(resp.json())

            if dae_resp.result:
                return resp
            else:
                raise Exception("DAE request failed.")

    def _do_request(self, data: dict):
        return requests.post(self.base_url, data=data, cookies=self.auth_cookie)


@dataclass
class DaeResponse:
    result: bool
    message: str

    @classmethod
    def from_response(cls, resp: dict):
        return DaeResponse(resp['result'], resp['message'])


@dataclass
class LoginResponse(DaeResponse):
    data: dict[str] | None

    @classmethod
    def from_response(cls, login_resp: dict):
        return LoginResponse(login_resp['result'], login_resp['message'], login_resp.get('data'))


@dataclass
class ListChannelsResponse(DaeResponse):
    data: list[Channel]

    @classmethod
    def from_response(cls, list_channels_resp: dict):
        channels = []
        for channel in list_channels_resp.get('data')[0]:
            channels.append(Channel(channel['channel-id'],
                                    channel['channel-name'],
                                    channel['email'],
                                    channel['device-type'],
                                    channel['model'],
                                    channel['project-name'],
                                    channel['mac-address']))
        return ListChannelsResponse(list_channels_resp['result'], list_channels_resp['message'], channels)


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
class ReadMetersResponse(DaeResponse):
    data: list[Meter]

    @classmethod
    def from_response(cls, read_meters_resp: dict):
        meters = []
        for meter in read_meters_resp.get('data'):
            meters.append(Meter(meter['unit'],
                                meter['value'],
                                meter['channel-id'],
                                meter['timestamp'],
                                meter['disconnected']))
        return ReadMetersResponse(read_meters_resp['result'], read_meters_resp['message'], meters)


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
