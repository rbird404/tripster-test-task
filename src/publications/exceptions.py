from src.common.exceptions import BadRequest


class AlreadyVoted(BadRequest):
    DETAIL = "You have already voted"


class PublicationDoesNotExist(BadRequest):
    DETAIL = "Publication does not exist"


class VoteDoesNotExist(BadRequest):
    DETAIL = "Vote does not exist"
