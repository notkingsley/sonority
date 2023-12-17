from fastapi import status
from fastapi.responses import JSONResponse

from sonority.artists.exceptions import (
    ArtistExists,
    ArtistNameInUse,
    ArtistNotFound,
    BadParameters,
    DeniedNotArtist,
    VerifiedArtistIsImmutable,
)


async def artist_exists_exception_handler(request, exc: ArtistExists):
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={"detail": exc.args[0]},
    )


async def artist_name_in_use_exception_handler(request, exc: ArtistNameInUse):
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={"detail": exc.args[0]},
    )


async def artist_not_found_exception_handler(request, exc: ArtistNotFound):
    return JSONResponse(
        status_code=status.HTTP_404_NOT_FOUND,
        content={"detail": "Artist not found"},
    )


async def bad_parameters_exception_handler(request, exc: BadParameters):
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={"detail": exc.args[0]},
    )


async def denied_not_artist_exception_handler(request, exc: DeniedNotArtist):
    return JSONResponse(
        status_code=status.HTTP_403_FORBIDDEN,
        content={"detail": exc.args[0]},
    )


async def verified_artist_is_immutable_exception_handler(
    request, exc: VerifiedArtistIsImmutable
):
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={"detail": exc.args[0]},
    )


exception_handlers = {
    ArtistExists: artist_exists_exception_handler,
    ArtistNameInUse: artist_name_in_use_exception_handler,
    ArtistNotFound: artist_not_found_exception_handler,
    BadParameters: bad_parameters_exception_handler,
    DeniedNotArtist: denied_not_artist_exception_handler,
    VerifiedArtistIsImmutable: verified_artist_is_immutable_exception_handler,
}
