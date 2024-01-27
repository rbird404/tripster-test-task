import pytest

from src.auth.schemas import AuthUser
from src.auth.use_case import CreateTokenPair


@pytest.mark.asyncio
async def test_register_user(db_session) -> None:
    use_case = CreateTokenPair(db_session)
    data = AuthUser(
        username="dasd12312312",
        password="dasd12312312"
    )
    await use_case(data)
