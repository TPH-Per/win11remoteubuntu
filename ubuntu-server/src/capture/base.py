from abc import ABC, abstractmethod
import numpy as np

class CaptureBackend(ABC):
    @abstractmethod
    async def start(self) -> None:
        pass

    @abstractmethod
    async def grab_frame(self) -> np.ndarray:
        pass

    @abstractmethod
    async def stop(self) -> None:
        pass

    @property
    @abstractmethod
    def resolution(self) -> tuple[int, int]:
        pass
