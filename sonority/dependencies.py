from typing import Annotated

from fastapi import Depends, Query
from sqlalchemy.orm import Session as SQLAlchemySession

from sonority.database import get_new_db_session

Skip = Annotated[int, Query(ge=0, alias="offset")]
Take = Annotated[int, Query(ge=1, le=50, alias="limit")]

SKIP_DEFAULT = 0
TAKE_DEFAULT = 20


Session = Annotated[SQLAlchemySession, Depends(get_new_db_session)]
