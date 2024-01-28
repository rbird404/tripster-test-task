import datetime

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
async def test_update_vote_auth(client: TestClient, db_session) -> None:
    vote = VoteFactory.create(grade=False)
    user = VoteFactory.get_current_session().scalar(
        select(User).where(User.id == vote.user_id)
    )
    credentials = UserFactory.get_credentials(user)

    vote_in_db = await db_session.scalar(
        select(Vote).where(Vote.publication_id == vote.publication_id, Vote.user_id == user.id)
    )
    assert vote_in_db.grade is False

    resp = client.put(
        f"/publications/{vote.publication_id}/vote",
        json={"grade": True},
        headers={"Authorization": credentials}
    )
    assert resp.status_code == status.HTTP_200_OK
    assert resp.json()["details"]["grade"] is True


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


def test_get_publications(client):
    publication = PublicationFactory()
    VoteFactory.create_batch(publication_id=publication.id, grade=True, size=3)
    VoteFactory.create_batch(publication_id=publication.id, grade=False, size=2)

    resp = client.get("/publications")
    assert resp.status_code == status.HTTP_200_OK
    publication_data = resp.json()["details"][0]
    assert publication_data["rating"] == 1.0
    assert publication_data["vote_count"] == 5


def test_get_publications_ordering_by_rating_desc(client):
    publication = PublicationFactory()  # rating 1
    VoteFactory.create_batch(publication_id=publication.id, grade=True, size=3)
    VoteFactory.create_batch(publication_id=publication.id, grade=False, size=2)

    publication2 = PublicationFactory()  # rating -1
    VoteFactory.create_batch(publication_id=publication2.id, grade=True, size=3)
    VoteFactory.create_batch(publication_id=publication2.id, grade=False, size=4)

    resp = client.get(
        "/publications",
        params={
            "order_by": "rating",
            "desc": True
        }
    )

    true_order = [publication, publication2]
    assert resp.status_code == status.HTTP_200_OK

    publications_data = resp.json()["details"]
    for i in range(2):
        if publications_data[i]["id"] != true_order[i].id:
            assert False


def test_get_publications_ordering_by_rating_asc(client):
    publication = PublicationFactory()  # rating 1
    VoteFactory.create_batch(publication_id=publication.id, grade=True, size=3)
    VoteFactory.create_batch(publication_id=publication.id, grade=False, size=2)

    publication2 = PublicationFactory()  # rating -1
    VoteFactory.create_batch(publication_id=publication2.id, grade=True, size=3)
    VoteFactory.create_batch(publication_id=publication2.id, grade=False, size=4)

    resp = client.get(
        "/publications",
        params={
            "order_by": "rating",
            "desc": False
        }
    )

    true_order = [publication2, publication]
    assert resp.status_code == status.HTTP_200_OK

    publications_data = resp.json()["details"]
    for i in range(2):
        if publications_data[i]["id"] != true_order[i].id:
            assert False


def test_get_publications_ordering_by_rating_desc(client):
    publication = PublicationFactory()  # rating 1
    VoteFactory.create_batch(publication_id=publication.id, grade=True, size=3)
    VoteFactory.create_batch(publication_id=publication.id, grade=False, size=2)

    publication2 = PublicationFactory()  # rating -1
    VoteFactory.create_batch(publication_id=publication2.id, grade=True, size=3)
    VoteFactory.create_batch(publication_id=publication2.id, grade=False, size=4)

    resp = client.get(
        "/publications",
        params={
            "order_by": "rating",
            "desc": True
        }
    )

    true_order = [publication, publication2]
    assert resp.status_code == status.HTTP_200_OK

    publications_data = resp.json()["details"]
    for i in range(2):
        if publications_data[i]["id"] != true_order[i].id:
            assert False


def test_get_publications_ordering_by_creation_date(client):
    date = datetime.datetime.now()
    publication = PublicationFactory.create(created_at=date)
    publication2 = PublicationFactory.create(created_at=date - datetime.timedelta(days=1))

    resp = client.get(
        "/publications",
        params={
            "order_by": "created_at",
            "desc": False
        }
    )

    true_order = [publication2, publication]
    assert resp.status_code == status.HTTP_200_OK

    publications_data = resp.json()["details"]
    for i in range(2):
        if publications_data[i]["id"] != true_order[i].id:
            assert False


def test_get_publications_ordering_by_creation_date_desc(client):
    date = datetime.datetime.now()
    publication = PublicationFactory.create(created_at=date)
    publication2 = PublicationFactory.create(created_at=date - datetime.timedelta(days=1))

    resp = client.get(
        "/publications",
        params={
            "order_by": "created_at",
            "desc": True
        }
    )

    true_order = [publication, publication2]
    assert resp.status_code == status.HTTP_200_OK

    publications_data = resp.json()["details"]
    for i in range(2):
        if publications_data[i]["id"] != true_order[i].id:
            assert False
