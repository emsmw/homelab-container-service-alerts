#!/usr/bin/env python3
import docker
import sys
import config_secret
import requests
from colorama import Fore, Style, init
from datetime import datetime
from zoneinfo import ZoneInfo

init(autoreset=True)

WEBHOOK_URL = config_secret.DISCORD_WEBHOOK

def main():
    # CONNECT TO DOCKER DAEMON
    # Initialize the docker client connections
    healthy_container_list =[]
    bad_container_list = []
    client = docker.from_env()
    all_containers = client.containers.list(all=True)

    for container in all_containers:
        container_name = container.name
        container_status = container.status
    
        if container_status == "running" or container_status == "healthy":
            healthy_container_list.append(container_name)
        else:
            bad_container_list.append(container_name)

    #Print services status summary in terminal
    print("\n########################################")
    print("             SCAN COMPLETE              ")
    print("########################################")

    col_width = 30
    print(f"{'CONTAINER NAME':<{col_width}} {'STATUS'}")
    print("-" * (col_width + 10))
    if healthy_container_list:
        for health_container in healthy_container_list:
            print(f"{health_container:<{col_width}} {Fore.GREEN}RUNNING{Style.RESET_ALL}")
    if bad_container_list:
        for bad_container in bad_container_list:
            print(f"{bad_container:<{col_width}} {Fore.RED}STOPPED{Style.RESET_ALL}")
    print("-" * (col_width + 10) + "\n")

    total_containers = len(healthy_container_list) + len(bad_container_list)
    print(f"Summary: {len(healthy_container_list)}/{total_containers} containers running")

    timestamp = datetime.now(ZoneInfo("America/Toronto")).strftime("%Y-%m-%d %H:%M:%S %Z")
    print(f"Scan time: {timestamp}")

    return healthy_container_list, bad_container_list


def discord_msg(bad_container_list):
    timestamp = datetime.now(ZoneInfo("America/Toronto")).strftime("%Y-%m-%d %H:%M:%S %Z")
    if bad_container_list:
        alert_message = f"🚨 **ALERT** `{timestamp}`\n"
        alert_message += "The following containers are down on Minos:\n"
        for bad_container in bad_container_list:
            alert_message += f"❌ `{bad_container}` is down!\n"    
        payload = {"content": alert_message}

    else:
        noti_message = f"✅ `{timestamp}`\n All services running on Minos"
        payload = {"content": noti_message}

    try:
        response = requests.post(WEBHOOK_URL, json=payload)
        if response.status_code == 204:
            print("Notification successfully sent to Discord!")
        else:
            print(f"Failed to send Discord notification. Status code: {response.status_code}")
    except Exception as e:
        print(f"Error sending webhook request: {e}")

if __name__ == "__main__":
    healthy_container_list, bad_container_list = main()
    discord_msg(bad_container_list)