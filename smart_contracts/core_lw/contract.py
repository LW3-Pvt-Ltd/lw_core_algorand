# @lw3core_iotshipping
# @author `lw3`
# functionality: add and get any iot devicecs by providing the url and ipfs hash

from beaker import *
from pyteal import *
from pathlib import Path
from beaker.lib.storage import BoxMapping

class IotDevice(abi.NamedTuple):
    iotURL: abi.Field[abi.String]
    ipfsHash: abi.Field[abi.String]

class appState:
    # assign owner
    deployer = GlobalStateValue(
        stack_type=TealType.bytes,
        key="g",
        default=Global.creator_address(),
        descr="The current governor of this contract, allowed to do admin type actions",
    )
    
    iotDevices = BoxMapping(abi.String, IotDevice)
    members = BoxMapping(abi.Address, abi.Uint64)
    memberCount = GlobalStateValue(stack_type=TealType.uint64, default=Int(0), descr="Number of members registered")

app = (Application("LW3Core1.79", state= appState())
    # On create, init app state
    .apply(unconditional_create_approval, initialize_global_state=True)
)

# Only the account set in global_state.owner may call this method
@app.external(authorize=Authorize.only(app.state.deployer))
def setMember(newMember: abi.Address) -> Expr:
    """sets the member of the contract, may only be called by the current governor"""
    state = abi.Uint64()
    return Seq(
        state.set(1),
        app.state.members[newMember].set(state),
        app.state.memberCount.increment()
    )

# @params `_iotURL` & `_ipfsHash`: url and the hash of the devices that user want to add
#, replenish: abi.PaymentTransaction
@app.external
def addIOTDevice( _iotURL: abi.String, _ipfsHash: abi.String ) -> Expr:
    """add your IoT Devices"""
    iotTupple = IotDevice()
    return Seq(
        Assert(app.state.members[Txn.sender()].exists() == Int(1), comment="You are not authorized member"),
        iotTupple.set(_iotURL, _ipfsHash),
        app.state.iotDevices[_iotURL.get()].set(iotTupple),
    )

# @params `_iotURL` & `_ipfsHash`: url and the hash of the devices that user want to add
@app.external
def addTracePoint(_iotURL: abi.String, _ipfsHash: abi.String) -> Expr:
    """add updated shipping details"""
    trace = IotDevice()
    return Seq(
        Assert(app.state.members[Txn.sender()].exists() == Int(1), comment="You are not authorized member"),
        Assert(app.state.iotDevices[_iotURL.get()].exists() == Int(1), comment="Device ID doesn't exists"),
        trace.set(_iotURL, _ipfsHash),
        app.state.iotDevices[_iotURL.get()].set(trace),
    )

# @params `_iotURL`: url to get the details of the iotDevices
@app.external(read_only=True)
def getIOT(_iotURL: abi.String,*,output: IotDevice)-> Expr:
    """get details about the added iot devices"""
    return Seq(
        Assert(app.state.iotDevices[_iotURL.get()].exists() == Int(1), comment="Device ID doesn't exists"),
        app.state.iotDevices[_iotURL.get()].store_into(output),
    )

# @params `addr`: removing address from members
@app.external(authorize=Authorize.only(app.state.deployer))
def deleteMember(addr: abi.Address) -> Expr:
    """delete the member of the contract, may only be called by deployer"""
    return Seq(
        Pop(app.state.members[addr].delete()),
        app.state.memberCount.decrement()
    )

if __name__ == "__main__":
    app.build().export(
        Path(__file__).resolve().parent / f"./artifacts/{app.name}"
    )

