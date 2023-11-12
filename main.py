from __future__ import annotations
from dataclasses import dataclass, field, asdict
from colorama import Fore, Style, init
from datetime import datetime
from requests import Session
from typing import List
import time
import json
import re

init()

class Config:
    PROXY = {
        "http": "http://your_proxy_here",
        "https": "http://your_proxy_here"
    }
    SLEEP_DELAY = 2.5
    USERNAME_FILE_PATH = "usernames.txt"

@dataclass
class UserData:
    datetime: str
    username: str
    old_user_id: str
    new_user_id: str

@dataclass
class UserDataManager:
    user_data: List[UserData] = field(default_factory=list)
    json_file_path: str = "./monitor_data"

    @classmethod
    def load_from_json(cls, json_file_path: str) -> UserDataManager:
        try:
            with open(json_file_path, "r") as json_file:
                instance = cls(user_data=[UserData(**entry) for entry in json.load(json_file)])
        except (FileNotFoundError, json.JSONDecodeError):
            instance = cls(user_data=[])
        return instance

    def save_to_json(self):
        with open(self.json_file_path, "w") as json_file:
            json.dump([asdict(entry) for entry in self.user_data], json_file, indent=2)

    def log_initial_data(self, username: str, current_user_id: str) -> None:
        if not self.user_data or self.user_data[-1].old_user_id is not None:
            self.user_data.append(UserData(
                datetime=datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f"),
                username=username,
                old_user_id=current_user_id,
                new_user_id=None
            ))
            self.save_to_json()
            self.print_log(f"Initialized data for {username}:", asdict(self.user_data[-1]))

    def log_user_id_change(self, username: str, old_user_id: str, new_user_id: str) -> None:
        if old_user_id != new_user_id:
            self.user_data[-1].new_user_id = new_user_id
            self.save_to_json()
            self.print_log(f"User ID has changed for {username}. Logging the change:", asdict(self.user_data[-1]))

    @staticmethod
    def print_log(message: str, data: dict = None):
        log_message = f"{Fore.CYAN}[LOG]{Style.RESET_ALL} | {message}"
        if data:
            log_message += f" {Fore.YELLOW}| {data}"
        print(log_message)

class SoundCloudMonitor:
    def __init__(self, usernames: List[str]):
        self.usernames = usernames
        self.user_data_managers = {username: UserDataManager(json_file_path=f"./monitor_data/{username}_data.json") for username in self.usernames}
        self.invalid_usernames = set()

    def monitor_usernames(self):
        sessions = {username: self.create_session() for username in self.usernames}
        for username, session in sessions.items():
            session.proxies = Config.PROXY
        
        while True:
            for username in self.invalid_usernames.copy():
                if username not in self.usernames:
                    continue

                try:
                    session = sessions[username]
                    resp = session.get(f"https://soundcloud.com/{username}", stream=True)

                    if resp.status_code != 404:
                        self.invalid_usernames.remove(username)
                        self.user_data_managers[username].print_log(f"{username} is valid again. Resuming monitoring.")

                except Exception as e:
                    self.user_data_managers[username].print_log(f"An error occurred for {username}: {e}")

            for username in self.usernames:
                if username in self.invalid_usernames:
                    continue

                try:
                    session = sessions[username]
                    resp = session.get(f"https://soundcloud.com/{username}", stream=True)

                    if resp.status_code == 404:
                        if username not in self.invalid_usernames:
                            self.invalid_usernames.add(username)
                            self.user_data_managers[username].print_log(f"{username} is invalid. Skipping.")
                        continue

                    if username in self.invalid_usernames:
                        self.invalid_usernames.remove(username)

                    for chunk in resp.iter_content(8192):
                        pattern = r"https://api.soundcloud.com/users/(\d+)"
                        matches = re.findall(pattern, chunk.decode('utf-8'), re.DOTALL)

                        if matches:
                            current_user_id = matches[0]

                            manager = self.user_data_managers[username]
                            if not manager.user_data or manager.user_data[-1].username != username:
                                manager.log_initial_data(username, current_user_id)
                            elif manager.user_data[-1].old_user_id != current_user_id:
                                manager.log_user_id_change(username, manager.user_data[-1].old_user_id, current_user_id)

                except Exception as e:
                    self.user_data_managers[username].print_log(f"An error occurred for {username}: {e}")

            time.sleep(Config.SLEEP_DELAY)

    @staticmethod
    def create_session() -> Session:
        session = Session()
        return session

def read_usernames_from_file(file_path: str) -> List[str]:
    try:
        with open(file_path, "r") as file:
            usernames = [line.strip() for line in file if line.strip()]
        return usernames
    except FileNotFoundError:
        print(f"Usernames file '{file_path}' not found.")
        return []

if __name__ == "__main__":
    usernames_to_monitor = read_usernames_from_file(Config.USERNAME_FILE_PATH)
    soundcloud_monitor = SoundCloudMonitor(usernames_to_monitor)
    soundcloud_monitor.monitor_usernames()
