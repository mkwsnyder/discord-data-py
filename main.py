# %%

import json
import os
import re

import matplotlib.pyplot as plt
import numpy as np

YEAR = "2025"

dms = {}
servers = {}

with open("./discord-package/Messages/index.json", "r") as f:
    entries = json.load(f)

    for entry in entries:
        if entries[entry].startswith("Direct Message with"):
            name = re.search(r"Direct Message with (.*?)#0", entries[entry])
            if name:
                dms[entry] = {"name": name.group(1), "count": 0}

message_folder = "./discord-package/Messages"
types = {}

entries = os.listdir(message_folder)
for name in entries:
    full = os.path.join(message_folder, name)
    if os.path.isdir(full):
        channel_info = {}
        with open(full + "/channel.json", "r") as f:
            channel_info = json.load(f)

        if "type" not in channel_info:
            continue

        if channel_info["type"] in types:
            types[channel_info["type"]] += 1
        else:
            types[channel_info["type"]] = 1
            # print(channel_info)

        with open(full + "/messages.json", "r") as f:
            arr = json.load(f)

            if channel_info["type"] == "DM":
                for message in arr:
                    if message["Timestamp"].startswith(YEAR):
                        if channel_info["id"] in dms:
                            dms[channel_info["id"]]["count"] += 1
                        else:
                            print(f"No DM info for {channel_info['id']}")

            elif channel_info["type"] == "GROUP_DM":
                pass
            else:  # guild (GUILD_TEXT, PUBLIC_THREAD, GUILD_VOICE)
                if "guild" not in channel_info:
                    continue  # this is a server you're no longer in
                if channel_info["guild"]["id"] not in servers:
                    servers[channel_info["guild"]["id"]] = {
                        "name": channel_info["guild"]["name"],
                        "count": 0,
                    }

                for message in arr:
                    if message["Timestamp"].startswith(YEAR):
                        servers[channel_info["guild"]["id"]]["count"] += 1

# %%

sorted_dms = sorted(dms.items(), key=lambda item: item[1]["count"], reverse=True)
sorted_servers = sorted(
    servers.items(), key=lambda item: item[1]["count"], reverse=True
)

for arr in [sorted_dms, sorted_servers]:
    top_dms = arr[:10]
    dm_names = [dm[1]["name"] for dm in top_dms]
    dm_counts = [dm[1]["count"] for dm in top_dms]

    x = np.arange(len(dm_names))
    plt.bar(x, dm_counts)
    plt.xticks(x, dm_names, rotation=45, ha="right")
    plt.ylabel("Message Count")
    title = (
        f"Top 10 DMs in {YEAR}"
        if arr == sorted_dms
        else f"Top 10 Most Messaged Servers in {YEAR}"
    )
    plt.title(title)
    plt.tight_layout()
    plt.savefig(title.replace(" ", "-"))
    plt.show()
    plt.clf()

# %%

total_dms_sent = sum([dm[1]["count"] for dm in sorted_dms])
total_server_sent = sum([server[1]["count"] for server in sorted_servers])

# print("Total DMs sent: ", total_dms_sent)
# print("Total server messages sent: ", total_server_sent)
# print("Total messages sent:", total_dms_sent + total_server_sent)

with open(f"message-stats-{YEAR}.txt", "w") as f:
    f.write(f"Message Stats for {YEAR}\n\n")
    f.write(f"Total DMs sent: {total_dms_sent}\n")
    f.write(f"Total server messages sent: {total_server_sent}\n")
    f.write(f"Total messages sent: {total_dms_sent + total_server_sent}\n\n")

    f.write("Top 10 DMs:\n")
    for dm in sorted_dms[:10]:
        f.write(f"{dm[1]['name']}: {dm[1]['count']}\n")

    f.write("\nTop 10 Servers:\n")
    for server in sorted_servers[:10]:
        f.write(f"{server[1]['name']}: {server[1]['count']}\n")
