from app.utils.abstract_view import BasicViewProvider
from app.utils.view_provider import SessionTempViewProvider


async def view_provider_factory() -> BasicViewProvider:
    return SessionTempViewProvider()
