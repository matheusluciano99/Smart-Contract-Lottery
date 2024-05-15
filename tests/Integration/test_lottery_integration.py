from brownie import network
from scripts.helpful_scripts import get_account, get_contract, fund_with_link, LOCAL_BLOCKCHAIN_ENVIROMENTS
from scripts.deploy_lottery import deploy_lottery
import pytest
import time

def test_can_pick_winner(): # Use GOERLI
    # Arrange
    if network.show_active() in LOCAL_BLOCKCHAIN_ENVIROMENTS:
        pytest.skip()
    lottery = deploy_lottery()
    account = get_account()
    lottery.startLottery({"from": account})
    lottery.enter({"from": account, "value": lottery.getEntranceFee()})
    lottery.enter({"from": account, "value": lottery.getEntranceFee()})
    fund_with_link(lottery)
    lottery.endLottery({"from": account}) # ERROR HERE
    time.sleep(120)
    assert lottery.recentWinner() == account
    assert lottery.balance() == 0