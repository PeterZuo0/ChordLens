from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.models.audio import InstrumentHint, TransientAudioAnalysisResponse
from app.services.transient_audio_analysis import analyze_local_audio_file


EXPECTED_INSTRUMENTS = (
    "piano",
    "strings",
    "electric_bass",
    "drum_kit",
    "synth",
    "percussion",
    "acoustic_guitar",
)


def build_reference_summary(response: TransientAudioAnalysisResponse) -> dict[str, Any]:
    hints = collect_instrument_hints(response)
    coverage = {}
    missing = []
    for expected in EXPECTED_INSTRUMENTS:
        best = max((hint.confidence for hint in hints if hint.label == expected), default=0.0)
        if best >= 0.5:
            coverage[expected] = "medium"
        elif best > 0:
            coverage[expected] = "low"
        else:
            coverage[expected] = "missing"
            missing.append(expected)

    return {
        "source": {
            "fileName": response.source.fileName,
            "durationSec": response.source.durationSec,
            "format": response.source.format,
            "sampleRate": response.source.sampleRate,
            "channels": response.source.channels,
        },
        "bpm": response.music.bpm,
        "bpmConfidence": response.music.bpmConfidence,
        "bpmCandidates": [candidate.model_dump() for candidate in response.music.bpmCandidates],
        "bpmMessage": response.music.bpmMessage,
        "key": response.music.key,
        "keyConfidence": response.music.keyConfidence,
        "structure": [section.model_dump() for section in response.music.structure],
        "instrumentHints": [hint.model_dump() for hint in hints],
        "expectedInstrumentCoverage": coverage,
        "missingExpectedInstruments": missing,
        "stems": {
            "status": response.stems.status,
            "engine": response.stems.engine,
            "items": [
                {
                    "name": item.name,
                    "status": item.status,
                    "durationSec": item.durationSec,
                    "instrumentHints": [hint.model_dump() for hint in item.analysis.instrumentHints] if item.analysis else [],
                }
                for item in response.stems.items
            ],
        },
    }


def collect_instrument_hints(response: TransientAudioAnalysisResponse) -> list[InstrumentHint]:
    hints = list(response.music.instrumentSummary)
    for item in response.stems.items:
        if item.analysis:
            hints.extend(item.analysis.instrumentHints)
    return sorted(hints, key=lambda hint: (-hint.confidence, hint.label))


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Validate ChordLens B1 audio intelligence against a local file.")
    parser.add_argument("path", help="Local audio file path.")
    parser.add_argument("--separate-stems", action="store_true", help="Run Demucs stems before summarizing.")
    args = parser.parse_args(argv)

    path = Path(args.path)
    if not path.exists():
        print(json.dumps({"error": "file_not_found", "fileName": path.name}, ensure_ascii=False), file=sys.stderr)
        return 2

    try:
        response = analyze_local_audio_file(path, original_name=path.name, separate_stems=args.separate_stems)
    except Exception as issue:
        print(json.dumps({"error": "analysis_failed", "message": str(issue), "fileName": path.name}, ensure_ascii=False), file=sys.stderr)
        return 1

    print(json.dumps(build_reference_summary(response), ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
