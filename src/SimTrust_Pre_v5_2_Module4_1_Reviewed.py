"""SimTrust-Pre v5.2 — Module 4.1 (reviewed implementation).

Build real Operation-phase PY23 windows for the fault-segment primary analysis.

Primary label mapping follows the dataset's documented phase codes:
    0 = normal -> binary label 0
    1 = blind phase -> excluded (not silently relabelled normal)
    2 = observable anomalous phase -> binary label 1
    3 = recovery phase while effects remain observable -> binary label 1
Other/missing labels are excluded.

Windows are half-open [start, end), 30 s long, stride 30 s. Sensor/label
alignment uses exact timestamps. Interpolated or unknown-quality observations,
unknown labels, mixed binary labels, non-finite PY23 values, and windows with
insufficient coverage/gaps are rejected and counted.

Tests use synthetic ZIP fixtures only; no Zenodo data are read here.
"""
from __future__ import annotations

import io
import zipfile
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd

FEATURES = ("PY23_mean_mbar", "PY23_std_mbar", "PY23_delta_mbar")
LABEL_COL = "label_anomaly"
EXPERIMENT_COL = "experiment_key"
WINDOW_START_COL = "window_start_s"
WINDOW_END_COL = "window_end_s"

WINDOW_SECONDS = 30.0
WINDOW_STRIDE = 30.0
MIN_POINTS_PER_WINDOW = 24
MAX_GAP_SECONDS = 2.5

REAL_TIME_COL = "Time"
REAL_PY23_COL = "PY23"
REAL_INTERP_COL = "Data_interpolated"
LABEL_TIME_COL = "Time"
LABEL_VALUE_COL = "Label (anomaly)"
UNC_TIME_COL = "Time"

SENSOR_ROOT = "01_Batch_Distillation_Plant_M-202210_Timeseries_Sensors"
LABEL_ROOT = "00_Batch_Distillation_Plant_M-202210_Timeseries_Label_Anomaly_Metadata"
UNC_ROOT = "03_Batch_Distillation_Plant_M-202210_Timeseries_Sensor_Uncertainties"

_TRUE = {"true", "1", "1.0", "yes", "y", "t"}
_FALSE = {"false", "0", "0.0", "no", "n", "f"}


def _parse_clock_seconds(series: pd.Series, *, name: str) -> np.ndarray:
    """Parse elapsed HH:MM:SS[.fraction] or 'N days HH:MM:SS' strictly."""
    if not isinstance(series, pd.Series):
        raise TypeError(f"{name} must be a pandas Series.")
    if pd.api.types.is_numeric_dtype(series.dtype):
        raise TypeError(f"{name} is numeric; refusing to interpret it as a clock string.")
    values = series.astype("string").str.strip()
    pattern = r"^(?:(?:\d+)\s+days?\s+)?\d{1,3}:[0-5]\d:[0-5]\d(?:\.\d+)?$"
    ok = values.str.match(pattern, na=False)
    parsed = pd.to_timedelta(values.where(ok), errors="coerce")
    if (~ok).any() or parsed.isna().any():
        bad = values[parsed.isna()].head(3).tolist()
        raise ValueError(f"{name}: unparseable times; examples={bad}")
    sec = parsed.dt.total_seconds().to_numpy(dtype=float)
    if not np.isfinite(sec).all():
        raise ValueError(f"{name}: non-finite parsed timestamps.")
    if np.any(np.diff(sec) <= 0):
        raise ValueError(f"{name}: timestamps must be strictly increasing and unique.")
    return sec


def _strict_bool(series: pd.Series, *, name: str) -> pd.Series:
    """Parse documented boolean spellings; retain unknown values as pd.NA."""
    out = []
    for value in series.tolist():
        if pd.isna(value):
            out.append(pd.NA)
        elif isinstance(value, (bool, np.bool_)):
            out.append(bool(value))
        elif isinstance(value, (int, np.integer, float, np.floating)):
            number = float(value)
            if number == 1.0:
                out.append(True)
            elif number == 0.0:
                out.append(False)
            else:
                out.append(pd.NA)
        else:
            token = str(value).strip().casefold()
            if token in _TRUE:
                out.append(True)
            elif token in _FALSE:
                out.append(False)
            else:
                out.append(pd.NA)
    return pd.Series(pd.array(out, dtype="boolean"), index=series.index, name=name)


def _primary_binary_label(value: Any) -> int | None:
    """Map dataset phase labels to the predeclared observable-anomaly task.

    0 -> normal (0); 2 and 3 -> observable anomaly/recovery (1);
    1 (blind phase), missing, and unsupported codes -> excluded (None).
    """
    if pd.isna(value):
        return None
    try:
        number = float(value)
    except (TypeError, ValueError):
        return None
    if number == 0.0:
        return 0
    if number in (2.0, 3.0):
        return 1
    return None


def _label_exclusion_reason(value: Any) -> str:
    if pd.isna(value):
        return "missing_label"
    try:
        number = float(value)
    except (TypeError, ValueError):
        return "unknown_or_nonbinary_label"
    if number == 1.0:
        return "blind_phase_excluded"
    if number == 3.0:
        # Label 3 is positive in the primary mapping; this branch is defensive only.
        return "unmapped_recovery_phase"
    return "unknown_or_nonbinary_label"


def _validate_experiment_key(experiment_key: str) -> tuple[str, str, str, str]:
    if not isinstance(experiment_key, str):
        raise TypeError("experiment_key must be a string.")
    parts = experiment_key.split("/")
    if len(parts) != 4 or parts[0] != "Operation" or any(p in {"", ".", ".."} for p in parts):
        raise ValueError("experiment_key must be 'Operation/<chemical>/<operating_point>/<experiment>'.")
    return tuple(parts)  # type: ignore[return-value]


def _read_zip_csv(zip_path: Path, member: str, *, sep: str = ",") -> pd.DataFrame:
    zip_path = Path(zip_path)
    if not zip_path.is_file():
        raise FileNotFoundError(f"Archive not found: {zip_path}")
    with zipfile.ZipFile(zip_path) as archive:
        if member not in archive.namelist():
            raise KeyError(f"Member not found: {member!r}")
        with archive.open(member) as stream:
            frame = pd.read_csv(stream, sep=sep, low_memory=False)
    frame.columns = [str(column).strip() for column in frame.columns]
    return frame


def _members_for_experiment(experiment_key: str) -> tuple[str, str, str]:
    _, chemical, operating_point, experiment = _validate_experiment_key(experiment_key)
    suffix = f"Operation/{chemical}/{operating_point}/{experiment}.csv"
    return (
        f"{SENSOR_ROOT}/{suffix}",
        f"{LABEL_ROOT}/{suffix}",
        f"{UNC_ROOT}/{suffix}",
    )


def load_real_with_labels(
    sensor_archive: Path,
    label_archive: Path,
    experiment_key: str,
) -> pd.DataFrame:
    """Return sensor rows with exact-time labels; unmatched labels remain missing."""
    sensor_member, label_member, _ = _members_for_experiment(experiment_key)
    sensor = _read_zip_csv(sensor_archive, sensor_member)
    for column in (REAL_TIME_COL, REAL_PY23_COL):
        if column not in sensor.columns:
            raise KeyError(f"Sensor missing {column!r}; available={list(sensor.columns)}")
    sensor_time = _parse_clock_seconds(sensor[REAL_TIME_COL], name="sensor.Time")
    py23 = pd.to_numeric(sensor[REAL_PY23_COL], errors="coerce").to_numpy(dtype=float)

    labels = _read_zip_csv(label_archive, label_member)
    for column in (LABEL_TIME_COL, LABEL_VALUE_COL):
        if column not in labels.columns:
            raise KeyError(f"Label archive missing {column!r}; available={list(labels.columns)}")
    label_time = _parse_clock_seconds(labels[LABEL_TIME_COL], name="label.Time")

    sensor_frame = pd.DataFrame({
        "t_sec": sensor_time,
        "PY23_mbar": py23,
        "source_row": np.arange(len(sensor_time), dtype=int),
    })
    label_frame = pd.DataFrame({
        "t_sec": label_time,
        "label_raw": labels[LABEL_VALUE_COL].to_numpy(),
    })
    merged = sensor_frame.merge(label_frame, on="t_sec", how="left", validate="one_to_one")
    return merged.sort_values("t_sec").reset_index(drop=True)


def load_interpolation_flags(
    sensor_archive: Path,
    uncertainty_archive: Path,
    experiment_key: str,
) -> pd.DataFrame:
    """Load interpolation status from either/both archives and cross-check if duplicated."""
    sensor_member, _, unc_member = _members_for_experiment(experiment_key)
    sensor = _read_zip_csv(sensor_archive, sensor_member)
    unc = _read_zip_csv(uncertainty_archive, unc_member)
    frames: dict[str, pd.DataFrame] = {}

    if REAL_INTERP_COL in sensor.columns:
        if REAL_TIME_COL not in sensor.columns:
            raise KeyError("Sensor interpolation flag exists but sensor Time is missing.")
        frames["sensor"] = pd.DataFrame({
            "t_sec": _parse_clock_seconds(sensor[REAL_TIME_COL], name="sensor.Time"),
            "flag": _strict_bool(sensor[REAL_INTERP_COL], name="sensor.Data_interpolated").array,
        })
    if REAL_INTERP_COL in unc.columns:
        if UNC_TIME_COL not in unc.columns:
            raise KeyError("Uncertainty interpolation flag exists but uncertainty Time is missing.")
        frames["uncertainty"] = pd.DataFrame({
            "t_sec": _parse_clock_seconds(unc[UNC_TIME_COL], name="uncertainty.Time"),
            "flag": _strict_bool(unc[REAL_INTERP_COL], name="uncertainty.Data_interpolated").array,
        })
    if not frames:
        raise KeyError(f"{REAL_INTERP_COL!r} is missing from both sensor and uncertainty archives.")

    if len(frames) == 1:
        source, frame = next(iter(frames.items()))
        out = frame.rename(columns={"flag": "is_interpolated"}).copy()
        flag_source = source
    else:
        left = frames["sensor"].rename(columns={"flag": "flag_sensor"})
        right = frames["uncertainty"].rename(columns={"flag": "flag_uncertainty"})
        merged = left.merge(right, on="t_sec", how="outer", indicator=True, validate="one_to_one")
        if not (merged["_merge"] == "both").all():
            raise ValueError("Interpolation flags in both archives have different timestamp coverage.")
        sensor_flag = pd.array(merged["flag_sensor"], dtype="boolean")
        unc_flag = pd.array(merged["flag_uncertainty"], dtype="boolean")
        missingness_differs = pd.isna(sensor_flag) != pd.isna(unc_flag)
        values_differ = (
            ~pd.isna(sensor_flag) & ~pd.isna(unc_flag)
            & (np.asarray(sensor_flag, dtype=object) != np.asarray(unc_flag, dtype=object))
        )
        if np.any(missingness_differs) or np.any(values_differ):
            raise ValueError("Data_interpolated values (including unknown status) disagree between archives.")
        out = pd.DataFrame({"t_sec": merged["t_sec"], "is_interpolated": sensor_flag})
        flag_source = "both_verified"

    out.attrs["flag_source"] = flag_source
    out.attrs["experiment_key"] = experiment_key
    return out.reset_index(drop=True)


def build_real_windows_for_experiment(
    sensor_archive: Path,
    label_archive: Path,
    uncertainty_archive: Path,
    experiment_key: str,
    *,
    window_s: float = WINDOW_SECONDS,
    stride_s: float = WINDOW_STRIDE,
    min_points: int = MIN_POINTS_PER_WINDOW,
    max_gap_s: float = MAX_GAP_SECONDS,
) -> tuple[pd.DataFrame, dict[str, Any]]:
    """Build label-pure 30-s windows; phases 2 and 3 are positive, phase 1 excluded."""
    if not (np.isclose(window_s, WINDOW_SECONDS) and np.isclose(stride_s, WINDOW_STRIDE)):
        raise ValueError("Primary Phase 0 windowing is frozen at 30-s windows and 30-s stride.")
    if min_points != MIN_POINTS_PER_WINDOW or not np.isclose(max_gap_s, MAX_GAP_SECONDS):
        raise ValueError("Primary Phase 0 quality gates are frozen at >=24 points and max gap 2.5 s.")

    merged = load_real_with_labels(sensor_archive, label_archive, experiment_key)
    interp = load_interpolation_flags(sensor_archive, uncertainty_archive, experiment_key)
    merged = merged.merge(interp, on="t_sec", how="left", validate="one_to_one")
    merged["is_interpolated"] = merged["is_interpolated"].astype("boolean")
    merged = merged.sort_values("t_sec").reset_index(drop=True)

    audit: dict[str, Any] = {
        "experiment_key": experiment_key,
        "status": "OK",
        "flag_source": interp.attrs.get("flag_source"),
        "n_sensor_rows": int(len(merged)),
        "n_missing_labels": int(merged["label_raw"].isna().sum()),
        "n_missing_interpolation_flags": int(merged["is_interpolated"].isna().sum()),
        "n_windows": 0,
        "n_positive_windows": 0,
        "n_negative_windows": 0,
        "rejected": {},
    }
    empty_columns = [EXPERIMENT_COL, WINDOW_START_COL, WINDOW_END_COL, LABEL_COL, *FEATURES]
    if merged.empty:
        audit["status"] = "EMPTY_EXPERIMENT"
        return pd.DataFrame(columns=empty_columns), audit

    t = merged["t_sec"].to_numpy(dtype=float)
    py = merged["PY23_mbar"].to_numpy(dtype=float)
    interp_values = merged["is_interpolated"].array
    raw_labels = merged["label_raw"].to_numpy()

    if len(t) < 2:
        audit["status"] = "INSUFFICIENT_TIME_POINTS"
        return pd.DataFrame(columns=empty_columns), audit
    diffs = np.diff(t)
    positive_diffs = diffs[diffs > 0]
    if len(positive_diffs) == 0:
        audit["status"] = "INVALID_TIME_GRID"
        return pd.DataFrame(columns=empty_columns), audit
    nominal_dt = float(np.median(positive_diffs))
    if not np.isfinite(nominal_dt) or nominal_dt <= 0:
        audit["status"] = "INVALID_TIME_GRID"
        return pd.DataFrame(columns=empty_columns), audit

    t_min = float(t[0])
    coverage_end_exclusive = float(t[-1] + nominal_dt)
    rows: list[dict[str, Any]] = []
    rejected: dict[str, int] = {}

    def reject(reason: str) -> None:
        rejected[reason] = rejected.get(reason, 0) + 1

    start = t_min
    while start + window_s <= coverage_end_exclusive + 1e-9:
        end = start + window_s
        ix = np.flatnonzero((t >= start) & (t < end))
        if len(ix) < min_points:
            reject("insufficient_points")
            start += stride_s
            continue
        tw = t[ix]
        # A full half-open window must be covered at both edges as well as internally.
        leading_gap = float(tw[0] - start)
        trailing_gap = float(end - (tw[-1] + nominal_dt))
        if leading_gap > max_gap_s or trailing_gap > max_gap_s:
            reject("edge_gap")
            start += stride_s
            continue
        if np.max(np.diff(tw)) > max_gap_s:
            reject("internal_gap")
            start += stride_s
            continue

        mapped_labels = [_primary_binary_label(value) for value in raw_labels[ix]]
        if any(label is None for label in mapped_labels):
            reasons = {_label_exclusion_reason(value) for value in raw_labels[ix]
                       if _primary_binary_label(value) is None}
            for reason in reasons:
                reject(reason)
            start += stride_s
            continue
        if len(set(mapped_labels)) != 1:
            reject("mixed_binary_labels")
            start += stride_s
            continue

        flags = interp_values[ix]
        # Any interpolated=True or unknown flag rejects the complete window.
        if any((flag is pd.NA) or pd.isna(flag) or bool(flag) for flag in flags):
            reject("interpolated_or_unknown_quality")
            start += stride_s
            continue

        values = py[ix]
        if not np.isfinite(values).all():
            reject("nonfinite_PY23")
            start += stride_s
            continue

        rows.append({
            EXPERIMENT_COL: experiment_key,
            WINDOW_START_COL: float(start),
            WINDOW_END_COL: float(end),
            LABEL_COL: int(mapped_labels[0]),
            "PY23_mean_mbar": float(np.mean(values)),
            "PY23_std_mbar": float(np.std(values, ddof=0)),
            "PY23_delta_mbar": float(values[-1] - values[0]),
        })
        start += stride_s

    windows = pd.DataFrame(rows, columns=empty_columns)
    audit.update({
        "n_windows": int(len(windows)),
        "n_positive_windows": int((windows[LABEL_COL] == 1).sum()) if not windows.empty else 0,
        "n_negative_windows": int((windows[LABEL_COL] == 0).sum()) if not windows.empty else 0,
        "n_blind_phase_rows": int(pd.to_numeric(merged["label_raw"], errors="coerce").eq(1).sum()),
        "n_recovery_phase_rows": int(pd.to_numeric(merged["label_raw"], errors="coerce").eq(3).sum()),
        "rejected": rejected,
    })
    return windows, audit


def build_real_windows_bulk(
    sensor_archive: Path,
    label_archive: Path,
    uncertainty_archive: Path,
    experiment_keys: list[str],
    *,
    window_s: float = WINDOW_SECONDS,
    stride_s: float = WINDOW_STRIDE,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Build all requested experiments and retain one audit row per requested key."""
    all_windows: list[pd.DataFrame] = []
    audits: list[dict[str, Any]] = []
    for key in experiment_keys:
        try:
            windows, audit = build_real_windows_for_experiment(
                sensor_archive, label_archive, uncertainty_archive, key,
                window_s=window_s, stride_s=stride_s,
            )
            all_windows.append(windows)
            audits.append(audit)
        except Exception as exc:
            audits.append({"experiment_key": key, "status": "ERROR", "error": repr(exc), "n_windows": 0})
    windows_df = pd.concat(all_windows, ignore_index=True) if all_windows else pd.DataFrame(columns=[EXPERIMENT_COL, WINDOW_START_COL, WINDOW_END_COL, LABEL_COL, *FEATURES])
    return windows_df, pd.DataFrame(audits)


# -------------------------- Synthetic ZIP tests --------------------------
def _to_hhmmss(seconds: float) -> str:
    seconds = int(seconds)
    hours, rem = divmod(seconds, 3600)
    minutes, sec = divmod(rem, 60)
    return f"{hours:02d}:{minutes:02d}:{sec:02d}"


def _write_zip(path: Path, member: str, frame: pd.DataFrame, sep: str = ",") -> None:
    buf = io.StringIO()
    frame.to_csv(buf, index=False, sep=sep)
    mode = "a" if path.exists() else "w"
    with zipfile.ZipFile(path, mode, zipfile.ZIP_DEFLATED) as archive:
        archive.writestr(member, buf.getvalue().encode("utf-8"))


def run_smoke_tests() -> None:
    import tempfile

    print("Running reviewed synthetic smoke tests for v5.2 Module 4.1...")
    with tempfile.TemporaryDirectory() as tmp_dir:
        tmp = Path(tmp_dir)
        sensor_zip = tmp / "sensors.zip"
        label_zip = tmp / "labels.zip"
        unc_zip = tmp / "uncertainties.zip"
        exp_key = "Operation/ChemA/OP1/Exp001"
        sensor_member, label_member, unc_member = _members_for_experiment(exp_key)

        n = 600
        times = [_to_hhmmss(i) for i in range(n)]
        py = 650.0 + 0.1 * np.arange(n)
        # Documented phase scheme: 0 normal, 2 observable anomaly, 3 recovery.
        labels = np.concatenate([np.zeros(300, dtype=int), np.full(240, 2, dtype=int), np.full(60, 3, dtype=int)])
        sensor_frame = pd.DataFrame({"Time": times, "PY23": py})
        label_frame = pd.DataFrame({"Time": times, "Label (anomaly)": labels})
        unc_frame = pd.DataFrame({"Time": times, "±ΔPY23": np.full(n, 0.5), "Data_interpolated": np.zeros(n, dtype=int)})
        _write_zip(sensor_zip, sensor_member, sensor_frame)
        _write_zip(label_zip, label_member, label_frame)
        _write_zip(unc_zip, unc_member, unc_frame)

        # 1. 600 samples at 1 Hz cover [0, 600): 20 windows; phases 2+3 map positive.
        windows, audit = build_real_windows_for_experiment(sensor_zip, label_zip, unc_zip, exp_key)
        assert len(windows) == 20, f"Expected 20 windows, got {len(windows)}"
        assert audit["n_positive_windows"] == 10 and audit["n_negative_windows"] == 10
        assert audit["flag_source"] == "uncertainty"
        print(f"  PASS 1: baseline -> {len(windows)} windows, 10 positive, 10 negative")

        # 2. Internal gap >2.5 s rejects affected window.
        times_gap = [t for i, t in enumerate(times) if i not in {100, 101, 102}]
        py_gap = np.delete(py, [100, 101, 102])
        sensor_gap_zip = tmp / "sensor_gap.zip"
        _write_zip(sensor_gap_zip, sensor_member, pd.DataFrame({"Time": times_gap, "PY23": py_gap}))
        wg, ag = build_real_windows_for_experiment(sensor_gap_zip, label_zip, unc_zip, exp_key)
        assert ag["rejected"].get("internal_gap", 0) >= 1
        print(f"  PASS 2: internal gap -> {ag['rejected'].get('internal_gap', 0)} windows rejected")

        # 3. Mixed mapped labels in the same 30-s window rejected.
        labels_mixed = labels.copy()
        labels_mixed[105] = 2  # original phase is normal(0), so [90,120) is mixed.
        label_mixed_zip = tmp / "label_mixed.zip"
        _write_zip(label_mixed_zip, label_member, pd.DataFrame({"Time": times, "Label (anomaly)": labels_mixed}))
        wm, am = build_real_windows_for_experiment(sensor_zip, label_mixed_zip, unc_zip, exp_key)
        assert am["rejected"].get("mixed_binary_labels", 0) >= 1
        print(f"  PASS 3: mixed labels -> {am['rejected'].get('mixed_binary_labels', 0)} windows rejected")

        # 4. Blind phase(1) is excluded, never relabelled normal.
        labels_blind = labels.copy(); labels_blind[105] = 1
        label_blind_zip = tmp / "label_blind.zip"
        _write_zip(label_blind_zip, label_member, pd.DataFrame({"Time": times, "Label (anomaly)": labels_blind}))
        wb, ab = build_real_windows_for_experiment(sensor_zip, label_blind_zip, unc_zip, exp_key)
        assert ab["rejected"].get("blind_phase_excluded", 0) >= 1
        print(f"  PASS 4: blind phase excluded -> {ab['rejected'].get('blind_phase_excluded', 0)} windows rejected")

        # 5. Missing label rejects affected window.
        labels_nan = labels.astype(float); labels_nan[205] = np.nan
        label_nan_zip = tmp / "label_nan.zip"
        _write_zip(label_nan_zip, label_member, pd.DataFrame({"Time": times, "Label (anomaly)": labels_nan}))
        wn, an = build_real_windows_for_experiment(sensor_zip, label_nan_zip, unc_zip, exp_key)
        assert an["rejected"].get("missing_label", 0) >= 1
        print(f"  PASS 5: missing label -> {an['rejected'].get('missing_label', 0)} windows rejected")

        # 6. Interpolated=True excludes its window.
        interp_zip = tmp / "interp.zip"
        interp_flags = np.zeros(n, dtype=int); interp_flags[105:110] = 1
        _write_zip(interp_zip, unc_member, pd.DataFrame({"Time": times, "±ΔPY23": np.full(n, 0.5), "Data_interpolated": interp_flags}))
        wi, ai = build_real_windows_for_experiment(sensor_zip, label_zip, interp_zip, exp_key)
        assert ai["rejected"].get("interpolated_or_unknown_quality", 0) >= 1
        print(f"  PASS 6: interpolated flag -> {ai['rejected'].get('interpolated_or_unknown_quality', 0)} windows rejected")

        # 7. Non-finite PY23 excludes its window.
        py_nan = py.copy(); py_nan[405] = np.nan
        sensor_nan_zip = tmp / "sensor_nan.zip"
        _write_zip(sensor_nan_zip, sensor_member, pd.DataFrame({"Time": times, "PY23": py_nan}))
        wv, av = build_real_windows_for_experiment(sensor_nan_zip, label_zip, unc_zip, exp_key)
        assert av["rejected"].get("nonfinite_PY23", 0) >= 1
        print(f"  PASS 7: non-finite PY23 -> {av['rejected'].get('nonfinite_PY23', 0)} windows rejected")

        # 8. Non-overlap invariant.
        ws = windows.sort_values(WINDOW_START_COL).reset_index(drop=True)
        assert all(ws.loc[i, WINDOW_START_COL] >= ws.loc[i-1, WINDOW_END_COL] - 1e-9 for i in range(1, len(ws)))
        print(f"  PASS 8: {len(ws)} windows are non-overlapping")

        # 9. Feature schema exactly matches Module 2.
        for column in (EXPERIMENT_COL, WINDOW_START_COL, WINDOW_END_COL, LABEL_COL, *FEATURES):
            assert column in windows.columns
        assert len(windows.columns) == 7
        print("  PASS 9: feature schema matches Module 2")

        # 10. Feature values match manual computation.
        first = windows.iloc[0]
        assert np.isclose(first["PY23_mean_mbar"], np.mean(py[:30]))
        assert np.isclose(first["PY23_std_mbar"], np.std(py[:30], ddof=0))
        assert np.isclose(first["PY23_delta_mbar"], py[29] - py[0])
        print("  PASS 10: feature values match manual computation")

        # 11. Empty experiment returns a clean empty result.
        sensor_empty_zip = tmp / "sensor_empty.zip"; label_empty_zip = tmp / "label_empty.zip"; unc_empty_zip = tmp / "unc_empty.zip"
        _write_zip(sensor_empty_zip, sensor_member, pd.DataFrame({"Time": [], "PY23": []}))
        _write_zip(label_empty_zip, label_member, pd.DataFrame({"Time": [], "Label (anomaly)": []}))
        _write_zip(unc_empty_zip, unc_member, pd.DataFrame({"Time": [], "±ΔPY23": [], "Data_interpolated": []}))
        we, ae = build_real_windows_for_experiment(sensor_empty_zip, label_empty_zip, unc_empty_zip, exp_key)
        assert we.empty and ae["status"] == "EMPTY_EXPERIMENT"
        print("  PASS 11: empty experiment handled")

        # 12. Bulk builder returns windows/audit for each experiment.
        keys = [f"Operation/ChemA/OP1/Exp{i:03d}" for i in (0, 2, 3)]
        for index, key in enumerate(keys):
            sm, lm, um = _members_for_experiment(key)
            _write_zip(sensor_zip, sm, pd.DataFrame({"Time": times, "PY23": py + index}))
            _write_zip(label_zip, lm, pd.DataFrame({"Time": times, "Label (anomaly)": labels}))
            _write_zip(unc_zip, um, unc_frame)
        bulk_windows, bulk_audit = build_real_windows_bulk(sensor_zip, label_zip, unc_zip, keys)
        assert bulk_windows[EXPERIMENT_COL].nunique() == 3 and len(bulk_audit) == 3
        print(f"  PASS 12: bulk builder -> {len(bulk_windows)} windows across 3 experiments")

        # 13. Phase 3 (recovery) is explicitly mapped to the observable-anomaly class.
        assert _primary_binary_label(3) == 1 and _primary_binary_label(2) == 1
        print("  PASS 13: recovery phase(3) maps to positive; blind phase(1) stays excluded")

        # 14. Unsupported label value never becomes normal.
        labels_bad = labels.copy(); labels_bad[105] = 4
        label_bad_zip = tmp / "label_bad.zip"
        _write_zip(label_bad_zip, label_member, pd.DataFrame({"Time": times, "Label (anomaly)": labels_bad}))
        wx, ax = build_real_windows_for_experiment(sensor_zip, label_bad_zip, unc_zip, exp_key)
        assert ax["rejected"].get("unknown_or_nonbinary_label", 0) >= 1
        print("  PASS 14: unsupported label value excluded")

        # 15. Both flag archives must agree, including unknown-vs-known status.
        sensor_flag_zip = tmp / "sensor_flag.zip"
        sensor_flag_frame = pd.DataFrame({"Time": times, "PY23": py, "Data_interpolated": np.zeros(n, dtype=int)})
        _write_zip(sensor_flag_zip, sensor_member, sensor_flag_frame)
        flag_both = load_interpolation_flags(sensor_flag_zip, unc_zip, exp_key)
        assert flag_both.attrs["flag_source"] == "both_verified"
        unc_disagree_zip = tmp / "unc_disagree.zip"
        unc_disagree = unc_frame.copy(); unc_disagree.loc[110, "Data_interpolated"] = 1
        _write_zip(unc_disagree_zip, unc_member, unc_disagree)
        try:
            load_interpolation_flags(sensor_flag_zip, unc_disagree_zip, exp_key)
            raise AssertionError("Disagreeing flag archives were accepted.")
        except ValueError as exc:
            assert "disagree" in str(exc).lower()
        print("  PASS 15: duplicate interpolation sources cross-validated")

        # 16. Leading/trailing edge gaps inside otherwise candidate windows are rejected.
        sensor_edge_zip = tmp / "sensor_edge.zip"
        times_edge = [t for i, t in enumerate(times) if i not in {30, 31, 32, 57, 58, 59}]
        py_edge = np.delete(py, [30, 31, 32, 57, 58, 59])
        _write_zip(sensor_edge_zip, sensor_member, pd.DataFrame({"Time": times_edge, "PY23": py_edge}))
        wedge, aedge = build_real_windows_for_experiment(sensor_edge_zip, label_zip, unc_zip, exp_key)
        assert aedge["rejected"].get("edge_gap", 0) >= 1
        print(f"  PASS 16: incomplete window-edge coverage rejected ({aedge['rejected'].get('edge_gap', 0)})")

        # 17. Exact timestamp join does not silently carry a missing label across rows.
        label_shift_zip = tmp / "label_shift.zip"
        shifted_times = times.copy(); shifted_times[150] = "00:02:30.500"
        _write_zip(label_shift_zip, label_member, pd.DataFrame({"Time": shifted_times, "Label (anomaly)": labels}))
        wshift, ashift = build_real_windows_for_experiment(sensor_zip, label_shift_zip, unc_zip, exp_key)
        assert ashift["n_missing_labels"] >= 1 and ashift["rejected"].get("missing_label", 0) >= 1
        print("  PASS 17: unmatched label timestamp remains missing and rejects window")

        # 18. Phase 0 primary window/quality settings cannot be silently changed.
        try:
            build_real_windows_for_experiment(sensor_zip, label_zip, unc_zip, exp_key, window_s=60.0)
            raise AssertionError("Non-frozen primary window length was accepted.")
        except ValueError as exc:
            assert "frozen" in str(exc).lower()
        print("  PASS 18: Phase 0 window length/stride/quality gates are locked")

    print("\nAll reviewed Module 4.1 smoke tests passed (synthetic ZIP fixtures only).")
    print("Module 4.1 does not read any Zenodo archive and establishes no empirical result.")


if __name__ == "__main__":
    run_smoke_tests()