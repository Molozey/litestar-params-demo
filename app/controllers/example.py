from litestar import Controller
from litestar import get
from litestar import post
from litestar.di import Provide

from app.utils import BasicViewProvider
from app.utils import view_provider_factory


class ExampleController(Controller):
    """
    Example Controller
    """

    path = "/example"
    tags = ["Example"]

    # If we remove dependencies examples: all is OK!
    dependencies = {"view_repo": Provide(view_provider_factory)}

    @post(path="/put")  # If we remove dependencies examples: all is OK!
    async def put(self, idx: str, obj_id: str, view_repo: BasicViewProvider) -> None:
        view_repo.put(idx, obj_id)

    @post(path="/delete")
    async def delete(
        self,
        idx: str,
        view_repo: BasicViewProvider,  # If we remove dependencies examples: all is OK!
    ) -> None:
        view_repo.delete(idx)

    @get(path="/get")
    async def get(
        self,
        idx: str,
        view_repo: BasicViewProvider,  # If we remove dependencies examples: all is OK!
    ) -> None:
        view_repo.get(key=idx)
