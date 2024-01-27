import logging

import pytest
from async_asgi_testclient import TestClient
from fastapi import status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.publications.models import Publication, Vote


@pytest.mark.asyncio
async def test_create_publication_no_auth(client: TestClient) -> None:
    resp = await client.post(
        "/publications",
        json={
            "content": "test",
        },
    )
    assert resp.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.asyncio
async def test_create_publication_auth(client: TestClient, credentials, db_session: AsyncSession) -> None:
    resp = await client.post(
        "/publications",
        json={
            "content": "test",
        },
        headers={"Authorization": credentials}
    )
    assert resp.status_code == status.HTTP_201_CREATED
    details = resp.json()["details"]

    pub_in_db = await db_session.scalar(
        select(Publication).where(Publication.id == details["id"])
    )
    assert pub_in_db.content == details["content"]


@pytest.mark.asyncio
async def test_create_vote_no_auth(client: TestClient, publication, credentials) -> None:
    resp = await client.post(
        f"/publications/{publication.id}/vote",
        json={
            "grade": True,
        },
    )
    assert resp.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.asyncio
async def test_create_vote_auth(client: TestClient, publication, credentials, db_session) -> None:
    vote_in_db = await db_session.scalar(
        select(Vote).where(Vote.publication_id == publication.id)
    )
    assert vote_in_db is None

    resp = await client.post(
        f"/publications/{publication.id}/vote",
        json={
            "grade": True,
        },
        headers={"Authorization": credentials}
    )
    assert resp.status_code == status.HTTP_201_CREATED

    vote_in_db = await db_session.scalar(
        select(Vote).where(Vote.publication_id == publication.id)
    )
    assert vote_in_db is not None

    resp = await client.post(
        f"/publications/{publication.id}/vote",
        json={
            "grade": True,
        },
        headers={"Authorization": credentials}
    )
    assert resp.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.asyncio
async def test_remove_vote_auth(client: TestClient, publication, credentials, db_session) -> None:
    vote = Vote(publication_id=publication.id, user_id=publication.creator_id, grade=True)
    db_session.add(vote)
    await db_session.commit()

    resp = await client.delete(
        f"/publications/{publication.id}/vote",
        headers={"Authorization": credentials}
    )
    assert resp.status_code == status.HTTP_200_OK
    vote_in_db = await db_session.scalar(
        select(Vote).where(Vote.publication_id == publication.id, Vote.user_id == publication.creator_id)
    )
    assert vote_in_db is None

    resp = await client.delete(
        f"/publications/{publication.id}/vote",
        headers={"Authorization": credentials}
    )
    assert resp.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.asyncio
async def test_remove_vote_no_auth(client: TestClient, publication, credentials) -> None:
    resp = await client.delete(f"/publications/{publication.id}/vote")
    assert resp.status_code == status.HTTP_403_FORBIDDEN
