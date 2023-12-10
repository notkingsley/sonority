class RegistrationError(Exception):
    """
    Raised when a user cannot be registered.
    """

    pass


class PasswordChangeError(Exception):
	"""
	Raised when a user's password cannot be changed.
	"""

	pass


class AuthenticationError(Exception):
	"""
	Raised when a user cannot be authenticated.
	"""

	pass


class UserUpdateError(Exception):
	"""
	Raised when a user cannot be updated.
	"""

	pass