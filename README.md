Hello everyone! I encountered a behavior, and I'm not sure if it's correct.

The reproduction steps are attached in the form of a repository (the following description will refer to it).

As a demonstration, I wanted to create BasicViewProvider, which is a simple key-value pair and used as dependency at Controller
```
class BasicViewProvider(ABC):
    """
    Abstract View Provider for demo key-value
    """

    @abstractmethod
    def put(self, key: str, value: str) -> None: ...

    @abstractmethod
    def get(self, key: str) -> str: ...

    @abstractmethod
    def delete(self, key: str) -> bool: ...
 ```
```
class ExampleController(Controller):
    """
    Example Controller
    """

    path = "/example"
    tags = ["Example"]

    # If we remove dependencies examples: all is OK!
    dependencies = {"view_repo": Provide(view_provider_factory)}

    @post(path="/put")  # If we remove dependencies examples: all is OK!
    async def put(
        self,
        idx: str,
        obj_id: str,
        view_repo: BasicViewProvider
    ) -> None:
        view_repo.put(idx, obj_id)
      ...
```

At the same time, my path group requires additional parameters (in the real task, to provide object access models via middleware). So, I register the group as

```
example_route = Router(
    path="/objects",
    route_handlers=[ExampleController],
    parameters={
        # For simple parameter we can provide examples to solve problem
        "team_id": Parameter(
            str,
            description="Affected team id",
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
            # examples=[]
        ),
    },
    # middleware=[auth_middleware()],     # Assume that we need parameters to auth and permissions
)
```

The handler calls work correctly and do what they should, however, after I enter Swagger, I get an error:
```
500: OpenAPI schema generation for handler `app.controllers.example.ExampleController.hidden` detected multiple parameters named 'x-session-token' with different types.
```

It's important to note that when the application starts, I add example creation in the OpenAPI configuration.

If I turn off example generation, the error disappears.
```
def app():

    return Litestar(
        debug=True,
        route_handlers=[example_route],
        openapi_config=OpenAPIConfig(
            title="API",
            version=Configuration.VERSION,
            description="API",
            path="/docs",
            create_examples=True,  # If we remove create examples: all is OK!
        ),
        on_startup=[__startup],
        on_shutdown=[_shutdown],
    )

```

If I disable dependency injection, the error disappears.

```
class ExampleController(Controller):
    """
    Example Controller
    """

    path = "/example"
    tags = ["Example"]

    # If we remove dependencies examples: all is OK!
    # dependencies = {"view_repo": Provide(view_provider_factory)}

    @post(path="/put")  # If we remove dependencies examples: all is OK!
    async def put(
        self,
        idx: str,
        obj_id: str,
        # view_repo: BasicViewProvider
    ) -> None:
        view_repo.put(idx, obj_id)

    @post(path="/delete")
    async def delete(
        self,
        idx: str,
        # view_repo: BasicViewProvider   # If we remove dependencies examples: all is OK!
    ) -> None:
        view_repo.delete(idx)

    @get(path="/get")
    async def get(
        self,
        idx: str,
        # view_repo: BasicViewProvider  # If we remove dependencies examples: all is OK!
    ) -> None:
        view_repo.get(key=idx)

 ```
If I set an example parameter when registering the group, the error disappears, but I was unable to set an example for a cookie-type parameter (Swagger will open, but gives infinite spinner after clicking at route).
```
example_route = Router(
    path="/objects",
    route_handlers=[ExampleController],
    parameters={
        # For simple parameter we can provide examples to solve problem
        "team_id": Parameter(
            str,
            description="Team ID",
            required=True,
            examples=[
                Example(
                    value="mocked-team-id-uuid",
                    summary="summary",
                    description="descr",
                    external_value="Test-team-id",
                )
            ],
        ),

        # For cookie parameter examples will not help
        "x-session-token": Parameter(
            str,
            description="Session JWT token",
            cookie="x-session-token",
            required=False,
            examples=[Example(value="mocked-session")]
        ),
    },
    # middleware=[auth_middleware()],     # Assume that we need parameters to auth and permissions
)
```
Next, I started investigating the cause of this behavior and found that multiple parameter declarations are being called because the examples in the Schema type differ, even when all other fields match.

litestar/_openapi/parameters.py
```
        pre_existing = self._parameters[(parameter.name, parameter.param_in)]
        if parameter == pre_existing: # <--------- Not equals then different examples at schema
            return
        
        # Add this block to understand what is different
        for key, val in parameter.__dict__.items():
            print(
                "Equals for key={}: {}".format(
                    key, val == pre_existing.__getattribute__(key)
                )
            )
            if key == "schema":
                for schema_key, schema_value in val.__dict__.items():
                    print(
                        "[Schema Field] key={}: {}".format(
                            schema_key,
                            schema_value
                            == pre_existing.__getattribute__(key).__getattribute__(
                                schema_key
                            ),
                        )
                    )
        raise ImproperlyConfiguredException(
            f"OpenAPI schema generation for handler `{self.route_handler}` detected multiple parameters named "
            f"'{parameter.name}' with different types."
        )
```
Which gives me next results
```
Equals for key=name: True
Equals for key=param_in: True
Equals for key=schema: False
[Schema Field] key=all_of: True
[Schema Field] key=any_of: True
[Schema Field] key=one_of: True
[Schema Field] key=schema_not: True
[Schema Field] key=schema_if: True
[Schema Field] key=then: True
[Schema Field] key=schema_else: True
[Schema Field] key=dependent_schemas: True
[Schema Field] key=prefix_items: True
[Schema Field] key=items: True
[Schema Field] key=contains: True
[Schema Field] key=properties: True
[Schema Field] key=pattern_properties: True
[Schema Field] key=additional_properties: True
[Schema Field] key=property_names: True
[Schema Field] key=unevaluated_items: True
[Schema Field] key=unevaluated_properties: True
[Schema Field] key=type: True
[Schema Field] key=enum: True
[Schema Field] key=const: True
[Schema Field] key=multiple_of: True
[Schema Field] key=maximum: True
[Schema Field] key=exclusive_maximum: True
[Schema Field] key=minimum: True
[Schema Field] key=exclusive_minimum: True
[Schema Field] key=max_length: True
[Schema Field] key=min_length: True
[Schema Field] key=pattern: True
[Schema Field] key=max_items: True
[Schema Field] key=min_items: True
[Schema Field] key=unique_items: True
[Schema Field] key=max_contains: True
[Schema Field] key=min_contains: True
[Schema Field] key=max_properties: True
[Schema Field] key=min_properties: True
[Schema Field] key=required: True
[Schema Field] key=dependent_required: True
[Schema Field] key=format: True
[Schema Field] key=content_encoding: True
[Schema Field] key=content_media_type: True
[Schema Field] key=content_schema: True
[Schema Field] key=title: True
[Schema Field] key=description: True
[Schema Field] key=default: True
[Schema Field] key=deprecated: True
[Schema Field] key=read_only: True
[Schema Field] key=write_only: True
[Schema Field] key=examples: False <-------------------- Only one DIFF which breaks all
[Schema Field] key=discriminator: True
[Schema Field] key=xml: True
[Schema Field] key=external_docs: True
[Schema Field] key=example: True
Equals for key=description: True
Equals for key=required: True
Equals for key=deprecated: True
Equals for key=allow_empty_value: True
Equals for key=style: True
Equals for key=explode: True
Equals for key=allow_reserved: True
Equals for key=example: True
Equals for key=examples: True
Equals for key=content: True
```

So my general question, is there any reasons that we need to check examples equality?