from __future__ import annotations

from collections.abc import Iterable

import numpy as np

from app.models.audio import InstrumentHint, StemInsight
from app.services.audio_features import summarize_audio_features


def analyze_instruments_for_scope(samples: np.ndarray, sample_rate: int, source: str) -> StemInsight:
    insight = summarize_audio_features(samples, sample_rate)
    features = insight.features
    hints: list[InstrumentHint] = []

    low = features.lowEnergyRatio or 0.0
    mid = features.midEnergyRatio or 0.0
    high = features.highEnergyRatio or 0.0
    onset = features.onsetDensity or 0.0
    centroid = features.spectralCentroid or 0.0
    flatness = features.spectralFlatness or 0.0

    if source == "bass" or (source == "full_mix" and low > 0.55):
        confidence = _score(0.55 + low * 0.4 + (0.1 if source == "bass" else 0.0))
        hints.append(_hint("electric_bass", confidence, source, f"low_energy_ratio={low:.2f}", f"source={source}"))

    if source == "drums" or (source == "full_mix" and onset > 1.8):
        confidence = _score(0.5 + min(0.35, onset / 8) + (0.16 if source == "drums" else 0.0))
        hints.append(_hint("drum_kit", confidence, source, f"onset_density={onset:.2f}", f"source={source}"))
        hints.append(_hint("percussion", _score(confidence - 0.08), source, f"transient_strength={features.transientStrength or 0:.2f}", f"source={source}"))
    elif source == "other" and onset > 2.5:
        hints.append(_hint("percussion", _score(0.32 + min(0.22, onset / 24)), source, f"onset_density={onset:.2f}", f"source={source}"))

    if source == "vocals":
        hints.append(_hint("vocal", 0.72, source, "source=vocals"))

    if source == "piano":
        confidence = _score(0.68 + mid * 0.18 + min(0.12, onset / 24))
        hints.append(_hint("piano", confidence, source, f"mid_energy_ratio={mid:.2f}", f"onset_density={onset:.2f}", "source=piano"))

    if source == "strings":
        confidence = _score(0.68 + mid * 0.18 + max(0.0, 0.12 - min(0.1, onset * 0.01)))
        hints.append(_hint("strings", confidence, source, f"mid_energy_ratio={mid:.2f}", f"onset_density={onset:.2f}", "source=strings"))
        if low > 0.08:
            hints.append(_hint("cello_low_strings", _score(confidence - 0.1), source, f"low_energy_ratio={low:.2f}"))
        if high > 0.04 or centroid > 1600:
            hints.append(_hint("violin_high_strings", _score(confidence - 0.12), source, f"spectral_centroid={centroid:.0f}"))

    if source in {"other", "full_mix", "vocals"}:
        if mid > 0.35 and onset > 0.2:
            hints.append(_hint("piano", _score(0.38 + mid * 0.25 + min(0.18, onset / 18)), source, f"mid_energy_ratio={mid:.2f}", f"onset_density={onset:.2f}"))
        if mid > 0.3 and (onset < 3.5 or source == "other"):
            confidence = _score(0.34 + mid * 0.3 + max(0.0, 0.16 - min(0.12, onset * 0.012)))
            hints.append(_hint("strings", confidence, source, f"mid_energy_ratio={mid:.2f}", f"onset_density={onset:.2f}"))
            if low > 0.12:
                hints.append(_hint("cello_low_strings", _score(confidence - 0.12), source, f"low_energy_ratio={low:.2f}"))
            if high > 0.05 or centroid > 1800:
                hints.append(_hint("violin_high_strings", _score(confidence - 0.14), source, f"spectral_centroid={centroid:.0f}"))
        if high > 0.04 and onset > 1.0:
            hints.append(_hint("acoustic_guitar", _score(0.28 + high * 0.6 + min(0.18, onset / 18)), source, f"high_energy_ratio={high:.2f}", f"onset_density={onset:.2f}"))
        if flatness > 0.01 or centroid > 2500:
            hints.append(_hint("synth", _score(0.26 + min(0.28, flatness * 4) + min(0.18, centroid / 12000)), source, f"spectral_flatness={flatness:.3f}", f"spectral_centroid={centroid:.0f}"))

    insight.instrumentHints = merge_instrument_hints(hints)
    return insight


def summarize_full_mix_instruments(samples: np.ndarray, sample_rate: int) -> list[InstrumentHint]:
    return analyze_instruments_for_scope(samples, sample_rate, source="full_mix").instrumentHints


def merge_instrument_hints(hints: Iterable[InstrumentHint]) -> list[InstrumentHint]:
    merged: dict[str, InstrumentHint] = {}
    for hint in hints:
        existing = merged.get(hint.label)
        if existing is None or hint.confidence > existing.confidence:
            visible = hint.confidence >= 0.5
            merged[hint.label] = InstrumentHint(
                label=hint.label,
                confidence=round(max(0.0, min(1.0, hint.confidence)), 4),
                source=hint.source,
                evidence=hint.evidence,
                visible=visible,
            )
    return sorted(merged.values(), key=lambda item: (-item.confidence, item.label))


def _hint(label, confidence: float, source: str, *evidence: str) -> InstrumentHint:
    confidence = _score(confidence)
    return InstrumentHint(label=label, confidence=confidence, source=source, evidence=list(evidence), visible=confidence >= 0.5)


def _score(value: float) -> float:
    return round(max(0.0, min(1.0, value)), 4)
