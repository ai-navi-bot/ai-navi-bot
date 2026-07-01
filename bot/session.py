"""HTTP-сессия бота с поддержкой системного прокси."""

from aiohttp import ClientSession
from aiohttp.hdrs import USER_AGENT
from aiohttp.http import SERVER_SOFTWARE

from aiogram.__meta__ import __version__
from aiogram.client.session.aiohttp import AiohttpSession


class ProxyAwareAiohttpSession(AiohttpSession):
    """Сессия aiohttp, использующая системные настройки прокси (trust_env)."""

    async def create_session(self) -> ClientSession:
        """Создаёт ClientSession с trust_env для работы через локальный прокси."""
        if self._should_reset_connector:
            await self.close()

        if self._session is None or self._session.closed:
            self._session = ClientSession(
                connector=self._connector_type(**self._connector_init),
                headers={
                    USER_AGENT: f"{SERVER_SOFTWARE} aiogram/{__version__}",
                },
                trust_env=True,
            )
            self._should_reset_connector = False

        return self._session
