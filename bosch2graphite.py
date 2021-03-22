""" Test script of bosch_thermostat_client. """
import asyncio
import logging
import time
import os
import aiohttp
import time
import graphyte
import bosch_thermostat_client as bosch
from bosch_thermostat_client.const.ivt import IVT, HTTP
from bosch_thermostat_client.const import HC, DHW, TYPE, RECORDINGS

logging.basicConfig()
logging.getLogger().setLevel(logging.INFO)

graphitePrefix=os.environ.get("GRAPHITE_PREFIX")
graphiteLogs=os.environ.get("LOG_GRAPHITE")
graphiteServer=os.environ.get("GRAPHITE_IP")
accessToken=os.environ.get("MBLAN_ACCESS_KEY")
password=os.environ.get("MBLAN_PASSWORD")
mblanIp=os.environ.get("MBLAN_IP")
sleep=int(os.environ.get("MBLAN_SLEEP"))

def str2bool(v):
      return v.lower() in ("yes", "true", "t", "1")

graphyte.init(graphiteServer, prefix=graphitePrefix,
              log_sends=str2bool(graphiteLogs))

async def main():

    async with aiohttp.ClientSession() as session:
        data_file = open("data_file.txt", "r")
        data = data_file.read().splitlines()
        BoschGateway = bosch.gateway_chooser(device_type=IVT)
        gateway = BoschGateway(
            session=session,
            session_type=HTTP,
            host=mblanIp,
            access_token=accessToken,
            password=password,
        )
        await gateway.check_connection()
        sensors = await gateway.initialize_sensors()
        while True:
            for sensor in sensors:
                if str(sensor.kind) == 'regular':
                    key = str(sensor.name.replace(" ", ".")).lower()
                    await sensor.update()
                    value = sensor.state
                    if value == "on":
                        value = 1
                    if value == "off":
                        value = 0
                    if (isinstance(value, float)):
                        graphyte.send(key, value)
            time.sleep(sleep)
        await gateway.initialize_circuits(HC)
        await session.close()

asyncio.get_event_loop().run_until_complete(main())
