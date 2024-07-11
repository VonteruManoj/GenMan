import datetime
import os

import numpy as np

embeddings_dimensions = int(os.environ.get("EMBEDDINGS_DIMENSIONS", 4096))

SEMANTIC_SEARCH_ZT_TREE_ITEM = {
    "node_id": 1,
    "tree_name": "test",
    "tree_description": "test description",
    "tree_id": 1,
    "active": True,
    "create_date": datetime.datetime(2023, 1, 1, 12, 12, 12),
    "last_opened": datetime.datetime(2023, 1, 1, 12, 12, 12),
    "last_modified": datetime.datetime(2023, 1, 1, 12, 12, 12),
    "is_private": False,
    "page_title": "test title",
    "content": "some content",
    "question": "test question",
    "keywords": ["test", "test2"],
    "tags": ["tag1", "tag2"],
    "tree_tags": ["test-tree"],
}

SEMANTIC_SEARCH_HTML_ITEM = {
    "html_id": "test",
    "url": "test url",
    "title": "test title",
    "content": "some content",
    "type_": "test type",
}

SEMANTIC_SEARCH_ZT_TREE_ITEM_ZEROS = {
    "embeddings": [1e-12] * embeddings_dimensions,
    "org_id": 1,
    "language": "en",
    "text": "some text",
    "snippet": "some snippet",
}

SEMANTIC_SEARCH_ZT_TREE_ITEM_ONES = {
    "embeddings": np.ones(embeddings_dimensions),
    "org_id": 1,
    "language": "en",
    "text": "",
    "snippet": "some snippet",
}

SEMANTIC_SEARCH_HTML_ITEM_ZEROS = {
    "embeddings": [1e-12] * embeddings_dimensions,
    "org_id": 1,
    "language": "en",
    "text": "some text",
    "snippet": "some snippet",
}

SEMANTIC_SEARCH_HTML_ITEM_ONES = {
    "embeddings": np.ones(embeddings_dimensions),
    "org_id": 1,
    "language": "en",
    "text": "",
    "snippet": "some snippet",
}
