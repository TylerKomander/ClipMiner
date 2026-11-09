import json
import os
import queue
import re
import shutil
import subprocess
import threading
import time
import tkinter as tk
from pathlib import Path
from tkinter import messagebox, ttk

from . import post, review
from .__main__ import FINISHED, ROOT, finish
from .download import fetch
from .score import score
from .signals import loudness
from .transcribe import transcribe

JOBS = ROOT / "queue.json"
PROFILES = ROOT / "profiles.json"
POSTS = ROOT / "posts.json"
READY = ROOT / "ready.json"
AUTOPOST = ROOT / "autopost.json"
RUNNING = ("download", "transcribe", "signals", "score", "render")
CATEGORIES = [folder for folder, _ in review.KINDS.values()]

# Dark tech palette after TerraPlayer's default skin: black, neon green, cyan.
BG, PANEL, FIELD, LINE = "#07090b", "#0e1318", "#141b22", "#22303b"
INK, MUTED = "#d6e2ea", "#7a8a96"
GREEN, CYAN, AMBER, RED = "#00ff88", "#00e5ff", "#ffb000", "#ff4d5e"
MONO, SANS = "Consolas", "Segoe UI"
STAGE_COLOR = {"queued": MUTED, "review": AMBER, "done": GREEN, "failed": RED, **{s: CYAN for s in RUNNING}}


def score_of(base: Path) -> int:
    m = re.match(r"\d+_s(\d+)_", base.name)
    return int(m.group(1)) if m else 0


def number_of(base: Path) -> int:
    return int(base.name.split("_")[0])


def category_of(base: Path) -> str:
    # Clips from before the type folders sit straight under Finished_Clips: all podcasts.
    parts = base.parent.relative_to(FINISHED).parts
    return parts[0] if parts and parts[0] in CATEGORIES else CATEGORIES[0]


def set_up(profile: dict | None) -> list[str]:
    return [name for name, s in (profile or {}).get("socials", {}).items() if s.get("handle") or s.get("url")]


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
    s.configure("Slot.TFrame", background=FIELD)
    s.configure("Slot.TLabel", background=FIELD, foreground=INK)
    s.configure("Panel.TRadiobutton", background=PANEL, foreground=INK, indicatorcolor=FIELD)
    s.map("Panel.TRadiobutton", indicatorcolor=[("selected", GREEN)], background=[("active", PANEL)])
    s.configure("Panel.TCheckbutton", background=PANEL, foreground=INK, indicatorcolor=FIELD)
    s.map("Panel.TCheckbutton", indicatorcolor=[("selected", GREEN)], background=[("active", PANEL)],
          foreground=[("disabled", MUTED)])
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
            # A finished job comes back too when new picks are approved for it (a second batch).
            for job in self.jobs:
                if job["stage"] in ("review", "done") and review.load(ROOT / "work" / job["slug"])["status"] == "approved":
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
                if job["stage"] in ("review", "done"):
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
        score(work, kind=job.get("kind", "podcast"))
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
        super().__init__(app, "Queue", "Pick the type, then paste links, one per line. They run one at a time "
                                       "(download → transcribe → pick clips) and then wait in Review.")
        add = self.card("Add episodes", expand=False, fill="x")
        row = ttk.Frame(add, style="Panel.TFrame")
        row.pack(fill="x")
        self.kind = tk.StringVar(value=CATEGORIES[0])
        ttk.Combobox(row, textvariable=self.kind, values=CATEGORIES, state="readonly", width=11).pack(side="left", padx=(0, 10))
        self.urls = text_box(row, 3)
        self.urls.pack(side="left", fill="x", expand=True)
        ttk.Button(row, text="Add to queue", style="Accent.TButton", command=self.add).pack(side="left", padx=(10, 0))

        jobs = self.card("Episodes")
        self.tree = table(jobs, {"episode": 440, "type": 90, "stage": 110, "clips": 70, "time": 70})
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
        kind = next(k for k, (folder, _) in review.KINDS.items() if folder == self.kind.get())
        with self.app.lock:
            next_id = max((j["id"] for j in self.app.jobs), default=0) + 1
            for i, source in enumerate(lines):
                self.app.jobs.append({"id": next_id + i, "source": source, "title": source, "slug": "", "kind": kind,
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
                    j["title"], review.KINDS[j.get("kind", "podcast")][0], j["stage"], j["clips"] or "", f"{j['elapsed'] / 60:.0f}m" if j["elapsed"] else ""))
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
        self.picks.tag_configure("overlap", foreground=AMBER)
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
            tag = "overlap" if c.get("overlaps") else "kept" if c["keep"] else "dropped"
            self.picks.insert("", "end", iid=str(i), tags=(tag,), values=(
                ("⚠ " if c.get("overlaps") else "") + c["name"], "✓" if c["keep"] else "✗",
                c["score"], c["seconds"], c["opens"], c["closes"]))

    def show(self) -> None:
        sel = self.picks.selection()
        if sel:
            c = self.data["clips"][int(sel[0])]
            self.detail.delete("1.0", "end")
            spliced = "".join(f"\nSpliced out: {cut}" for cut in c.get("spliced_out", []))
            spliced += "".join(f"\n⚠ Overlaps {name}: untick one or both render" for name in c.get("overlaps", []))
            self.detail.insert("end", f"Picked by {c['by']}\nPayoff: {c['payoff']}\nWhy: {c['reason']}{spliced}\n\n{c['description']}")

    def toggle(self) -> None:
        sel = self.picks.selection()
        if sel:
            # Re-read first: GURT may have edited the same file from chat since it was opened.
            self.data = review.load(self.work)
            clip = self.data["clips"][int(sel[0])]
            clip["keep"] = not clip["keep"]
            review.save(self.work, self.data)
            self.fill()
            self.picks.selection_set(sel)

    def approve(self) -> None:
        if not self.data:
            return
        self.data = review.load(self.work)
        kept = sum(c["keep"] for c in self.data["clips"])
        cap = review.clip_cap(self.work)
        if kept > cap:
            messagebox.showerror("Approve", f"{kept} clips ticked, the limit for this video is {cap}: untick {kept - cap}.")
            return
        unclean = [f"  {c['name']}:  {', '.join(review.off_limits(c['description']))}" for c in self.data["clips"]
                   if c["keep"] and not c.get("rendered_as") and review.off_limits(c["description"])]
        if unclean:
            messagebox.showerror("Approve", "Post descriptions can't swear or mention sex or drugs. Reword these in "
                                            "review.json (or untick them):\n\n" + "\n".join(unclean))
            return
        pairs = sorted({tuple(sorted((c["name"], o))) for c in self.data["clips"] for o in c.get("overlaps", [])})
        warning = ("\n\nThese ticked picks cover the same moment and would both render:\n"
                   + "\n".join(f"  {a}  ↔  {b}" for a, b in pairs)) if pairs else ""
        if messagebox.askyesno("Approve", f"Render {kept} clip(s) from this episode?{warning}"):
            self.data["status"] = "approved"
            review.save(self.work, self.data)
            self.work, self.data = None, None
            self.fill()
            self.app.refresh()


class ClipsPage(Page):
    def __init__(self, app):
        super().__init__(app, "Clips", "Grouped by type, then show, best score first. Pick a clip to see its description and "
                                       "where it has been posted, then post it: you only click Post. Tick Ready to let auto-post pick it.")
        split = ttk.Frame(self)
        split.pack(fill="both", expand=True)
        left = ttk.Frame(split, style="Panel.TFrame", padding=14)
        left.pack(side="left", fill="y", padx=(0, 12))
        ttk.Label(left, text="CLIPS", style="Section.TLabel").pack(anchor="w", pady=(0, 8))
        self.tree = ttk.Treeview(left, columns=("score", "posted"), show="tree headings", selectmode="browse")
        self.tree.heading("#0", text="TYPE / SHOW / CLIP", anchor="w")
        self.tree.heading("score", text="SCORE", anchor="w")
        self.tree.heading("posted", text="POSTED", anchor="w")
        self.tree.column("#0", width=330)
        self.tree.column("score", width=55, stretch=False)
        self.tree.column("posted", width=130, stretch=False)
        self.tree.tag_configure("category", foreground=GREEN, font=(MONO, 11, "bold"))
        self.tree.tag_configure("show", foreground=CYAN, font=(MONO, 10, "bold"))
        self.tree.tag_configure("posted", foreground=MUTED)
        self.tree.tag_configure("ready", foreground=GREEN)
        self.tree.pack(fill="y", expand=True)
        auto = ttk.Frame(left, style="Panel.TFrame")
        auto.pack(fill="x", pady=(12, 0))
        ttk.Label(auto, text="AUTO-POST", style="Section.TLabel").pack(anchor="w", pady=(0, 6))
        self.schedule_list = list_box(auto)
        self.schedule_list.configure(height=4)
        self.schedule_list.pack(fill="x")
        self.schedule_list.bind("<Double-Button-1>", lambda _: self.edit_schedule())
        bar = ttk.Frame(auto, style="Panel.TFrame")
        bar.pack(fill="x", pady=(6, 0))
        ttk.Button(bar, text="New…", command=lambda: ScheduleDialog(self, None)).pack(side="left")
        ttk.Button(bar, text="Edit…", command=self.edit_schedule).pack(side="left", padx=6)
        ttk.Button(bar, text="Turn on/off", command=self.toggle_schedule).pack(side="left")
        ttk.Button(bar, text="Delete", command=self.delete_schedule).pack(side="left", padx=6)
        self.auto_status = ttk.Label(auto, text="All off.", style="Help.TLabel", background=PANEL, wraplength=500, justify="left")
        self.auto_status.pack(anchor="w", pady=(6, 0))
        self.tree.bind("<<TreeviewSelect>>", lambda _: self.show())

        right = ttk.Frame(split)
        right.pack(side="left", fill="both", expand=True)
        text = ttk.Frame(right, style="Panel.TFrame", padding=14)
        text.pack(fill="both", expand=True)
        ttk.Label(text, text="POST DESCRIPTION  ·  edit before posting if you like", style="Section.TLabel").pack(anchor="w", pady=(0, 8))
        self.description = text_box(text, 6)
        self.description.pack(fill="both", expand=True)
        bar = ttk.Frame(text, style="Panel.TFrame")
        bar.pack(fill="x", pady=(10, 0))
        ttk.Button(bar, text="Copy description", command=self.copy).pack(side="left")
        ttk.Button(bar, text="Play", command=self.play).pack(side="left", padx=8)
        ttk.Button(bar, text="Open folder", command=self.open_folder).pack(side="left")
        self.copied = ttk.Label(bar, style="Help.TLabel", background=PANEL)
        self.copied.pack(side="left", padx=10)

        history = ttk.Frame(right, style="Panel.TFrame", padding=14)
        history.pack(fill="x", pady=(12, 0))
        ttk.Label(history, text="POSTED", style="Section.TLabel").pack(anchor="w", pady=(0, 6))
        self.history = ttk.Label(history, style="Panel.TLabel", justify="left", font=(MONO, 10))
        self.history.pack(anchor="w")

        post_card = ttk.Frame(right, style="Panel.TFrame", padding=14)
        post_card.pack(fill="x", pady=(12, 0))
        ttk.Label(post_card, text="POST", style="Section.TLabel").pack(anchor="w", pady=(0, 8))
        row = ttk.Frame(post_card, style="Panel.TFrame")
        row.pack(fill="x")
        ttk.Label(row, text="Layout", style="Panel.TLabel").pack(side="left")
        self.layout = tk.StringVar(value="track")
        self.layouts = ttk.Frame(row, style="Panel.TFrame")
        self.layouts.pack(side="left", padx=(8, 24))
        ttk.Label(row, text="Account", style="Panel.TLabel").pack(side="left")
        self.account = tk.StringVar()
        self.picker = ttk.Combobox(row, textvariable=self.account, state="readonly", width=24)
        self.picker.pack(side="left", padx=8)
        self.picker.bind("<<ComboboxSelected>>", lambda _: self.draw_platforms())
        self.ready_var = tk.BooleanVar()
        ttk.Checkbutton(row, text="Ready for auto-post", variable=self.ready_var, command=self.toggle_ready,
                        style="Panel.TCheckbutton").pack(side="left", padx=(16, 0))
        self.platforms = ttk.Frame(post_card, style="Panel.TFrame")
        self.platforms.pack(fill="x", pady=(10, 0))
        self.post_status = ttk.Label(post_card, style="Help.TLabel", background=PANEL, wraplength=700)
        self.post_status.pack(anchor="w", pady=(8, 0))

        self.posts = load_json(POSTS, [])
        self.clips: dict[str, Path] = {}
        self.busy: set[str] = set()
        self.status_text = ""
        self.finished: list[tuple[str, str, str, str]] = []
        self.ready: set[str] = set(load_json(READY, []))
        saved = load_json(AUTOPOST, [])
        # autopost.json held one setting before schedules: it becomes one schedule per account it named.
        self.schedules: list[dict] = saved if isinstance(saved, list) else [
            {"account": a, "platforms": p, "kinds": saved["kinds"], "times": saved["times"]} for a, p in saved["accounts"].items()]
        self.on: set[int] = set()  # id() of each schedule turned on; off again at every start
        self.fired: set[str] = set()
        self.draw_schedules()

    def scan(self) -> dict[tuple[str, str], list[Path]]:
        # Show folders from before the type folders sit straight under Finished_Clips: all podcasts.
        # Clips from before per-show folders sit loose there (or in Used-Clips).
        shows: dict[tuple[str, str], list[Path]] = {}
        # Every clip has a BLUR file except a movie recap, which only has its BAND file.
        for video in [*FINISHED.rglob("*_blur.mp4"), *FINISHED.rglob("*_band.mp4")]:
            parts = video.parent.relative_to(FINISHED).parts
            category = category_of(video)
            parts = parts[1:] if parts and parts[0] == category else parts
            show = "Older clips" if parts in ((), ("Used-Clips",)) else "\\".join(parts)
            shows.setdefault((category, show), []).append(video.with_name(video.name.rsplit("_", 1)[0]))
        return shows

    def refresh(self, force: bool = False) -> None:
        names = [p["name"] for p in self.app.profiles]
        self.picker["values"] = names
        if names and self.account.get() not in names:
            self.account.set(names[0])
        self.draw_platforms()
        shows = self.scan()
        found = {str(base) for bases in shows.values() for base in bases}
        if found == {str(b) for b in self.clips.values()} and not force:
            return
        keep = self.base()
        self.tree.delete(*self.tree.get_children())
        self.clips = {}
        for category in CATEGORIES:
            names = sorted((s for c, s in shows if c == category), key=lambda s: (s == "Older clips", s.lower()))
            if not names:
                continue
            count = sum(len(shows[category, s]) for s in names)
            top = self.tree.insert("", "end", text=f"{category.upper()}  ({count})", open=True, tags=("category",))
            for show in names:
                bases = shows[category, show]
                parent = self.tree.insert(top, "end", text=f"{show}  ({len(bases)})", open=True, tags=("show",))
                for base in sorted(bases, key=lambda b: (-score_of(b), -number_of(b))):
                    where = self.posted_on(base.name)
                    iid = self.tree.insert(parent, "end", text=f"{number_of(base)}  {base.name.split('_', 2)[-1]}",
                                           tags=("posted",) if where else ("ready",) if base.name in self.ready else (),
                                           values=(score_of(base), ", ".join(where)))
                    self.clips[iid] = base
                    if base == keep:
                        self.tree.selection_set(iid)

    def base(self) -> Path | None:
        sel = self.tree.selection()
        return self.clips.get(sel[0]) if sel else None

    def posted_on(self, stem: str) -> list[str]:
        return sorted({p["platform"] for p in self.posts if p["clip"] == stem})

    def show(self) -> None:
        base = self.base()
        if not base:
            return
        txt = base.with_suffix(".txt")
        self.description.delete("1.0", "end")
        self.description.insert("end", txt.read_text(encoding="utf-8") if txt.exists() else "")
        self.copied.config(text="" if txt.exists() else "No saved description (older clip): write one above.")
        entries = [p for p in self.posts if p["clip"] == base.name]
        self.ready_var.set(base.name in self.ready)
        self.history.config(text="\n".join(f"{p['platform']:<10} {p['handle']:<22} {p['layout']:<6} {p['date']}"
                                           for p in entries) or "Not posted anywhere yet.",
                            foreground=INK if entries else MUTED)
        for child in self.layouts.winfo_children():
            child.destroy()
        available = [name for name in ("game", "track", "blur", "split", "band") if base.with_name(f"{base.name}_{name}.mp4").exists()]
        if self.layout.get() not in available:
            self.layout.set(available[0])
        for name in available:
            ttk.Radiobutton(self.layouts, text=name, value=name, variable=self.layout,
                            style="Panel.TRadiobutton").pack(side="left", padx=(0, 8))

    def draw_platforms(self) -> None:
        for child in self.platforms.winfo_children():
            child.destroy()
        profile = next((p for p in self.app.profiles if p["name"] == self.account.get()), None)
        ready = set_up(profile)
        if not ready:
            ttk.Label(self.platforms, text="No platforms set up for this account yet: see Accounts.",
                      style="Help.TLabel", background=PANEL).pack(side="left")
            return
        buttons = ttk.Frame(self.platforms, style="Panel.TFrame")
        buttons.pack(fill="x")
        for name in ready:
            ttk.Button(buttons, text=f"Post to {name}", style="Accent.TButton",
                       command=lambda n=name: self.send(profile, n)).pack(side="left", padx=(0, 8))
        elsewhere = ttk.Frame(self.platforms, style="Panel.TFrame")
        elsewhere.pack(fill="x", pady=(10, 0))
        ttk.Label(elsewhere, text="Posted it some other way?", style="Help.TLabel", background=PANEL).pack(side="left", padx=(0, 6))
        mark = ttk.Combobox(elsewhere, values=ready, state="readonly", width=11)
        mark.set(ready[0])
        mark.pack(side="left")
        ttk.Button(elsewhere, text="Mark posted",
                   command=lambda: self.record(profile, mark.get(), ask=False)).pack(side="left", padx=6)

    def record(self, profile: dict, platform: str, ask: bool, stem: str | None = None, layout: str | None = None) -> None:
        stem = stem or (self.base().name if self.base() else None)
        if not stem:
            messagebox.showinfo("Posted", "Pick a clip first.")
            return
        handle = profile["socials"][platform].get("handle") or profile["name"]
        if ask and not messagebox.askyesno("Posted?", f"Did you post {stem} to {platform} as {handle}?"):
            return
        self.posts.append({"clip": stem, "platform": platform, "account": profile["name"], "handle": handle,
                           "layout": layout or self.layout.get(), "date": time.strftime("%Y-%m-%d %H:%M")})
        save_json(POSTS, self.posts)
        self.refresh(force=True)
        self.show()

    def send(self, profile: dict, platform: str) -> None:
        base = self.base()
        if not base:
            messagebox.showinfo("Post", "Pick a clip first.")
            return
        folder = ROOT / profile["folder"]
        if category_of(base) == review.KINDS["movie"][0] and not profile.get("movies"):
            messagebox.showinfo("Post", "Movie recaps only go to an account ticked Movie channel on the Accounts page.")
            return
        layout = self.layout.get()
        video = base.with_name(f"{base.name}_{layout}.mp4")
        handle = profile["socials"][platform].get("handle") or profile["name"]
        description = self.description.get("1.0", "end").strip()
        if review.off_limits(description):
            messagebox.showerror("Post", "The description can't swear or mention sex or drugs. Reword: "
                                         + ", ".join(review.off_limits(description)))
            return
        if platform in self.posted_on(base.name) and not messagebox.askyesno(
                "Already posted", f"This clip is already marked as posted to {platform}. Post it again?"):
            return
        if not messagebox.askyesno("Post", f"Open {platform} as {handle} with\n{video.name}\nand this description filled in?\n\n"
                                           "Nothing is published until you click Post in the browser."):
            return
        # Checked after the questions: a listed auto-post time can open this account while they wait.
        if str(folder) in self.busy:
            messagebox.showinfo("Post", "That account's browser is already open. Close it first.")
            return
        self.copied.config(text="Copied.")
        self.launch(profile, base, layout, description, [platform])

    def launch(self, profile: dict, base: Path, layout: str, description: str, platforms: list[str]) -> None:
        folder = ROOT / profile["folder"]
        video = base.with_name(f"{base.name}_{layout}.mp4")
        self.app.clipboard_clear()
        self.app.clipboard_append(description)
        idle = not self.busy
        self.busy.add(str(folder))

        def step(text: str) -> None:
            self.status_text = text

        def run() -> None:
            published = set()
            try:
                published = post.prepare(folder, [(p, video, description) for p in platforms], step)
                self.status_text = f"{profile['name']}: browser closed."
            except Exception as e:
                self.status_text = (f"{profile['name']}: stopped ({type(e).__name__}: {str(e).splitlines()[0][:160]}). "
                                    f"Finish by hand; Copy description on {number_of(base)} has its caption.")
            finally:
                # A post the app saw go through is recorded; any other tab gets asked about once the browser
                # is closed. The account stays busy until then, or an auto-post time could re-open a clip just posted.
                self.finished.append((str(folder), profile["name"], platforms, published, base.name, layout))

        threading.Thread(target=run, daemon=True).start()
        if idle:
            self.watch()

    def toggle_ready(self) -> None:
        base = self.base()
        if not base:
            self.ready_var.set(False)
            return
        (self.ready.add if self.ready_var.get() else self.ready.discard)(base.name)
        save_json(READY, sorted(self.ready))
        # Retag the one row: a full refresh would reload the description box and lose unsaved edits.
        self.tree.item(self.tree.selection()[0], tags=("posted",) if self.posted_on(base.name)
                       else ("ready",) if base.name in self.ready else ())

    def draw_schedules(self) -> None:
        keep = self.schedule_list.curselection()
        self.schedule_list.delete(0, "end")
        for schedule in self.schedules:
            on = id(schedule) in self.on
            kinds = " + ".join(review.KINDS[k][0] for k in schedule["kinds"])
            self.schedule_list.insert("end", f" {'ON ' if on else 'off'}  {schedule['account']} · {', '.join(schedule['platforms'])}"
                                             f" · {kinds} · {', '.join(schedule['times'])}")
            self.schedule_list.itemconfig("end", foreground=GREEN if on else MUTED)
        if keep and keep[0] < len(self.schedules):
            self.schedule_list.selection_set(keep[0])

    def schedule(self) -> dict | None:
        sel = self.schedule_list.curselection()
        if not sel:
            messagebox.showinfo("Auto-post", "Pick a schedule first.")
        return self.schedules[sel[0]] if sel else None

    def edit_schedule(self) -> None:
        schedule = self.schedule()
        if schedule:
            ScheduleDialog(self, schedule)

    def save_schedule(self, old: dict | None, new: dict) -> None:
        if old:
            old.update(new)
        else:
            self.schedules.append(new)
            self.set_on(new, True)
        save_json(AUTOPOST, self.schedules)
        self.draw_schedules()
        self.app.refresh()

    def toggle_schedule(self) -> None:
        schedule = self.schedule()
        if schedule:
            self.set_on(schedule, id(schedule) not in self.on)
            self.draw_schedules()
            self.app.refresh()

    def delete_schedule(self) -> None:
        schedule = self.schedule()
        if schedule and messagebox.askyesno("Auto-post", f"Delete the {schedule['account']} schedule at "
                                                         f"{', '.join(schedule['times'])}?"):
            self.on.discard(id(schedule))
            del self.schedules[self.schedule_list.curselection()[0]]
            save_json(AUTOPOST, self.schedules)
            self.draw_schedules()
            self.app.refresh()

    def set_on(self, schedule: dict, on: bool) -> None:
        if on:
            self.on.add(id(schedule))
            # Turned on inside a listed minute, it waits for the next time instead of firing at once.
            self.fired.add(f"{id(schedule)} {time.strftime('%Y-%m-%d %H:%M')}")
            self.note(f"{schedule['account']}: on at {', '.join(schedule['times'])}. {len(self.ready)} clip(s) ticked Ready.")
        else:
            self.on.discard(id(schedule))
            self.note(f"{schedule['account']}: off.")

    def note(self, text: str) -> None:
        self.auto_status.config(text=text, foreground=GREEN if self.on else MUTED)

    def tick(self) -> None:
        now = time.strftime("%H:%M")
        slot = time.strftime("%Y-%m-%d ") + now
        due = [s for s in self.schedules if id(s) in self.on and now in s["times"] and f"{id(s)} {slot}" not in self.fired]
        if not due:
            return
        self.fired.update(f"{id(s)} {slot}" for s in due)
        if self.busy:
            self.note(f"{now}: skipped {', '.join(s['account'] for s in due)}. A post is still open or waiting for its "
                      "Posted? answer.")
            return
        opened, skipped = [], []
        for schedule in due:
            profile = next((p for p in self.app.profiles if p["name"] == schedule["account"]), None)
            platforms = [p for p in schedule["platforms"] if p in set_up(profile)]
            if not platforms:
                skipped.append(f"{schedule['account']} (account renamed or deleted, or its platforms aren't set up)")
                continue
            pick = self.pick(profile, platforms, schedule["kinds"], skipped)
            if not pick:
                skipped.append(f"{schedule['account']} (nothing Ready left of its kinds)")
                continue
            base, layout, description, due_on = pick
            self.launch(profile, base, layout, description, due_on)
            opened.append(f"{number_of(base)} on {', '.join(due_on)} as {schedule['account']}")
        text = f"{now}: opened " + "; ".join(opened) + ". Check each tab and click Post." if opened else f"{now}: nothing opened."
        self.note(text + (" Passed over: " + "; ".join(skipped) + "." if skipped else ""))

    def pick(self, profile: dict, platforms: list[str], kinds: list[str],
             skipped: list[str]) -> tuple[Path, str, str, list[str]] | None:
        # Movies only ever go to a movie channel, whatever autopost.json says.
        categories = {review.KINDS[k][0] for k in kinds if k != "movie" or profile.get("movies")}
        candidates = [b for b in self.clips.values() if b.name in self.ready and category_of(b) in categories]
        for base in sorted(candidates, key=lambda b: (-score_of(b), -number_of(b))):
            due = [p for p in platforms if not any(e["clip"] == base.name and e["platform"] == p
                                                   and e["account"] == profile["name"] for e in self.posts)]
            if not due:
                continue
            layout = next((l for l in ("track", "blur", "band") if base.with_name(f"{base.name}_{l}.mp4").exists()), None)
            txt = base.with_suffix(".txt")
            if not layout or not txt.exists():
                skipped.append(f"{number_of(base)} (no {'TRACK, BLUR or BAND file' if not layout else 'description'})")
                continue
            description = txt.read_text(encoding="utf-8").strip()
            if review.off_limits(description):
                skipped.append(f"{number_of(base)} (description: {', '.join(review.off_limits(description))})")
                continue
            return base, layout, description, due
        return None

    def watch(self) -> None:
        self.post_status.config(text=self.status_text)
        while self.finished:
            folder, name, platforms, published, stem, layout = self.finished.pop(0)
            profile = next((p for p in self.app.profiles if p["name"] == name), None)
            for platform in platforms if profile else []:
                self.record(profile, platform, ask=platform not in published, stem=stem, layout=layout)
            self.busy.discard(folder)
        if self.busy:
            self.after(500, self.watch)

    def copy(self) -> None:
        self.app.clipboard_clear()
        self.app.clipboard_append(self.description.get("1.0", "end").strip())
        self.copied.config(text="Copied.")

    def play(self) -> None:
        base = self.base()
        if base:
            os.startfile(base.with_name(f"{base.name}_{self.layout.get()}.mp4"))

    def open_folder(self) -> None:
        base = self.base()
        if base:
            subprocess.Popen(["explorer", "/select,", str(base.with_name(f"{base.name}_{self.layout.get()}.mp4"))])


class ScheduleDialog(tk.Toplevel):
    def __init__(self, page: ClipsPage, schedule: dict | None):
        super().__init__(page.app)
        self.page, self.schedule = page, schedule
        saved = schedule or {"account": "", "platforms": [], "kinds": ["podcast"], "times": []}
        self.title("Auto-post schedule")
        self.configure(bg=PANEL)
        self.transient(page.app)
        self.resizable(False, False)
        body = ttk.Frame(self, style="Panel.TFrame", padding=18)
        body.pack(fill="both", expand=True)
        ttk.Label(body, text="At each time below, the best-scored clip ticked Ready of these kinds that this account hasn't "
                             "posted opens in its browser, filled in. Nothing is published until you click Post. A time "
                             "is skipped while a post is still waiting for you.",
                  style="Help.TLabel", background=PANEL, wraplength=460, justify="left").pack(anchor="w", pady=(0, 14))

        ttk.Label(body, text="ACCOUNT AND PLATFORMS", style="Section.TLabel").pack(anchor="w", pady=(0, 6))
        names = [p["name"] for p in page.app.profiles]
        self.account = tk.StringVar(value=saved["account"] if saved["account"] in names else (names or [""])[0])
        picker = ttk.Combobox(body, textvariable=self.account, values=names, state="readonly", width=28)
        picker.pack(anchor="w")
        picker.bind("<<ComboboxSelected>>", lambda _: self.draw_platforms(saved))
        self.platform_row = ttk.Frame(body, style="Panel.TFrame")
        self.platform_row.pack(fill="x", pady=(6, 0))
        self.platforms: dict[str, tk.BooleanVar] = {}
        self.draw_platforms(saved)

        ttk.Label(body, text="KINDS OF CLIPS", style="Section.TLabel").pack(anchor="w", pady=(14, 6))
        row = ttk.Frame(body, style="Panel.TFrame")
        row.pack(fill="x")
        self.kinds: dict[str, tk.BooleanVar] = {}
        for kind, (folder, _) in review.KINDS.items():
            self.kinds[kind] = tk.BooleanVar(value=kind in saved["kinds"])
            label = f"{folder} (movie channels only)" if kind == "movie" else folder
            ttk.Checkbutton(row, text=label, variable=self.kinds[kind], style="Panel.TCheckbutton").pack(side="left", padx=(0, 10))

        ttk.Label(body, text="TIMES  ·  24-hour, comma-separated", style="Section.TLabel").pack(anchor="w", pady=(14, 6))
        self.times = tk.StringVar(value=", ".join(saved["times"]))
        ttk.Entry(body, textvariable=self.times).pack(fill="x")
        self.error = ttk.Label(body, style="Error.TLabel", background=PANEL, wraplength=460)
        self.error.pack(anchor="w", pady=(8, 0))
        bar = ttk.Frame(body, style="Panel.TFrame")
        bar.pack(fill="x", pady=(8, 0))
        ttk.Button(bar, text="Save" if schedule else "Save and turn on", style="Accent.TButton",
                   command=self.save).pack(side="left")
        ttk.Button(bar, text="Cancel", command=self.destroy).pack(side="left", padx=8)
        self.grab_set()

    def draw_platforms(self, saved: dict) -> None:
        for child in self.platform_row.winfo_children():
            child.destroy()
        profile = next((p for p in self.page.app.profiles if p["name"] == self.account.get()), None)
        ready = set_up(profile)
        if not ready:
            ttk.Label(self.platform_row, text="No platforms set up for this account: see Accounts.",
                      style="Help.TLabel", background=PANEL).pack(side="left")
        same = self.account.get() == saved["account"]
        self.platforms = {name: tk.BooleanVar(value=same and name in saved["platforms"]) for name in ready}
        for name, var in self.platforms.items():
            ttk.Checkbutton(self.platform_row, text=name, variable=var, style="Panel.TCheckbutton").pack(side="left", padx=(0, 10))

    def save(self) -> None:
        platforms = [name for name, var in self.platforms.items() if var.get()]
        kinds = [kind for kind, var in self.kinds.items() if var.get()]
        times, bad = set(), []
        for t in filter(None, (t.strip() for t in self.times.get().split(","))):
            m = re.fullmatch(r"([01]?\d|2[0-3]):([0-5]\d)", t)
            if m:
                times.add(f"{int(m.group(1)):02d}:{m.group(2)}")
            else:
                bad.append(t)
        profile = next((p for p in self.page.app.profiles if p["name"] == self.account.get()), {})
        # One browser per account, so the same account at the same minute could only open one of the two.
        clash = sorted({t for other in self.page.schedules if other is not self.schedule
                        and other["account"] == self.account.get() for t in other["times"]} & times)
        problem = ("Tick at least one platform." if not platforms else "Tick at least one kind of clip." if not kinds
                   else f"Not a time: {', '.join(bad)} (use 18:00)." if bad else "Add at least one time." if not times
                   else f"{self.account.get()} already has a schedule at {', '.join(clash)}." if clash
                   else f"{self.account.get()} isn't ticked Movie channel on the Accounts page: untick Movies."
                   if "movie" in kinds and not profile.get("movies") else "")
        if problem:
            self.error.config(text=problem)
            return
        self.page.save_schedule(self.schedule, {"account": self.account.get(), "platforms": platforms, "kinds": kinds,
                                                "times": sorted(times)})
        self.destroy()


class AccountsPage(Page):
    def __init__(self, app):
        super().__init__(app, "Accounts", "Each account has its own browser that stays logged in. Fill in a slot per "
                                          "platform, then click Log in once and sign in to each site.")
        split = ttk.Frame(self)
        split.pack(fill="both", expand=True)
        left = ttk.Frame(split, style="Panel.TFrame", padding=14)
        left.pack(side="left", fill="y", padx=(0, 12))
        ttk.Label(left, text="ACCOUNTS", style="Section.TLabel").pack(anchor="w", pady=(0, 8))
        self.list = list_box(left)
        self.list.configure(width=26)
        self.list.pack(fill="y", expand=True)
        self.list.bind("<<ListboxSelect>>", lambda _: self.load())
        ttk.Button(left, text="New account", command=self.new).pack(fill="x", pady=(10, 0))
        ttk.Button(left, text="Delete", command=self.delete).pack(fill="x", pady=(6, 0))

        form = ttk.Frame(split, style="Panel.TFrame", padding=14)
        form.pack(side="left", fill="both", expand=True)
        ttk.Label(form, text="ACCOUNT NAME", style="Section.TLabel").pack(anchor="w")
        self.name = tk.StringVar()
        ttk.Entry(form, textvariable=self.name, font=(SANS, 11)).pack(fill="x", pady=(4, 14))
        self.fields: dict[str, dict[str, tk.StringVar]] = {}
        for platform in post.PLATFORMS:
            slot = ttk.Frame(form, style="Slot.TFrame", padding=12)
            slot.pack(fill="x", pady=(0, 10))
            ttk.Label(slot, text=platform.upper(), style="Slot.TLabel", font=(MONO, 10, "bold"),
                      foreground=CYAN).grid(row=0, column=0, sticky="w", columnspan=4, pady=(0, 6))
            self.fields[platform] = {"handle": tk.StringVar(), "url": tk.StringVar()}
            for col, (key, label, width) in enumerate((("handle", "Username", 22), ("url", "Profile link", 52))):
                ttk.Label(slot, text=label, style="Slot.TLabel").grid(row=1, column=col * 2, sticky="w", padx=(0, 6))
                ttk.Entry(slot, textvariable=self.fields[platform][key], width=width).grid(
                    row=1, column=col * 2 + 1, sticky="we", padx=(0, 16))
            ttk.Button(slot, text="Open", command=lambda p=platform: self.open_profile(p)).grid(row=1, column=4)
            slot.columnconfigure(3, weight=1)
        self.movies = tk.BooleanVar()
        ttk.Checkbutton(form, text="Movie channel: Movies recaps post here, and never to an account without this tick",
                        variable=self.movies, style="Panel.TCheckbutton").pack(anchor="w", pady=(0, 6))
        ttk.Label(form, text="No passwords here: you sign in once inside the account's own browser and it stays "
                             "signed in.", style="Help.TLabel", background=PANEL).pack(anchor="w", pady=(4, 10))
        bar = ttk.Frame(form, style="Panel.TFrame")
        bar.pack(fill="x")
        ttk.Button(bar, text="Save", style="Accent.TButton", command=self.store).pack(side="left")
        ttk.Button(bar, text="Log in to this account's sites", command=self.log_in).pack(side="left", padx=8)
        self.redraw()

    def redraw(self, select: int = 0) -> None:
        self.list.delete(0, "end")
        for p in self.app.profiles:
            self.list.insert("end", f" {p['name']}")
        if self.app.profiles:
            self.list.selection_set(min(select, len(self.app.profiles) - 1))
            self.load()

    def current(self) -> dict | None:
        sel = self.list.curselection()
        return self.app.profiles[sel[0]] if sel else None

    def load(self) -> None:
        profile = self.current()
        if not profile:
            return
        self.name.set(profile["name"])
        self.movies.set(profile.get("movies", False))
        for platform, fields in self.fields.items():
            saved = profile["socials"].get(platform, {})
            for key, var in fields.items():
                var.set(saved.get(key, ""))

    def store(self) -> None:
        profile = self.current()
        if not profile:
            return
        profile["name"] = self.name.get().strip() or "Unnamed"
        profile["socials"] = {platform: {key: var.get().strip() for key, var in fields.items()}
                              for platform, fields in self.fields.items()}
        profile["movies"] = self.movies.get()
        save_json(PROFILES, self.app.profiles)
        self.redraw(self.list.curselection()[0])
        self.app.refresh()

    def new(self) -> None:
        name = f"Account {len(self.app.profiles) + 1}"
        # The browser folder is fixed at creation, so renaming an account keeps its logins.
        self.app.profiles.append({"name": name, "folder": str(post.browser_dir(name).relative_to(ROOT)), "socials": {}})
        save_json(PROFILES, self.app.profiles)
        self.redraw(len(self.app.profiles) - 1)
        self.app.refresh()

    def delete(self) -> None:
        profile = self.current()
        if profile and messagebox.askyesno("Delete", f"Delete '{profile['name']}'? Its browser folder (and logins) "
                                                     "stays on disk under browsers\\."):
            self.app.profiles.remove(profile)
            save_json(PROFILES, self.app.profiles)
            self.redraw()
            self.app.refresh()

    def log_in(self) -> None:
        profile = self.current()
        if profile:
            self.store()
            filled = [p for p, s in profile["socials"].items() if s.get("handle") or s.get("url")]
            post.log_in(ROOT / profile["folder"], filled or list(post.PLATFORMS))

    def open_profile(self, platform: str) -> None:
        profile = self.current()
        url = self.fields[platform]["url"].get().strip()
        if profile and url:
            (ROOT / profile["folder"]).mkdir(parents=True, exist_ok=True)
            subprocess.Popen([str(post.CHROME), f"--user-data-dir={ROOT / profile['folder']}", url])


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
        self.profiles = load_json(PROFILES, [])
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
        on = len(self.pages["Clips"].on)
        auto = f"\nauto-post: {on} on" if on else ""
        if active:
            self.status.configure(text=f"● {active['stage'].upper()}\n{active['title'][:60]}\n{queued} queued{auto}", foreground=CYAN)
        else:
            self.status.configure(text=f"○ IDLE\n{queued} queued{auto}", foreground=MUTED)

    def poll(self) -> None:
        changed = False
        while not self.events.empty():
            self.events.get()
            changed = True
        # Chat approvals edit review.json directly, so the review list is re-checked even without events.
        self.ticks = getattr(self, "ticks", 0) + 1
        if changed or self.ticks % 5 == 0:
            self.refresh()
        self.pages["Clips"].tick()
        self.after(1000, self.poll)


def main() -> None:
    if not shutil.which("ffmpeg"):
        messagebox.showerror("ClipMiner", "ffmpeg isn't on PATH. Open a new terminal after installing it.")
        return
    App().mainloop()


if __name__ == "__main__":
    main()
