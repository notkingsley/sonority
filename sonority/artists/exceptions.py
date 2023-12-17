class VerifiedArtistIsImmutable(Exception):
    """
    Raised when a verified artist is attempted to be modified.
    """

    pass


class ArtistNameInUse(Exception):
    """
    Raised when an artist name is already in use.
    """

    pass


class ArtistExists(Exception):
    """
    Raised when an artist already exists.
    """

    pass


class DeniedNotArtist(Exception):
    """
    Raised when a user is not an artist.
    """

    pass


class ArtistNotFound(Exception):
    """
    Raised when an artist cannot be found.
    """

    pass


class BadParameters(Exception):
    """
    Raised when bad parameters are provided.
    """

    pass
