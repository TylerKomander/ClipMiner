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
RUNNING = ("download", "transcribe", "signals", "score", "render")

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
            spliced = "".join(f"\nSpliced out: {cut}" for cut in c.get("spliced_out", []))
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
        if messagebox.askyesno("Approve", f"Render {kept} clip(s) from this episode?"):
            self.data["status"] = "approved"
            review.save(self.work, self.data)
            self.work, self.data = None, None
            self.fill()
            self.app.refresh()


class ClipsPage(Page):
    def __init__(self, app):
        super().__init__(app, "Clips", "Grouped by podcast, best score first. Pick a clip to see its description and "
                                       "where it has been posted, then post it: you only click Post.")
        split = ttk.Frame(self)
        split.pack(fill="both", expand=True)
        left = ttk.Frame(split, style="Panel.TFrame", padding=14)
        left.pack(side="left", fill="y", padx=(0, 12))
        ttk.Label(left, text="CLIPS", style="Section.TLabel").pack(anchor="w", pady=(0, 8))
        self.tree = ttk.Treeview(left, columns=("score", "posted"), show="tree headings", selectmode="browse")
        self.tree.heading("#0", text="PODCAST / CLIP", anchor="w")
        self.tree.heading("score", text="SCORE", anchor="w")
        self.tree.heading("posted", text="POSTED", anchor="w")
        self.tree.column("#0", width=330)
        self.tree.column("score", width=55, stretch=False)
        self.tree.column("posted", width=130, stretch=False)
        self.tree.tag_configure("show", foreground=CYAN, font=(MONO, 10, "bold"))
        self.tree.tag_configure("posted", foreground=MUTED)
        self.tree.pack(fill="y", expand=True)
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
        self.platforms = ttk.Frame(post_card, style="Panel.TFrame")
        self.platforms.pack(fill="x", pady=(10, 0))
        self.post_status = ttk.Label(post_card, style="Help.TLabel", background=PANEL, wraplength=700)
        self.post_status.pack(anchor="w", pady=(8, 0))

        self.posts = load_json(POSTS, [])
        self.clips: dict[str, Path] = {}
        self.busy: set[str] = set()
        self.status_text = ""
        self.finished: list[tuple[str, str, str, str]] = []

    def scan(self) -> dict[str, list[Path]]:
        # Clips from before per-podcast folders sit loose in Finished_Clips (or in Used-Clips).
        shows: dict[str, list[Path]] = {}
        for video in FINISHED.rglob("*_blur.mp4"):
            folder = video.parent.relative_to(FINISHED)
            show = "Older clips" if folder in (Path("."), Path("Used-Clips")) else str(folder)
            shows.setdefault(show, []).append(video.with_name(video.name.removesuffix("_blur.mp4")))
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
        for show in sorted(shows, key=lambda s: (s == "Older clips", s.lower())):
            parent = self.tree.insert("", "end", text=f"{show}  ({len(shows[show])})", open=True, tags=("show",))
            ranked = sorted(shows[show], key=lambda b: (-score_of(b), -number_of(b)))
            for base in ranked:
                where = self.posted_on(base.name)
                iid = self.tree.insert(parent, "end", text=f"{number_of(base)}  {base.name.split('_', 2)[-1]}", tags=("posted",) if where else (),
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
        self.history.config(text="\n".join(f"{p['platform']:<10} {p['handle']:<22} {p['layout']:<6} {p['date']}"
                                           for p in entries) or "Not posted anywhere yet.",
                            foreground=INK if entries else MUTED)
        for child in self.layouts.winfo_children():
            child.destroy()
        available = [name for name in ("track", "blur", "split") if base.with_name(f"{base.name}_{name}.mp4").exists()]
        if self.layout.get() not in available:
            self.layout.set(available[0])
        for name in available:
            ttk.Radiobutton(self.layouts, text=name, value=name, variable=self.layout,
                            style="Panel.TRadiobutton").pack(side="left", padx=(0, 8))

    def draw_platforms(self) -> None:
        for child in self.platforms.winfo_children():
            child.destroy()
        profile = next((p for p in self.app.profiles if p["name"] == self.account.get()), None)
        ready = [name for name, s in (profile or {}).get("socials", {}).items() if s.get("handle") or s.get("url")]
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
        if str(folder) in self.busy:
            messagebox.showinfo("Post", "That account's browser is already open. Close it first.")
            return
        layout = self.layout.get()
        video = base.with_name(f"{base.name}_{layout}.mp4")
        handle = profile["socials"][platform].get("handle") or profile["name"]
        description = self.description.get("1.0", "end").strip()
        if platform in self.posted_on(base.name) and not messagebox.askyesno(
                "Already posted", f"This clip is already marked as posted to {platform}. Post it again?"):
            return
        if not messagebox.askyesno("Post", f"Open {platform} as {handle} with\n{video.name}\nand this description filled in?\n\n"
                                           "Nothing is published until you click Post in the browser."):
            return
        self.copy()
        self.busy.add(str(folder))

        def step(text: str) -> None:
            self.status_text = f"{platform}: {text}"

        def run() -> None:
            try:
                post.prepare(folder, platform, video, description, step)
                self.status_text = f"{platform}: browser closed."
            except Exception as e:
                self.status_text = (f"{platform}: stopped ({type(e).__name__}: {str(e).splitlines()[0][:160]}). "
                                    "Finish by hand; the caption is on the clipboard.")
            finally:
                # The app can't see the Post click, so it asks once the browser is closed.
                self.finished.append((profile["name"], platform, base.name, layout))
                self.busy.discard(str(folder))

        threading.Thread(target=run, daemon=True).start()
        self.watch()

    def watch(self) -> None:
        self.post_status.config(text=self.status_text)
        while self.finished:
            name, platform, stem, layout = self.finished.pop(0)
            profile = next((p for p in self.app.profiles if p["name"] == name), None)
            if profile:
                self.record(profile, platform, ask=True, stem=stem, layout=layout)
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
