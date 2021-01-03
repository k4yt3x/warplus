# WARPlus

WARPlus helps you to get free quota on CloudFlare's WARP+.

This project is based on [ALIILAPRO/warp-plus-cloudflare](https://github.com/ALIILAPRO/warp-plus-cloudflare)'s concepts. WARPlus differs by being a CLI application and supports a lot of extra features.

Please do not abuse this script and use CloudFlare's services fairly. Don't let this become a tragedy of the commons  and ruin it for everyone. This script is for educational purposes only.

![screenshot](https://user-images.githubusercontent.com/21986859/103475930-77397c80-4da9-11eb-8e84-a780c3e0ea21.png)

## Quick Start

The most basic way to use this application is shown below. `DEVICE_ID` here should be replaced with your WARP application's device ID (e.g., `9a4190b3-ab1c-465c-aa03-189aa5141ec1`). This ID can be found in `Menu > Advanced > Diagnostics > Client Configuration > ID` on mobile phones. If you're using `wgcf`, it will be in the `wgcf-account.toml` file.

This command will run WARPlus with one thread using your own IP. It will send a request every 15 seconds to avoid being rate-limited by CloudFlare.

```shell
python3 warplus.py -w DEVICE_ID
```

If you'd like to do it faster, you can try multi-threading + proxies. WARPlus can retrieve a list of proxies automatically from ProxyScrape, just like [ALIILAPRO/warp-plus-cloudflare](https://github.com/ALIILAPRO/warp-plus-cloudflare)'s GUI version.

The example below will launch 100 threads, use proxies, have a sending-interval of 1 second, automatically delete unusable proxies from the proxy list, and wait for the server to respond for a maximum of 10 seconds. Threads without jobs to do will exit automatically.

```shell
py3 warplus.py -w DEVICE_ID -t 100 -p -i 1 -a -o 10
```

You can also set a limit on the maximum number of times the script will send successful requests. For example, if you want to get *about* 10 gigabytes of quota, you can set `-l/--limit` to 10. Be aware that if you have too many threads, the limit might get exceeded.

## Full Usages

```console
usage: warplus [-h] -w WARPID [-t THREADS] [-i INTERVAL] [-l LIMIT] [-o TIMEOUT] [-p] [-a] [-u URL] [-v]

optional arguments:
  -h, --help            show this help message and exit
  -w WARPID, --warpid WARPID
                        WARP device ID (default: None)
  -t THREADS, --threads THREADS
                        number of threads to use (default: 5)
  -i INTERVAL, --interval INTERVAL
                        time interval between sending two requests in one thread (default: 15)
  -l LIMIT, --limit LIMIT
                        set the maximum number of successful requests the script will send (default: None)
  -o TIMEOUT, --timeout TIMEOUT
                        server connection timeout (default: None)
  -p, --proxies         use proxies (default: False)
  -a, --autoremove      automatically remove unusable proxies (default: False)
  -u URL, --url URL     URL to send the POST request to (default: https://api.cloudflareclient.com/v0a398/reg)
  -v, --version         print WARPlus's version and exit (default: False)
```
