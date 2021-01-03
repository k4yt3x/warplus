#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Name: WARPlus
Author: K4YT3X
Date Created: January 1, 2021
Last Modified: January 3, 2021

Descriptin: WARPlus is a tool similar to ALIILAPRO/warp-plus-cloudflare.
"""

# built-in imports
import argparse
import collections
import datetime
import random
import string
import sys
import threading
import time

# third-party imports
import requests


VERSION = "1.0.0"

HEADERS = {
    "Content-Type": "application/json; charset=UTF-8",
    "Host": "api.cloudflareclient.com",
    "Connection": "Keep-Alive",
    "Accept-Encoding": "gzip",
    "User-Agent": "okhttp/3.12.1",
}


class RequestSender(threading.Thread):
    """RequesterSender instances are workers that send
    POST requests to CloudFlare's servers. It inherits
    threading.Thread and can be started/stopped like a
    thread.
    """

    def __init__(
        self,
        warpid: str,
        interval: int,
        post_url: str,
        limit: int,
        timeout: int,
        autoremove: bool,
    ):
        threading.Thread.__init__(self)
        self.warpid = warpid
        self.interval = interval
        self.post_url = post_url
        self.limit = limit
        self.timeout = timeout
        self.autoremove = autoremove
        self.running = False

    def run(self):
        global successes
        self.running = True
        while self.running and (self.limit is None or successes < self.limit):
            self.send_request()
            time.sleep(self.interval)
        _print(f"Thread {self.name} exiting")

    def stop(self):
        self.running = False
        self.join()

    def send_request(self):
        """send POST request to CloudFlare's server"""
        global successes
        global fails
        global proxies

        succeeded = False
        error_message = ""

        try:

            # generate random installation ID
            install_id = "".join(
                random.choices(string.ascii_uppercase + string.digits, k=22)
            )

            # construct POST request payload
            post_data = {
                "key": f"{''.join(random.choices(string.ascii_uppercase + string.digits, k=43))}=",
                "install_id": install_id,
                "fcm_token": f"{install_id}:APA91b{''.join(random.choices(string.ascii_uppercase + string.digits, k=134))}",
                "referrer": self.warpid,
                "warp_enabled": False,
                "tos": datetime.datetime.utcnow().isoformat()[:-3] + "+00:00",
                "type": "Android",
                "locale": "en_US",
            }

            # send request
            if proxies is None:
                response = requests.post(
                    self.post_url, json=post_data, headers=HEADERS, timeout=self.timeout
                )

            else:

                proxy = proxies.popleft()

                response = requests.post(
                    self.post_url,
                    json=post_data,
                    headers=HEADERS,
                    timeout=self.timeout,
                    proxies={
                        "http": f"https://{proxy}",
                        "https": f"https://{proxy}",
                    },
                )

            if response.status_code == requests.codes.ok:
                successes += 1
                succeeded = True
            else:
                fails += 1
                error_message = f" with code {response.status_code}"

            if proxies:
                proxies.append(proxy)

        except IndexError:
            self.running = False
            return

        # print error and carryon on upon exceptions
        except Exception as e:
            # _print(f"Thread {self.name} encountered an exception")
            # _print(traceback.format_exc(), file=sys.stderr)

            fails += 1
            error_message = f" with Python exception {e}"

            if proxies and not self.autoremove:
                proxies.append(proxy)

        finally:
            #if proxies is Nonetype, then it has no len()
            if proxies is None:
                proxies = []
            if succeeded:
                _print(
                    f"[Successes: {successes} | Fails: {fails} | Proxies: {len(proxies)}] Thread {self.name} succeeded",
                    file=sys.stderr,
                )

            else:
                _print(
                    f"[Successes: {successes} | Fails: {fails} | Proxies: {len(proxies)}] Thread {self.name} failed{error_message}",
                    file=sys.stderr,
                )


def _print(message: str, **kwargs):
    """thread-safe print

    Args:
        message (str): message to print
    """
    print_lock.acquire()
    print(message, **kwargs)
    print_lock.release()


def parse_arguments():

    parser = argparse.ArgumentParser(
        prog="warplus", formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )

    parser.add_argument("-w", "--warpid", help="WARP device ID", required=True)

    parser.add_argument(
        "-t",
        "--threads",
        help="number of threads to use",
        default=1,
        type=int,
    )

    parser.add_argument(
        "-i",
        "--interval",
        help="time interval between sending two requests in one thread",
        default=15,
        type=int,
    )

    parser.add_argument(
        "-l",
        "--limit",
        help="set the maximum number of successful requests the script will send",
        type=int,
    )

    parser.add_argument("-o", "--timeout", help="server connection timeout", type=int)

    parser.add_argument("-p", "--proxies", help="use proxies", action="store_true")

    parser.add_argument(
        "-a",
        "--autoremove",
        help="automatically remove unusable proxies",
        action="store_true",
    )

    parser.add_argument(
        "-u",
        "--url",
        help="URL to send the POST request to",
        default=f"https://api.cloudflareclient.com/v0a{random.randint(100, 999)}/reg",
    )

    parser.add_argument(
        "-v",
        "--version",
        help="print WARPlus's version and exit",
        action="store_true",
    )

    return parser.parse_args()


def get_proxies() -> collections.deque:
    """get a list of proxies from ProxyScrape

    Returns:
        collections.deque: a deque of retrieved proxies
    """

    proxies_request = requests.get(
        "https://api.proxyscrape.com/v2/?request=getproxies&protocol=http&timeout=10000&country=all&ssl=all&anonymity=all"
    )

    # if response status code is 200, return the list of retrieved proxies
    if proxies_request.status_code == requests.codes.ok:
        proxies = proxies_request.text.split()
        _print(f"Successfully retried a list of proxies ({len(proxies)} proxies)")
        return collections.deque(proxies)

    # requests failed to download the list of proxies, raise an exception
    else:
        _print("An error occured while retrieving a list of proxies")
        proxies_request.raise_for_status()


# parse command line arguments
args = parse_arguments()

if args.version:
    sys.exit(0)

print(f"WARPlus v{VERSION}")
print("(C) K4YT3X 2021")

# initialize variables for the next section
print_lock = threading.Lock()
thread_pool = []

# successes / failures counters
successes = 0
fails = 0
proxies = None

# download a list of proxies if proxies are to be used
if args.proxies:
    proxies = get_proxies()

# start threads and add them into the thread pool
for thread_id in range(args.threads):

    thread = RequestSender(
        args.warpid, args.interval, args.url, args.limit, args.timeout, args.autoremove
    )

    thread.name = str(thread_id)
    _print(f"Starting thread {thread.name}")
    thread.start()
    thread_pool.append(thread)

# wait for threads to join
try:
    for thread in thread_pool:
        thread.join()

# if OS kill signal is received or ^C is pressed, stop threads
except (SystemExit, KeyboardInterrupt):
    _print("Exit signal received, stopping threads")
    for thread in thread_pool:
        thread.stop()

    _print("Waiting for threads to exit")
    for thread in thread_pool:
        thread.join()

print("Script finished")
