from json import load
from random import choice
from secrets import token_hex
from terminut import log
from tls_client import Session
from capmonster_python import turnstile
from concurrent.futures import ThreadPoolExecutor

config: dict = load(open("./data/config.json"))
proxies: list = [i.strip() for i in open("./data/proxies.txt").readlines()]
if config.get("random_usernames"):
    usernames: list = [token_hex(4) for _ in range(50)]
else:
    usernames: list = [i.strip() for i in open("./data/usernames.txt").readlines()]
    if len(usernames) == 0:
        log.error("No usernames found.")
        exit()


def _solve():
    capmonster = turnstile.TurnstileTask(config.get("capmonster_api_key"))
    task_id = capmonster.create_task(
        "https://solo.to/register", "0x4AAAAAAAAleWC9vsi5kuH5"
    )
    result: dict = capmonster.join_task_result(task_id)

    log.info(
        f"Solved Captcha. [{result.get('token')[:50]}...]",
    )
    return result.get("token")


class SoloTo:
    def __init__(self) -> None:
        self.headers = {
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
            "Accept-Encoding": "gzip, deflate, br",
            "Accept-Language": "en-US,en;q=0.5",
            "Connection": "keep-alive",
            "Cookie": "cf_clearance=G3jluJl3s395MJYNkIvqnNzFG2ZePC2Fh8j29fsCC6Q-1707785730-1-Aeph2S7uV7EpY9G7/JpbEIKwGJusquaFl6BLqy7P6gW0ViSJkhTK8IBuu5UHXApv8Ji45mXzPfdHb7SfqVny0+Q=",
            "Host": "solo.to",
            "Referer": "https://solo.to/",
            "Sec-Fetch-Dest": "document",
            "Sec-Fetch-Mode": "navigate",
            "Sec-Fetch-Site": "same-origin",
            "Sec-Fetch-User": "?1",
            "Upgrade-Insecure-Requests": "1",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:122.0) Gecko/20100101 Firefox/122.0",
        }
        self.client = Session(
            client_identifier="firefox_120", random_tls_extension_order=False
        )
        proxy = choice(proxies)
        self.client.proxies = {
            "http": proxy,
            "https": proxy,
        }

    def get_token(self):
        res = self.client.get("https://solo.to/register", headers=self.headers)
        _token = res.text.split('"_token" value="')[1].split('"')[0]
        return _token

    def register(self, username: str):
        headers = {
            **self.headers,
            "Content-Type": "application/x-www-form-urlencoded",
            "Origin": "https://solo.to",
            "Referer": "https://solo.to/register",
        }

        data = {
            "_token": self.get_token(),
            "username": username,
            "email": f"{token_hex(5)}@gmail.com",
            "password": "CcJB-)PKh3Gua-i",
            "password_confirmation": "CcJB-)PKh3Gua-i",
            "cf-turnstile-response": _solve(),
        }

        res = self.client.post("https://solo.to/register", data=data, headers=headers)
        if "https://solo.to/upgrade/register" in res.text:
            log.vert("Successfully registered.", Username=username)
        else:
            log.error(f"Failed to register. [{username}]")


def main(username):
    gen = SoloTo()
    gen.register(username)


if __name__ == "__main__":
    log.info(f"Starting register with {len(usernames):_} usernames.")
    with ThreadPoolExecutor(max_workers=10) as executor:
        for username in usernames:
            executor.submit(main, username)
