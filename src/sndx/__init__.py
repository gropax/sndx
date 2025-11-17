import os
import subprocess
import time
import asyncio
import secrets
import re
from pathlib import Path
from datetime import timedelta
from pyppeteer import launch


CHROMIUM_PATH = os.environ.get("CHROMIUM_PATH")
LOGIN_URL = "https://vod.catalogue-crc.org/connexion.html"
WAIT_SECONDS = 2  # Wait duration between navigation operations


def parse_duration(s: str) -> int:
    parts = list(map(int, s.split(":")))
    if len(parts) == 3:
        h, m, sec = parts
    elif len(parts) == 2:
        h = 0
        m, sec = parts
    else:
        raise ValueError(f"Invalid duration format: {s}")

    seconds = h * 3600 + m * 60 + sec
    return timedelta(seconds=seconds)


def safe_filename(s):
    s = s.strip()
    s = re.sub(r"[^A-Za-z0-9._-]+", "_", s)
    return s or "file"


def generate_id():
    return secrets.token_urlsafe(4)[:6]


class Sink:
    def __init__(self):
        self.id = generate_id()
        self.name = f"sndx-{self.id}"
        self.module_id = None

    def open(self):
        print(f"Opening sink {self.name}")
        self.module_id = subprocess.check_output(
            ["pactl", "load-module", "module-null-sink", self.name],
            text=True).strip()

    def close(self):
        print(f"Closing sink {self.name}")
        subprocess.Popen(["pactl", "unload-module", self.module_id])

    def __repr__(self):
        return f"Sink(id={self.id!r}, module_id={self.module_id!r})"

    def __enter__(self):
        self.open()
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.close()
        return False



class RecordingMetadata:
    def __init__(self, url, category, title, subtitle, code, date, place, authors, duration):
        self.url = url
        self.category = category
        self.title = title
        self.subtitle = subtitle
        self.code = code
        self.date = date
        self.place = place
        self.authors = authors
        self.duration = duration



class AudioRecording:
    def __init__(self, sink, filename):
        self.sink = sink
        self.filename = filename
        self.subprocess = None

    def start(self):
        self.subprocess = subprocess.Popen([
            "ffmpeg",
            "-y",
            "-f", "pulse",
            "-i", f"{self.sink.name}.monitor",
            "-ac", "2",
            "-vn",
            "-b:a", "192k",
            self.filename])
        print(f"Started recording from {self.sink.name} in {self.filename}.")

    def stop(self, exc_type, exc_value, traceback):
        self.subprocess.terminate()
        print(f"Stopped recording from {self.sink.name} in {self.filename}.")



class Scrapper:
    def __init__(self, profile_id, headless, email, pwd):
        self.id = generate_id()
        self.profile_id = profile_id
        self.profile_path = f"/path/{profile_id}"
        self.headless = headless
        self.email = email
        self.pwd = pwd
        self.browser = None
        self.page = None

    async def __aenter__(self):
        await self.open()
        return self

    async def __aexit__(self, exc_type, exc_value, traceback):
        await self.close()
        return False

    async def wait_a_bit(self):
        await asyncio.sleep(WAIT_SECONDS)

    async def get_first(self, xpath):
        elements = await self.page.xpath(xpath)
        if elements:
            return await self.get_text(elements[0])
        else:
            return None

    async def get_text(self, element):
        return await self.page.evaluate('(el) => el.textContent', element)

    async def is_logged_in(self):
        elements = await self.page.xpath("//button[contains(text(), 'Se connecter')]")
        if len(elements) == 1:
            return False
        else:
            return True

    async def login(self):
        await self.page.goto(LOGIN_URL)
        await self.wait_a_bit()

        await self.page.type("input[name='email']", self.email)
        await self.page.type("input[name='password']", self.pwd)
        elements = await self.page.xpath("//button[text()='Connexion']")
        await elements[0].click()

    async def goto_logged_in(self, url):
        await self.page.goto(url)
        await self.wait_a_bit()

        if not await self.is_logged_in():
            await self.login()
            await self.wait_a_bit()
            await self.page.goto(url)



class RecordingScrapper(Scrapper):
    def __init__(self, profile_id, sink, email, pwd, headless=True):
        super().__init__(profile_id, headless, email, pwd)
        self.sink = sink


    async def open(self):
        print(f"[RecordingScrapper-{self.id}] Starting with profile [{self.profile_path}] and sink [{self.sink.name}]...")
        self.browser = await launch(
            headless=self.headless,
            executablePath=CHROMIUM_PATH,
            userDataDir=self.profile_path,
            args= [
                "--autoplay-policy=no-user-gesture-required",
                f"--audio-output-sink={self.sink.name}",
            ])
        pages = await self.browser.pages()
        self.page = pages[0]


    async def close(self):
        print(f"[RecordingScrapper-{self.id}] Terminating...")
        await self.browser.close()


    async def scrap_recording(self, url):
        await self.goto_logged_in(url)
        await self.wait_a_bit()

        metadata = await self.extract_metadata()

        audio_file = output_dir / safe_filename(f"{metadata.title or "no-title"}.mp3")
        recording = AudioRecording(self.sink, audio_file)
        recording.start()

        await self.play_recording()

        await asyncio.sleep(metadata.duration.seconds)
        recording.stop()


    async def extract_metadata(self):
        url = await self.page.evaluate('() => window.location.href')
        category = await self.get_first("//h3[following-sibling::*[2][self::h1]]")
        title = await self.get_first("//h1[preceding-sibling::*[2][self::h3]]")
        subtitle = await self.get_first("//h2[preceding-sibling::*[3][self::h3]]")

        details = await self.page.xpath("//ul[@id='details']//dd")
        code = (await self.get_text(details[0])).strip()
        date = (await self.get_text(details[1])).strip()
        place = (await self.get_text(details[2])).strip()
        authors = [s.strip() for s in (await self.get_text(details[3])).split("<br/>")]
        duration_str = (await self.get_text(details[4])).strip()

        return RecordingMetadata(
            url=url,
            category=category,
            title=title,
            subtitle=subtitle,
            code=code,
            date=date,
            place=place,
            authors=authors,
            duration=parse_duration(duration_str))


    async def play_recording(self):
        elements = await self.page.xpath("//a[contains(text(), 'Audio bas débit')]")
        await elements[0].click()



__all__ = ["Sink", "Scrapper", "RecordingScrapper"]
