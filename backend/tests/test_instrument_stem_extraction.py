import zipfile

from audio_fixtures import write_chord_bed_wav


def test_derives_piano_and_strings_stems_from_other(monkeypatch, tmp_path):
    from app.services.instrument_stem_extraction import derive_piano_strings_from_other
    from app.services import stem_sessions

    session_id = "session_with_instruments"
    stems_dir = tmp_path / session_id / "stems"
    write_chord_bed_wav(stems_dir / "other.wav", frequencies=[220.0, 330.0, 440.0], duration_sec=0.6)

    items = derive_piano_strings_from_other(stems_dir, session_id)

    assert {item.name for item in items} == {"piano", "strings"}
    assert all(item.streamUrl for item in items)
    assert all(item.downloadUrl for item in items)
    assert all(item.fileSizeBytes and item.fileSizeBytes > 0 for item in items)
    assert (stems_dir / "piano.wav").exists()
    assert (stems_dir / "strings.wav").exists()

    import app.services.stem_sessions as stem_session_module

    monkeypatch.setattr(stem_session_module, "STEM_SESSIONS_DIR", tmp_path)
    archive = stem_sessions.build_stems_zip(session_id)
    with zipfile.ZipFile(archive) as zip_file:
        assert "piano.wav" in zip_file.namelist()
        assert "strings.wav" in zip_file.namelist()
