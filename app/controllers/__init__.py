from litestar import Router
from litestar.params import Parameter
from litestar.openapi.spec.example import Example

from app.controllers.example import ExampleController

example_route = Router(
    path="/objects",
    route_handlers=[ExampleController],
    parameters={
        # For simple parameter we can provide examples to solve problem
        "team_id": Parameter(
            str,
            description="Team ID",
            required=True,
            # examples=[
            #     Example(
            #         value="mocked-team-id-uuid",
            #         summary="summary",
            #         description="descr",
            #         external_value="Test-team-id",
            #     )
            # ],
        ),
        # For cookie parameter examples will not help
        "x-session-token": Parameter(
            str,
            description="Session JWT token",
            cookie="x-session-token",
            required=False,
            # examples=[Example(value="mocked-session")]
        ),
    },
    # middleware=[auth_middleware()],     # Assume that we need parameters to auth and permissions
)
