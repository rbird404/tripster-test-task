from sqlalchemy import func, select, update, delete, case
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import aliased

from src.publications.models import Publication, Vote
from src.users.models import User


async def create_publication(
        session: AsyncSession, user_id: int, content: str
) -> Publication:
    publication = Publication(content=content, creator_id=user_id)
    session.add(publication)
    return publication


async def get_publication_by_id(
        session: AsyncSession, id: int
) -> Publication | None:
    publication = await session.scalar(
        select(Publication).where(Publication.id == id)
    )
    return publication


async def get_publications(
        session: AsyncSession, order_by: str, desc: bool, limit: int
):
    subq = select(
        Vote.publication_id,
        func.count(Vote.publication_id).label('vote_count'),
        (
            func.sum(
                case(
                    (Vote.grade == True, 1),
                    (Vote.grade == False, -1),
                    else_=0
                )
            )
        ).label('rating')
    ).group_by(Vote.publication_id).subquery()

    creator_alias = aliased(User, name='creator')
    stmt = (
        select(
            Publication.id,
            Publication.content,
            Publication.created_at,
            func.coalesce(subq.c.rating, 0).label("rating"),
            func.coalesce(subq.c.vote_count, 0).label("vote_count"),
            creator_alias,
        ).outerjoin(
            subq, subq.c.publication_id == Publication.id
        ).join(
            creator_alias, creator_alias.id == Publication.creator_id
        )
    )
    match order_by:
        case "rating":
            if desc:
                stmt = stmt.order_by(func.coalesce(subq.c.rating, 0).desc())
            else:
                stmt = stmt.order_by(func.coalesce(subq.c.rating, 0))
        case "created_at":
            if desc:
                stmt = stmt.order_by(Publication.created_at.desc())
            else:
                stmt = stmt.order_by(Publication.created_at)
    if limit:
        stmt = stmt.limit(limit)

    pubs = await session.execute(stmt)
    return pubs.all()


async def create_vote(
        session: AsyncSession, user_id: int, publication_id: int, grade: bool
) -> Vote:
    vote = Vote(
        publication_id=publication_id, user_id=user_id, grade=grade
    )
    session.add(vote)
    return vote


async def get_vote(
        session: AsyncSession, user_id: int, publication_id: int
) -> Vote | None:
    vote = await session.scalar(
        select(Vote)
        .where(Vote.publication_id == publication_id, Vote.user_id == user_id)
    )
    return vote


async def update_vote(
        session: AsyncSession,
        user_id: int,
        publication_id: int,
        grade: bool
) -> Vote | None:
    vote = await session.scalar(
        update(Vote).values(grade=grade)
        .where(
            Vote.publication_id == publication_id,
            Vote.user_id == user_id
        ).returning(Vote)
    )
    return vote


async def remove_vote(
        session: AsyncSession,
        user_id: int,
        publication_id: int,
):
    vote = await session.scalar(
        delete(Vote)
        .where(
            Vote.publication_id == publication_id,
            Vote.user_id == user_id
        ).returning(Vote)
    )
    return vote
