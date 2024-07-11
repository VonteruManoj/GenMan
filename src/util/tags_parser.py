import re


class TagParser:
    def __init__(self, tags: dict[str, list[str]]):
        self._tags = tags

    def to_str(self) -> list[str]:
        return [
            f'"{key}"."{v}"'
            for key, values in self._tags.items()
            for v in values
        ]

    @property
    def tags(self):
        return self._tags

    @tags.setter
    def tags(self, tags: dict[str, list[str]]):
        self._tags = tags

    @classmethod
    def from_dict(cls, tags: dict[str, list[str]]):
        return cls(tags)

    @classmethod
    def from_str(cls, tags_str: list[str]):
        if not tags_str:
            return cls({})
        tags = {}
        for tag in tags_str:
            re_expression = re.search(r"\"(.*)\"\.\"(.*)\"", tag)
            key = re_expression.group(1)
            value = re_expression.group(2)
            key = cls.clean_str(key)
            value = cls.clean_str(value)
            if key not in tags:
                tags[key] = []
            tags[key].append(value)
        return cls(tags)

    @staticmethod
    def clean_str(text: str) -> str:
        return text.strip('"')
