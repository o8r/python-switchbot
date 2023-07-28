import json
import uuid
from typing import List

from switchbot.client import SwitchBotClient
from switchbot.devices import Device
from switchbot.remotes import Remote
from switchbot.scene import Scene
from switchbot.webhook import Webhook

__version__ = "2.3.1"


class SwitchBot:
    def __init__(self, token: str, secret: str):
        self.client = SwitchBotClient(token, secret, nonce=str(uuid.uuid4()))

    def devices(self) -> List[Device]:
        response = self.client.get("devices")
        return [
            Device.create(client=self.client, id=device["device_id"], **device)
            for device in response["body"]["device_list"]
        ]

    def device(self, id: str) -> Device:
        # Currently, SwitchBot API does not support to retrieve device_name,
        # enable_cloud_service and hub_device_id without getting all device list
        # Therefore, for backward compatibility reason,
        # we query all devices first, then return the matching device
        for device in self.devices():
            if device.id == id:
                return device
        raise ValueError(f"Unknown device {id}")

    def remotes(self) -> List[Remote]:
        response = self.client.get("devices")
        return [
            Remote.create(client=self.client, id=remote["device_id"], **remote)
            for remote in response["body"]["infrared_remote_list"]
        ]

    def remote(self, id: str) -> Remote:
        for remote in self.remotes():
            if remote.id == id:
                return remote
        raise ValueError(f"Unknown remote {id}")

    def scenes(self) -> List[Scene]:
        response = self.client.get("scenes")
        return [Scene(client=self.client, id=scene["scene_id"], **scene) for scene in response["body"]]

    def scene(self, id: str) -> Scene:
        for scene in self.scenes():
            if scene.id == id:
                return scene
        raise ValueError(f"Unknown scene {id}")

    def webhooks(self) -> List[Webhook]:
        try:
            response = self.client.post(
                'webhook/queryWebhook', data=json.dumps({'action': 'queryUrl'}))
        except RuntimeError as e:
            return []  # No webhooks here
        return [Webhook(url) for url in response['body']['urls']]

    def webhook(self, url: str) -> Webhook:
        for webhook in self.webhooks():
            if webhook.url == url:
                return webhook
        raise ValueError(f'Unknown webhook {url}')

    def setupWebhook(self, url: str, deviceList: List[Device] = None) -> bool:
        if deviceList:
            raise 'deviceList in setupWebhook is not supported by API v1.1'

        response = self.client.post(
            'webhook/setupWebhook', data=json.dumps({'action': 'setupWebhook', 'url': url, 'deviceList': 'ALL'}))
        return response['status_code'] == 100

    def enableWebhook(self, webhook: Webhook, enable: bool = True) -> bool:
        response = self.client.post('webhook/updateWebhook', data=json.dumps(
            {'action': 'updateWebhook', 'config': {'url': webhook.url, 'enable': enable}}))
        return response['status_code'] == 100

    def disableWebhook(self, webhook: Webhook) -> bool:
        return self.enableWebhook(webhook, False)

    def deleteWebhook(self, webhook: Webhook) -> bool:
        response = self.client.post(
            'webhook/deleteWebhook', data=json.dumps({'action': 'deleteWebhook', 'url': webhook.url}))
        return response['status_code'] == 100
