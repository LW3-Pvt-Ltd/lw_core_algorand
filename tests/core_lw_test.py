import pytest
from algokit_utils import (
    ApplicationClient,
    ApplicationSpecification,
    get_localnet_default_account,
)
from algosdk.v2client.algod import AlgodClient

from smart_contracts.core_lw import contract as core_lw_contract


@pytest.fixture(scope="session")
def core_lw_app_spec(algod_client: AlgodClient) -> ApplicationSpecification:
    return core_lw_contract.app.build(algod_client)


@pytest.fixture(scope="session")
def core_lw_client(
    algod_client: AlgodClient, core_lw_app_spec: ApplicationSpecification
) -> ApplicationClient:
    client = ApplicationClient(
        algod_client,
        app_spec=core_lw_app_spec,
        signer=get_localnet_default_account(algod_client),
        template_values={"UPDATABLE": 1, "DELETABLE": 1},
    )
    client.create()
    return client


def test_says_hello(core_lw_client: ApplicationClient) -> None:
    result = core_lw_client.call(core_lw_contract.hello, name="World")

    assert result.return_value == "Hello, World"
