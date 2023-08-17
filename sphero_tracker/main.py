import cv2

from tracker_filters import ColorFilter
from trackable_object import TrackableObject
from tracker import Tracker
import json
from datetime import datetime
import numpy as np
import time

from spherov2 import scanner
from spherov2.adapter.bleak_adapter import PacketHandler
from spherov2.sphero_edu import SpheroEduAPI
from contextlib import AsyncExitStack
from spherov2.types import Color
import asyncio
import colorsys

async def connect_to_sphero(stack, name, index):
    # Get adapter
    adapter = "hci{index}".format(index=index % 3)
    attempts = 0
    while attempts < 3:
        try:
            print("Finding toy...")
            toy = await scanner.find_toy(toy_name=name, bleak_adapter=adapter)
            print(
            "Connecting to sphero {name} (#{index}) ({address}), attempt {attempt}, using {adapter}".format(
                name=toy.name, index=index, attempt=attempts + 1, adapter=adapter, address=toy.address
            ))
            bots.append(await stack.enter_async_context(SpheroEduAPI(toy)))
            print("Connected to sphero {name} (#{index})".format(name=toy.name, index=index))
            return
        except Exception as e:
            print(
                "Something went wrong with sphero {name} (#{index}), retrying".format(name=name, index=index)
            )
            print(e)
            attempts += 1

async def set_bots_matrix(colors):
    tasks = []
    for bot, color in zip(bots, colors):
        r,g,b = color
        tasks.append(bot.set_matrix_fill(0, 0, 7, 7, Color(r=r, g=g, b=b)))
    await asyncio.gather(*tasks)

async def set_bots_heading(heading):
    tasks = []
    for bot in bots:
        tasks.append(bot.set_heading(heading))
    await asyncio.gather(*tasks)

sphero_names = ["SB-BFD4", "SB-1B35", "SB-F860", "SB-2175", "SB-3026", "SB-618E", "SB-6B58", "SB-9938", "SB-C1D2", "SB-CEFA", "SB-DF1D", "SB-F465", "SB-F479", "SB-F885", "SB-FCB2"]
bots = []

tracker = Tracker()
spheros = 1

def angles_to_rgb(angles_rad):
    # Convert the angles to hue values (ranges from 0.0 to 1.0 in the HSV color space)
    hues = angles_rad / (2 * np.pi)

    # Set fixed values for saturation and value (you can adjust these as desired)
    saturation = np.ones_like(hues)
    value = np.ones_like(hues)

    hsv_colors = np.stack((hues, saturation, value), axis=-1)
    rgb_colors = np.apply_along_axis(lambda x: colorsys.hsv_to_rgb(*x), -1, hsv_colors)

    # Scale RGB values to 0-255 range
    rgb_colors *= 255
    rgb_colors = rgb_colors.astype(int)

    return rgb_colors

async def main():
    K = 1

    tracker.set_trackable_count(spheros)

    # Create starting state for the phase
    state = np.random.rand(spheros, 2)
    state[:, 0] = np.pi
    # state[:, 0] = 0
    state[:, 1] *= 2 * np.pi

    now = time.time()

    # Connect to spheros
    PacketHandler.init()
    async with AsyncExitStack() as stack:
        for i in range(min(len(sphero_names), spheros)):
                await connect_to_sphero(stack, sphero_names[i], i)

        # # We need to match sphero indexes with tracked ids
        # pos = []
        # for bot in bots:
        #     await bot.set_front_led(Color(r=0, g=255, b=0))
        #     pos = tracker.find_color((0, 255, 0))
        #     if (not pos):
        #         print("Failed to identify color")
        #         quit()
        #     await bot.set_front_led(Color(r=0, g=0, b=0))

        # print(pos)

        # tracker._update_tracker(pos)

        # while True:
        #     try:
        #         positions = tracker.get_positions()
        #         print(positions)
        #         break
        #     except Exception as e:
        #         continue

        # tracker.start_tracking_objects()

        # now = time.time()
        
        # heading = 0

        # while True:
        #     for bot in bots:
        #         bot.set_speed(15)
        #     await set_bots_heading(heading)
        #     heading += 40
        #     try:
        #         positions = tracker.get_positions()

        #         if positions is None:
        #             continue

        #         # First we will calculate the difference of sins
        #         thetas = state[:, 1:]

        #         theta_sin_difference = np.sin(thetas.T - thetas)

        #         # Now we will calculate the unit vectors
        #         vectors = positions[:, :2][:, np.newaxis] - positions[:, :2]
        #         pairwise_distances = np.linalg.norm(vectors, axis=2)

        #         mask = (pairwise_distances != 0)
                
        #         sums = np.sum(np.where(mask, theta_sin_difference / pairwise_distances, 0), axis=1)

        #         # Calculate the new state
        #         delta_thetas = state[:, 0] + (K/spheros) * sums
        #         state[:, 1] += delta_thetas * (time.time() - now) 

        #         # Bound the values between 0 and 2 pi
        #         state[:, 1] %= 2 * np.pi

        #         colors = angles_to_rgb(state[:, 1])

        #         # print(colors)

        #         await set_bots_matrix(colors)

        #         print("Elapsed time: {time}".format(time=time.time() - now))
        #         now = time.time()

        #     except Exception as e:
        #         # print(e)
        #         continue

## EXAMPLE CODE
if __name__ == "__main__":
    print("Sphero Swarm! Beginning to connect to {spheros} spheros".format(spheros=spheros))
    # asyncio.run(main())

    tracker.set_trackable_count(spheros)
    tracker.start_tracking_objects(run_server=True)

    while True:
        time.sleep(0.1)

    # # # tracker.add_trackable_objects([sphero_test, sphero_test1, sphero_test3, sphero_test4])
    # # # tracker.start_tracking_objects()

    