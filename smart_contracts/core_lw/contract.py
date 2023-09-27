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

class _owner(abi.NamedTuple):
    addr: abi.Field[abi.Address]

class iotShipping:
    # mapping(url=> iotdevices)
    iot_devices_mapping = BoxMapping(abi.String, IotDevice)

    # assign owner
    deployer = GlobalStateValue(
        stack_type=TealType.bytes,
        key="g",
        default=Global.creator_address(),
        descr="The current governor of this contract, allowed to do admin type actions",
    )

    owner = BoxMapping(_owner, abi.String)

app = (Application("iotShipping", state= iotShipping())
    # On create, init app state
    .apply(unconditional_create_approval, initialize_global_state=True)
)

# Only the account set in global_state.owner may call this method
@app.external(authorize=Authorize.only(app.state.deployer))
def set_owner(new_governor: abi.Address) -> Expr:
    """sets the owner of the contract, may only be called by the current governor"""
    _addr = _owner()
    status = abi.String()
    return Seq(
        _addr.set(new_governor),
        status.set('owned'),
        app.state.owner[_addr].set(status),
    )

# function for add iot devices
# @params `_iotURL` & `_ipfsHash`: url and the hash of the devices that user want to add
@app.external
def add_IOT_device(_iotURL: abi.String, _ipfsHash: abi.String) -> Expr:
    iotShipping_tuple = IotDevice()
    return Seq(
        Assert(app.state.owner[Txn.sender()].exists() == Int(1)),
        iotShipping_tuple.set(_iotURL, _ipfsHash),
        app.state.iot_devices_mapping[_iotURL.get()].set(iotShipping_tuple),
    )

# function for get iot devices
# @params `_iotURL`: url to get the details of the iotDevices
@app.external(read_only=True)
def get_IOT(_iotURL: abi.String,*,output: IotDevice)-> Expr:
    return Seq(
        Assert(app.state.iot_devices_mapping[_iotURL.get()].exists() == Int(1)),
        app.state.iot_devices_mapping[_iotURL.get()].store_into(output),
    )

# if __name__ == "__main__":
#     app.build().export(
#         Path(__file__).resolve().parent / f"./artifacts/{app.name}"
#     )

