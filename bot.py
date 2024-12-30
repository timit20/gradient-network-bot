from aiohttp import (
    ClientResponseError,
    ClientSession,
    ClientTimeout
)
from curl_cffi import requests # type: ignore
from aiohttp_socks import ProxyConnector # type: ignore
from colorama import *
from datetime import datetime
import asyncio
import time
import json
import os
import uuid
import pytz
from typing import Optional, Dict, Any, List
from dataclasses import dataclass
from fake_useragent import FakeUserAgent # type: ignore
import logging
from contextlib import asynccontextmanager
import random

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('nodepay.log'),
        logging.StreamHandler()
    ]
)

@dataclass
class ProxyConfig:
    url: str
    protocol: str = "http"
    username: Optional[str] = None
    password: Optional[str] = None

    @classmethod
    def from_string(cls, proxy_str: str) -> 'ProxyConfig':
        parts = proxy_str.strip().split(':')
        if len(parts) == 4:  # ip:port:username:password
            return cls(
                url=f"{parts[0]}:{parts[1]}",
                username=parts[2],
                password=parts[3]
            )
        elif len(parts) == 2:  # ip:port
            return cls(url=proxy_str)
        elif '://' in proxy_str:  # protocol://ip:port or protocol://user:pass@ip:port
            return cls(url=proxy_str)
        else:
            return cls(url=proxy_str)

    def get_formatted_url(self) -> str:
        if self.username and self.password:
            base_url = self.url if ':' in self.url else f"{self.url}:80"
            return f"{self.protocol}://{self.username}:{self.password}@{base_url}"
        return f"{self.protocol}://{self.url}"

class RateLimiter:
    def __init__(self, calls: int, period: float):
        self.calls = calls
        self.period = period
        self.timestamps: List[float] = []
        self._lock = asyncio.Lock()

    async def acquire(self):
        async with self._lock:
            now = time.time()
            self.timestamps = [t for t in self.timestamps if now - t <= self.period]
            
            if len(self.timestamps) >= self.calls:
                sleep_time = self.timestamps[0] + self.period - now
                if sleep_time > 0:
                    await asyncio.sleep(sleep_time)
            
            self.timestamps.append(now)

class Nodepay:
    def __init__(self) -> None:
        self.headers = {
            "Accept": "*/*",
            "Accept-Language": "zh-CN,zh;q=0.9",
            "Origin": "https://app.nodepay.ai",
            "Referer": "https://app.nodepay.ai/",
            "Sec-Fetch-Dest": "empty",
            "Sec-Fetch-Mode": "cors",
            "Sec-Fetch-Site": "cross-site",
            "User-Agent": FakeUserAgent().random
        }
        self.proxies: List[ProxyConfig] = []
        self.proxy_index = 0
        self.rate_limiter = RateLimiter(calls=10, period=60)
        self.session: Optional[ClientSession] = None
        self.wib = pytz.timezone('Asia/Shanghai')

    def show_banner(self):
        print(f"\n{Fore.CYAN}{'='*50}")
        print(f"{Fore.GREEN}Nodepay Bot - 开发者: 小林")
        print(f"{Fore.GREEN}推特: @YOYOMYOYOA")
        print(f"{Fore.CYAN}{'='*50}\n")

    async def input_proxy(self) -> str:
        print(f"{Fore.YELLOW}请选择代理输入方式:")
        print("1. 直接输入代理地址")
        print("2. 从文件加载代理")
        print(f"3. 不使用代理{Style.RESET_ALL}")
        
        while True:
            try:
                choice = int(input("请选择 [1/2/3]: ").strip())
                if choice in [1, 2, 3]:
                    if choice == 1:
                        print(f"{Fore.YELLOW}支持的代理格式:")
                        print("1. ip:port:username:password")
                        print("2. ip:port")
                        print("3. protocol://ip:port")
                        print(f"4. protocol://username:password@ip:port{Style.RESET_ALL}")
                        proxy = input(f"{Fore.YELLOW}请输入代理地址: {Style.RESET_ALL}").strip()
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
                        return ""
                else:
                    print(f"{Fore.RED}无效选择，请输入 1、2 或 3{Style.RESET_ALL}")
            except ValueError:
                print(f"{Fore.RED}无效输入，请输入数字{Style.RESET_ALL}")

    @asynccontextmanager
    async def get_session(self, proxy: Optional[str] = None) -> ClientSession: # type: ignore
        if not self.session:
            connector = ProxyConnector.from_url(proxy) if proxy else None
            self.session = ClientSession(
                connector=connector,
                timeout=ClientTimeout(total=30)
            )
        try:
            yield self.session
        finally:
            if self.session and self.session.closed:
                await self.session.close()
                self.session = None

    async def make_request(
        self, 
        method: str, 
        url: str, 
        proxy: Optional[str] = None, 
        **kwargs
    ) -> Optional[Dict[str, Any]]:
        await self.rate_limiter.acquire()
        
        async with self.get_session(proxy) as session:
            try:
                async with session.request(method, url, **kwargs) as response:
                    response.raise_for_status()
                    return await response.json()
            except Exception as e:
                logging.error(f"Request failed: {e}")
                return None

    async def load_auto_proxies(self) -> None:
        url = "https://raw.githubusercontent.com/monosans/proxy-list/main/proxies/all.txt"
        try:
            async with self.get_session() as session:
                async with session.get(url) as response:
                    content = await response.text()
                    
                    with open('proxy.txt', 'w') as f:
                        f.write(content)

                    self.proxies = [
                        ProxyConfig(url=line.strip())
                        for line in content.splitlines()
                        if line.strip()
                    ]
                    
                    if not self.proxies:
                        logging.error("No proxies found in downloaded list")
                        return
                    
                    logging.info(f"Successfully loaded {len(self.proxies)} proxies")
        except Exception as e:
            logging.error(f"Failed to load auto proxies: {e}")

    def get_next_proxy(self) -> Optional[ProxyConfig]:
        if not self.proxies:
            return None

        proxy = self.proxies[self.proxy_index]
        self.proxy_index = (self.proxy_index + 1) % len(self.proxies)
        return proxy
    
    @staticmethod
    def hide_token(token: str) -> str:
        return f"{token[:3]}{'*' * 3}{token[-3:]}" if len(token) > 6 else token

    async def process_account(
        self, 
        token: str,
        use_proxy: bool = False
    ) -> None:
        hide_token = self.hide_token(token)
        proxy = None

        if use_proxy:
            proxy_config = self.get_next_proxy()
            if proxy_config:
                proxy = proxy_config.get_formatted_url()

        try:
            user_data = await self.user_session(token, proxy)
            if not user_data:
                logging.error(f"Failed to login account {hide_token}")
                return

            username = user_data.get('name', 'Unknown')
            user_id = user_data.get('uid')

            logging.info(f"Successfully logged in: {username}")
            
            # Process missions
            await self.process_missions(token, username, proxy)
            
            # Start ping loop
            await self.ping_loop(token, username, user_id, proxy)

        except Exception as e:
            logging.error(f"Error processing account {hide_token}: {e}")

    async def process_missions(
        self,
        token: str,
        username: str,
        proxy: Optional[str]
    ) -> None:
        missions = await self.mission_lists(token, proxy)
        if not missions:
            logging.warning(f"No missions available for {username}")
            return

        for mission in missions:
            if mission['status'] == "AVAILABLE":
                result = await self.complete_missions(
                    token,
                    mission['id'],
                    proxy
                )
                if result:
                    logging.info(
                        f"Completed mission {mission['title']} "
                        f"for {username}"
                    )

    async def ping_loop(
        self,
        token: str,
        username: str,
        user_id: str,
        proxy: Optional[str]
    ) -> None:
        while True:
            try:
                result = await self.send_ping(token, user_id, proxy)
                if result:
                    logging.info(
                        f"Ping successful for {username} "
                        f"(IP Score: {result.get('ip_score', 'N/A')})"
                    )
                else:
                    logging.warning(f"Ping failed for {username}")

                await asyncio.sleep(60)  # Wait for 1 minute
            except Exception as e:
                logging.error(f"Error in ping loop for {username}: {e}")
                await asyncio.sleep(60)  # Wait before retry

    async def main(self) -> None:
        try:
            self.show_banner()
            
            with open('tokens.txt', 'r') as file:
                tokens = [line.strip() for line in file if line.strip()]

            if not tokens:
                logging.error("No tokens found in tokens.txt")
                return
            
            logging.info(f"Found {len(tokens)} tokens")

            proxy = await self.input_proxy()
            use_proxy = bool(proxy)

            if use_proxy:
                proxy_config = ProxyConfig.from_string(proxy)
                self.proxies = [proxy_config]
                logging.info(f"Using proxy: {proxy_config.get_formatted_url()}")

            tasks = [
                self.process_account(token, use_proxy)
                for token in tokens
            ]
            await asyncio.gather(*tasks)

        except Exception as e:
            logging.error(f"Main process error: {e}")

    async def user_session(self, token: str, proxy: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """获取用户会话信息"""
        url = "http://api.nodepay.ai/api/auth/session"
        headers = {
            **self.headers,
            "Authorization": f"Bearer {token}",
            "Content-Length": "2",
            "Content-Type": "application/json",
        }
        return await self.make_request('POST', url, proxy, headers=headers, json={})

    async def user_earning(self, token: str, proxy: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """获取用户收益信息"""
        url = "http://api.nodepay.ai/api/earn/info"
        headers = {
            **self.headers,
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
        }
        return await self.make_request('GET', url, proxy, headers=headers)

    async def mission_lists(self, token: str, proxy: Optional[str] = None) -> Optional[List[Dict[str, Any]]]:
        """获取任务列表"""
        url = "http://api.nodepay.ai/api/mission"
        headers = {
            **self.headers,
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
        }
        result = await self.make_request('GET', url, proxy, headers=headers)
        return result.get('data') if result else None

    async def complete_missions(self, token: str, mission_id: str, proxy: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """完成任务"""
        url = "http://api.nodepay.ai/api/mission/complete-mission"
        headers = {
            **self.headers,
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
        }
        return await self.make_request('POST', url, proxy, headers=headers, json={'mission_id': mission_id})

    async def send_ping(self, token: str, user_id: str, proxy: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """发送 ping 请求"""
        url = "https://nw.nodepay.org/api/network/ping"
        headers = {
            "Accept": "*/*",
            "Accept-Language": "zh-CN,zh;q=0.9",
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
            "Origin": "chrome-extension://lgmpfmgeabnnlemejacfljbmonaomfmm",
            "Referer": "chrome-extension://lgmpfmgeabnnlemejacfljbmonaomfmm/",
            "Sec-Ch-Ua": '"Not_A Brand";v="8", "Chromium";v="120", "Microsoft Edge";v="120"',
            "Sec-Ch-Ua-Mobile": "?0",
            "Sec-Ch-Ua-Platform": '"Windows"',
            "Sec-Fetch-Dest": "empty",
            "Sec-Fetch-Mode": "cors",
            "Sec-Fetch-Site": "cross-site",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36 Edg/120.0.0.0"
        }
        data = {
            "id": user_id,
            "browser_id": str(uuid.uuid4()),
            "timestamp": int(time.time() * 1000),
            "version": "2.2.7"
        }
        
        try:
            proxies = {'http': proxy, 'https': proxy} if proxy else None
            response = requests.post(
                url=url,
                headers=headers,
                json=data,
                proxies=proxies,
                timeout=30,
                impersonate="chrome110"
            )
            response.raise_for_status()
            return response.json().get('data')
        except Exception as e:
            logging.error(f"Request failed: {e}")
            return None

    # ... (其他方法保持不变)

if __name__ == "__main__":
    try:
        bot = Nodepay()
        asyncio.run(bot.main())
    except KeyboardInterrupt:
        logging.info("Bot stopped by user")
    except Exception as e:
        logging.error(f"Fatal error: {e}")
