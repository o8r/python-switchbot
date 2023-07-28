from switchbot.client import SwitchBotClient


class Webhook():
    def __init__(self, url: str):
        self.url = url
        self.details = None
