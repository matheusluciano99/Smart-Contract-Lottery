from brownie import network, config, accounts, Contract, MockV3Aggregator, VRFCoordinatorMock, LinkToken


FORKED_LOCAL_ENVIRONMENTS = ["mainnet-fork", "mainnet-fork-dev"] # when I was writing this, there was no need for this mainnet-fork-dev. The contract was being normally deployed
LOCAL_BLOCKCHAIN_ENVIROMENTS = ["development", "ganache-local"]


def get_account(index=None, id=None):
    if index:
        return accounts[index]
    if id:
        return accounts.load(id)
    if(
        network.show_active() in LOCAL_BLOCKCHAIN_ENVIROMENTS 
        or network.show_active() in FORKED_LOCAL_ENVIRONMENTS
    ):
        return accounts[0]
    return accounts.add(config["wallets"]["from_key"])

contract_to_mock = {
    "eth_usd_price_feed": MockV3Aggregator, 
    "vrf_coordinator": VRFCoordinatorMock, 
    "link_token": LinkToken
}

def get_contract(contract_name): # see the github repo
    """ This function will grab the contract addresses from the brownie config
    if defined, otherwise, it will deploy a mock version of that contract, and 
    return that mock contract.

        Args:
            contract_name (string)
        
        Returns:
            brownie.network.contract.ProjectContract: The most recently deployed
            version of this contract.
            MockV3Aggregator[-1]
    """
    contract_type = contract_to_mock[contract_name]

    if network.show_active() in LOCAL_BLOCKCHAIN_ENVIROMENTS:
        if len(contract_type) <= 0:
            # MockV3Aggregator length    
            deploy_mocks()
        contract = contract_type[-1] # MockV3Aggregator[-1]
    else:
        contract_address = config["networks"][network.show_active()][contract_name]
        # address
        # ABI
        contract = Contract.from_abi(contract_type._name, contract_address, contract_type.abi)
    return contract

DECIMALS = 8
INITIAL_VALUE = 200000000000


def deploy_mocks(decimals=DECIMALS, initial_value=INITIAL_VALUE):
    account = get_account()
    MockV3Aggregator.deploy(
        decimals, initial_value, {"from": account}
    )
    link_token = LinkToken.deploy({"from": account})
    VRFCoordinatorMock.deploy(link_token.address, {"from": account})
    print("Deployed!")

def fund_with_link(contract_address, account=None, link_token=None, amount=500000000000000000): # 0.5 LINK
    account = account if account else get_account()
    link_token = link_token if link_token else get_contract("link_token")
    tx = link_token.transfer(contract_address, amount, {"from": account}) # ERROR HERE
    # Could've done like this too using LinkTokenInterface.sol and importing interface: (It's better because it doesn't need the contract abi)
    # link_token_contract = interface.LinkTokenInterface(link_token.address)
    # tx = link_token_contract.transfer(contract_address, amount, {"from": account})
    tx.wait(1)
    print("Contract Funded!")
    return tx