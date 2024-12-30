import requests
import time
import logging
import random
from datetime import datetime, timedelta
from typing import Dict, Optional, Any, List
import re
import threading
import asyncio
from dataclasses import dataclass
from concurrent.futures import ThreadPoolExecutor
from colorama import Fore, Style, init

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('game_bot.log'),
        logging.StreamHandler()
    ]
)

@dataclass
class GameConfig:
    api_url: str = "https://nodewars.nodepay.ai"
    headers: Dict[str, str] = None
    
    def __post_init__(self):
        self.headers = {
            "Content-Type": "application/json",
            "Accept": "*/*",
            "Accept-Encoding": "gzip, deflate, br, ztsd",
            "Accept-Language": "en-GB,en;q=0.9,en-US;q=0.8",
            "Priority": "u=1, i",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            "Origin": "https://minigame-nw.nodepay.ai",
            "Referer": "https://minigame-nw.nodepay.ai/",
            "Sec-CH-Ua": 'Microsoft Edge";v="131", "Chromium";v="131", "Not_A_Brand";v="24"',
            "Sec-CH-Ua-Mobile": "?0",
            "Sec-CH-Ua-Platform": "Windows",
        }

@dataclass
class GameSession:
    query_string: str
    username: str
    last_claim_time: Optional[datetime] = None
    proxy: Optional[str] = None

class RateLimiter:
    def __init__(self, max_requests: int, time_window: float):
        self.max_requests = max_requests
        self.time_window = time_window
        self.requests = []
        self._lock = threading.Lock()

    def acquire(self) -> bool:
        with self._lock:
            now = time.time()
            self.requests = [req_time for req_time in self.requests 
                           if now - req_time <= self.time_window]
            
            if len(self.requests) >= self.max_requests:
                return False
                
            self.requests.append(now)
            return True

class GameBot:
    def __init__(self):
        init(autoreset=True)
        self.config = GameConfig()
        self.rate_limiter = RateLimiter(max_requests=30, time_window=60)
        self.token_list = [
            "nodewars", "shiba", "nodepay", "pepe", "polkadot", 
            "babydoge", "bnb", "avax", "eth", "usdt", "solana", 
            "aptos", "ton", "bonk", "bomb", "doge", "floki", 
            "chainlink", "uniswap", "trx", "lido", "xrp", "ltc", 
            "ada", "sui", "dogwifhat", "near", "bitcoin"
        ]

    def show_banner(self):
        print(f"\n{Fore.CYAN}{'='*50}")
        print(f"{Fore.GREEN}Nodewars Game Bot - 开发者: 小林")
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
                        file_path = input(f"{Fore.YELLOW}请输入代理文件路径 (默认: proxie.txt): {Style.RESET_ALL}").strip() or "proxie.txt"
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

    def load_proxies(self, file_path: str = 'proxie.txt') -> List[str]:
        try:
            with open(file_path, 'r') as file:
                proxies = [line.strip() for line in file if line.strip()]
                logging.info(f"Loaded {len(proxies)} proxies")
                return proxies
        except FileNotFoundError:
            logging.warning(f"Proxy file {file_path} not found")
            return []

    def load_query_strings(self, file_path: str = 'data.txt') -> List[str]:
        try:
            with open(file_path, 'r') as file:
                queries = [line.strip() for line in file if line.strip()]
                logging.info(f"Loaded {len(queries)} query strings")
                return queries
        except FileNotFoundError:
            logging.error(f"Data file {file_path} not found")
            return []

    def extract_username(self, query_string: str) -> str:
        try:
            match = re.search(r'username%22%3A%22([^%"]+)', query_string)
            username = match.group(1) if match else query_string[:15]
            return username.ljust(15)[:15]
        except Exception:
            return 'Unknown'.ljust(15)

    def make_request(
        self,
        method: str,
        endpoint: str,
        session: GameSession,
        json_data: Optional[Dict] = None
    ) -> Optional[Dict[str, Any]]:
        if not self.rate_limiter.acquire():
            time.sleep(1)
            return None

        url = f"{self.config.api_url}{endpoint}"
        headers = {
            **self.config.headers,
            "Authorization": f"Bearer {session.query_string}"
        }
        proxies = {'http': session.proxy, 'https': session.proxy} if session.proxy else None

        try:
            response = requests.request(
                method=method,
                url=url,
                headers=headers,
                json=json_data,
                proxies=proxies,
                timeout=30
            )
            response.raise_for_status()
            return response.json().get('data')
        except Exception as e:
            logging.error(f"Request failed for {session.username}: {e}")
            return None

    def login(self, session: GameSession) -> Optional[Dict[str, Any]]:
        return self.make_request('GET', '/users/profile', session)

    def claim_daily(self, session: GameSession) -> Optional[Dict[str, Any]]:
        if (session.last_claim_time and 
            datetime.now() - session.last_claim_time < timedelta(hours=24)):
            logging.info(f"Daily reward not yet available for {session.username}")
            return None

        payload = {"missionId": "66c4b006c767c2cee0afe806"}
        result = self.make_request('POST', '/missions/daily/claim', session, payload)
        
        if result:
            session.last_claim_time = datetime.now()
            logging.info(f"Daily reward claimed for {session.username}")
        
        return result

    def start_game(self, level: int, session: GameSession) -> Optional[Dict[str, Any]]:
        payload = {"level": level}
        return self.make_request('POST', '/game/start', session, payload)

    def finish_game(
        self,
        session_id: str,
        game_log_id: str,
        session: GameSession
    ) -> Optional[Dict[str, Any]]:
        collected_tokens = {
            token: random.randint(1, 3) 
            for token in random.sample(self.token_list, k=random.randint(5, 10))
        }
        
        payload = {
            "sessionId": session_id,
            "gameLogId": game_log_id,
            "isCompleted": True,
            "timeSpent": random.randint(25000, 30000),
            "actionLogs": [
                f"{random.choice(['10', '31', '53', '43'])}"
                f"{random.randint(1000, 9999)}"
                f"{int(time.time() * 1000000) + i}"
                for i in range(24)
            ],
            "score": random.randint(45, 60),
            "collectedTokens": collected_tokens
        }
        
        return self.make_request('POST', '/game/finish', session, payload)

    async def process_account(self, session: GameSession):
        logging.info(f"Starting process for {session.username}")
        
        user_data = self.login(session)
        if not user_data:
            logging.error(f"Login failed for {session.username}")
            return

        while True:
            try:
                # Claim daily reward
                self.claim_daily(session)

                # Start and finish game
                level = user_data.get("level", 1)
                game_data = self.start_game(level, session)
                
                if game_data:
                    time.sleep(random.randint(25, 35))
                    finish_data = self.finish_game(
                        game_data["sessionId"],
                        game_data["gameLogId"],
                        session
                    )
                    
                    if finish_data and finish_data.get("isLevelUp"):
                        user_data["level"] += 1
                        logging.info(f"{session.username} leveled up to {user_data['level']}")

                time.sleep(random.randint(30, 60))
            except Exception as e:
                logging.error(f"Error processing {session.username}: {e}")
                time.sleep(60)

    async def run(self):
        self.show_banner()
        
        query_strings = self.load_query_strings()
        if not query_strings:
            return

        proxy = self.input_proxy()
        sessions = []

        for query_string in query_strings:
            session = GameSession(
                query_string=query_string,
                username=self.extract_username(query_string),
                proxy=proxy
            )
            sessions.append(session)

        with ThreadPoolExecutor() as executor:
            loop = asyncio.get_event_loop()
            tasks = [
                loop.run_in_executor(
                    executor,
                    lambda s=session: asyncio.run(self.process_account(s))
                )
                for session in sessions
            ]
            await asyncio.gather(*tasks)

def main():
    bot = GameBot()
    try:
        asyncio.run(bot.run())
    except KeyboardInterrupt:
        logging.info("Bot stopped by user")
    except Exception as e:
        logging.error(f"Fatal error: {e}")

if __name__ == "__main__":
    main()
