"""Who says each word, from the audio. Jaw movement can't tell: a mic hides the talker's mouth and the
listeners laugh (run 15: TRACK sat on a listener in 17 of 20 clips).

Two steps (2026-10-06 trial). Diarization finds the voices in the whole episode but its turn times are loose
and it never splits out a "Did you?", so it is only used to build one voiceprint per speaker. Each sentence
of the transcript is then given to the voiceprint it sounds most like."""
import json
import subprocess
from pathlib import Path

import numpy as np
import sherpa_onnx

MODELS = Path(__file__).resolve().parent.parent / "models"
RATE = 16000
THREADS = 4
CLUSTER = 0.9      # diarization's clustering threshold; high, because step two tidies up
CLEAN_TURN = 1.0   # only clean turns this long go into a voiceprint
MIN_VOICE = 3.0    # a cluster with less clean speech than this is noise, not a voice
SAME_VOICE = 0.6   # groups of voiceprints this alike on average are one person, split by shouting or laughing
MIN_SHARE = 0.02   # someone with less of the episode's clean speech than this is an ad or a clip played on the show
SENTENCE_GAP = 0.35  # a pause this long ends a sentence where Whisper wrote no full stop
PAD = 0.05         # audio taken either side of a sentence: Whisper's word times clip the first and last sounds
UNSURE = 0.15      # a sentence this close between two voices is left unlabelled ("Did you?" is 0.2s of audio)


def _audio(video: Path) -> np.ndarray:
    raw = subprocess.run(
        ["ffmpeg", "-hide_banner", "-loglevel", "error", "-i", str(video), "-vn", "-ac", "1", "-ar", str(RATE), "-f", "s16le", "-"],
        capture_output=True, check=True).stdout
    return np.frombuffer(raw, np.int16).astype(np.float32) / 32768


def _turns(audio: np.ndarray) -> list[tuple[float, float, int]]:
    config = sherpa_onnx.OfflineSpeakerDiarizationConfig(
        segmentation=sherpa_onnx.OfflineSpeakerSegmentationModelConfig(
            pyannote=sherpa_onnx.OfflineSpeakerSegmentationPyannoteModelConfig(model=str(MODELS / "pyannote_segmentation_3.onnx")),
            num_threads=THREADS),
        embedding=sherpa_onnx.SpeakerEmbeddingExtractorConfig(model=str(MODELS / "nemo_en_titanet_small.onnx"), num_threads=THREADS),
        clustering=sherpa_onnx.FastClusteringConfig(num_clusters=-1, threshold=CLUSTER),
        min_duration_on=0.2, min_duration_off=0.3)
    return [(s.start, s.end, s.speaker) for s in sherpa_onnx.OfflineSpeakerDiarization(config).process(audio).sort_by_start_time()]


def _voiceprint(extractor, audio: np.ndarray, start: float, end: float) -> np.ndarray:
    stream = extractor.create_stream()
    stream.accept_waveform(RATE, audio[max(int(start * RATE), 0):int(end * RATE)])
    stream.input_finished()
    v = np.array(extractor.compute(stream))
    return v / (np.linalg.norm(v) + 1e-9)


def _voices(extractor, audio: np.ndarray, turns: list[tuple[float, float, int]]) -> list[np.ndarray]:
    """One voiceprint per speaker, most talkative first."""
    found = []
    for k in {k for _, _, k in turns}:
        clean = []
        for s, e, kk in turns:
            if kk != k:
                continue
            for s2, e2, k2 in turns:  # drop the part where someone talks over them
                if k2 != k and s2 < e and e2 > s:
                    if s2 - s >= e - e2:
                        e = s2
                    else:
                        s = e2
            if e - s >= CLEAN_TURN:
                clean.append((s, e))
        total = sum(e - s for s, e in clean)
        if total >= MIN_VOICE:
            v = sum(_voiceprint(extractor, audio, s, e) * (e - s) for s, e in clean)
            found.append((total, v / np.linalg.norm(v)))
    # A whole episode comes back as dozens of clusters for three people (a 69-minute show: 99 clusters, 20 with
    # enough speech). Join the two most alike groups until none are alike; comparing each new one only with
    # the biggest so far missed chains of 0.65-0.73.
    groups = [[f] for f in found]
    while len(groups) > 1:
        alike, i, j = max((np.mean([float(a @ b) for _, a in groups[i] for _, b in groups[j]]), i, j)
                          for i in range(len(groups)) for j in range(i + 1, len(groups)))
        if alike < SAME_VOICE:
            break
        groups[i] += groups.pop(j)
    heard = sum(total for total, _ in found)
    voices = []
    for group in groups:
        total = sum(t for t, _ in group)
        if total >= heard * MIN_SHARE:
            v = sum(t * p for t, p in group)
            voices.append((total, v / np.linalg.norm(v)))
    return [v for _, v in sorted(voices, key=lambda f: -f[0])]


def label(video: Path, work: Path, words: list[dict]) -> list[int | None]:
    """A speaker number for every word of the transcript (0 talks most), None where it's too close to call.
    Worked out once per episode and kept in `speakers.json`, until the transcript it was made from changes."""
    cache = work / "speakers.json"
    made_from = [len(words), words[-1]["end"]]
    if cache.exists():
        kept = json.loads(cache.read_text(encoding="utf-8"))
        if kept["transcript"] == made_from:
            return kept["speakers"]
    # The faces learned for these voices go by their numbers, and the numbers are about to change.
    (work / "faces.json").unlink(missing_ok=True)
    audio = _audio(video)
    extractor = sherpa_onnx.SpeakerEmbeddingExtractor(sherpa_onnx.SpeakerEmbeddingExtractorConfig(
        model=str(MODELS / "nemo_en_titanet_small.onnx"), num_threads=THREADS))
    voices = _voices(extractor, audio, _turns(audio))
    speakers, sentence = [], []
    for i, w in enumerate(words):
        sentence.append(w)
        last = i + 1 == len(words)
        if last or words[i + 1]["start"] - w["end"] > SENTENCE_GAP or w["word"].rstrip().endswith((".", "?", "!")):
            who = None
            if voices and sentence[-1]["end"] > sentence[0]["start"]:
                heard = _voiceprint(extractor, audio, sentence[0]["start"] - PAD, sentence[-1]["end"] + PAD)
                scores = sorted(((float(heard @ v), n) for n, v in enumerate(voices)), reverse=True)
                if len(scores) == 1 or scores[0][0] - scores[1][0] >= UNSURE:
                    who = scores[0][1]
            speakers += [who] * len(sentence)
            sentence = []
    cache.write_text(json.dumps({"transcript": made_from, "speakers": speakers}), encoding="utf-8")
    return speakers
