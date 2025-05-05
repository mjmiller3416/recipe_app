from typing import Dict, Protocol, runtime_checkable


@runtime_checkable
class ThemedIcon(Protocol):
    def refresh_theme(self, palette: Dict) -> None: ...
    def objectName(self) -> str: ...      