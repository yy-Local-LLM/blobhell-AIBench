import asyncio
from blobhell.devices import FakeDevice

def test_fake_device():
    device = FakeDevice({"reboot": {"ok": True}})
    assert asyncio.run(device.invoke("reboot", {})) == {"ok": True}
    assert device.operations == [("reboot", {})]
