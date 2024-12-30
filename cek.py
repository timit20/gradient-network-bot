from curl_cffi import requests as curl_requests # type: ignore
from colorama import Fore, Style, init
from datetime import datetime
import time
import logging
import json
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from concurrent.futures import ThreadPoolExecutor
import asyncio
import random

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('ip_check.log'),
        logging.StreamHandler()
    ]
)

@dataclass
class DeviceInfo:
    ip_address: str
    ip_score: float
    total_points: int

class IPChecker:
    def __init__(self):
        init(autoreset=True)
        self.url = "https://api.nodepay.org/api/network/device-networks"
        self.headers = {
            "Accept": "*/*",
            "Accept-Encoding": "gzip, deflate, br, zstd",
            "Content-Type": "application/json",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            "Origin": "https://app.nodepay.ai",
            "Referer": "https://app.nodepay.ai/",
            "Sec-Fetch-Site": "cross-site",
            "Sec-Fetch-Mode": "cors",
            "Sec-Fetch-Dest": "empty"
        }
        self.params = {
            "page": 0,
            "limit": 10,
            "active": "true"
        }

    def show_banner(self):
        print(f"\n{Fore.CYAN}{'='*50}")
        print(f"{Fore.GREEN}Nodepay IP Checker - 开发者: 小林")
        print(f"{Fore.GREEN}推特: @YOYOMYOYOA")
        print(f"{Fore.CYAN}{'='*50}\n")

    def input_proxy(self) -> Optional[str]:
        print(f"{Fore.YELLOW}请选择代理输入方式:")
        print("1. 直接输入代理地址")
        print("2. 从文件加载代理")
        print(f"3. 不使用代理{Style.RESET_ALL}")
        
        while True:
            try:
                choice = int(input("请选择 [1/2/3]: ").strip())
                if choice in [1, 2, 3]:
                    if choice == 1:
                        proxy = input(f"{Fore.YELLOW}请输入代理地址 (格式: protocol://ip:port 或 protocol://user:pass@ip:port): {Style.RESET_ALL}").strip()
                        if proxy:
                            return proxy
                    elif choice == 2:
                        file_path = input(f"{Fore.YELLOW}请输入代理文件路径 (默认: manual_proxy.txt): {Style.RESET_ALL}").strip() or "manual_proxy.txt"
                        try:
                            with open(file_path, 'r') as f:
                                proxies = [line.strip() for line in f if line.strip()]
                                if proxies:
                                    return random.choice(proxies)
                                else:
                                    print(f"{Fore.RED}代理文件为空{Style.RESET_ALL}")
                        except FileNotFoundError:
                            print(f"{Fore.RED}找不到代理文件: {file_path}{Style.RESET_ALL}")
                    else:
                        return None
                else:
                    print(f"{Fore.RED}无效选择，请输入 1、2 或 3{Style.RESET_ALL}")
            except ValueError:
                print(f"{Fore.RED}无效输入，请输入数字{Style.RESET_ALL}")

    def load_tokens(self) -> List[str]:
        try:
            with open('tokens.txt', 'r') as file:
                return [token.strip() for token in file if token.strip()]
        except FileNotFoundError:
            logging.error("tokens.txt file not found")
            return []
        except Exception as e:
            logging.error(f"Error loading tokens: {e}")
            return []

    def check_device(self, token: str, proxy: Optional[str] = None) -> Optional[List[DeviceInfo]]:
        token_display = f"{token[:4]}{'*' * 10}{token[-4:]}"
        logging.info(f"Processing account: {token_display}")

        try:
            headers = {**self.headers, "Authorization": f"Bearer {token}"}
            proxies = {'http': proxy, 'https': proxy} if proxy else None
            response = curl_requests.get(
                self.url,
                headers=headers,
                params=self.params,
                proxies=proxies,
                impersonate="chrome110"
            )
            response.raise_for_status()
            data = response.json()

            if not data.get("success"):
                logging.error(f"Request failed for {token_display}: {data.get('msg')}")
                return None

            devices = []
            for device in data["data"]:
                device_info = DeviceInfo(
                    ip_address=device.get("ip_address", "Unknown"),
                    ip_score=device.get("ip_score", 0),
                    total_points=device.get("total_points", 0)
                )
                devices.append(device_info)
                logging.info(
                    f"Device info - IP: {device_info.ip_address}, "
                    f"Score: {device_info.ip_score}, "
                    f"Points: {device_info.total_points}"
                )

            return devices

        except Exception as e:
            logging.error(f"Error checking device for {token_display}: {e}")
            return None

    async def process_tokens(self):
        self.show_banner()
        
        tokens = self.load_tokens()
        if not tokens:
            logging.error("No tokens found to process")
            return

        logging.info(f"Total accounts: {len(tokens)}")
        print(f"{Fore.YELLOW}{'='*35}")
        print(f"{Fore.YELLOW} NODEPAY IP ACCOUNT VALIDITY CHECK ")
        print(f"{Fore.YELLOW}{'='*35}\n")

        proxy = self.input_proxy()
        if proxy:
            logging.info(f"Using proxy: {proxy}")

        with ThreadPoolExecutor() as executor:
            loop = asyncio.get_event_loop()
            tasks = [
                loop.run_in_executor(executor, self.check_device, token, proxy)
                for token in tokens
            ]
            results = await asyncio.gather(*tasks)

            success_count = sum(1 for r in results if r is not None)
            logging.info(
                f"Check completed - Success: {success_count}, "
                f"Failed: {len(tokens) - success_count}"
            )

def main():
    checker = IPChecker()
    try:
        asyncio.run(checker.process_tokens())
    except KeyboardInterrupt:
        logging.info("Check process stopped by user")
    except Exception as e:
        logging.error(f"Fatal error: {e}")

if __name__ == "__main__":
    main()
