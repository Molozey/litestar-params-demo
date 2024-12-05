from app.utils.abstract_view import BasicViewProvider


class SessionTempViewProvider(BasicViewProvider):
    storage: dict[str, str]

    def put(self, key: str, value: str) -> None:
        self.storage[key] = value

    def get(self, key: str) -> str | None:
        return self.storage.get(key, None)

    def delete(self, key: str) -> bool:
        return self.delete(key)
