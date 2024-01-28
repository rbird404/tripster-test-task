import random

import factory

from src.publications.models import Vote
from tests.factories.base import BaseFactory


class VoteFactory(BaseFactory):
    class Meta:
        model = Vote

    id = factory.Sequence(lambda n: n + 1)
    grade = factory.Sequence(lambda n: bool(random.randint(0, 1)))

    @classmethod
    def _create(cls, model_class, *args, **kwargs):
        if "user_id" not in kwargs:
            from tests.factories import UserFactory
            creator = UserFactory()
            kwargs["user_id"] = creator.id
        if "publication_id" not in kwargs:
            from tests.factories import PublicationFactory
            creator = PublicationFactory()
            kwargs["publication_id"] = creator.id

        return super()._create(model_class, *args, **kwargs)
