from src.data.util import S3IsolationLocationSolver


def test_calculate_bucket():
    solver = S3IsolationLocationSolver("abc", "def")
    assert solver.calculate_bucket("123-abc") == "123-def"
    assert solver.calculate_bucket("abc-123") == "abc-123"
    assert solver.calculate_bucket("-abc-123") == "-abc-123"
    assert solver.calculate_bucket("123-abc-123") == "123-abc-123"


def test_calculate_key():
    solver = S3IsolationLocationSolver("abc", "def")
    assert solver.calculate_key("abc/123") == "def/123"
    assert solver.calculate_key("/abc/123") == "/abc/123"
    assert solver.calculate_key("123/abc") == "123/abc"
