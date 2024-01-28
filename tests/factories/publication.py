import factory
from factory.fuzzy import FuzzyText

from src.publications.models import Publication
from tests.factories.base import BaseFactory


class PublicationFactory(BaseFactory):
    class Meta:
        model = Publication

    id = factory.Sequence(lambda n: n + 1)
    content = FuzzyText(length=10)
    created_at = factory.Faker("date_time")
    updated_at = factory.Faker("date_time")

    @classmethod
    def _create(cls, model_class, *args, **kwargs):
        if "creator_id" not in kwargs:
            from tests.factories import UserFactory
            creator = UserFactory()
            kwargs["creator_id"] = creator.id
        return super()._create(model_class, *args, **kwargs)
