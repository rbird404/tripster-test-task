from pydantic import TypeAdapter

from src.common.use_case import BaseAsyncUseCase
from src.publications import service
from src.publications.exceptions import AlreadyVoted, PublicationDoesNotExist, VoteDoesNotExist
from src.publications.schemas import (
    PublicationCreate,
    VoteBase,
    PublicationListResponse,
    PublicationReadDetail,
    VoteResponse,
    PublicationResponse, ItemQueryParams
)


class CreatePublication(BaseAsyncUseCase):
    async def __call__(self, user_id: int, in_: PublicationCreate):
        pub = await service.create_publication(self.session, user_id, in_.content)
        await self.session.commit()
        return PublicationResponse(msg="Publication created successfully.", details=pub)


class GetPublicationList(BaseAsyncUseCase):
    _pubs_adapter = TypeAdapter(list[PublicationReadDetail])

    async def __call__(self, params: ItemQueryParams):
        pubs = await service.get_publications(self.session, **params.model_dump())
        details = self._pubs_adapter.validate_python(pubs, from_attributes=True)
        return PublicationListResponse(msg="Publications successfully received.", details=details)


class VotedForPublication(BaseAsyncUseCase):
    async def __call__(self, user_id: int, publication_id: int, in_: VoteBase):
        publication_in_db = await service.get_publication_by_id(
            self.session, publication_id
        )

        if publication_in_db is None:
            raise PublicationDoesNotExist()

        vote_id_db = await service.get_vote(
            self.session, user_id=user_id, publication_id=publication_id
        )
        if vote_id_db is not None:
            raise AlreadyVoted()

        vote = await service.create_vote(
            self.session,
            user_id=user_id,
            publication_id=publication_id,
            grade=in_.grade
        )
        await self.session.commit()
        return VoteResponse(msg="Voted successfully.", details=vote)


class UpdateUserVoteForPublication(BaseAsyncUseCase):
    async def __call__(self, user_id: int, publication_id: int, in_: VoteBase):
        vote_id_db = await service.get_vote(
            self.session, user_id=user_id, publication_id=publication_id
        )
        if vote_id_db is None:
            raise VoteDoesNotExist()

        vote = await service.update_vote(
            self.session,
            user_id=user_id,
            publication_id=publication_id,
            grade=in_.grade
        )
        await self.session.commit()
        return VoteResponse(msg="Vote has been updated.", details=vote)


class RemoveUserVoteForPublication(BaseAsyncUseCase):
    async def __call__(self, user_id: int, publication_id: int):
        vote_id_db = await service.get_vote(
            self.session, user_id=user_id, publication_id=publication_id
        )
        if vote_id_db is None:
            raise VoteDoesNotExist()

        vote = await service.remove_vote(
            self.session,
            user_id=user_id,
            publication_id=publication_id,
        )
        await self.session.commit()
        return VoteResponse(msg="Vote has been removed.", details=vote)
