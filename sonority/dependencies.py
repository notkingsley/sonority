from typing import Annotated

from fastapi import Query


Skip = Annotated[int, Query(ge=0, alias="offset")]
Take = Annotated[int, Query(ge=1, le=50, alias="limit")]
SKIP_DEFAULT = 0
TAKE_DEFAULT = 20
