"""Fill in a platform's upload page in the account's own browser and stop before Post: Tko clicks it."""
import re
import subprocess
from pathlib import Path
from typing import Callable

from playwright.sync_api import Page, sync_playwright

from .review import REQUIRED_TAGS

ROOT = Path(__file__).resolve().parent.parent
BROWSERS = ROOT / "browsers"
CHROME = Path(r"C:\Program Files\Google\Chrome\Application\chrome.exe")
PLATFORMS = {
    "TikTok": {"login": "https://www.tiktok.com/login", "upload": "https://www.tiktok.com/tiktokstudio/upload"},
    "YouTube": {"login": "https://studio.youtube.com", "upload": "https://www.youtube.com/upload"},
    "Instagram": {"login": "https://www.instagram.com/accounts/login/", "upload": "https://www.instagram.com/"},
    "Facebook": {"login": "https://www.facebook.com/login", "upload": "https://www.facebook.com/reels/create"},
}
WAIT = 120_000  # uploads have to finish processing before the caption box appears


def browser_dir(name: str) -> Path:
    return BROWSERS / (re.sub(r"[^A-Za-z0-9]+", "-", name).strip("-").lower() or "profile")


def log_in(folder: Path, platforms: list[str]) -> None:
    # Plain Chrome, no automation: Google refuses sign-in from an automated browser. The cookies
    # saved here are what the automated posting session reuses.
    folder.mkdir(parents=True, exist_ok=True)
    subprocess.Popen([str(CHROME), f"--user-data-dir={folder}", *(PLATFORMS[p]["login"] for p in platforms)])


def clear_and_type(page: Page, box, text: str) -> None:
    box.click()
    page.keyboard.press("Control+A")
    page.keyboard.press("Delete")
    page.keyboard.insert_text(text)


def tiktok(page: Page, video: Path, hook: str, body: str, step: Callable[[str], None]) -> None:
    step("opening upload page")
    page.goto(PLATFORMS["TikTok"]["upload"])
    step("attaching clip")
    page.locator('input[type="file"]').first.set_input_files(video, timeout=WAIT)
    step("filling caption")
    caption = page.locator('div[contenteditable="true"]').first
    caption.wait_for(timeout=WAIT)
    clear_and_type(page, caption, f"{hook}\n{body}")


# YouTube ignores every hashtag on a video with more than 15; these go first when trimming.
GENERIC_TAGS = ["#funny", "#podcast", "#comedypodcast", "#standupcomedy", "#standup", "#comedy"]


def at_most_15_tags(body: str) -> str:
    # Line breaks become their own tokens, so a tag that opens a line can be removed as a whole word.
    words = body.replace("\n", " \n ").split(" ")
    tags = [w for w in body.split() if w.startswith("#")]
    for generic in GENERIC_TAGS:
        if len(tags) <= 15:
            break
        if generic in tags:
            tags.remove(generic)
            words.remove(generic)
    for tag in tags[::-1]:
        if len(tags) <= 15:
            break
        if tag not in REQUIRED_TAGS:
            tags.remove(tag)
            words.remove(tag)
    return " ".join(words).replace(" \n ", "\n")


def youtube(page: Page, video: Path, hook: str, body: str, step: Callable[[str], None]) -> None:
    step("opening upload page")
    page.goto(PLATFORMS["YouTube"]["upload"])
    step("attaching clip")
    page.locator('input[type="file"]').first.set_input_files(video, timeout=WAIT)
    step("filling title and description")
    title = page.locator("#title-textarea #textbox")
    title.wait_for(timeout=WAIT)
    clear_and_type(page, title, hook[:100])
    clear_and_type(page, page.locator("#description-textarea #textbox"), at_most_15_tags(body))
    step("marking not made for kids")
    page.locator('tp-yt-paper-radio-button[name="VIDEO_MADE_FOR_KIDS_NOT_MFK"]').click()


def instagram(page: Page, video: Path, hook: str, body: str, step: Callable[[str], None]) -> None:
    step("opening create menu")
    page.goto(PLATFORMS["Instagram"]["upload"])
    page.get_by_role("link", name=re.compile("new post|create", re.I)).first.click(timeout=30_000)
    menu_post = page.get_by_role("link", name=re.compile("^post$", re.I))
    if menu_post.count():
        menu_post.first.click()
    step("attaching clip")
    page.locator('input[type="file"]').first.set_input_files(video, timeout=WAIT)
    step("keeping the original crop")
    dialog = page.get_by_role("dialog")
    dialog.get_by_role("button", name=re.compile("select crop", re.I)).click(timeout=30_000)
    dialog.get_by_text("Original", exact=True).click()
    for _ in range(2):
        dialog.get_by_role("button", name="Next").click()
    step("filling caption")
    caption = dialog.locator('div[aria-label^="Write a caption"]')
    caption.wait_for(timeout=WAIT)
    clear_and_type(page, caption, f"{hook}\n{body}")


def facebook(page: Page, video: Path, hook: str, body: str, step: Callable[[str], None]) -> None:
    # Posts as whichever profile or Page is switched to in this browser: check the name before Publish.
    step("opening reel composer")
    page.goto(PLATFORMS["Facebook"]["upload"])
    step("attaching clip")
    page.locator('input[type="file"]').first.set_input_files(video, timeout=WAIT)
    step("skipping the edit screen")
    for _ in range(2):
        page.get_by_role("button", name="Next", exact=True).last.click(timeout=WAIT)
    step("filling description")
    caption = page.locator('div[role="textbox"][contenteditable="true"]').first
    caption.wait_for(timeout=WAIT)
    clear_and_type(page, caption, f"{hook}\n{body}")


FILLERS = {"TikTok": tiktok, "YouTube": youtube, "Instagram": instagram, "Facebook": facebook}


def prepare(folder: Path, platform: str, video: Path, description: str, step: Callable[[str], None]) -> None:
    """Blocks until Tko closes the browser. If a step fails the browser stays open where it stopped,
    so the post can be finished by hand; the error is re-raised for the app to show."""
    hook, _, body = description.strip().partition("\n")
    with sync_playwright() as p:
        context = p.chromium.launch_persistent_context(
            folder, channel="chrome", headless=False, no_viewport=True,
            ignore_default_args=["--enable-automation"], args=["--disable-blink-features=AutomationControlled"])
        page = context.pages[0] if context.pages else context.new_page()
        failure = None
        try:
            FILLERS[platform](page, video, hook, body.strip(), step)
            step("ready: check it and click Post")
        except Exception as e:
            failure = e
            step("stopped: finish by hand (caption is on the clipboard)")
        page.wait_for_event("close", timeout=0)
        context.close()
        if failure:
            raise failure
