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

class iotShipping:
    # mapping(url=> iotdevices)
    iot_devices_mapping = BoxMapping(abi.String, IotDevice)

    # assign owner
    owner = Global.creator_address()

    # mapping(address=> iotdevices)
    ownerMapping = BoxMapping(abi.Address, IotDevice)

app = Application("iotShipping", state= iotShipping())


# function for add iot devices
# @params `_iotURL` & `_ipfsHash`: url and the hash of the devices that user want to add
@app.external
def add_IOT_device(_iotURL: abi.String, _ipfsHash: abi.String) -> Expr:
    iotShipping_tuple = IotDevice()

    return Seq(
        Assert(Txn.sender() == app.state.owner),
        iotShipping_tuple.set(_iotURL, _ipfsHash),
        app.state.iot_devices_mapping[_iotURL.get()].set(iotShipping_tuple),
        app.state.ownerMapping[Txn.sender()].set(iotShipping_tuple),
    )

# function for get iot devices
# @params `_iotURL`: url to get the details of the iotDevices
@app.external
def get_IOT(_iotURL: abi.String,*,output: IotDevice)-> Expr:
    return Seq(
        Assert(app.state.iot_devices_mapping[_iotURL.get()].exists() == Int(1)),
        app.state.iot_devices_mapping[_iotURL.get()].store_into(output),
    )

# if __name__ == "__main__":
#     app.build().export(
#         Path(__file__).resolve().parent / f"./artifacts/{app.name}"
#     )

