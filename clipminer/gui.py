import json
import os
import queue
import shutil
import subprocess
import threading
import time
import tkinter as tk
import webbrowser
from pathlib import Path
from tkinter import messagebox, ttk

from . import review
from .__main__ import FINISHED, ROOT, finish
from .download import fetch
from .score import score
from .signals import loudness
from .transcribe import transcribe

JOBS = ROOT / "queue.json"
PROFILES = ROOT / "profiles.json"
RUNNING = ("download", "transcribe", "signals", "score", "render")
CHROME = [
    Path(os.environ.get("PROGRAMFILES", ""), "Google/Chrome/Application/chrome.exe"),
    Path(os.environ.get("PROGRAMFILES(X86)", ""), "Google/Chrome/Application/chrome.exe"),
    Path(os.environ.get("LOCALAPPDATA", ""), "Google/Chrome/Application/chrome.exe"),
]

# Dark tech palette after TerraPlayer's default skin: black, neon green, cyan.
BG, PANEL, FIELD, LINE = "#07090b", "#0e1318", "#141b22", "#22303b"
INK, MUTED = "#d6e2ea", "#7a8a96"
GREEN, CYAN, AMBER, RED = "#00ff88", "#00e5ff", "#ffb000", "#ff4d5e"
MONO, SANS = "Consolas", "Segoe UI"
STAGE_COLOR = {"queued": MUTED, "review": AMBER, "done": GREEN, "failed": RED, **{s: CYAN for s in RUNNING}}


def load_json(path: Path, default):
    return json.loads(path.read_text(encoding="utf-8")) if path.exists() else default


def save_json(path: Path, data) -> None:
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")


def style(root: tk.Tk) -> None:
    s = ttk.Style(root)
    s.theme_use("clam")
    s.configure(".", background=BG, foreground=INK, fieldbackground=FIELD, bordercolor=LINE,
                lightcolor=LINE, darkcolor=LINE, font=(SANS, 10))
    s.configure("TFrame", background=BG)
    s.configure("Panel.TFrame", background=PANEL)
    s.configure("TLabel", background=BG, foreground=INK)
    s.configure("Panel.TLabel", background=PANEL)
    s.configure("Title.TLabel", font=(MONO, 18, "bold"), foreground=GREEN)
    s.configure("Help.TLabel", foreground=MUTED, font=(SANS, 10))
    s.configure("Section.TLabel", background=PANEL, foreground=CYAN, font=(MONO, 10, "bold"))
    s.configure("Error.TLabel", foreground=RED)
    s.configure("TButton", background=FIELD, foreground=INK, borderwidth=1, focusthickness=0, padding=(12, 6))
    s.map("TButton", background=[("active", LINE)], foreground=[("disabled", MUTED)])
    s.configure("Accent.TButton", background=GREEN, foreground=BG, font=(SANS, 10, "bold"))
    s.map("Accent.TButton", background=[("active", CYAN)])
    s.configure("Nav.TButton", background=PANEL, foreground=MUTED, anchor="w", padding=(18, 10),
                font=(MONO, 11), borderwidth=0)
    s.map("Nav.TButton", background=[("active", FIELD)], foreground=[("active", INK)])
    s.configure("NavOn.TButton", background=FIELD, foreground=GREEN, anchor="w", padding=(18, 10),
                font=(MONO, 11, "bold"), borderwidth=0)
    s.configure("Treeview", background=FIELD, fieldbackground=FIELD, foreground=INK, rowheight=26,
                borderwidth=0, font=(SANS, 10))
    s.configure("Treeview.Heading", background=PANEL, foreground=CYAN, font=(MONO, 9, "bold"), borderwidth=0)
    s.map("Treeview", background=[("selected", "#123a2a")], foreground=[("selected", GREEN)])
    s.configure("TCombobox", fieldbackground=FIELD, background=FIELD, foreground=INK, arrowcolor=GREEN)
    s.map("TCombobox", fieldbackground=[("readonly", FIELD)], foreground=[("readonly", INK)],
          selectbackground=[("readonly", FIELD)], selectforeground=[("readonly", GREEN)])
    s.configure("TEntry", fieldbackground=FIELD, foreground=INK, insertcolor=GREEN)
    s.configure("Vertical.TScrollbar", background=PANEL, troughcolor=BG, arrowcolor=MUTED)
    root.option_add("*TCombobox*Listbox.background", FIELD)
    root.option_add("*TCombobox*Listbox.foreground", INK)


def text_box(parent, height: int, **kw) -> tk.Text:
    return tk.Text(parent, height=height, bg=FIELD, fg=INK, insertbackground=GREEN, relief="flat",
                   highlightthickness=1, highlightbackground=LINE, highlightcolor=GREEN,
                   font=(SANS, 10), padx=8, pady=6, wrap="word", **kw)


def list_box(parent) -> tk.Listbox:
    return tk.Listbox(parent, bg=FIELD, fg=INK, selectbackground="#123a2a", selectforeground=GREEN,
                      relief="flat", highlightthickness=1, highlightbackground=LINE, highlightcolor=GREEN,
                      font=(MONO, 10), activestyle="none", exportselection=False)


def table(parent, columns: dict[str, int]) -> ttk.Treeview:
    tree = ttk.Treeview(parent, columns=list(columns), show="headings", selectmode="browse")
    for col, width in columns.items():
        tree.heading(col, text=col.upper(), anchor="w")
        tree.column(col, width=width, minwidth=40, anchor="w", stretch=True)
    return tree


class Worker(threading.Thread):
    """One job at a time: Whisper and ffmpeg share one GPU, so parallel jobs only slow each other."""

    def __init__(self, jobs: list[dict], lock: threading.Lock, events: queue.Queue):
        super().__init__(daemon=True)
        self.jobs, self.lock, self.events = jobs, lock, events

    def set(self, job: dict, **fields) -> None:
        with self.lock:
            job.update(fields)
            save_json(JOBS, self.jobs)
        self.events.put(job["id"])

    def next_job(self) -> dict | None:
        with self.lock:
            # Approved reviews go first: they are one render away from finished clips.
            for job in self.jobs:
                if job["stage"] == "review" and review.load(ROOT / "work" / job["slug"])["status"] == "approved":
                    return job
            return next((job for job in self.jobs if job["stage"] == "queued"), None)

    def run(self) -> None:
        while True:
            job = self.next_job()
            if job is None:
                time.sleep(2)
                continue
            began = time.time()
            try:
                if job["stage"] == "review":
                    self.set(job, stage="render")
                    finish(ROOT / "work" / job["slug"])
                    kept = sum(c["keep"] for c in review.load(ROOT / "work" / job["slug"])["clips"])
                    self.set(job, stage="done", clips=kept)
                else:
                    self.prepare(job)
            except Exception as e:
                self.set(job, stage="failed", error=f"{type(e).__name__}: {e}")
            self.set(job, elapsed=job.get("elapsed", 0) + time.time() - began)

    def prepare(self, job: dict) -> None:
        self.set(job, stage="download", error="")
        work, video = fetch(job["source"], ROOT / "work")
        title = load_json(work / "info.json", {}).get("title") or work.name
        self.set(job, slug=work.name, title=title, stage="transcribe")
        transcribe(video, work)
        self.set(job, stage="signals")
        loudness(video, work)
        self.set(job, stage="score")
        score(work)
        self.set(job, stage="review", clips=len(review.load(work)["clips"]))


class Page(ttk.Frame):
    def __init__(self, app: "App", title: str, help_text: str):
        super().__init__(app.body)
        self.app = app
        ttk.Label(self, text=title, style="Title.TLabel").pack(anchor="w")
        ttk.Label(self, text=help_text, style="Help.TLabel").pack(anchor="w", pady=(2, 14))

    def card(self, title: str, **pack) -> ttk.Frame:
        outer = ttk.Frame(self, style="Panel.TFrame", padding=14)
        outer.pack(**({"fill": "both", "expand": True, "pady": (0, 12)} | pack))
        ttk.Label(outer, text=title.upper(), style="Section.TLabel").pack(anchor="w", pady=(0, 8))
        return outer

    def refresh(self) -> None:
        pass


class QueuePage(Page):
    def __init__(self, app):
        super().__init__(app, "Queue", "Paste episode links, one per line. They run one at a time "
                                       "(download → transcribe → pick clips) and then wait in Review.")
        add = self.card("Add episodes", expand=False, fill="x")
        row = ttk.Frame(add, style="Panel.TFrame")
        row.pack(fill="x")
        self.urls = text_box(row, 3)
        self.urls.pack(side="left", fill="x", expand=True)
        ttk.Button(row, text="Add to queue", style="Accent.TButton", command=self.add).pack(side="left", padx=(10, 0))

        jobs = self.card("Episodes")
        self.tree = table(jobs, {"episode": 520, "stage": 110, "clips": 70, "time": 70})
        self.tree.pack(fill="both", expand=True)
        for stage, color in STAGE_COLOR.items():
            self.tree.tag_configure(stage, foreground=color)
        self.tree.bind("<<TreeviewSelect>>", lambda _: self.error.config(text=(self.selected() or {}).get("error", "")))
        bar = ttk.Frame(jobs, style="Panel.TFrame")
        bar.pack(fill="x", pady=(10, 0))
        ttk.Button(bar, text="Retry", command=self.retry).pack(side="left")
        ttk.Button(bar, text="Remove", command=self.remove).pack(side="left", padx=8)
        self.error = ttk.Label(bar, style="Error.TLabel", background=PANEL, wraplength=600)
        self.error.pack(side="left", padx=10)

    def add(self) -> None:
        lines = [line.strip() for line in self.urls.get("1.0", "end").splitlines() if line.strip()]
        with self.app.lock:
            next_id = max((j["id"] for j in self.app.jobs), default=0) + 1
            for i, source in enumerate(lines):
                self.app.jobs.append({"id": next_id + i, "source": source, "title": source, "slug": "",
                                      "stage": "queued", "clips": 0, "elapsed": 0, "error": ""})
            save_json(JOBS, self.app.jobs)
        self.urls.delete("1.0", "end")
        self.app.refresh()

    def selected(self) -> dict | None:
        sel = self.tree.selection()
        return next((j for j in self.app.jobs if str(j["id"]) == sel[0]), None) if sel else None

    def retry(self) -> None:
        job = self.selected()
        if job and job["stage"] == "failed":
            with self.app.lock:
                work = ROOT / "work" / job["slug"] if job["slug"] else None
                approved = work and (work / "review.json").exists() and review.load(work)["status"] == "approved"
                job.update(stage="review" if approved else "queued", error="")
                save_json(JOBS, self.app.jobs)
            self.app.refresh()

    def remove(self) -> None:
        job = self.selected()
        if job and job["stage"] not in RUNNING:
            with self.app.lock:
                self.app.jobs.remove(job)
                save_json(JOBS, self.app.jobs)
            self.app.refresh()

    def refresh(self) -> None:
        keep = self.tree.selection()
        self.tree.delete(*self.tree.get_children())
        with self.app.lock:
            for j in self.app.jobs:
                self.tree.insert("", "end", iid=str(j["id"]), tags=(j["stage"],), values=(
                    j["title"], j["stage"], j["clips"] or "", f"{j['elapsed'] / 60:.0f}m" if j["elapsed"] else ""))
        if keep and self.tree.exists(keep[0]):
            self.tree.selection_set(keep)


class ReviewPage(Page):
    def __init__(self, app):
        super().__init__(app, "Review", "Sonnet's picks for each episode. Drop the weak ones, then approve "
                                        "to render. GURT can review and approve the same picks from chat.")
        split = ttk.Frame(self)
        split.pack(fill="both", expand=True)
        left = ttk.Frame(split, style="Panel.TFrame", padding=14)
        left.pack(side="left", fill="y", padx=(0, 12))
        ttk.Label(left, text="WAITING", style="Section.TLabel").pack(anchor="w", pady=(0, 8))
        self.episodes = list_box(left)
        self.episodes.configure(width=34)
        self.episodes.pack(fill="y", expand=True)
        self.episodes.bind("<<ListboxSelect>>", lambda _: self.open())

        right = ttk.Frame(split, style="Panel.TFrame", padding=14)
        right.pack(side="left", fill="both", expand=True)
        ttk.Label(right, text="PICKS  ·  double-click to keep or drop", style="Section.TLabel").pack(anchor="w", pady=(0, 8))
        self.picks = table(right, {"clip": 190, "keep": 45, "score": 50, "sec": 50, "opens": 200, "closes": 200})
        self.picks.tag_configure("dropped", foreground=MUTED)
        self.picks.tag_configure("kept", foreground=INK)
        self.picks.pack(fill="both", expand=True)
        self.picks.bind("<<TreeviewSelect>>", lambda _: self.show())
        self.picks.bind("<Double-1>", lambda _: self.toggle())
        self.detail = text_box(right, 8)
        self.detail.pack(fill="x", pady=(10, 0))
        bar = ttk.Frame(right, style="Panel.TFrame")
        bar.pack(fill="x", pady=(10, 0))
        ttk.Button(bar, text="Keep / drop", command=self.toggle).pack(side="left")
        ttk.Button(bar, text="Approve and render", style="Accent.TButton", command=self.approve).pack(side="right")
        self.waiting, self.work, self.data = [], None, None

    def refresh(self) -> None:
        with self.app.lock:
            waiting = [j for j in self.app.jobs if j["stage"] == "review"
                       and review.load(ROOT / "work" / j["slug"])["status"] == "awaiting"]
        if [j["id"] for j in waiting] == [j["id"] for j in self.waiting]:
            return
        self.waiting = waiting
        self.episodes.delete(0, "end")
        for j in waiting:
            self.episodes.insert("end", f" {j['title'][:40]}  ({j['clips']})")
        if self.work and self.work.name not in [j["slug"] for j in waiting]:
            self.work, self.data = None, None
            self.fill()

    def open(self) -> None:
        sel = self.episodes.curselection()
        if sel:
            self.work = ROOT / "work" / self.waiting[sel[0]]["slug"]
            self.data = review.load(self.work)
            self.fill()

    def fill(self) -> None:
        self.picks.delete(*self.picks.get_children())
        self.detail.delete("1.0", "end")
        for i, c in enumerate((self.data or {}).get("clips", [])):
            self.picks.insert("", "end", iid=str(i), tags=("kept" if c["keep"] else "dropped",), values=(
                c["name"], "✓" if c["keep"] else "✗", c["score"], c["seconds"], c["opens"], c["closes"]))

    def show(self) -> None:
        sel = self.picks.selection()
        if sel:
            c = self.data["clips"][int(sel[0])]
            self.detail.delete("1.0", "end")
            self.detail.insert("end", f"Picked by {c['by']}\nPayoff: {c['payoff']}\nWhy: {c['reason']}\n\n{c['description']}")

    def toggle(self) -> None:
        sel = self.picks.selection()
        if sel:
            clip = self.data["clips"][int(sel[0])]
            clip["keep"] = not clip["keep"]
            review.save(self.work, self.data)
            self.fill()
            self.picks.selection_set(sel)

    def approve(self) -> None:
        if not self.data:
            return
        kept = sum(c["keep"] for c in self.data["clips"])
        if messagebox.askyesno("Approve", f"Render {kept} clip(s) from this episode?"):
            self.data["status"] = "approved"
            review.save(self.work, self.data)
            self.work, self.data = None, None
            self.fill()
            self.app.refresh()


class ClipsPage(Page):
    def __init__(self, app):
        super().__init__(app, "Clips", "Finished clips, highest number first. Copy the description into your post; "
                                       "move posted clips to Used-Clips yourself.")
        split = ttk.Frame(self)
        split.pack(fill="both", expand=True)
        left = ttk.Frame(split, style="Panel.TFrame", padding=14)
        left.pack(side="left", fill="y", padx=(0, 12))
        ttk.Label(left, text="CLIPS", style="Section.TLabel").pack(anchor="w", pady=(0, 8))
        self.clips = list_box(left)
        self.clips.configure(width=52)
        self.clips.pack(fill="y", expand=True)
        self.clips.bind("<<ListboxSelect>>", lambda _: self.show())
        right = ttk.Frame(split, style="Panel.TFrame", padding=14)
        right.pack(side="left", fill="both", expand=True)
        ttk.Label(right, text="POST DESCRIPTION", style="Section.TLabel").pack(anchor="w", pady=(0, 8))
        self.description = text_box(right, 10)
        self.description.pack(fill="both", expand=True)
        bar = ttk.Frame(right, style="Panel.TFrame")
        bar.pack(fill="x", pady=(10, 0))
        ttk.Button(bar, text="Copy description", style="Accent.TButton", command=self.copy).pack(side="left")
        ttk.Button(bar, text="Play", command=self.play).pack(side="left", padx=8)
        ttk.Button(bar, text="Open folder", command=self.open_folder).pack(side="left")
        self.copied = ttk.Label(bar, style="Help.TLabel", background=PANEL)
        self.copied.pack(side="left", padx=10)
        self.stems: list[str] = []

    def refresh(self) -> None:
        videos = sorted(FINISHED.glob("*_blur.mp4"), key=lambda f: int(f.name.split("_")[0]), reverse=True)
        stems = [f.name.removesuffix("_blur.mp4") for f in videos]
        if stems == self.stems:
            return
        self.stems = stems
        self.clips.delete(0, "end")
        for stem in stems:
            self.clips.insert("end", f" {stem}")

    def stem(self) -> str | None:
        sel = self.clips.curselection()
        return self.stems[sel[0]] if sel else None

    def show(self) -> None:
        txt = FINISHED / f"{self.stem()}.txt"
        self.description.delete("1.0", "end")
        self.description.insert("end", txt.read_text(encoding="utf-8") if txt.exists()
                                else "No description: this clip was made before descriptions existed.")
        self.copied.config(text="")

    def copy(self) -> None:
        self.app.clipboard_clear()
        self.app.clipboard_append(self.description.get("1.0", "end").strip())
        self.copied.config(text="Copied.")

    def play(self) -> None:
        if self.stem():
            os.startfile(FINISHED / f"{self.stem()}_blur.mp4")

    def open_folder(self) -> None:
        if self.stem():
            subprocess.Popen(["explorer", "/select,", str(FINISHED / f"{self.stem()}_blur.mp4")])


class AccountsPage(Page):
    def __init__(self, app):
        super().__init__(app, "Accounts", "Each profile opens its social accounts in its own Chrome profile, "
                                          "so you land already logged into the right account.")
        self.profiles = load_json(PROFILES, [])
        launch = self.card("Open an account", expand=False, fill="x")
        row = ttk.Frame(launch, style="Panel.TFrame")
        row.pack(fill="x")
        self.active = tk.StringVar()
        self.picker = ttk.Combobox(row, textvariable=self.active, state="readonly", width=28)
        self.picker.pack(side="left")
        self.picker.bind("<<ComboboxSelected>>", lambda _: self.draw_buttons())
        self.buttons = ttk.Frame(row, style="Panel.TFrame")
        self.buttons.pack(side="left", padx=12)

        edit = self.card("Edit profiles")
        split = ttk.Frame(edit, style="Panel.TFrame")
        split.pack(fill="both", expand=True)
        self.list = list_box(split)
        self.list.configure(width=24)
        self.list.pack(side="left", fill="y")
        self.list.bind("<<ListboxSelect>>", lambda _: self.load())
        form = ttk.Frame(split, style="Panel.TFrame")
        form.pack(side="left", fill="both", expand=True, padx=(14, 0))
        self.name, self.chrome = tk.StringVar(), tk.StringVar()
        for label, var, hint in (("Profile name", self.name, ""),
                                 ("Chrome profile folder", self.chrome,
                                  "From chrome://version → Profile Path: the last folder (Default, Profile 1, …)")):
            ttk.Label(form, text=label, style="Panel.TLabel").pack(anchor="w")
            ttk.Entry(form, textvariable=var).pack(fill="x")
            ttk.Label(form, text=hint, style="Help.TLabel", background=PANEL).pack(anchor="w", pady=(0, 8))
        ttk.Label(form, text="Socials: one per line, platform then link", style="Panel.TLabel").pack(anchor="w")
        self.socials = text_box(form, 6)
        self.socials.pack(fill="both", expand=True)
        ttk.Label(form, text="e.g.  TikTok https://www.tiktok.com/@handle", style="Help.TLabel",
                  background=PANEL).pack(anchor="w")
        bar = ttk.Frame(form, style="Panel.TFrame")
        bar.pack(fill="x", pady=(10, 0))
        ttk.Button(bar, text="Save", style="Accent.TButton", command=self.store).pack(side="left")
        ttk.Button(bar, text="New profile", command=self.new).pack(side="left", padx=8)
        ttk.Button(bar, text="Delete", command=self.delete).pack(side="left")
        self.redraw()

    def redraw(self, select: int = 0) -> None:
        names = [p["name"] for p in self.profiles]
        self.picker["values"] = names
        if names and self.active.get() not in names:
            self.active.set(names[0])
        self.draw_buttons()
        self.list.delete(0, "end")
        for name in names:
            self.list.insert("end", f" {name}")
        if names:
            self.list.selection_set(select)
            self.load()

    def draw_buttons(self) -> None:
        for child in self.buttons.winfo_children():
            child.destroy()
        profile = next((p for p in self.profiles if p["name"] == self.active.get()), None)
        if not profile:
            ttk.Label(self.buttons, text="No profiles yet: add one below.", style="Help.TLabel",
                      background=PANEL).pack(side="left")
            return
        for social in profile["socials"]:
            ttk.Button(self.buttons, text=social["platform"],
                       command=lambda s=social: self.launch(profile, s)).pack(side="left", padx=(0, 6))

    def launch(self, profile: dict, social: dict) -> None:
        chrome = next((c for c in CHROME if c.is_file()), None)
        if chrome:
            subprocess.Popen([str(chrome), f"--profile-directory={profile['browser_profile']}", social["url"]])
        else:
            webbrowser.open(social["url"])
            messagebox.showwarning("Chrome not found", "Opened in the default browser; account selection won't apply.")

    def current(self) -> int | None:
        sel = self.list.curselection()
        return sel[0] if sel else None

    def load(self) -> None:
        i = self.current()
        if i is None:
            return
        p = self.profiles[i]
        self.name.set(p["name"])
        self.chrome.set(p.get("browser_profile", ""))
        self.socials.delete("1.0", "end")
        self.socials.insert("end", "\n".join(f"{s['platform']} {s['url']}" for s in p["socials"]))

    def store(self) -> None:
        i = self.current()
        if i is None:
            return
        lines = [line.split(None, 1) for line in self.socials.get("1.0", "end").splitlines() if line.strip()]
        self.profiles[i] = {"name": self.name.get().strip() or "Unnamed", "browser_profile": self.chrome.get().strip(),
                            "socials": [{"platform": s[0], "url": s[1].strip()} for s in lines if len(s) == 2]}
        save_json(PROFILES, self.profiles)
        self.redraw(i)

    def new(self) -> None:
        self.profiles.append({"name": "New profile", "browser_profile": "Default", "socials": []})
        self.redraw(len(self.profiles) - 1)

    def delete(self) -> None:
        i = self.current()
        if i is not None and messagebox.askyesno("Delete", f"Delete profile '{self.profiles[i]['name']}'?"):
            del self.profiles[i]
            save_json(PROFILES, self.profiles)
            self.redraw()


class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("ClipMiner")
        self.geometry("1320x780")
        self.minsize(1080, 640)
        self.configure(bg=BG)
        style(self)
        self.lock, self.events = threading.Lock(), queue.Queue()
        self.jobs = load_json(JOBS, [])
        for job in self.jobs:
            # An app closed mid-job resumes from the work/ cache. A render cut short may have written
            # some clips already, so it stops for a look instead of re-rendering duplicates.
            if job["stage"] == "render":
                job.update(stage="failed", error="Closed during render: check Finished_Clips, then Retry.")
            elif job["stage"] in RUNNING:
                job["stage"] = "queued"

        side = ttk.Frame(self, style="Panel.TFrame", width=220)
        side.pack(side="left", fill="y")
        side.pack_propagate(False)
        ttk.Label(side, text="▌CLIPMINER", style="Section.TLabel", foreground=GREEN,
                  font=(MONO, 15, "bold")).pack(anchor="w", padx=18, pady=(22, 26))
        self.body = ttk.Frame(self, padding=(26, 22))
        self.body.pack(side="left", fill="both", expand=True)
        self.pages = {"Queue": QueuePage(self), "Review": ReviewPage(self),
                      "Clips": ClipsPage(self), "Accounts": AccountsPage(self)}
        self.nav = {}
        for n, name in enumerate(self.pages, 1):
            self.nav[name] = ttk.Button(side, text=f"{n}  {name}", style="Nav.TButton",
                                        command=lambda nm=name: self.show(nm))
            self.nav[name].pack(fill="x")
        self.status = ttk.Label(side, style="Panel.TLabel", foreground=MUTED, font=(MONO, 9), wraplength=190)
        self.status.pack(side="bottom", anchor="w", padx=18, pady=18)

        self.show("Queue")
        self.refresh()
        Worker(self.jobs, self.lock, self.events).start()
        self.after(300, self.poll)

    def show(self, name: str) -> None:
        for n, page in self.pages.items():
            page.pack_forget()
            self.nav[n].configure(style="Nav.TButton")
        self.pages[name].pack(fill="both", expand=True)
        self.nav[name].configure(style="NavOn.TButton")
        self.pages[name].refresh()

    def refresh(self) -> None:
        for page in self.pages.values():
            page.refresh()
        waiting = len(self.pages["Review"].waiting)
        self.nav["Review"].configure(text=f"2  Review ({waiting})" if waiting else "2  Review")
        with self.lock:
            active = next((j for j in self.jobs if j["stage"] in RUNNING), None)
            queued = sum(j["stage"] == "queued" for j in self.jobs)
        if active:
            self.status.configure(text=f"● {active['stage'].upper()}\n{active['title'][:60]}\n{queued} queued", foreground=CYAN)
        else:
            self.status.configure(text=f"○ IDLE\n{queued} queued", foreground=MUTED)

    def poll(self) -> None:
        changed = False
        while not self.events.empty():
            self.events.get()
            changed = True
        # Chat approvals edit review.json directly, so the review list is re-checked even without events.
        self.ticks = getattr(self, "ticks", 0) + 1
        if changed or self.ticks % 5 == 0:
            self.refresh()
        self.after(1000, self.poll)


def main() -> None:
    if not shutil.which("ffmpeg"):
        messagebox.showerror("ClipMiner", "ffmpeg isn't on PATH. Open a new terminal after installing it.")
        return
    App().mainloop()


if __name__ == "__main__":
    main()
