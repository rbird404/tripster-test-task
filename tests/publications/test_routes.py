import pytest
from fastapi.testclient import TestClient
from fastapi import status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.publications.models import Publication, Vote
from src.users.models import User
from tests.factories import UserFactory
from tests.factories.publication import PublicationFactory
from tests.factories.vote import VoteFactory


def test_create_publication_no_auth(client: TestClient) -> None:
    resp = client.post("/publications", json={"content": "test"})
    assert resp.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.asyncio
async def test_create_publication_auth(client: TestClient, db_session: AsyncSession) -> None:
    user = UserFactory()
    credentials = UserFactory.get_credentials(user)

    resp = client.post(
        "/publications",
        json={"content": "test"},
        headers={"Authorization": credentials}
    )
    assert resp.status_code == status.HTTP_201_CREATED
    details = resp.json()["details"]

    pub_in_db = await db_session.scalar(
        select(Publication).where(Publication.id == details["id"])
    )
    assert pub_in_db.content == details["content"]


@pytest.mark.asyncio
async def test_create_vote_no_auth(client: TestClient) -> None:
    publication = PublicationFactory()
    resp = client.post(
        f"/publications/{publication.id}/vote",
        json={"grade": True}
    )
    assert resp.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.asyncio
async def test_create_vote_auth(client: TestClient, db_session) -> None:
    publication = PublicationFactory()
    user = UserFactory()
    credentials = UserFactory.get_credentials(user)

    vote_in_db = await db_session.scalar(
        select(Vote).where(
            Vote.publication_id == publication.id, Vote.user_id == user.id)
    )
    assert vote_in_db is None

    resp = client.post(
        f"/publications/{publication.id}/vote",
        json={"grade": True},
        headers={"Authorization": credentials}
    )
    assert resp.status_code == status.HTTP_201_CREATED

    vote_in_db = await db_session.scalar(
        select(Vote).where(Vote.publication_id == publication.id, Vote.user_id == user.id)
    )
    assert vote_in_db is not None

    resp = client.post(
        f"/publications/{publication.id}/vote",
        json={
            "grade": True,
        },
        headers={"Authorization": credentials}
    )
    assert resp.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.asyncio
async def test_remove_vote_auth(client: TestClient, db_session) -> None:
    vote = VoteFactory()
    user = VoteFactory.get_current_session().scalar(
        select(User).where(User.id == vote.user_id)
    )
    credentials = UserFactory.get_credentials(user)

    resp = client.delete(
        f"/publications/{vote.publication_id}/vote",
        headers={"Authorization": credentials}
    )
    assert resp.status_code == status.HTTP_200_OK
    vote_in_db = await db_session.scalar(
        select(Vote).where(Vote.publication_id == vote.publication_id, Vote.user_id == vote.user_id)
    )
    assert vote_in_db is None

    resp = client.delete(
        f"/publications/{vote.publication_id}/vote",
        headers={"Authorization": credentials}
    )
    assert resp.status_code == status.HTTP_400_BAD_REQUEST


def test_remove_vote_no_auth(client: TestClient) -> None:
    publication = PublicationFactory()
    resp = client.delete(f"/publications/{publication.id}/vote")
    assert resp.status_code == status.HTTP_403_FORBIDDEN
