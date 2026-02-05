# Config Flow Discovery Methods Reference

## Zeroconf / mDNS Discovery

For devices advertising themselves via mDNS on the local network.

**manifest.json:**
```json
{
  "zeroconf": [
    {"type": "_mydevice._tcp.local."}
  ]
}
```

**config_flow.py:**
```python
from homeassistant.components.zeroconf import ZeroconfServiceInfo

async def async_step_zeroconf(
    self, discovery_info: ZeroconfServiceInfo
) -> ConfigFlowResult:
    """Handle zeroconf discovery."""
    self._host = discovery_info.host
    self._port = discovery_info.port
    unique_id = discovery_info.properties.get("id")

    await self.async_set_unique_id(unique_id)
    self._abort_if_unique_id_configured(updates={"host": self._host})

    self.context["title_placeholders"] = {"name": discovery_info.name}
    return await self.async_step_confirm()

async def async_step_confirm(
    self, user_input: dict[str, Any] | None = None
) -> ConfigFlowResult:
    """Confirm discovery."""
    if user_input is not None:
        return self.async_create_entry(
            title=self._name,
            data={"host": self._host, "port": self._port},
        )
    return self.async_show_form(step_id="confirm")
```

## SSDP Discovery

For UPnP/SSDP devices (common in media devices, routers).

**manifest.json:**
```json
{
  "ssdp": [
    {"st": "urn:schemas-upnp-org:device:Basic:1", "manufacturer": "MyBrand"}
  ]
}
```

**config_flow.py:**
```python
from homeassistant.components.ssdp import SsdpServiceInfo

async def async_step_ssdp(
    self, discovery_info: SsdpServiceInfo
) -> ConfigFlowResult:
    unique_id = discovery_info.upnp.get("serialNumber")
    await self.async_set_unique_id(unique_id)
    self._abort_if_unique_id_configured()

    self._host = discovery_info.ssdp_headers.get("_host", "")
    self._name = discovery_info.upnp.get("friendlyName", "Unknown")
    return await self.async_step_confirm()
```

## DHCP Discovery

For devices identified by MAC address prefix when they join the network.

**manifest.json:**
```json
{
  "dhcp": [
    {"macaddress": "AABBCC*", "hostname": "mydevice*"}
  ]
}
```

**config_flow.py:**
```python
from homeassistant.components.dhcp import DhcpServiceInfo

async def async_step_dhcp(
    self, discovery_info: DhcpServiceInfo
) -> ConfigFlowResult:
    self._host = discovery_info.ip
    self._mac = discovery_info.macaddress
    await self.async_set_unique_id(self._mac)
    self._abort_if_unique_id_configured(updates={"host": self._host})
    return await self.async_step_confirm()
```

## USB Discovery

For USB-attached devices (Zigbee/Z-Wave sticks).

**manifest.json:**
```json
{
  "usb": [
    {"vid": "10C4", "pid": "EA60", "description": "*cp2102*"}
  ]
}
```

**config_flow.py:**
```python
from homeassistant.components.usb import UsbServiceInfo

async def async_step_usb(
    self, discovery_info: UsbServiceInfo
) -> ConfigFlowResult:
    self._device_path = discovery_info.device
    unique_id = f"{discovery_info.vid}:{discovery_info.pid}:{discovery_info.serial_number}"
    await self.async_set_unique_id(unique_id)
    self._abort_if_unique_id_configured()
    return await self.async_step_confirm()
```

## Bluetooth Discovery

**manifest.json:**
```json
{
  "bluetooth": [
    {"service_uuid": "0000fee0-0000-1000-8000-00805f9b34fb"}
  ]
}
```

## Key Rules for Discovery Flows

1. Always call `async_set_unique_id()` then `_abort_if_unique_id_configured()` to deduplicate.
2. Pass `updates={}` to `_abort_if_unique_id_configured` when the device's address may change (e.g., DHCP reassignment).
3. Show a confirmation step before creating the entry so the user can see what was discovered.
4. Use `context["title_placeholders"]` to show the device name in the flow title.
5. Discovery flows must still work if the user manually sets up the integration first.
