"""SimTrust-Pre v5.2 — Module 3 (reviewed implementation).

Loads one reviewed Operation experiment from the pinned sensor and uncertainty
archives, loads its paired simulation trace, applies an explicitly reviewed
sim-to-real time offset, and computes the pre-onset measurement-tolerance
normalized discrepancy q.

Safety / research contracts
---------------------------
* Data_interpolated is discovered in the paired SENSOR and/or UNCERTAINTY archive.
  If it occurs in both, timestamp coverage and values must agree exactly.
* The ±ΔPY23 denominator is loaded from the SENSOR-UNCERTAINTY archive.
* Time is never silently sorted, repaired, wrapped across midnight, or paired
  by row position.
* Real timestamps are the anchors. Uncertainty and simulation are nearest-time
  matched within a declared tolerance; source timestamps cannot be reused.
* The q interval is exactly 300 s and is evaluated on real-time anchors in
  [q_start, q_end). A tolerance-sized guard band is available for matching at
  interval boundaries.
* A synthetic smoke test validates mechanics only; it does not validate the
  physical meaning of PY23, uncertainty units/semantics, the real offset, or
  the simulator-to-experiment pairing.

The caller must provide a human-reviewed event record before computing q.
"""
from __future__ import annotations

import hashlib
import io
import math
import zipfile
from pathlib import Path, PurePosixPath
from typing import Any, Mapping

import numpy as np
import pandas as pd

PA_PER_MBAR = 100.0
Q_HORIZON_SECONDS = 300.0
TIME_MATCH_TOLERANCE_S = 0.5
MIN_Q_VALID_POINTS = 20

REAL_TIME_COL = "Time"
REAL_PY23_COL = "PY23"
REAL_INTERP_COL = "Data_interpolated"
UNC_TIME_COL = "Time"
UNC_PY23_COL = "±ΔPY23"
SIM_TIME_COL = "time"
SIM_PRESSURE_PA_COL = "pressure stage 12 / Pa"

SENSOR_ROOT = "01_Batch_Distillation_Plant_M-202210_Timeseries_Sensors"
UNC_ROOT = "03_Batch_Distillation_Plant_M-202210_Timeseries_Sensor_Uncertainties"

TRUE_TOKENS = {"true", "1", "yes", "y", "t"}
FALSE_TOKENS = {"false", "0", "no", "n", "f"}

REQUIRED_REVIEW_FIELDS = {
    "review_status",
    "experiment_key",
    "sim_member_expected",
    "reviewed_pre_perturbation_time",
    "reviewed_pre_perturbation_time_basis",
    "reviewed_primary_real_channel",
    "reviewed_primary_sim_channel",
    "reviewed_primary_uncertainty_column",
    "reviewed_primary_real_unit",
    "reviewed_primary_sim_unit",
    "reviewed_primary_uncertainty_unit",
    "reviewed_uncertainty_semantics_evidence",
    "reviewed_interpolation_flag_source",
    "reviewed_sim_to_real_time_offset_s",
    "reviewed_time_mapping_evidence",
    "reviewed_mapping_evidence",
}


def _strict_bool_flag(series: pd.Series, *, name: str) -> pd.Series:
    """Parse true/false flags to nullable BooleanDtype; unknown remains <NA>."""
    if not isinstance(series, pd.Series):
        raise TypeError(f"{name} must be a pandas Series.")
    out: list[Any] = []
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
            if token in TRUE_TOKENS:
                out.append(True)
            elif token in FALSE_TOKENS:
                out.append(False)
            else:
                out.append(pd.NA)
    return pd.Series(pd.array(out, dtype="boolean"), index=series.index, name=series.name)


def _parse_clock_seconds(series: pd.Series, *, name: str) -> np.ndarray:
    """Parse explicit clock/duration strings; reject numeric-as-nanoseconds and bad order.

    Timestamps are represented as seconds on the source clock. Midnight rollover is
    intentionally not inferred: it requires a documented date/time reconstruction.
    """
    if not isinstance(series, pd.Series):
        raise TypeError(f"{name} must be a pandas Series.")
    if pd.api.types.is_numeric_dtype(series.dtype):
        raise TypeError(
            f"{name} is numeric. Do not pass numeric seconds through to_timedelta; "
            "confirm its unit and convert explicitly before calling this parser."
        )
    values = series.astype("string").str.strip()
    # Do not let pandas interpret bare numeric strings (e.g. "1") as nanoseconds.
    clock_pattern = r"^(?:(?:\d+)\s+days?\s+)?\d{1,3}:[0-5]\d:[0-5]\d(?:\.\d+)?$"
    grammar_ok = values.str.match(clock_pattern, na=False)
    parsed = pd.to_timedelta(values.where(grammar_ok), errors="coerce")
    if (~grammar_ok).any() or parsed.isna().any():
        bad = values[parsed.isna()].head(5).tolist()
        raise ValueError(f"{name}: {int(parsed.isna().sum())} unparseable times; examples={bad}")
    seconds = parsed.dt.total_seconds().to_numpy(dtype=float)
    if not np.isfinite(seconds).all():
        raise ValueError(f"{name}: non-finite times.")
    diffs = np.diff(seconds)
    if np.any(diffs <= 0):
        n_dup = int(np.sum(diffs == 0))
        n_back = int(np.sum(diffs < 0))
        raise ValueError(
            f"{name}: timestamps must be strictly increasing and unique; "
            f"duplicates={n_dup}, backward_steps={n_back}. Midnight rollover is not auto-fixed."
        )
    return seconds


def _parse_reviewed_clock_scalar(value: Any, *, name: str) -> float:
    """Parse a registry-reviewed HH:MM:SS time into seconds; no numeric guessing."""
    if not isinstance(value, str):
        raise TypeError(f"{name} must be a reviewed HH:MM:SS string, not a numeric guess.")
    token = value.strip()
    if not pd.Series([token]).str.match(r"^(?:(?:\d+)\s+days?\s+)?\d{1,3}:[0-5]\d:[0-5]\d(?:\.\d+)?$").iloc[0]:
        raise ValueError(f"{name} must use explicit HH:MM:SS format; got {value!r}")
    parsed = pd.to_timedelta(token, errors="coerce")
    if pd.isna(parsed):
        raise ValueError(f"{name} is not a valid reviewed clock time: {value!r}")
    seconds = float(parsed.total_seconds())
    if not math.isfinite(seconds):
        raise ValueError(f"{name} must be finite.")
    return seconds


def _validate_experiment_key(experiment_key: str) -> tuple[str, str, str, str]:
    if not isinstance(experiment_key, str):
        raise TypeError("experiment_key must be a string.")
    parts = experiment_key.split("/")
    if len(parts) != 4 or parts[0] != "Operation" or any(p in {"", ".", ".."} for p in parts):
        raise ValueError(
            "experiment_key must be exactly 'Operation/<chemical_system>/<operating_point>/<experiment>'."
        )
    if any("\\" in p for p in parts):
        raise ValueError("Backslashes are not allowed in canonical experiment_key paths.")
    return tuple(parts)  # type: ignore[return-value]


def _read_zip_csv_with_provenance(
    zip_path: Path, member: str, *, sep: str = ","
) -> tuple[pd.DataFrame, dict[str, Any]]:
    zip_path = Path(zip_path)
    if not zip_path.is_file():
        raise FileNotFoundError(f"Archive not found: {zip_path}")
    with zipfile.ZipFile(zip_path, "r") as zf:
        try:
            info = zf.getinfo(member)
            if zf.namelist().count(member) != 1:
                raise ValueError(f"ZIP contains duplicate entries for exact member {member!r}.")
        except KeyError:
            basename = PurePosixPath(member).name
            candidates = [n for n in zf.namelist() if PurePosixPath(n).name == basename][:10]
            raise KeyError(f"Exact ZIP member not found: {member!r}; basename candidates={candidates}")
        raw = zf.read(info)
    sha = hashlib.sha256(raw).hexdigest()
    frame = pd.read_csv(io.BytesIO(raw), sep=sep, low_memory=False)
    frame.columns = [str(c).strip() for c in frame.columns]
    provenance = {
        "archive_path": str(zip_path),
        "member": member,
        "member_crc32": f"{info.CRC:08x}",
        "member_uncompressed_bytes": int(info.file_size),
        "member_sha256": sha,
        "csv_separator": sep,
        "columns": list(frame.columns),
        "n_rows": int(len(frame)),
    }
    return frame, provenance


def _attach_provenance(df: pd.DataFrame, provenance: dict[str, Any]) -> pd.DataFrame:
    df.attrs["source_provenance"] = provenance
    return df


def load_real_py23(archive_path: Path, experiment_key: str) -> pd.DataFrame:
    """Load measured PY23 from the SENSOR archive (flag is loaded separately)."""
    _, chemical, operating_point, experiment = _validate_experiment_key(experiment_key)
    member = f"{SENSOR_ROOT}/Operation/{chemical}/{operating_point}/{experiment}.csv"
    raw, provenance = _read_zip_csv_with_provenance(archive_path, member, sep=",")
    required = (REAL_TIME_COL, REAL_PY23_COL)
    missing = [c for c in required if c not in raw.columns]
    if missing:
        raise KeyError(f"Real sensor archive member {member!r} missing {missing}; available={list(raw.columns)}")
    out = pd.DataFrame({
        "t_sec": _parse_clock_seconds(raw[REAL_TIME_COL], name="real_Time"),
        "PY23_mbar": pd.to_numeric(raw[REAL_PY23_COL], errors="coerce").to_numpy(float),
    })
    provenance.update({"experiment_key": experiment_key, "source_role": "real_sensor_PY23"})
    return _attach_provenance(out, provenance)


def load_real_uncertainty(archive_path: Path, experiment_key: str) -> pd.DataFrame:
    """Load ±ΔPY23 from uncertainty archive; interpolation flag may or may not be here."""
    _, chemical, operating_point, experiment = _validate_experiment_key(experiment_key)
    member = f"{UNC_ROOT}/Operation/{chemical}/{operating_point}/{experiment}.csv"
    raw, provenance = _read_zip_csv_with_provenance(archive_path, member, sep=",")
    required = (UNC_TIME_COL, UNC_PY23_COL)
    missing = [c for c in required if c not in raw.columns]
    if missing:
        raise KeyError(f"Uncertainty archive member {member!r} missing {missing}; available={list(raw.columns)}")
    out = pd.DataFrame({
        "t_sec": _parse_clock_seconds(raw[UNC_TIME_COL], name="unc_Time"),
        "u_mbar": pd.to_numeric(raw[UNC_PY23_COL], errors="coerce").to_numpy(float),
    })
    provenance.update({"experiment_key": experiment_key, "source_role": "sensor_uncertainty"})
    return _attach_provenance(out, provenance)


def load_interpolation_flags(
    sensor_archive_path: Path,
    uncertainty_archive_path: Path,
    experiment_key: str,
) -> pd.DataFrame:
    """Find Data_interpolated in sensor and/or uncertainty archive, with cross-checks.

    If the flag occurs in exactly one archive, use and record that source. If it occurs
    in both, exact timestamp coverage and every parsed value must agree. If neither
    contains the flag, stop rather than pretending all observations are measured.
    """
    _, chemical, operating_point, experiment = _validate_experiment_key(experiment_key)
    sensor_member = f"{SENSOR_ROOT}/Operation/{chemical}/{operating_point}/{experiment}.csv"
    unc_member = f"{UNC_ROOT}/Operation/{chemical}/{operating_point}/{experiment}.csv"
    sensor_raw, sensor_prov = _read_zip_csv_with_provenance(sensor_archive_path, sensor_member, sep=",")
    unc_raw, unc_prov = _read_zip_csv_with_provenance(uncertainty_archive_path, unc_member, sep=",")

    candidates: dict[str, pd.DataFrame] = {}
    if REAL_INTERP_COL in sensor_raw.columns:
        candidates["sensor"] = pd.DataFrame({
            "t_sec": _parse_clock_seconds(sensor_raw[REAL_TIME_COL], name="sensor_flag_Time"),
            "is_interpolated": _strict_bool_flag(sensor_raw[REAL_INTERP_COL], name=f"sensor.{REAL_INTERP_COL}"),
        })
    if REAL_INTERP_COL in unc_raw.columns:
        candidates["uncertainty"] = pd.DataFrame({
            "t_sec": _parse_clock_seconds(unc_raw[UNC_TIME_COL], name="uncertainty_flag_Time"),
            "is_interpolated": _strict_bool_flag(unc_raw[REAL_INTERP_COL], name=f"uncertainty.{REAL_INTERP_COL}"),
        })
    if not candidates:
        raise KeyError(
            f"{REAL_INTERP_COL!r} was absent from both paired sensor and uncertainty members. "
            "The interpolation policy cannot be applied until the authoritative flag source is identified."
        )
    if len(candidates) == 1:
        source, chosen = next(iter(candidates.items()))
        out = chosen.copy()
        flag_source = source
    else:
        left = candidates["sensor"].rename(columns={"is_interpolated": "flag_sensor"})
        right = candidates["uncertainty"].rename(columns={"is_interpolated": "flag_uncertainty"})
        compared = left.merge(right, on="t_sec", how="outer", indicator=True, validate="one_to_one")
        if not (compared["_merge"] == "both").all():
            raise ValueError("Data_interpolated is present in both archives but timestamp coverage differs.")
        a = pd.array(compared["flag_sensor"], dtype="boolean")
        b = pd.array(compared["flag_uncertainty"], dtype="boolean")
        both_known = ~np.asarray(pd.isna(a) | pd.isna(b), dtype=bool)
        disagree = both_known & (np.asarray(a.fillna(False), dtype=bool) != np.asarray(b.fillna(False), dtype=bool))
        known_mismatch = np.asarray(pd.isna(a), dtype=bool) != np.asarray(pd.isna(b), dtype=bool)
        if disagree.any() or known_mismatch.any():
            raise ValueError(
                "Data_interpolated differs between sensor and uncertainty archives; "
                "do not choose one source silently."
            )
        out = pd.DataFrame({"t_sec": compared["t_sec"], "is_interpolated": a})
        flag_source = "both_verified"

    provenance = {
        "flag_source": flag_source,
        "experiment_key": experiment_key,
        "column": REAL_INTERP_COL,
        "sensor_archive_provenance": sensor_prov,
        "uncertainty_archive_provenance": unc_prov,
        "source_role": "interpolation_quality_flag",
    }
    return _attach_provenance(out.reset_index(drop=True), provenance)

def load_simulation_pressure(archive_path: Path, sim_member: str) -> pd.DataFrame:
    """Load stage-12 pressure (Pa) from a registry-specified simulation ZIP member."""
    if not isinstance(sim_member, str) or not sim_member or sim_member.startswith("/"):
        raise ValueError("sim_member must be a non-empty archive-relative member path.")
    raw, provenance = _read_zip_csv_with_provenance(archive_path, sim_member, sep=";")
    required = (SIM_TIME_COL, SIM_PRESSURE_PA_COL)
    missing = [c for c in required if c not in raw.columns]
    if missing:
        raise KeyError(f"Simulation member missing columns {missing}; available={list(raw.columns)}")
    out = pd.DataFrame({
        "t_sec_sim": _parse_clock_seconds(raw[SIM_TIME_COL], name="sim_time"),
        "P_pa": pd.to_numeric(raw[SIM_PRESSURE_PA_COL], errors="coerce").to_numpy(float),
    })
    provenance.update({"sim_member": sim_member, "source_role": "simulation_stage12_pressure"})
    return _attach_provenance(out, provenance)


def apply_offset_and_convert(sim_df: pd.DataFrame, sim_to_real_offset_s: float) -> pd.DataFrame:
    """Apply reviewed time offset and convert Pa to mbar, without silent sorting."""
    if not isinstance(sim_df, pd.DataFrame) or sim_df.empty:
        raise ValueError("sim_df must be a non-empty DataFrame.")
    try:
        offset = float(sim_to_real_offset_s)
    except (TypeError, ValueError):
        raise ValueError("sim_to_real_offset_s must be a finite reviewed number; blank is not zero.")
    if not math.isfinite(offset):
        raise ValueError("sim_to_real_offset_s must be finite; blank is not zero.")
    missing = {"t_sec_sim", "P_pa"} - set(sim_df.columns)
    if missing:
        raise KeyError(f"sim_df missing columns {sorted(missing)}")
    t = pd.to_numeric(sim_df["t_sec_sim"], errors="coerce").to_numpy(float)
    p = pd.to_numeric(sim_df["P_pa"], errors="coerce").to_numpy(float)
    if not np.isfinite(t).all():
        raise ValueError("Simulation time contains missing/non-finite values.")
    if np.any(np.diff(t) <= 0):
        raise ValueError("Simulation time must be strictly increasing and unique; no sorting is applied.")
    if np.isinf(p).any():
        raise ValueError("Simulation pressure contains +/- infinity.")
    out = pd.DataFrame({"t_sec": t + offset, "sim_PY23_mbar": p / PA_PER_MBAR})
    if "source_row" in sim_df.columns:
        out["source_row"] = sim_df["source_row"].to_numpy()
    out.attrs["sim_to_real_offset_s"] = offset
    out.attrs["unit_conversion"] = "Pa / 100 = mbar"
    out.attrs["source_provenance"] = sim_df.attrs.get("source_provenance", {})
    return out


def validate_review_record(review_record: Mapping[str, Any]) -> dict[str, Any]:
    """Require human approval and explicit mapping/time evidence before primary q."""
    if not isinstance(review_record, Mapping):
        raise TypeError("review_record must be a mapping from the reviewed event registry.")
    missing = sorted(REQUIRED_REVIEW_FIELDS - set(review_record.keys()))
    if missing:
        raise ValueError(f"Reviewed event record is missing required fields: {missing}")
    if review_record["review_status"] != "APPROVED_SINGLE_EVENT":
        raise ValueError("Primary q requires review_status='APPROVED_SINGLE_EVENT'.")
    _validate_experiment_key(str(review_record["experiment_key"]))
    expected = {
        "reviewed_primary_real_channel": "PY23",
        "reviewed_primary_sim_channel": SIM_PRESSURE_PA_COL,
        "reviewed_primary_uncertainty_column": UNC_PY23_COL,
        "reviewed_primary_real_unit": "mbar",
        "reviewed_primary_sim_unit": "Pa",
        "reviewed_primary_uncertainty_unit": "mbar",
    }
    mismatches = {
        k: (review_record.get(k), v)
        for k, v in expected.items()
        if str(review_record.get(k, "")).strip() != v
    }
    if mismatches:
        raise ValueError(f"Primary physical mapping does not match the frozen protocol: {mismatches}")
    for field in (
        "reviewed_time_mapping_evidence",
        "reviewed_mapping_evidence",
        "reviewed_uncertainty_semantics_evidence",
        "sim_member_expected",
    ):
        if not str(review_record.get(field, "")).strip():
            raise ValueError(f"{field} must contain explicit human-review evidence or exact member path.")
    if review_record.get("reviewed_interpolation_flag_source") not in {"sensor", "uncertainty", "both_verified"}:
        raise ValueError("reviewed_interpolation_flag_source must be sensor, uncertainty, or both_verified.")
    if review_record.get("reviewed_pre_perturbation_time_basis") != "REAL_NATIVE_TIME":
        raise ValueError("reviewed_pre_perturbation_time_basis must be REAL_NATIVE_TIME.")
    reviewed_onset_s = _parse_reviewed_clock_scalar(
        review_record["reviewed_pre_perturbation_time"], name="reviewed_pre_perturbation_time"
    )
    try:
        offset = float(review_record["reviewed_sim_to_real_time_offset_s"])
    except (TypeError, ValueError):
        raise ValueError("Reviewed sim-to-real offset must be an explicit finite number; blank is not zero.")
    if not math.isfinite(offset):
        raise ValueError("Reviewed sim-to-real offset must be finite.")
    out = dict(review_record)
    out["reviewed_sim_to_real_time_offset_s"] = offset
    out["reviewed_pre_perturbation_time_s"] = reviewed_onset_s
    return out


def _validate_time_frame(df: pd.DataFrame, time_col: str, frame_name: str) -> np.ndarray:
    if not isinstance(df, pd.DataFrame) or df.empty:
        raise ValueError(f"{frame_name} must be a non-empty DataFrame.")
    if time_col not in df.columns:
        raise KeyError(f"{frame_name} missing {time_col!r}.")
    t = pd.to_numeric(df[time_col], errors="coerce").to_numpy(float)
    if not np.isfinite(t).all():
        raise ValueError(f"{frame_name}.{time_col} contains non-finite values.")
    if np.any(np.diff(t) <= 0):
        raise ValueError(f"{frame_name}.{time_col} must be strictly increasing and unique.")
    return t


def compute_q_median(
    real_df: pd.DataFrame,
    unc_df: pd.DataFrame,
    interp_df: pd.DataFrame,
    sim_df_shifted: pd.DataFrame,
    *,
    q_window_real_time: tuple[float, float],
    review_record: Mapping[str, Any],
    tolerance_s: float = TIME_MATCH_TOLERANCE_S,
    min_valid_points: int = MIN_Q_VALID_POINTS,
) -> dict[str, Any]:
    """Compute primary q with strict review, 300s window, nearest-time and provenance checks."""
    reviewed = validate_review_record(review_record)
    if not isinstance(q_window_real_time, (tuple, list)) or len(q_window_real_time) != 2:
        raise ValueError("q_window_real_time must be a (start_s, end_s) pair.")
    q_start, q_end = map(float, q_window_real_time)
    if not (math.isfinite(q_start) and math.isfinite(q_end) and q_end > q_start):
        raise ValueError(f"Invalid q_window_real_time: {q_window_real_time}")
    if not math.isclose(q_end - q_start, Q_HORIZON_SECONDS, rel_tol=0.0, abs_tol=1e-6):
        raise ValueError(f"Primary q window must be exactly {Q_HORIZON_SECONDS:g}s.")
    if not math.isclose(q_end, reviewed["reviewed_pre_perturbation_time_s"], rel_tol=0.0, abs_tol=1e-6):
        raise ValueError(
            "Primary q-window end must equal the reviewed real perturbation time; "
            "the interval is [onset-300s, onset)."
        )
    try:
        tolerance = float(tolerance_s)
    except (TypeError, ValueError):
        raise ValueError("tolerance_s must be finite and >0.")
    if not math.isfinite(tolerance) or tolerance <= 0:
        raise ValueError("tolerance_s must be finite and >0.")
    if not isinstance(min_valid_points, (int, np.integer)) or min_valid_points < 1:
        raise ValueError("min_valid_points must be a positive integer.")

    for col in ("t_sec", "PY23_mbar"):
        if col not in real_df.columns:
            raise KeyError(f"real_df missing {col!r}.")
    for col in ("t_sec", "u_mbar"):
        if col not in unc_df.columns:
            raise KeyError(f"unc_df missing {col!r}.")
    for col in ("t_sec", "is_interpolated"):
        if col not in interp_df.columns:
            raise KeyError(f"interp_df missing {col!r}; load from the reviewed archive source.")
    for col in ("t_sec", "sim_PY23_mbar"):
        if col not in sim_df_shifted.columns:
            raise KeyError(f"sim_df_shifted missing {col!r}.")

    rt = _validate_time_frame(real_df, "t_sec", "real_df")
    _validate_time_frame(unc_df, "t_sec", "unc_df")
    _validate_time_frame(interp_df, "t_sec", "interp_df")
    _validate_time_frame(sim_df_shifted, "t_sec", "sim_df_shifted")

    actual_offset = sim_df_shifted.attrs.get("sim_to_real_offset_s")
    if actual_offset is None or not math.isclose(float(actual_offset), reviewed["reviewed_sim_to_real_time_offset_s"], abs_tol=1e-9):
        raise ValueError("Shifted simulation offset does not match the human-reviewed registry offset.")
    actual_member = sim_df_shifted.attrs.get("source_provenance", {}).get("member")
    if actual_member != reviewed["sim_member_expected"]:
        raise ValueError(
            f"Loaded simulation member {actual_member!r} does not match reviewed sim_member_expected "
            f"{reviewed['sim_member_expected']!r}."
        )
    actual_flag_source = interp_df.attrs.get("source_provenance", {}).get("flag_source")
    if actual_flag_source != reviewed["reviewed_interpolation_flag_source"]:
        raise ValueError(
            f"Interpolation flag source {actual_flag_source!r} does not match reviewed source "
            f"{reviewed['reviewed_interpolation_flag_source']!r}."
        )
    for frame_name, frame in (("real_df", real_df), ("unc_df", unc_df), ("interp_df", interp_df)):
        loaded_key = frame.attrs.get("source_provenance", {}).get("experiment_key")
        if loaded_key != reviewed["experiment_key"]:
            raise ValueError(
                f"{frame_name} provenance experiment_key {loaded_key!r} does not match "
                f"reviewed event {reviewed['experiment_key']!r}."
            )

    # Anchor on real observations inside [start, end). Match against full uncertainty
    # and simulation series so points just outside the boundary can serve as the nearest
    # sample within tolerance (guard-band matching); the anchor itself remains in-window.
    anchors = real_df.loc[(rt >= q_start) & (rt < q_end)].copy().reset_index(drop=True)
    provenance = {
        "q_window_real_start": q_start,
        "q_window_real_end": q_end,
        "q_window_seconds": Q_HORIZON_SECONDS,
        "reviewed_real_onset_s": reviewed["reviewed_pre_perturbation_time_s"],
        "time_match_tolerance_s": tolerance,
        "min_valid_points": int(min_valid_points),
        "review_status": reviewed["review_status"],
        "experiment_key": reviewed.get("experiment_key", ""),
        "anomaly_id": reviewed.get("anomaly_id", ""),
        "sim_to_real_offset_s": reviewed["reviewed_sim_to_real_time_offset_s"],
        "mapping_evidence": reviewed["reviewed_mapping_evidence"],
        "time_mapping_evidence": reviewed["reviewed_time_mapping_evidence"],
        "uncertainty_semantics_evidence": reviewed["reviewed_uncertainty_semantics_evidence"],
        "uncertainty_unit": reviewed["reviewed_primary_uncertainty_unit"],
        "interpolation_flag_source": actual_flag_source,
        "real_sensor_provenance": real_df.attrs.get("source_provenance", {}),
        "uncertainty_provenance": unc_df.attrs.get("source_provenance", {}),
        "simulation_provenance": sim_df_shifted.attrs.get("source_provenance", {}),
    }
    base_counts = {
        "n_real_anchors": int(len(anchors)),
        "n_matched_uncertainty": 0,
        "n_matched_interpolation_flag": 0,
        "n_matched_simulation": 0,
        "n_matched_all_four": 0,
        "n_valid": 0,
        "n_unmatched_uncertainty": 0,
        "n_unmatched_interpolation_flag": 0,
        "n_unmatched_simulation": 0,
        "n_nonfinite_real": 0,
        "n_nonfinite_uncertainty": 0,
        "n_nonfinite_simulation": 0,
        "n_excluded_nonpositive_u": 0,
        "n_excluded_interpolated": 0,
        "n_excluded_interpolation_flag_unknown": 0,
        "n_reused_uncertainty_rows": 0,
        "n_reused_interpolation_flag_rows": 0,
        "n_reused_simulation_rows": 0,
    }
    if anchors.empty:
        return {**provenance, **base_counts, "q_median": np.nan, "q_p90": np.nan,
                "q_mean": np.nan, "status": "NO_REAL_PREWINDOW_COVERAGE"}

    anchor = pd.DataFrame({
        "anchor_t_sec": anchors["t_sec"].to_numpy(float),
        "PY23_mbar": pd.to_numeric(anchors["PY23_mbar"], errors="coerce").to_numpy(float),
    }).sort_values("anchor_t_sec", kind="stable")
    unc = pd.DataFrame({
        "unc_t_sec": unc_df["t_sec"].to_numpy(float),
        "u_mbar": pd.to_numeric(unc_df["u_mbar"], errors="coerce").to_numpy(float),
    }).sort_values("unc_t_sec", kind="stable")
    quality = pd.DataFrame({
        "flag_t_sec": interp_df["t_sec"].to_numpy(float),
        "is_interpolated": _strict_bool_flag(interp_df["is_interpolated"], name="is_interpolated").to_numpy(),
    }).sort_values("flag_t_sec", kind="stable")
    sim = pd.DataFrame({
        "sim_t_sec": sim_df_shifted["t_sec"].to_numpy(float),
        "sim_PY23_mbar": pd.to_numeric(sim_df_shifted["sim_PY23_mbar"], errors="coerce").to_numpy(float),
    }).sort_values("sim_t_sec", kind="stable")

    merged = pd.merge_asof(anchor, unc, left_on="anchor_t_sec", right_on="unc_t_sec", direction="nearest", tolerance=tolerance)
    merged = pd.merge_asof(merged.sort_values("anchor_t_sec", kind="stable"), quality,
                           left_on="anchor_t_sec", right_on="flag_t_sec", direction="nearest", tolerance=tolerance)
    merged = pd.merge_asof(merged.sort_values("anchor_t_sec", kind="stable"), sim,
                           left_on="anchor_t_sec", right_on="sim_t_sec", direction="nearest", tolerance=tolerance)

    has_unc_time = merged["unc_t_sec"].notna().to_numpy()
    has_flag_time = merged["flag_t_sec"].notna().to_numpy()
    has_sim_time = merged["sim_t_sec"].notna().to_numpy()
    base_counts["n_matched_uncertainty"] = int(has_unc_time.sum())
    base_counts["n_matched_interpolation_flag"] = int(has_flag_time.sum())
    base_counts["n_matched_simulation"] = int(has_sim_time.sum())
    base_counts["n_unmatched_uncertainty"] = int((~has_unc_time).sum())
    base_counts["n_unmatched_interpolation_flag"] = int((~has_flag_time).sum())
    base_counts["n_unmatched_simulation"] = int((~has_sim_time).sum())

    for name, mask, time_col, count_col in (
        ("uncertainty", has_unc_time, "unc_t_sec", "n_reused_uncertainty_rows"),
        ("interpolation flag", has_flag_time, "flag_t_sec", "n_reused_interpolation_flag_rows"),
        ("simulation", has_sim_time, "sim_t_sec", "n_reused_simulation_rows"),
    ):
        if mask.any():
            reused = int(merged.loc[mask, time_col].duplicated(keep=False).sum())
            base_counts[count_col] = reused
            if reused:
                raise ValueError(f"Nearest-time matching reused {reused} {name} rows; no implicit row reuse is allowed.")

    all_four = has_unc_time & has_flag_time & has_sim_time
    base_counts["n_matched_all_four"] = int(all_four.sum())
    real_v = pd.to_numeric(merged["PY23_mbar"], errors="coerce").to_numpy(float)
    unc_v = pd.to_numeric(merged["u_mbar"], errors="coerce").to_numpy(float)
    sim_v = pd.to_numeric(merged["sim_PY23_mbar"], errors="coerce").to_numpy(float)
    interp = pd.array(merged["is_interpolated"], dtype="boolean")
    interp_na = np.asarray(pd.isna(interp), dtype=bool)
    interp_true = np.asarray(interp.fillna(False), dtype=bool)

    nonfinite_real = all_four & ~np.isfinite(real_v)
    nonfinite_u = all_four & ~np.isfinite(unc_v)
    nonfinite_sim = all_four & ~np.isfinite(sim_v)
    base_counts["n_nonfinite_real"] = int(nonfinite_real.sum())
    base_counts["n_nonfinite_uncertainty"] = int(nonfinite_u.sum())
    base_counts["n_nonfinite_simulation"] = int(nonfinite_sim.sum())

    finite_all = all_four & np.isfinite(real_v) & np.isfinite(unc_v) & np.isfinite(sim_v)
    nonpositive = finite_all & (unc_v <= 0)
    interp_excluded = finite_all & (unc_v > 0) & interp_true
    interp_unknown = finite_all & (unc_v > 0) & interp_na
    valid = finite_all & (unc_v > 0) & ~interp_true & ~interp_na
    base_counts["n_excluded_nonpositive_u"] = int(nonpositive.sum())
    base_counts["n_excluded_interpolated"] = int(interp_excluded.sum())
    base_counts["n_excluded_interpolation_flag_unknown"] = int(interp_unknown.sum())
    base_counts["n_valid"] = int(valid.sum())

    if base_counts["n_valid"] < min_valid_points:
        return {
            **provenance, **base_counts,
            "valid_fraction_of_real_anchors": float(base_counts["n_valid"] / len(anchors)),
            "q_median": np.nan, "q_p90": np.nan, "q_mean": np.nan,
            "raw_residual_median": np.nan, "raw_residual_abs_p90": np.nan,
            "status": f"INSUFFICIENT_VALID_POINTS (<{min_valid_points})",
        }

    q = np.abs(real_v[valid] - sim_v[valid]) / unc_v[valid]
    residual = real_v[valid] - sim_v[valid]
    return {
        **provenance, **base_counts,
        "valid_fraction_of_real_anchors": float(base_counts["n_valid"] / len(anchors)),
        "q_median": float(np.median(q)),
        "q_p90": float(np.quantile(q, 0.90)),
        "q_mean": float(np.mean(q)),
        "raw_residual_median": float(np.median(residual)),
        "raw_residual_abs_p90": float(np.quantile(np.abs(residual), 0.90)),
        "status": "OK",
    }


def compute_q_for_reviewed_event(
    real_df: pd.DataFrame,
    unc_df: pd.DataFrame,
    interp_df: pd.DataFrame,
    sim_df: pd.DataFrame,
    *,
    review_record: Mapping[str, Any],
    q_window_real_time: tuple[float, float],
    tolerance_s: float = TIME_MATCH_TOLERANCE_S,
    min_valid_points: int = MIN_Q_VALID_POINTS,
) -> dict[str, Any]:
    """Validate registry, apply its reviewed offset, and compute primary q."""
    reviewed = validate_review_record(review_record)
    shifted = apply_offset_and_convert(
        sim_df,
        reviewed["reviewed_sim_to_real_time_offset_s"],
    )
    return compute_q_median(
        real_df, unc_df, interp_df, shifted,
        q_window_real_time=q_window_real_time,
        review_record=reviewed,
        tolerance_s=tolerance_s,
        min_valid_points=min_valid_points,
    )


def load_and_compute_q(
    sensor_archive_path: Path,
    uncertainty_archive_path: Path,
    simulation_archive_path: Path,
    review_record: Mapping[str, Any],
    *,
    tolerance_s: float = TIME_MATCH_TOLERANCE_S,
    min_valid_points: int = MIN_Q_VALID_POINTS,
) -> dict[str, Any]:
    """End-to-end single-row loader + primary pre-onset q computation.

    The reviewed onset determines [onset-300s, onset); the registry determines
    the exact simulation member, time offset, and accepted interpolation-flag source.
    """
    reviewed = validate_review_record(review_record)
    exp_key = str(reviewed["experiment_key"])
    real = load_real_py23(sensor_archive_path, exp_key)
    unc = load_real_uncertainty(uncertainty_archive_path, exp_key)
    interp = load_interpolation_flags(sensor_archive_path, uncertainty_archive_path, exp_key)
    sim = load_simulation_pressure(simulation_archive_path, str(reviewed["sim_member_expected"]))
    onset = reviewed["reviewed_pre_perturbation_time_s"]
    q_window = (onset - Q_HORIZON_SECONDS, onset)
    result = compute_q_for_reviewed_event(
        real, unc, interp, sim,
        review_record=reviewed,
        q_window_real_time=q_window,
        tolerance_s=tolerance_s,
        min_valid_points=min_valid_points,
    )
    return result


# -------------------------- Synthetic smoke tests --------------------------
def _review_record(offset: float = 0.0) -> dict[str, Any]:
    return {
        "review_status": "APPROVED_SINGLE_EVENT",
        "experiment_key": "Operation/ChemA/OP1/Exp001",
        "anomaly_id": "A001",
        "sim_member_expected": "Operation/ChemA/OP1/Exp001.csv",
        "reviewed_pre_perturbation_time": "00:05:50",
        "reviewed_pre_perturbation_time_basis": "REAL_NATIVE_TIME",
        "reviewed_primary_real_channel": "PY23",
        "reviewed_primary_sim_channel": SIM_PRESSURE_PA_COL,
        "reviewed_primary_uncertainty_column": UNC_PY23_COL,
        "reviewed_primary_real_unit": "mbar",
        "reviewed_primary_sim_unit": "Pa",
        "reviewed_primary_uncertainty_unit": "mbar",
        "reviewed_uncertainty_semantics_evidence": "SYNTHETIC TEST: declared same-unit absolute tolerance fixture.",
        "reviewed_interpolation_flag_source": "uncertainty",
        "reviewed_sim_to_real_time_offset_s": offset,
        "reviewed_time_mapping_evidence": "SYNTHETIC TEST: known 10-second clock shift.",
        "reviewed_mapping_evidence": "SYNTHETIC TEST: declared PY23/stage-12 mapping.",
    }


def _synthetic_real(n: int = 400, start: float = 0.0, freq: float = 1.0, val: float = 650.0,
                    slope_mbar_per_s: float = 0.0):
    t = start + np.arange(n, dtype=float) * freq
    frame = pd.DataFrame({"t_sec": t, "PY23_mbar": val + slope_mbar_per_s * t})
    frame.attrs["source_provenance"] = {"experiment_key": "Operation/ChemA/OP1/Exp001"}
    return frame


def _synthetic_unc(n: int = 400, start: float = 0.0, freq: float = 1.0, u: float = 0.5):
    t = start + np.arange(n, dtype=float) * freq
    frame = pd.DataFrame({"t_sec": t, "u_mbar": u})
    frame.attrs["source_provenance"] = {"experiment_key": "Operation/ChemA/OP1/Exp001"}
    return frame



def _synthetic_interp(n: int = 400, start: float = 0.0, freq: float = 1.0, source: str = "uncertainty"):
    t = start + np.arange(n, dtype=float) * freq
    frame = pd.DataFrame({"t_sec": t, "is_interpolated": pd.array([False] * n, dtype="boolean")})
    frame.attrs["source_provenance"] = {"flag_source": source, "experiment_key": "Operation/ChemA/OP1/Exp001"}
    return frame

def _synthetic_sim(n: int = 400, start: float = 0.0, freq: float = 1.0, p_pa: float = 65000.0,
                   slope_pa_per_s: float = 0.0):
    t = start + np.arange(n, dtype=float) * freq
    frame = pd.DataFrame({"t_sec_sim": t, "P_pa": p_pa + slope_pa_per_s * t})
    frame.attrs["source_provenance"] = {"member": "Operation/ChemA/OP1/Exp001.csv"}
    return frame


def _to_hhmmss(seconds: float) -> str:
    seconds = int(seconds)
    hours, rem = divmod(seconds, 3600)
    minutes, secs = divmod(rem, 60)
    return f"{hours:02d}:{minutes:02d}:{secs:02d}"


def _write_zip_csv(path: Path, member: str, frame: pd.DataFrame, sep: str = ",") -> None:
    import io
    buffer = io.StringIO()
    frame.to_csv(buffer, index=False, sep=sep)
    with zipfile.ZipFile(path, "a" if path.exists() else "w", compression=zipfile.ZIP_DEFLATED) as zf:
        zf.writestr(member, buffer.getvalue().encode("utf-8"))


def run_smoke_tests() -> None:
    import tempfile

    print("Running reviewed synthetic smoke tests for v5.2 Module 3.5...")
    real = _synthetic_real()
    unc = _synthetic_unc()
    sim = _synthetic_sim()
    review = _review_record()

    # 1. Perfect match.
    r = compute_q_for_reviewed_event(real, unc, _synthetic_interp(), sim, review_record=review, q_window_real_time=(50, 350))
    assert r["status"] == "OK" and np.isclose(r["q_median"], 0.0)
    print(f"  PASS 1: perfect match -> q=0; n_valid={r['n_valid']}")

    # 2. Explicit offset is applied to a dynamic signal; wrong offset gives nonzero q.
    real_dynamic = _synthetic_real(val=650.0, slope_mbar_per_s=0.1)
    sim_dynamic = _synthetic_sim(start=-10.0, p_pa=65100.0, slope_pa_per_s=10.0)
    right = compute_q_for_reviewed_event(
        real_dynamic, unc, _synthetic_interp(), sim_dynamic,
        review_record=_review_record(10.0), q_window_real_time=(50, 350)
    )
    wrong = compute_q_for_reviewed_event(
        real_dynamic, unc, _synthetic_interp(), sim_dynamic,
        review_record=_review_record(0.0), q_window_real_time=(50, 350)
    )
    assert right["status"] == "OK" and np.isclose(right["q_median"], 0.0, atol=1e-9)
    assert wrong["status"] == "OK" and wrong["q_median"] > 0
    print(f"  PASS 2: dynamic trace aligned by +10s -> q≈0; wrong zero offset -> q={wrong['q_median']:.3f}")

    # 3. Interpolated and unknown flags excluded.
    real_i = real.copy()
    flags = pd.array([False] * len(real_i), dtype="boolean")
    flags[100:110] = True
    flags[110:115] = pd.NA
    real_i["is_interpolated"] = flags
    interp_i = real_i[["t_sec", "is_interpolated"]].copy()
    interp_i.attrs["source_provenance"] = {"flag_source": "uncertainty", "experiment_key": "Operation/ChemA/OP1/Exp001"}
    ri = compute_q_for_reviewed_event(real, unc, interp_i, sim, review_record=review, q_window_real_time=(50, 350))
    assert ri["n_excluded_interpolated"] == 10
    assert ri["n_excluded_interpolation_flag_unknown"] == 5
    assert ri["n_valid"] == 285
    print("  PASS 3: interpolated=True and unknown flag rows are excluded and separately counted")

    # 4. Non-positive uncertainty excluded without epsilon.
    unc0 = unc.copy(); unc0.loc[unc0["t_sec"].between(100, 120, inclusive="left"), "u_mbar"] = 0.0
    r0 = compute_q_for_reviewed_event(real, unc0, _synthetic_interp(), sim, review_record=review, q_window_real_time=(50, 350))
    assert r0["n_excluded_nonpositive_u"] == 20 and r0["n_valid"] == 280
    print("  PASS 4: zero uncertainty excluded without epsilon")

    # 5. Exact 300-second window enforced.
    try:
        compute_q_for_reviewed_event(real, unc, _synthetic_interp(), sim, review_record=review, q_window_real_time=(50, 349))
    except ValueError as e:
        assert "exactly 300" in str(e)
    else:
        raise AssertionError("A non-300-second q window was accepted.")
    print("  PASS 5: non-300s q-window rejected")

    # 6. Pa to mbar conversion.
    shifted = apply_offset_and_convert(_synthetic_sim(p_pa=65000.0), 0.0)
    assert np.allclose(shifted["sim_PY23_mbar"], 650.0)
    print("  PASS 6: 65000 Pa -> 650 mbar")

    # 7. Blank / NaN offset rejected.
    for bad in (None, np.nan, "", "  "):
        try:
            apply_offset_and_convert(sim, bad)
        except ValueError:
            continue
        raise AssertionError(f"Invalid offset accepted: {bad!r}")
    print("  PASS 7: blank/NaN offsets rejected")

    # 8. Duplicate, descending, and numeric-as-clock timestamps rejected.
    for bad_series in (
        pd.Series(["00:00:00", "00:00:01", "00:00:01"]),
        pd.Series(["00:00:02", "00:00:01", "00:00:03"]),
        pd.Series([0, 1, 2]),
    ):
        try:
            _parse_clock_seconds(bad_series, name="bad_time")
        except (TypeError, ValueError):
            continue
        raise AssertionError("Invalid timestamps accepted.")
    print("  PASS 8: duplicate/backward/numeric clock values rejected")

    # 9. Guard-band matching: sim sample just before q_start can match in-window real anchor.
    real_b = _synthetic_real(n=400, start=100.0)
    unc_b = _synthetic_unc(n=400, start=100.0)
    sim_b = _synthetic_sim(n=400, start=99.6)
    review_400 = dict(review); review_400["reviewed_pre_perturbation_time"] = "00:06:40"
    rb = compute_q_for_reviewed_event(real_b, unc_b, _synthetic_interp(n=400, start=100.0), sim_b, review_record=review_400, q_window_real_time=(100, 400))
    assert rb["status"] == "OK" and rb["n_matched_all_four"] >= 299 and np.isclose(rb["q_median"], 0.0)
    print("  PASS 9: tolerance guard-band matching works at q-window boundary")

    # 10. Reuse of one uncertainty/simulation row is rejected.
    real_dense = pd.DataFrame({
        "t_sec": [100.0, 100.4] + list(np.arange(101.0, 399.0, 1.0)),
        "PY23_mbar": 650.0,
    })
    real_dense.attrs["source_provenance"] = {"experiment_key": "Operation/ChemA/OP1/Exp001"}
    unc_sparse = _synthetic_unc(start=100.2, n=300, freq=1.0)
    sim_sparse = _synthetic_sim(start=100.2, n=300, freq=1.0)
    try:
        compute_q_for_reviewed_event(real_dense, unc_sparse, _synthetic_interp(n=400), sim_sparse, review_record=review_400, q_window_real_time=(100, 400))
    except ValueError as e:
        assert "reused" in str(e)
    else:
        raise AssertionError("Nearest-time matching row reuse was not rejected.")
    print("  PASS 10: nearest-time source-row reuse rejected")

    # 11. Different missing/nonfinite sources are correctly counted.
    real_m = real.copy(); real_m.loc[100, "PY23_mbar"] = np.nan
    unc_m = unc.copy(); unc_m.loc[101, "u_mbar"] = np.nan
    sim_m = sim.copy(); sim_m.loc[102, "P_pa"] = np.nan
    sim_m = apply_offset_and_convert(sim_m, 0.0)
    rm = compute_q_median(real_m, unc_m, _synthetic_interp(), sim_m, q_window_real_time=(50, 350), review_record=review)
    assert rm["n_nonfinite_real"] == 1
    assert rm["n_nonfinite_uncertainty"] == 1
    assert rm["n_nonfinite_simulation"] == 1
    print("  PASS 11: NaN real, uncertainty, simulation independently counted")

    # 12. Insufficient/absent coverage correctly reported.
    short_real = _synthetic_real(n=50)
    rshort = compute_q_for_reviewed_event(short_real, _synthetic_unc(n=50), _synthetic_interp(n=50), sim, review_record=review, q_window_real_time=(50, 350))
    assert rshort["status"] == "NO_REAL_PREWINDOW_COVERAGE"
    print("  PASS 12: no real pre-window coverage reported distinctly")

    # 13. Review record must be approved and contain evidence.
    bad_review = dict(review); bad_review["review_status"] = "PENDING"
    try:
        compute_q_for_reviewed_event(real, unc, _synthetic_interp(), sim, review_record=bad_review, q_window_real_time=(50, 350))
    except ValueError as e:
        assert "APPROVED_SINGLE_EVENT" in str(e)
    else:
        raise AssertionError("Unapproved event record accepted.")
    print("  PASS 13: unreviewed event blocked")

    # 14. Provenance and event evidence are present.
    rp = compute_q_for_reviewed_event(real, unc, _synthetic_interp(), sim, review_record=review, q_window_real_time=(50, 350))
    for key in ("experiment_key", "anomaly_id", "sim_to_real_offset_s", "mapping_evidence", "time_mapping_evidence",
                "q_window_seconds", "n_matched_all_four", "n_excluded_interpolation_flag_unknown", "status"):
        assert key in rp, f"Missing provenance field {key!r}"
    print("  PASS 14: reviewed-event provenance captured")

    # 15. Synthetic ZIP fixture proves interpolation flag can be loaded from UNCERTAINTY archive.
    with tempfile.TemporaryDirectory() as tmp:
        tmp = Path(tmp)
        exp_key = "Operation/ChemA/OP1/Exp001"
        sensor_zip = tmp / "sensors.zip"
        unc_zip = tmp / "uncertainties.zip"
        sim_zip = tmp / "simulations.zip"
        sensor_member = f"{SENSOR_ROOT}/{exp_key}.csv"
        unc_member = f"{UNC_ROOT}/{exp_key}.csv"
        sim_member = "Operation/ChemA/OP1/Exp001.csv"
        sensor_frame = pd.DataFrame({
            "Time": ["00:00:00", "00:00:01", "00:00:02"],
            "PY23": [650.0, 651.0, 652.0],
        })
        unc_frame = pd.DataFrame({
            "Time": ["00:00:00", "00:00:01", "00:00:02"],
            "±ΔPY23": [0.5, 0.5, 0.5],
            "Data_interpolated": [False, True, "unknown"],
        })
        sim_frame = pd.DataFrame({
            "time": ["00:00:00", "00:00:01", "00:00:02"],
            "pressure stage 12 / Pa": [65000, 65100, 65200],
        })
        _write_zip_csv(sensor_zip, sensor_member, sensor_frame)
        _write_zip_csv(unc_zip, unc_member, unc_frame)
        _write_zip_csv(sim_zip, sim_member, sim_frame, sep=";")
        loaded_real = load_real_py23(sensor_zip, exp_key)
        loaded_unc = load_real_uncertainty(unc_zip, exp_key)
        loaded_flags = load_interpolation_flags(sensor_zip, unc_zip, exp_key)
        loaded_sim = load_simulation_pressure(sim_zip, sim_member)
        assert pd.isna(loaded_flags["is_interpolated"].iloc[2])
        assert loaded_flags.attrs["source_provenance"]["flag_source"] == "uncertainty"
        assert "Data_interpolated" not in loaded_real.columns
        assert np.isclose(loaded_unc["u_mbar"].iloc[0], 0.5)
        assert np.isclose(load_simulation_pressure(sim_zip, sim_member)["P_pa"].iloc[-1], 65200)
        assert loaded_real.attrs["source_provenance"]["member_sha256"]
        print("  PASS 15: ZIP fixtures load sensor interpolation flag and uncertainty from separate archives")

    # 16. Missing interpolation flag in both archives is a hard schema error.
    with tempfile.TemporaryDirectory() as tmp:
        tmp = Path(tmp); sensor_zip = tmp / "sensors.zip"
        member = f"{SENSOR_ROOT}/Operation/ChemA/OP1/Exp001.csv"
        _write_zip_csv(sensor_zip, member, pd.DataFrame({"Time": ["00:00:00"], "PY23": [650.0]}))
        unc_zip = tmp / "uncertainties.zip"
        unc_member = f"{UNC_ROOT}/Operation/ChemA/OP1/Exp001.csv"
        _write_zip_csv(unc_zip, unc_member, pd.DataFrame({"Time": ["00:00:00"], "±ΔPY23": [0.5]}))
        try:
            load_interpolation_flags(sensor_zip, unc_zip, "Operation/ChemA/OP1/Exp001")
        except KeyError as e:
            assert "Data_interpolated" in str(e)
        else:
            raise AssertionError("Missing interpolation flag was silently accepted.")
    print("  PASS 16: missing interpolation flag in both archives is rejected")

    # 17. Bad experiment key rejected.
    for key in ("ChemA/OP1/Exp001", "Operation/ChemA/OP1", "Operation/../OP1/Exp001", "Operation\\ChemA\\OP1\\Exp001"):
        try:
            _validate_experiment_key(key)
        except (TypeError, ValueError):
            continue
        raise AssertionError(f"Malformed experiment key accepted: {key}")
    print("  PASS 17: malformed experiment keys rejected")

    # 18. Both archives contain the flag: they must agree exactly.
    with tempfile.TemporaryDirectory() as tmp:
        tmp = Path(tmp); sensor_zip = tmp / "sensors.zip"; unc_zip = tmp / "uncertainties.zip"
        exp_key = "Operation/ChemA/OP1/Exp001"
        sensor_member = f"{SENSOR_ROOT}/{exp_key}.csv"; unc_member = f"{UNC_ROOT}/{exp_key}.csv"
        times = ["00:00:00", "00:00:01"]
        _write_zip_csv(sensor_zip, sensor_member, pd.DataFrame({"Time": times, "PY23": [650, 651], "Data_interpolated": [False, True]}))
        _write_zip_csv(unc_zip, unc_member, pd.DataFrame({"Time": times, "±ΔPY23": [0.5, 0.5], "Data_interpolated": [False, True]}))
        both = load_interpolation_flags(sensor_zip, unc_zip, exp_key)
        assert both.attrs["source_provenance"]["flag_source"] == "both_verified"
        print("  PASS 18: duplicate flag columns in both archives cross-validated")
        # Rebuild uncertainty archive with a disagreement.
        unc_zip_bad = tmp / "uncertainties_bad.zip"
        _write_zip_csv(unc_zip_bad, unc_member, pd.DataFrame({"Time": times, "±ΔPY23": [0.5, 0.5], "Data_interpolated": [False, False]}))
        try:
            load_interpolation_flags(sensor_zip, unc_zip_bad, exp_key)
        except ValueError as e:
            assert "differs" in str(e)
        else:
            raise AssertionError("Disagreeing interpolation flags were silently accepted.")
        print("  PASS 19: disagreeing flag columns across archives rejected")

    # 20. Flag location in SENSOR archive is also supported and recorded.
    with tempfile.TemporaryDirectory() as tmp:
        tmp = Path(tmp); sensor_zip = tmp / "sensors.zip"; unc_zip = tmp / "uncertainties.zip"
        exp_key = "Operation/ChemA/OP1/Exp001"
        sensor_member = f"{SENSOR_ROOT}/{exp_key}.csv"; unc_member = f"{UNC_ROOT}/{exp_key}.csv"
        _write_zip_csv(sensor_zip, sensor_member, pd.DataFrame({"Time": ["00:00:00", "00:00:01"], "PY23": [650, 651], "Data_interpolated": [False, True]}))
        _write_zip_csv(unc_zip, unc_member, pd.DataFrame({"Time": ["00:00:00", "00:00:01"], "±ΔPY23": [0.5, 0.5]}))
        from_sensor = load_interpolation_flags(sensor_zip, unc_zip, exp_key)
        assert from_sensor.attrs["source_provenance"]["flag_source"] == "sensor"
        print("  PASS 20: Data_interpolated located in SENSOR archive and source recorded")
    # 21. q interval must terminate at the independently reviewed real onset.
    try:
        compute_q_for_reviewed_event(real, unc, _synthetic_interp(), sim, review_record=review, q_window_real_time=(49, 349))
    except ValueError as e:
        assert "end must equal" in str(e)
    else:
        raise AssertionError("q window not ending at reviewed onset was accepted.")
    print("  PASS 21: q-window endpoint must equal reviewed real onset")

    # 22. Real/uncertainty/flag provenance must refer to the reviewed target experiment.
    wrong_real = real.copy()
    wrong_real.attrs["source_provenance"] = {"experiment_key": "Operation/ChemB/OP2/Exp999"}
    try:
        compute_q_for_reviewed_event(wrong_real, unc, _synthetic_interp(), sim, review_record=review, q_window_real_time=(50, 350))
    except ValueError as e:
        assert "does not match reviewed event" in str(e)
    else:
        raise AssertionError("A different real experiment was accepted for this reviewed event.")
    print("  PASS 22: target experiment provenance mismatch rejected")

    # 23. End-to-end synthetic ZIP loader -> reviewed q result.
    with tempfile.TemporaryDirectory() as tmp:
        tmp = Path(tmp); sensor_zip = tmp / "sensors.zip"; unc_zip = tmp / "uncertainties.zip"; sim_zip = tmp / "simulations.zip"
        exp_key = "Operation/ChemA/OP1/Exp001"; sim_member = "Operation/ChemA/OP1/Exp001.csv"
        times = [_to_hhmmss(t) for t in range(400)]
        _write_zip_csv(sensor_zip, f"{SENSOR_ROOT}/{exp_key}.csv",
                       pd.DataFrame({"Time": times, "PY23": np.full(400, 650.0)}))
        _write_zip_csv(unc_zip, f"{UNC_ROOT}/{exp_key}.csv",
                       pd.DataFrame({"Time": times, "±ΔPY23": np.full(400, 0.5), "Data_interpolated": np.zeros(400, dtype=int)}))
        _write_zip_csv(sim_zip, sim_member,
                       pd.DataFrame({"time": times, "pressure stage 12 / Pa": np.full(400, 65000.0)}), sep=";")
        end_to_end = load_and_compute_q(sensor_zip, unc_zip, sim_zip, review)
        assert end_to_end["status"] == "OK" and np.isclose(end_to_end["q_median"], 0.0)
        assert end_to_end["real_sensor_provenance"]["member_sha256"]
        assert end_to_end["simulation_provenance"]["member"] == sim_member
        print("  PASS 23: synthetic ZIP archives -> loader -> reviewed 300s q -> provenance")

    print("\nAll reviewed Module 3.5 smoke tests passed (synthetic fixtures only).")
    print("Module 3.5 reads synthetic ZIP fixtures only; no Zenodo archive was opened.")


if __name__ == "__main__":
    run_smoke_tests()