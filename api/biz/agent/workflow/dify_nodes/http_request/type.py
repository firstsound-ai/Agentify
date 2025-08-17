from dataclasses import dataclass, field
from typing import Any, List, Optional


@dataclass
class AuthConfig:
    type: str = "no-auth"
    config: Optional[Any] = None


@dataclass
class HTTPBody:
    type: str = "none"
    data: List[Any] = field(default_factory=list)


@dataclass
class HTTPTimeout:
    max_connect_timeout: int = 0
    max_read_timeout: int = 0
    max_write_timeout: int = 0


@dataclass
class HTTPRetryConfig:
    retry_enabled: bool = True
    max_retries: int = 3
    retry_interval: int = 100
