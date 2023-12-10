from pydantic import BaseModel, ConfigDict, EmailStr


class BaseUserSchema(BaseModel):
    """
    Base schema for a user.
    """

    email: EmailStr
    full_name: str
    username: str

    model_config = ConfigDict(extra="forbid")


class UserUpdateSchema(BaseModel):
    """
    Schema for updating a user.
    """

    email: EmailStr | None = None
    full_name: str | None = None
    username: str | None = None

    model_config = ConfigDict(extra="forbid")


class UserCreateSchema(BaseUserSchema):
    """
    Schema for creating a user.
    """

    password: str


class UserOutSchema(BaseUserSchema):
    """
    Schema for outputting a user.
    """

    id: int

    model_config = ConfigDict(from_attributes=True, **BaseUserSchema.model_config)


class UserSchema(UserOutSchema):
    """
    Full schema for a user, as stored in the database.
    """

    pwd_hash: str


class UserLoginSchema(BaseModel):
    """
    Schema for logging in a user.
    """

    email: EmailStr
    password: str

    model_config = ConfigDict(extra="forbid")


class UserPasswordChangeSchema(BaseModel):
    """
    Schema for changing a user's password.
    """

    old_password: str
    new_password: str

    model_config = ConfigDict(extra="forbid")
