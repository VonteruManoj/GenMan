import uuid

from src.contracts.chain import (
    ChainableServicesInterface,
    ChainResolverInterface,
)


class ChainResolver(ChainResolverInterface):
    """Used to resolve the excution of a chain of services"""

    def __init__(
        self, services: list[ChainableServicesInterface], operation: str = None
    ) -> None:
        """
        Constructor

        Parameters
        ----------
        services : list[ChainableServicesInterface]
            A list of services to be executed in order
        """
        self._services = services
        self._chain_id = ChainId(operation=operation)

    def resolve(self, input: str, **kwargs) -> str:
        """
        Resolves the execution of a chain of services

        Parameters
        ----------
        input : str
            The input to be processed by the chain of services

        Returns
        -------
        str
            The output of the chain of services
        """
        for service in self._services:
            service.set_chain_id(self._chain_id)
            input = service.handle(input, **kwargs)

        return input


class ChainId:
    def __init__(self, operation: str = None) -> None:
        self.id = uuid.uuid1()
        self.operation = operation
