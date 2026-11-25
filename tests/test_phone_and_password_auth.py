"""Tests for phone-based login, phone binding, and password changes."""

from httpx import AsyncClient
from sqlmodel import select

from treg.domain.identity.password import hash_password
from treg.domain.identity.phone import clean_phone, get_phone_candidates, is_probable_phone
from treg.infra.db import session_maker
from treg.models import User


def test_phone_utilities():
    assert is_probable_phone("0912345678")
    assert is_probable_phone("+84912345678")
    assert is_probable_phone("091-234-5678")
    assert is_probable_phone("(+84) 912 345 678")
    assert not is_probable_phone("user@example.com")
    assert not is_probable_phone("invalid_string")
    assert not is_probable_phone("123")  # too short

    assert clean_phone("091-234-5678") == "0912345678"
    assert clean_phone("+84 (912) 345-678") == "+84912345678"

    candidates = get_phone_candidates("0912345678")
    assert "0912345678" in candidates
    assert "+84912345678" in candidates
    assert "84912345678" in candidates

    candidates_intl = get_phone_candidates("+84912345678")
    assert "+84912345678" in candidates_intl
    assert "0912345678" in candidates_intl


async def test_phone_login_and_password_change(clients):
    client: AsyncClient = clients

    # 1. Create a user with password and phone directly in DB
    async with session_maker() as db:
        user = User(
            email="phoneuser@example.com",
            phone="0912345678",
            password_hash=hash_password("InitialPass123"),
        )
        db.add(user)
        await db.commit()
        await db.refresh(user)

    # 2. Test login using local phone format "0912345678"
    resp = await client.post("/auth/password/login", json={
        "account": "0912345678",
        "password": "InitialPass123",
    })
    assert resp.status_code == 200, resp.text
    data = resp.json()
    assert data["email"] == "phoneuser@example.com"
    assert data["phone"] == "0912345678"
    cookie = resp.cookies.get("treg_session")
    assert cookie is not None

    # 3. Test login using international format "+84912345678"
    resp_intl = await client.post("/auth/password/login", json={
        "account": "+84912345678",
        "password": "InitialPass123",
    })
    assert resp_intl.status_code == 200
    assert resp_intl.json()["email"] == "phoneuser@example.com"

    # 4. Test login using formatted input "091-234-5678"
    resp_formatted = await client.post("/auth/password/login", json={
        "account": "091-234-5678",
        "password": "InitialPass123",
    })
    assert resp_formatted.status_code == 200

    # 5. Test login with wrong password
    resp_wrong = await client.post("/auth/password/login", json={
        "account": "0912345678",
        "password": "WrongPassword",
    })
    assert resp_wrong.status_code == 401

    # 6. Test password status and phone update with authenticated client
    user_client = AsyncClient(
        transport=client._transport,
        base_url=client.base_url,
        cookies={"treg_session": cookie},
        headers={"X-Treg-Token": data["token"]},
    )

    resp_status = await user_client.get("/auth/password/status")
    assert resp_status.status_code == 200
    status_data = resp_status.json()
    assert status_data["has_password"] is True
    assert status_data["phone"] == "0912345678"

    # 7. Update phone number
    resp_phone = await user_client.post("/auth/phone/update", json={
        "phone": "0987654321",
    })
    assert resp_phone.status_code == 200
    assert resp_phone.json()["ok"] is True
    assert resp_phone.json()["phone"] == "0987654321"

    # Check updated in DB
    async with session_maker() as db:
        stmt = select(User).where(User.email == "phoneuser@example.com")
        updated_u = (await db.execute(stmt)).scalars().first()
        assert updated_u.phone == "0987654321"

    # 8. Change password
    resp_pwd = await user_client.post("/auth/password/change", json={
        "old_password": "InitialPass123",
        "new_password": "BrandNewPassword456",
    })
    assert resp_pwd.status_code == 200
    assert resp_pwd.json()["ok"] is True

    # 9. Login with new phone and new password
    anon_client = AsyncClient(
        transport=client._transport,
        base_url=client.base_url,
    )
    resp_new_login = await anon_client.post("/auth/password/login", json={
        "account": "0987654321",
        "password": "BrandNewPassword456",
    })
    assert resp_new_login.status_code == 200
    assert resp_new_login.json()["email"] == "phoneuser@example.com"


async def test_phone_and_email_registration(clients):
    client: AsyncClient = clients

    # 1. Register new account with phone
    resp = await client.post("/auth/password/register", json={
        "account": "0933445566",
        "password": "SecretPassword123",
    })
    assert resp.status_code == 200, resp.text
    data = resp.json()
    assert data["ok"] is True
    assert data["phone"] == "0933445566"
    assert "token" in data

    # 2. Try registering same phone again -> should be 400
    resp_dup = await client.post("/auth/password/register", json={
        "account": "0933445566",
        "password": "AnotherPassword123",
    })
    assert resp_dup.status_code == 400

    # 3. Login with newly registered phone
    anon_client = AsyncClient(
        transport=client._transport,
        base_url=client.base_url,
    )
    resp_login = await anon_client.post("/auth/password/login", json={
        "account": "+84933445566",
        "password": "SecretPassword123",
    })
    assert resp_login.status_code == 200
    assert resp_login.json()["phone"] == "0933445566"

    # 4. Register new account with email
    resp_email = await client.post("/auth/password/register", json={
        "account": "directuser@example.com",
        "password": "SecretPassword123",
    })
    assert resp_email.status_code == 200
    assert resp_email.json()["email"] == "directuser@example.com"

    # 5. Password too short (< 6)
    resp_short = await client.post("/auth/password/register", json={
        "account": "0911223344",
        "password": "123",
    })
    assert resp_short.status_code == 400
