import json
import os
import sys
from pathlib import Path

# ctranslate2 on Windows doesn't look inside the pip-installed nvidia packages for its CUDA DLLs.
for pkg in ("cublas", "cudnn"):
    dll_dir = Path(sys.prefix) / "Lib" / "site-packages" / "nvidia" / pkg / "bin"
    os.add_dll_directory(str(dll_dir))
    os.environ["PATH"] = f"{dll_dir}{os.pathsep}{os.environ['PATH']}"

from faster_whisper import WhisperModel  # noqa: E402


def transcribe(video: Path, work: Path, model_size: str = "large-v3") -> Path:
    out = work / "transcript.json"
    if out.exists():
        return out

    model = WhisperModel(model_size, device="cuda", compute_type="int8_float16")
    segments, info = model.transcribe(str(video), word_timestamps=True, vad_filter=True)
    data = {
        "language": info.language,
        "duration": info.duration,
        "segments": [
            {
                "start": s.start,
                "end": s.end,
                "text": s.text.strip(),
                "words": [{"start": w.start, "end": w.end, "word": w.word, "p": w.probability} for w in s.words],
            }
            for s in segments
        ],
    }
    out.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")
    return out
