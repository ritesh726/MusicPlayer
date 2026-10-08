"""
Music Player, Telegram Voice Chat Bot
Copyright (c) 2021-present Asm Safone <https://github.com/AsmSafone>

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU Affero General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU Affero General Public License for more details.

You should have received a copy of the GNU Affero General Public License
along with this program.  If not, see <https://www.gnu.org/licenses/>
"""

import json
import asyncio
import os
import base64
from shlex import quote
from subprocess import PIPE
from datetime import timedelta
from aiohttp import ClientSession
from pyrogram.types import User, Message
from typing import Dict, Tuple, Union, Optional


class Song:
    def __init__(self, link: Union[str, dict], request_msg: Message) -> None:
        if isinstance(link, str):
            self.title: str = None
            self.duration: str = None
            self.thumb: str = None
            self.remote: str = None
            self.source: str = link
            self.headers: dict = None
            self.request_msg: Message = request_msg
            self.requested_by: User = request_msg.from_user
            self.parsed: bool = False
            self._retries: int = 0
        elif isinstance(link, dict):
            self.parsed: bool = True
            self._retries: int = 0
            self.duration: str = "N/A"
            self.headers: dict = None
            self.thumb: str = "https://telegra.ph/file/820cac7cb7b1a025542e2.jpg"
            for key, value in link.items():
                setattr(self, key, value)
            self.request_msg: Message = request_msg
            self.requested_by: User = request_msg.from_user
            
    async def parse(self) -> Tuple[bool, str]:
        if self.parsed:
            return (True, "ALREADY_PARSED")

        if self._retries >= 5:
            return (False, "MAX_RETRY_LIMIT_REACHED")

        cookie_b64 = os.getenv("YOUTUBE_COOKIES_B64")
cookie_path = "/tmp/youtube_cookies.txt"

if cookie_b64:
    with open(cookie_path, "wb") as f:
        f.write(base64.b64decode(cookie_b64))

cookie_arg = f' --cookies "{cookie_path}"' if cookie_b64 else ""

process = await asyncio.create_subprocess_shell(
    f"yt-dlp --js-runtimes deno{cookie_arg} --print-json --skip-download -f best {quote(self.source)}",
    stdout=PIPE,
    stderr=PIPE,
)

        out, err = await process.communicate()

        if process.returncode != 0:
            error = err.decode(errors="ignore").strip()
            self._retries += 1

            if self._retries >= 5:
                return (False, f"YTDLP_ERROR: {error[-1500:]}")

            return await self.parse()

        try:
            video = json.loads(out.decode())
        except (json.JSONDecodeError, UnicodeDecodeError):
            self._retries += 1

            if self._retries >= 5:
                error = err.decode(errors="ignore").strip()
                return (False, f"YTDLP_JSON_ERROR: {error[-1500:]}")

            return await self.parse()

        try:
            check_remote = await self.check_remote_url(
                video["url"], video["http_headers"]
            )

            check_thumb = await self.check_remote_url(
                video["thumbnail"], video["http_headers"]
            )

            if check_remote and check_thumb:
                self.title = self._escape(video["title"])
                self.duration = str(timedelta(seconds=video["duration"]))
                self.thumb = video["thumbnail"]
                self.remote = video["url"]
                self.headers = video["http_headers"]
                self.parsed = True
                return (True, "PARSED")

        except (KeyError, TypeError):
            pass

        self._retries += 1

        if self._retries >= 5:
            return (False, "YTDLP_ERROR: Invalid YouTube response")

        return await self.parse()

    @staticmethod
    async def check_remote_url(
        path: str, headers: Optional[Dict[str, str]] = None
    ) -> bool:
        try:
            session = ClientSession()
            response = await session.get(path, timeout=5, headers=headers)
            response.close()
            await session.close()
            if response.status == 200:
                return True
            else:
                return False
        except BaseException:
            return False

    @staticmethod
    def _escape(_title: str) -> str:
        title = _title
        f = ["**", "__", "`", "~~", "--"]
        for i in f:
            title = title.replace(i, f"\\{i}")
        return title

    def to_dict(self) -> Dict[str, str]:
        return {"title": self.title, "source": self.source}
