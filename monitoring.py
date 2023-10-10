# linux monitoring
import platform
import subprocess
import requests
import socket
import psutil

# import credentials from
from config import TEAMS_WEBHOOK_URL

# function to get os information
def get_os_info():
    os_info = {
        "system": platform.system(),
        "release": platform.release(),
        "distribution": read_os_release(),
        "hostname": socket.gethostname(),
        "ip_address": get_ip_address(),
        "uptime": get_uptime(),
        "disk_info": get_disk_info(),
        "running_processes": get_running_processes(),
        "logged_in_users": get_logged_in_users(),
        "cpu_usage": get_cpu_usage(),
    }
    return os_info

def get_running_processes():
    try:
        running_processes = len(psutil.pids())
        return running_processes
    except Exception as e:
        print(f"Error can't get proces: {str(e)}")
        return "Not available"

def get_logged_in_users():
    try:
        logged_in_users = len(subprocess.check_output("who").decode().splitlines())
        return logged_in_users
    except Exception as e:
        print(f"Error can't retrieve loggin in users: {str(e)}")
        return "Not available"

def get_cpu_usage():
    try:
        # cpu usage with psutil
        cpu_usage = psutil.cpu_percent(interval=10)  # 10 seconds interval
        return cpu_usage
    except Exception as e:
        print(f"Error cant get CPU usage: {str(e)}")
        return "Not available"

def get_ip_address():
    try:
        # ip addr from interface 
        ip_address = subprocess.check_output("hostname -I | awk '{print $1}'", shell=True).decode().strip()
        return ip_address
    except:
        return "Not available"

def get_uptime():
    try:
        uptime = subprocess.check_output("uptime -p", shell=True).decode().strip()
        return uptime
    except:
        return "Not available"

def read_os_release():
    try:
        with open("/etc/os-release", "r") as file:
            for line in file:
                if line.startswith("PRETTY_NAME="):
                    return line.split("=")[1].strip().strip('"')
        return "Not available"
    except Exception as e:
        print(f"Error can't read OS version: {str(e)}")
        return "Not available"


def get_disk_info():
    try:
        # diskspace info and usage in percentage
        df_output = subprocess.check_output("df -h --total | tail -n 1", shell=True).decode().split()
        disk_info = {
            "total_space": convert_to_gb(df_output[1]),
            "used_space": convert_to_gb(df_output[2]),
            "free_space": convert_to_gb(df_output[3]),
            "usage_percentage": df_output[4]
        }
        return disk_info
    except Exception as e:
        print(f"Error occurred when getting disk info: {str(e)}")
        return "Not available"

def convert_to_gb(size_str):
    # extract numeric
    numeric_part = float(size_str[:-1])

    # get size
    unit = size_str[-1].lower()

    # convert to GB
    if unit == 't':
        return numeric_part * 1024  # 1TB = 1024 GB
    elif unit == 'g':
        return numeric_part
    elif unit == 'm':
        return numeric_part / 1024  # 1MB = 0.001 GB /
    else:
        return 0.0  # error


def send_to_teams(os_info, teams_webhook_url):
    formatted_info = "```\n"
    formatted_info += "OS information:\n"
    formatted_info += f"System: {os_info['system']}\n"
    formatted_info += f"Release: {os_info['release']}\n"
    formatted_info += f"Distribution: {os_info['distribution']}\n"
    formatted_info += f"Hostname: {os_info['hostname']}\n"
    formatted_info += f"IP Address: {os_info['ip_address']}\n"
    formatted_info += f"Uptime: {os_info['uptime']}\n"
    formatted_info += "\nDisk Info:\n"
    formatted_info += f"Total Space: {os_info['disk_info']['total_space']:.2f} GB\n"
    formatted_info += f"Used Space: {os_info['disk_info']['used_space']:.2f} GB\n"
    formatted_info += f"Free Space: {os_info['disk_info']['free_space']:.2f} GB\n"
    formatted_info += f"Usage Percentage: {os_info['disk_info']['usage_percentage']}\n"
    formatted_info += f"\nRunning Processes: {os_info['running_processes']}\n"
    formatted_info += f"Logged-in Users: {os_info['logged_in_users']}\n"
    formatted_info += f"CPU Usage (last 10 seconds): {os_info['cpu_usage']:.2f}%\n"
    formatted_info += "```"

    payload = {
        "text": formatted_info
    }

    headers = {
        "Content-Type": "application/json"
    }

    response = requests.post(teams_webhook_url, json=payload, headers=headers)

    if response.status_code == 200:
        print("OS information sent to Teams.")
    else:
        print("Problem sending. HTTP Statuscode:", response.status_code)

def main():
    # ms teams webhook url (Incoming Webhook APP)
    os_info = get_os_info()
    send_to_teams(os_info, TEAMS_WEBHOOK_URL)  # format is: TEAMS_WEBHOOK_URL = "url" in example_config.py (rename to config.py)

if __name__ == "__main__":
    main()
