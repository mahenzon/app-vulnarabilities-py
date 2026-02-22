from pydantic import BaseModel, ConfigDict, Field


class User(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    username: str
    password: str
    balance: float


class UserInfo(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    username: str


class PaymentForm(BaseModel):
    amount: float = Field(
        gt=0,
        description="Amount must be greater than 0",
    )
    to_user_id: int = Field(
        gt=0,
        description="Recipient user ID must be positive",
    )


class LoginForm(BaseModel):
    username: str = Field(
        min_length=1,
        description="Username is required",
    )
    password: str = Field(
        min_length=1,
        description="Password is required",
    )


class Payment(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    amount: float
    created_at: str
    from_username: str
    to_username: str
