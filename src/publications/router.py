from fastapi import APIRouter, Depends, Path
from fastapi import status

from src.auth.service import CurrentUser
from src.publications.schemas import PublicationCreate, VoteBase, ItemQueryParams
from src.publications.use_case import (
    CreatePublication,
    GetPublicationList,
    VotedForPublication,
    UpdateUserVoteForPublication,
    RemoveUserVoteForPublication
)

router = APIRouter()


@router.post("", status_code=status.HTTP_201_CREATED)
async def create_publication(
        schema: PublicationCreate,
        current_user: CurrentUser,
        use_case: CreatePublication = Depends(),
):
    return await use_case(current_user.id, schema)


@router.get("", status_code=status.HTTP_200_OK)
async def get_publications(
        use_case: GetPublicationList = Depends(),
        params: ItemQueryParams = Depends(),
):
    return await use_case(params)


@router.post("/{id}/vote", status_code=status.HTTP_201_CREATED)
async def create_vote(
        schema: VoteBase,
        current_user: CurrentUser,
        publication_id: int = Path(..., alias="id"),
        use_case: VotedForPublication = Depends(),
):
    return await use_case(current_user.id, publication_id, schema)


@router.put("/{id}/vote", status_code=status.HTTP_200_OK)
async def update_vote(
        schema: VoteBase,
        current_user: CurrentUser,
        publication_id: int = Path(..., alias="id"),
        use_case: UpdateUserVoteForPublication = Depends(),
):
    return await use_case(current_user.id, publication_id, schema)


@router.delete("/{id}/vote", status_code=status.HTTP_200_OK)
async def remove_vote(
        current_user: CurrentUser,
        publication_id: int = Path(..., alias="id"),
        use_case: RemoveUserVoteForPublication = Depends(),
):
    return await use_case(current_user.id, publication_id)
