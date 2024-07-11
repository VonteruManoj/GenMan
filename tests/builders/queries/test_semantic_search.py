import os

from src.api.v1.endpoints.requests.semantic_search import SearchFilters
from src.builders.queries.semantic_search import (
    SemanticSearchSearchQueryBuilder,
)

embeddings_dimensions = int(os.environ.get("EMBEDDINGS_DIMENSIONS", 4096))


class TestSemanticSearchSearchQueryBuilder:
    def test_init_values(self):
        builder = SemanticSearchSearchQueryBuilder(
            [0] * embeddings_dimensions, 1, 1.0
        )

        assert all([n == 0 for n in builder.embeddings])
        assert builder.org_id == 1
        assert builder.limit is None
        assert builder._query is None
        assert isinstance(builder.filters, SearchFilters)
        assert builder.filters == SearchFilters()
        assert builder.treshold == 1.0
