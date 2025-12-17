from typing import Any, Dict

class MqttListenerPlugin:
    def __init__(self, name: str, config: Dict[str, Any], context: Dict[str, Any]):
        self.name = name
        self.config = config
        self.context = context

    def validate(self) -> None:
        # Raise if required artifacts/config are missing
        pass

    def start(self) -> None:
        # Start thread(s) / MQTT client(s). Non-blocking.
        raise NotImplementedError

    def stop(self) -> None:
        # Optional clean shutdown
        pass