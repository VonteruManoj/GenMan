from src.chain.chain import ChainResolver


def test_chain_resolver():
    """Tests the chain resolver"""

    class DummyService:
        """A dummy service"""

        def handle(self, input, **kwargs):
            """Handles the input"""
            return input

    services = [DummyService() for _ in range(3)]
    resolver = ChainResolver(services)
    assert resolver.resolve("test") == "test"
