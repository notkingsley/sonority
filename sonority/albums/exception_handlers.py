from fastapi import status
from fastapi.responses import JSONResponse

from sonority.albums.exceptions import (
    AlbumAlreadyReleased,
    AlbumDoesNotExist,
    AlbumNameInUse,
    AlbumNotOwned,
    ReleasedAlbumIsImmutable,
)


async def album_name_in_use_exception_handler(request, exc: AlbumNameInUse):
    return JSONResponse(
        status_code=status.HTTP_409_CONFLICT,
        content={"detail": exc.args[0]},
    )


async def album_does_not_exist_exception_handler(request, exc: AlbumDoesNotExist):
    return JSONResponse(
        status_code=status.HTTP_404_NOT_FOUND,
        content={"detail": exc.args[0]},
    )


async def released_album_is_immutable_exception_handler(
    request, exc: ReleasedAlbumIsImmutable
):
    return JSONResponse(
        status_code=status.HTTP_409_CONFLICT,
        content={"detail": exc.args[0]},
    )


async def album_not_owned_exception_handler(request, exc: AlbumNotOwned):
    return JSONResponse(
        status_code=status.HTTP_403_FORBIDDEN,
        content={"detail": exc.args[0]},
    )


async def album_already_released_exception_handler(request, exc: AlbumAlreadyReleased):
    return JSONResponse(
        status_code=status.HTTP_409_CONFLICT,
        content={"detail": exc.args[0]},
    )


exception_handlers = {
    AlbumNameInUse: album_name_in_use_exception_handler,
    AlbumDoesNotExist: album_does_not_exist_exception_handler,
    ReleasedAlbumIsImmutable: released_album_is_immutable_exception_handler,
    AlbumNotOwned: album_not_owned_exception_handler,
    AlbumAlreadyReleased: album_already_released_exception_handler,
}
