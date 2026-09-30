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


def load_json(path: Path, default):
    return json.loads(path.read_text(encoding="utf-8")) if path.exists() else default


def save_json(path: Path, data) -> None:
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")


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


class ReviewDialog(tk.Toplevel):
    def __init__(self, master, work: Path):
        super().__init__(master)
        self.work, self.data = work, review.load(work)
        self.title(f"Review — {work.name}")
        self.geometry("1000x620")
        cols = ("keep", "score", "seconds", "name", "opens", "closes")
        self.tree = ttk.Treeview(self, columns=cols, show="headings", height=14)
        for col, width in zip(cols, (50, 50, 60, 220, 280, 280)):
            self.tree.heading(col, text=col)
            self.tree.column(col, width=width, anchor="w")
        self.tree.pack(fill="both", expand=True, padx=8, pady=8)
        self.tree.bind("<<TreeviewSelect>>", self.show)
        self.tree.bind("<Double-1>", self.toggle)
        self.detail = tk.Text(self, height=9, wrap="word")
        self.detail.pack(fill="x", padx=8)
        bar = ttk.Frame(self)
        bar.pack(fill="x", padx=8, pady=8)
        ttk.Label(bar, text="Double-click a row to keep or drop it.").pack(side="left")
        ttk.Button(bar, text="Approve and render", command=self.approve).pack(side="right")
        ttk.Button(bar, text="Save", command=self.save).pack(side="right", padx=6)
        self.fill()

    def fill(self) -> None:
        self.tree.delete(*self.tree.get_children())
        for i, c in enumerate(self.data["clips"]):
            self.tree.insert("", "end", iid=str(i), values=(
                "yes" if c["keep"] else "no", c["score"], c["seconds"], c["name"], c["opens"], c["closes"]))

    def show(self, _=None) -> None:
        sel = self.tree.selection()
        if not sel:
            return
        c = self.data["clips"][int(sel[0])]
        self.detail.delete("1.0", "end")
        self.detail.insert("end", f"by {c['by']}\npayoff: {c['payoff']}\nwhy: {c['reason']}\n\n{c['description']}")

    def toggle(self, _=None) -> None:
        for iid in self.tree.selection():
            clip = self.data["clips"][int(iid)]
            clip["keep"] = not clip["keep"]
        self.fill()

    def save(self) -> None:
        review.save(self.work, self.data)

    def approve(self) -> None:
        self.data["status"] = "approved"
        self.save()
        self.destroy()


class ProfilesDialog(tk.Toplevel):
    def __init__(self, master, profiles: list[dict], on_close):
        super().__init__(master)
        self.profiles, self.on_close = profiles, on_close
        self.title("Account profiles")
        self.geometry("720x420")
        self.list = tk.Listbox(self, width=24, exportselection=False)
        self.list.grid(row=0, column=0, rowspan=6, sticky="ns", padx=8, pady=8)
        self.list.bind("<<ListboxSelect>>", self.load)
        self.name, self.chrome = tk.StringVar(), tk.StringVar()
        ttk.Label(self, text="Name").grid(row=0, column=1, sticky="w")
        ttk.Entry(self, textvariable=self.name, width=50).grid(row=0, column=2, sticky="we")
        ttk.Label(self, text="Chrome profile").grid(row=1, column=1, sticky="w")
        ttk.Entry(self, textvariable=self.chrome, width=50).grid(row=1, column=2, sticky="we")
        ttk.Label(self, text="Folder name from chrome://version → Profile Path (Default, Profile 1, …)",
                  foreground="gray").grid(row=2, column=2, sticky="w")
        ttk.Label(self, text="Socials").grid(row=3, column=1, sticky="nw")
        self.socials = tk.Text(self, width=50, height=10)
        self.socials.grid(row=3, column=2, sticky="nsew")
        ttk.Label(self, text="One per line: Platform URL   (e.g. TikTok https://www.tiktok.com/@handle)",
                  foreground="gray").grid(row=4, column=2, sticky="w")
        bar = ttk.Frame(self)
        bar.grid(row=5, column=1, columnspan=2, sticky="e", pady=8)
        for text, command in (("New", self.new), ("Delete", self.delete), ("Save", self.store), ("Close", self.close)):
            ttk.Button(bar, text=text, command=command).pack(side="left", padx=3)
        self.protocol("WM_DELETE_WINDOW", self.close)
        self.refresh()

    def refresh(self, select: int = 0) -> None:
        self.list.delete(0, "end")
        for p in self.profiles:
            self.list.insert("end", p["name"])
        if self.profiles:
            self.list.selection_set(select)
            self.load()

    def current(self) -> int | None:
        sel = self.list.curselection()
        return sel[0] if sel else None

    def load(self, _=None) -> None:
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
        socials = [line.split(None, 1) for line in self.socials.get("1.0", "end").splitlines() if line.strip()]
        self.profiles[i] = {"name": self.name.get().strip() or "Unnamed",
                            "browser_profile": self.chrome.get().strip(),
                            "socials": [{"platform": s[0], "url": s[1].strip()} for s in socials if len(s) == 2]}
        save_json(PROFILES, self.profiles)
        self.refresh(i)

    def new(self) -> None:
        self.profiles.append({"name": "New profile", "browser_profile": "Default", "socials": []})
        self.refresh(len(self.profiles) - 1)

    def delete(self) -> None:
        i = self.current()
        if i is not None and messagebox.askyesno("Delete", f"Delete profile '{self.profiles[i]['name']}'?", parent=self):
            del self.profiles[i]
            save_json(PROFILES, self.profiles)
            self.refresh()

    def close(self) -> None:
        self.on_close()
        self.destroy()


class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("ClipMiner")
        self.geometry("1280x720")
        self.lock, self.events = threading.Lock(), queue.Queue()
        self.jobs = load_json(JOBS, [])
        for job in self.jobs:
            # An app closed mid-job resumes from the work/ cache. A render cut short may have written
            # some clips already, so it stops for a look instead of re-rendering duplicates.
            if job["stage"] == "render":
                job.update(stage="failed", error="closed during render: check Finished_Clips, then Retry")
            elif job["stage"] in RUNNING:
                job["stage"] = "queued"
        self.profiles = load_json(PROFILES, [])
        self.build_queue()
        self.build_profiles()
        self.build_clips()
        self.columnconfigure(0, weight=3)
        self.columnconfigure(1, weight=2)
        self.rowconfigure(1, weight=1)
        self.refresh_jobs()
        self.refresh_clips()
        Worker(self.jobs, self.lock, self.events).start()
        self.after(300, self.poll)

    # Queue
    def build_queue(self) -> None:
        frame = ttk.LabelFrame(self, text="Queue")
        frame.grid(row=0, column=0, rowspan=2, sticky="nsew", padx=8, pady=8)
        frame.columnconfigure(0, weight=1)
        frame.rowconfigure(1, weight=1)
        self.urls = tk.Text(frame, height=4)
        self.urls.grid(row=0, column=0, sticky="we", padx=6, pady=6)
        ttk.Button(frame, text="Add", command=self.add).grid(row=0, column=1, sticky="n", padx=6, pady=6)
        cols = ("title", "stage", "clips", "time")
        self.tree = ttk.Treeview(frame, columns=cols, show="headings")
        for col, width in zip(cols, (420, 110, 60, 70)):
            self.tree.heading(col, text=col)
            self.tree.column(col, width=width, anchor="w")
        self.tree.grid(row=1, column=0, columnspan=2, sticky="nsew", padx=6)
        self.tree.bind("<Double-1>", lambda _: self.open_review())
        bar = ttk.Frame(frame)
        bar.grid(row=2, column=0, columnspan=2, sticky="we", padx=6, pady=6)
        for text, command in (("Review", self.open_review), ("Retry", self.retry), ("Remove", self.remove)):
            ttk.Button(bar, text=text, command=command).pack(side="left", padx=3)
        self.error = ttk.Label(bar, foreground="firebrick")
        self.error.pack(side="left", padx=10)
        self.tree.bind("<<TreeviewSelect>>", lambda _: self.error.config(text=(self.selected() or {}).get("error", "")))

    def add(self) -> None:
        lines = [line.strip() for line in self.urls.get("1.0", "end").splitlines() if line.strip()]
        with self.lock:
            next_id = max((j["id"] for j in self.jobs), default=0) + 1
            for i, source in enumerate(lines):
                self.jobs.append({"id": next_id + i, "source": source, "title": source, "slug": "",
                                  "stage": "queued", "clips": 0, "elapsed": 0, "error": ""})
            save_json(JOBS, self.jobs)
        self.urls.delete("1.0", "end")
        self.refresh_jobs()

    def selected(self) -> dict | None:
        sel = self.tree.selection()
        return next((j for j in self.jobs if str(j["id"]) == sel[0]), None) if sel else None

    def open_review(self) -> None:
        job = self.selected()
        if job and job["stage"] == "review":
            ReviewDialog(self, ROOT / "work" / job["slug"])
        elif job:
            messagebox.showinfo("Review", f"This job is at '{job['stage']}'. Picks can be reviewed once it reaches 'review'.")

    def retry(self) -> None:
        job = self.selected()
        if job and job["stage"] == "failed":
            with self.lock:
                work = ROOT / "work" / job["slug"] if job["slug"] else None
                reviewed = work and (work / "review.json").exists() and review.load(work)["status"] == "approved"
                job.update(stage="review" if reviewed else "queued", error="")
                save_json(JOBS, self.jobs)
            self.refresh_jobs()

    def remove(self) -> None:
        job = self.selected()
        if job and job["stage"] not in RUNNING:
            with self.lock:
                self.jobs.remove(job)
                save_json(JOBS, self.jobs)
            self.refresh_jobs()

    def refresh_jobs(self) -> None:
        keep = self.tree.selection()
        self.tree.delete(*self.tree.get_children())
        with self.lock:
            for j in self.jobs:
                self.tree.insert("", "end", iid=str(j["id"]), values=(
                    j["title"], j["stage"], j["clips"] or "", f"{j['elapsed'] / 60:.0f}m" if j["elapsed"] else ""))
        if keep and self.tree.exists(keep[0]):
            self.tree.selection_set(keep)

    def poll(self) -> None:
        changed = False
        while not self.events.empty():
            self.events.get()
            changed = True
        if changed:
            self.refresh_jobs()
            self.refresh_clips()
        self.after(300, self.poll)

    # Profiles
    def build_profiles(self) -> None:
        frame = ttk.LabelFrame(self, text="Profile")
        frame.grid(row=0, column=1, sticky="nsew", padx=8, pady=8)
        self.profile = tk.StringVar()
        self.picker = ttk.Combobox(frame, textvariable=self.profile, state="readonly", width=30)
        self.picker.grid(row=0, column=0, padx=6, pady=6, sticky="w")
        self.picker.bind("<<ComboboxSelected>>", lambda _: self.draw_socials())
        ttk.Button(frame, text="Edit profiles", command=self.edit_profiles).grid(row=0, column=1, padx=6)
        self.social_bar = ttk.Frame(frame)
        self.social_bar.grid(row=1, column=0, columnspan=2, sticky="w", padx=6, pady=6)
        self.load_profiles()

    def load_profiles(self) -> None:
        names = [p["name"] for p in self.profiles]
        self.picker["values"] = names
        if names and self.profile.get() not in names:
            self.profile.set(names[0])
        self.draw_socials()

    def draw_socials(self) -> None:
        for child in self.social_bar.winfo_children():
            child.destroy()
        profile = next((p for p in self.profiles if p["name"] == self.profile.get()), None)
        for social in (profile or {}).get("socials", []):
            ttk.Button(self.social_bar, text=social["platform"],
                       command=lambda s=social: self.open_social(profile, s)).pack(side="left", padx=3)

    def open_social(self, profile: dict, social: dict) -> None:
        chrome = next((c for c in CHROME if c.is_file()), None)
        if chrome:
            subprocess.Popen([str(chrome), f"--profile-directory={profile['browser_profile']}", social["url"]])
        else:
            webbrowser.open(social["url"])
            messagebox.showwarning("Chrome not found", "Opened in the default browser; account selection won't apply.")

    def edit_profiles(self) -> None:
        ProfilesDialog(self, self.profiles, self.load_profiles)

    # Clips
    def build_clips(self) -> None:
        frame = ttk.LabelFrame(self, text="Clips")
        frame.grid(row=1, column=1, sticky="nsew", padx=8, pady=8)
        frame.columnconfigure(0, weight=1)
        frame.rowconfigure(0, weight=1)
        self.clips = tk.Listbox(frame, exportselection=False)
        self.clips.grid(row=0, column=0, sticky="nsew", padx=6, pady=6)
        self.clips.bind("<<ListboxSelect>>", lambda _: self.show_clip())
        self.description = tk.Text(frame, height=6, wrap="word")
        self.description.grid(row=1, column=0, sticky="we", padx=6)
        bar = ttk.Frame(frame)
        bar.grid(row=2, column=0, sticky="w", padx=6, pady=6)
        for text, command in (("Copy description", self.copy), ("Open folder", self.open_folder),
                              ("Play", self.play), ("Refresh", self.refresh_clips)):
            ttk.Button(bar, text=text, command=command).pack(side="left", padx=3)

    def refresh_clips(self) -> None:
        videos = sorted(FINISHED.glob("*_blur.mp4"), key=lambda f: f.stat().st_mtime, reverse=True)
        self.clip_stems = [f.name.removesuffix("_blur.mp4") for f in videos]
        self.clips.delete(0, "end")
        for stem in self.clip_stems:
            self.clips.insert("end", stem)

    def clip_stem(self) -> str | None:
        sel = self.clips.curselection()
        return self.clip_stems[sel[0]] if sel else None

    def show_clip(self) -> None:
        stem = self.clip_stem()
        txt = FINISHED / f"{stem}.txt"
        self.description.delete("1.0", "end")
        self.description.insert("end", txt.read_text(encoding="utf-8") if txt.exists() else "(no description: clip predates them)")

    def copy(self) -> None:
        self.clipboard_clear()
        self.clipboard_append(self.description.get("1.0", "end").strip())

    def open_folder(self) -> None:
        stem = self.clip_stem()
        if stem:
            subprocess.Popen(["explorer", "/select,", str(FINISHED / f"{stem}_blur.mp4")])

    def play(self) -> None:
        stem = self.clip_stem()
        if stem:
            os.startfile(FINISHED / f"{stem}_blur.mp4")


def main() -> None:
    if not shutil.which("ffmpeg"):
        messagebox.showerror("ClipMiner", "ffmpeg isn't on PATH. Open a new terminal after installing it.")
        return
    App().mainloop()


if __name__ == "__main__":
    main()
