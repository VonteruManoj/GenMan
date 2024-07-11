import datetime
import os

from factory import LazyFunction, SubFactory, alchemy, fuzzy, post_generation

from src.core.containers import container
from src.models.semantic_search_item import (
    SemanticSearchDocument,
    SemanticSearchItem,
)
from src.util.tags_parser import TagParser

embeddings_dimensions = int(os.environ.get("EMBEDDINGS_DIMENSIONS", 4096))


start_date = datetime.datetime(2008, 1, 1, 12, 12, 12, 12).astimezone(
    datetime.timezone.utc
)


def generate_tags():
    tags = [
        fuzzy.FuzzyText().fuzz()
        for _ in range(fuzzy.FuzzyInteger(0, 5).fuzz())
    ]
    r = {}
    for tag in tags:
        r[tag] = [
            fuzzy.FuzzyText().fuzz()
            for _ in range(fuzzy.FuzzyInteger(0, 5).fuzz())
        ]

    return TagParser.from_dict(r).to_str()


def generate_data():
    keys = [
        fuzzy.FuzzyText().fuzz()
        for _ in range(fuzzy.FuzzyInteger(0, 5).fuzz())
    ]
    r = {}
    for key in keys:
        if fuzzy.FuzzyChoice([True, False]).fuzz():
            r[key] = fuzzy.FuzzyText().fuzz()
        else:
            r[key] = fuzzy.FuzzyInteger(0, 1000).fuzz()

    return r


class SemanticSearchDocumentFactory(alchemy.SQLAlchemyModelFactory):
    class Meta:
        model = SemanticSearchDocument
        sqlalchemy_session = container.db()._session_factory()
        sqlalchemy_session_persistence = "commit"

    org_id = fuzzy.FuzzyInteger(1, 1000)
    language = fuzzy.FuzzyChoice(
        ["en", "de", "fr", "es", "it", "pt", "ru", "zh"]
    )
    title = fuzzy.FuzzyText()
    description = fuzzy.FuzzyText()
    tags = LazyFunction(generate_tags)
    data = LazyFunction(generate_data)
    connector_id = fuzzy.FuzzyInteger(1, 1000)
    document_id = fuzzy.FuzzyText()
    created_at = fuzzy.FuzzyDateTime(start_date)
    updated_at = fuzzy.FuzzyDateTime(start_date)

    @post_generation
    def items(obj, create, extracted, **kwargs):
        if not create:
            return

        if extracted:
            assert isinstance(extracted, int)
            SemanticSearchItemFactory.create_batch(
                size=extracted, document=obj, **kwargs
            )


class SemanticSearchItemFactory(alchemy.SQLAlchemyModelFactory):
    class Meta:
        model = SemanticSearchItem
        sqlalchemy_session = container.db()._session_factory()
        sqlalchemy_session_persistence = "commit"

    embeddings = fuzzy.FuzzyAttribute(
        lambda: [
            fuzzy.FuzzyDecimal(0.0, 10.0, 5).fuzz()
            for _ in range(embeddings_dimensions)
        ]
    )
    chunk = fuzzy.FuzzyText()
    snippet = fuzzy.FuzzyText()
    document = SubFactory(SemanticSearchDocumentFactory)
