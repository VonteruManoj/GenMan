import re


class S3IsolationLocationSolver:
    def __init__(self, current_stage: str, next_stage: str) -> None:
        self.current_stage = current_stage
        self.next_stage = next_stage

    def calculate_key(self, key: str):
        s = f"{self.current_stage}/"
        r = f"{self.next_stage}/"
        pattern = r"^" + re.escape(s)
        return re.sub(pattern, r, key)

    def calculate_bucket(self, bucket: str):
        s = f"-{self.current_stage}"
        r = f"-{self.next_stage}"
        pattern = re.escape(s) + r"$"
        return re.sub(pattern, r, bucket)


class S3IsolationLocationParser:
    def __init__(self, location: str) -> None:
        self.location = location
        self.segments = location.split("/")

    def get_org_id(self) -> str:
        return self.segments[-2]

    def get_id(self) -> str:
        return self.segments[-1].rsplit(".", 1)[0]


class S3ZTTreesIsolationLocationParser(S3IsolationLocationParser):
    def get_org_id(self) -> str:
        return self.segments[-2]
