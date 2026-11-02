"""SimTrust-Pre v5.2 — Module 5 (reviewed orchestrator).

Connects reviewed event registry -> pre-onset q -> paired fault-only ΔAP ->
matched negative/control arms. Uses all discoverable Operation real experiments
for the real training cohort, not only experiments that appear in the paired
simulation registry.

Primary estimand: fault-segment utility. Simulated training augmentation contains
only windows fully inside the human-reviewed observable-anomaly/recovery interval.

IMPORTANT
---------
All automated smoke tests use synthetic ZIP fixtures. They establish software
contracts only; they do not establish the empirical validity of labels, pairings,
time offsets, channel equivalence, or any scientific effect.
"""
from __future__ import annotations

import hashlib
import io
import json
import zipfile
from pathlib import Path, PurePosixPath
from typing import Any, Mapping

import numpy as np
import pandas as pd

from SimTrust_Pre_v5_2_Module1_reviewed import (
    assign_experiment_class_mass,
    build_augmented_weights,
    build_sim_fault_windows,
    sample_fault_only_K,
)
from SimTrust_Pre_v5_2_Module2_reviewed import (
    FEATURES,
    LABEL_COL,
    EXPERIMENT_COL,
    WINDOW_START_COL,
    WINDOW_END_COL,
    fit_predict_ap,
)
from SimTrust_Pre_v5_2_Module3_reviewed import (
    Q_HORIZON_SECONDS,
    load_real_py23,
    load_real_uncertainty,
    load_interpolation_flags,
    load_simulation_pressure,
    compute_q_for_reviewed_event,
    validate_review_record,
)
from SimTrust_Pre_v5_2_Module4_1_Reviewed import (
    SENSOR_ROOT,
    build_real_windows_bulk,
)

# Phase 0 / software protocol constants.
N_SEEDS = 20
K_MIN = 10
K_MAX = 100
MIN_ACCEPTED_EVENTS = 6
GROUP_COL = "group_id"
EVENT_COL = "event_key"
SEED_BASE = 20261030
SIM_LABEL_TIME_BASIS = "SIMULATION_NATIVE_TIME"
SIM_INTERVAL_SEMANTICS = "OBSERVABLE_ANOMALY_RECOVERY"
ONSET_ALIGNMENT_EPS_S = 1e-6

REQUIRED_MODULE5_FIELDS = (
    "review_include_primary",
    "anomaly_id",
    "reviewed_sim_label_start_time",
    "reviewed_sim_label_end_time",
    "reviewed_sim_label_time_basis",
    "reviewed_sim_label_interval_semantics",
    "reviewed_observable_interval_evidence",
)


def _stable_seed(key: str, seed_idx: int) -> int:
    if seed_idx < 0:
        raise ValueError("seed_idx must be non-negative.")
    digest = hashlib.sha256(f"{key}|{seed_idx}".encode("utf-8")).hexdigest()
    return SEED_BASE + int(digest[:8], 16) % (2**31 - 1)


def _parse_native_clock(value: Any, *, field: str) -> float:
    """Parse reviewed elapsed HH:MM:SS[.fraction] clock; no midnight wrapping."""
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{field} must be a non-empty native-time string.")
    token = value.strip()
    # pandas' timedelta parser is permissive; constrain accepted string grammar first.
    import re
    pattern = r"^(?:(?:\d+)\s+days?\s+)?\d{1,3}:[0-5]\d:[0-5]\d(?:\.\d+)?$"
    if not re.fullmatch(pattern, token):
        raise ValueError(f"{field} must use HH:MM:SS[.fraction] or N days HH:MM:SS; got {value!r}.")
    seconds = float(pd.to_timedelta(token).total_seconds())
    if not np.isfinite(seconds):
        raise ValueError(f"{field} must be finite.")
    return seconds


def _parse_review_bool(value: Any, *, field: str) -> bool:
    if isinstance(value, (bool, np.bool_)):
        return bool(value)
    token = str(value).strip().casefold()
    if token in {"true", "1", "yes", "y"}:
        return True
    if token in {"false", "0", "no", "n"}:
        return False
    raise ValueError(f"{field} must be a documented boolean; got {value!r}.")


def _group_from_key(experiment_key: str) -> str:
    parts = experiment_key.split("/")
    if len(parts) != 4 or parts[0] != "Operation":
        raise ValueError(f"Invalid Operation experiment_key: {experiment_key!r}")
    return f"{parts[1]}/{parts[2]}"


def discover_operation_experiment_keys(sensor_archive: Path) -> list[str]:
    """Discover the full real Operation cohort from the sensor ZIP hierarchy."""
    sensor_archive = Path(sensor_archive)
    if not sensor_archive.is_file():
        raise FileNotFoundError(sensor_archive)
    keys: set[str] = set()
    with zipfile.ZipFile(sensor_archive) as zf:
        for member in zf.namelist():
            p = PurePosixPath(member)
            parts = p.parts
            if (len(parts) == 5 and parts[0] == SENSOR_ROOT and parts[1] == "Operation"
                    and p.suffix.lower() == ".csv"):
                keys.add("/".join((parts[1], parts[2], parts[3], p.stem)))
    out = sorted(keys)
    if not out:
        raise RuntimeError(
            "No Operation experiment CSVs were discovered under the expected sensor archive root."
        )
    return out


def _window_id(experiment_key: str, start: float, end: float, source: str = "real") -> str:
    raw = f"{source}|{experiment_key}|{start:.9f}|{end:.9f}"
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()[:24]


def _attach_window_ids(frame: pd.DataFrame, *, source: str) -> pd.DataFrame:
    out = frame.copy()
    if out.empty:
        out["window_id"] = pd.Series(dtype="string")
        return out
    out["window_id"] = [
        _window_id(str(exp), float(start), float(end), source)
        for exp, start, end in zip(
            out[EXPERIMENT_COL], out[WINDOW_START_COL], out[WINDOW_END_COL]
        )
    ]
    if out["window_id"].duplicated().any():
        raise ValueError(f"Duplicate window IDs created for source={source!r}.")
    return out


def _exclude_q_overlaps(frame: pd.DataFrame, q_window: tuple[float, float]) -> pd.DataFrame:
    q_start, q_end = map(float, q_window)
    if not (np.isfinite(q_start) and np.isfinite(q_end) and q_end - q_start == Q_HORIZON_SECONDS):
        raise ValueError("Primary q window must be an exact 300-second finite interval.")
    overlap = (frame[WINDOW_START_COL] < q_end) & (frame[WINDOW_END_COL] > q_start)
    return frame.loc[~overlap].copy()


def validate_registry_row(row: Mapping[str, Any]) -> dict[str, Any]:
    """Validate Module 3 review evidence plus Module 5 observable interval semantics."""
    missing = [field for field in REQUIRED_MODULE5_FIELDS if field not in row]
    if missing:
        raise ValueError(f"Missing Module 5 registry fields: {missing}")

    if not _parse_review_bool(row["review_include_primary"], field="review_include_primary"):
        raise ValueError("review_include_primary is not true; event is intentionally excluded.")

    # Reuse Module 3's strict frozen physical/time provenance validation.
    reviewed = validate_review_record(row)

    anomaly_id = str(row.get("anomaly_id", "")).strip()
    if not anomaly_id:
        raise ValueError("anomaly_id must be a non-empty reviewed identifier.")

    if row["reviewed_sim_label_time_basis"] != SIM_LABEL_TIME_BASIS:
        raise ValueError(
            f"reviewed_sim_label_time_basis must be {SIM_LABEL_TIME_BASIS!r}."
        )
    if row["reviewed_sim_label_interval_semantics"] != SIM_INTERVAL_SEMANTICS:
        raise ValueError(
            f"reviewed_sim_label_interval_semantics must be {SIM_INTERVAL_SEMANTICS!r}; "
            "the primary sim training interval must represent observable anomaly + recovery, "
            "not merely the applied perturbation interval."
        )
    if not str(row["reviewed_observable_interval_evidence"]).strip():
        raise ValueError("reviewed_observable_interval_evidence must cite the reviewed label/metadata evidence.")

    sim_start = _parse_native_clock(row["reviewed_sim_label_start_time"], field="reviewed_sim_label_start_time")
    sim_end = _parse_native_clock(row["reviewed_sim_label_end_time"], field="reviewed_sim_label_end_time")
    if sim_end <= sim_start:
        raise ValueError("Reviewed simulation observable interval must have end > start.")

    offset = float(reviewed["reviewed_sim_to_real_time_offset_s"])
    onset_real = float(reviewed["reviewed_pre_perturbation_time_s"])
    mapped_sim_start = sim_start + offset
    if mapped_sim_start < onset_real - ONSET_ALIGNMENT_EPS_S:
        raise ValueError(
            "The mapped simulator observable-fault interval begins before the reviewed real perturbation "
            f"onset by {onset_real - mapped_sim_start:.6f}s. This would overlap the pre-onset q period; "
            "review the offset and observable-interval semantics."
        )

    out = dict(reviewed)
    out.update({
        "anomaly_id": anomaly_id,
        "reviewed_sim_label_start_s": sim_start,
        "reviewed_sim_label_end_s": sim_end,
        "reviewed_sim_label_time_basis": row["reviewed_sim_label_time_basis"],
        "reviewed_sim_label_interval_semantics": row["reviewed_sim_label_interval_semantics"],
        "reviewed_observable_interval_evidence": str(row["reviewed_observable_interval_evidence"]).strip(),
        "review_include_primary": True,
        "event_key": f"{reviewed['experiment_key']}::{anomaly_id}",
        "group_id": _group_from_key(str(reviewed["experiment_key"])),
        "reviewed_perturbation_family": str(row.get("reviewed_perturbation_family", "")).strip(),
        "mapped_sim_observable_start_real_s": mapped_sim_start,
        "mapped_sim_observable_end_real_s": sim_end + offset,
    })
    return out


def _prepare_cohort(
    registry: pd.DataFrame,
    sensor_archive: Path,
    label_archive: Path,
    uncertainty_archive: Path,
    sim_archive: Path,
    *,
    real_experiment_keys: list[str] | None = None,
) -> dict[str, Any]:
    """Load all real Operation windows, then validate each reviewed target event."""
    if not isinstance(registry, pd.DataFrame) or registry.empty:
        raise ValueError("registry must be a non-empty DataFrame.")

    all_real_keys = (discover_operation_experiment_keys(sensor_archive)
                     if real_experiment_keys is None else sorted(set(real_experiment_keys)))
    if not all_real_keys:
        raise ValueError("The full real Operation experiment cohort is empty.")

    # Validate unique PRIMARY target experiments only. The registry may also contain
    # rejected/unreviewed candidates; those rows must be reported as rejected rather
    # than preventing valid approved rows from being processed. The frozen primary
    # design still allows only one approved event per experiment.
    primary_keys: list[str] = []
    for candidate in registry.to_dict(orient="records"):
        try:
            include = _parse_review_bool(candidate.get("review_include_primary"), field="review_include_primary")
        except Exception:
            include = False
        exp_value = candidate.get("experiment_key")
        if include and isinstance(exp_value, str) and exp_value.strip():
            primary_keys.append(exp_value.strip())
    primary_key_series = pd.Series(primary_keys, dtype="string")
    dup_keys = primary_key_series[primary_key_series.duplicated(keep=False)].unique().tolist()
    if dup_keys:
        raise ValueError(
            "Multiple primary registry rows refer to the same experiment. The current target-level "
            f"test/ΔAP design requires one reviewed event per experiment: {dup_keys[:10]}"
        )

    windows_all, real_audit = build_real_windows_bulk(
        sensor_archive, label_archive, uncertainty_archive, all_real_keys
    )
    if windows_all.empty:
        raise RuntimeError("No real windows were built from the full Operation cohort.")
    windows_all = _attach_window_ids(windows_all, source="real")
    windows_all[GROUP_COL] = windows_all[EXPERIMENT_COL].map(_group_from_key)

    real_audit = real_audit.copy()
    if "status" not in real_audit.columns:
        real_audit["status"] = "UNKNOWN"

    accepted: list[dict[str, Any]] = []
    rejected: list[dict[str, Any]] = []
    event_context: dict[str, dict[str, Any]] = {}
    q_provenance_rows: list[dict[str, Any]] = []
    test_window_rows: list[dict[str, Any]] = []

    audit_index = real_audit.set_index("experiment_key", drop=False) if "experiment_key" in real_audit.columns else None

    for row_idx, row in registry.iterrows():
        raw = row.to_dict()
        try:
            reviewed = validate_registry_row(raw)
            exp_key = reviewed["experiment_key"]
            if exp_key not in all_real_keys:
                raise ValueError(f"Target experiment {exp_key!r} is absent from the discovered full Operation sensor cohort.")
            if audit_index is None or exp_key not in audit_index.index:
                raise ValueError("Target experiment has no real-window audit record.")
            target_audit = audit_index.loc[exp_key]
            if isinstance(target_audit, pd.DataFrame):
                raise ValueError("Duplicate target experiment rows in real-window audit.")
            if target_audit.get("status") != "OK":
                raise ValueError(f"Target real-window construction status={target_audit.get('status')!r}.")

            target_real_all = windows_all.loc[windows_all[EXPERIMENT_COL] == exp_key].copy()
            if target_real_all.empty:
                raise ValueError("Target experiment produced no valid real windows.")
            onset = float(reviewed["reviewed_pre_perturbation_time_s"])
            q_window = (onset - Q_HORIZON_SECONDS, onset)
            target_test = _exclude_q_overlaps(target_real_all, q_window)
            if len(target_test) < 10 or target_test[LABEL_COL].nunique() != 2:
                raise ValueError(
                    f"Target test set after q-window exclusion is ineligible: n={len(target_test)}, "
                    f"classes={sorted(target_test[LABEL_COL].unique().tolist())}."
                )

            train_pool = windows_all.loc[windows_all[EXPERIMENT_COL] != exp_key].copy()
            if len(train_pool) < 20 or train_pool[LABEL_COL].nunique() != 2:
                raise ValueError(
                    f"LOEO real training pool is ineligible: n={len(train_pool)}, "
                    f"classes={sorted(train_pool[LABEL_COL].unique().tolist())}."
                )

            # Load paired simulation by exact member and construct observable-fault windows
            # in native simulator time. Module 1 performs Pa -> mbar conversion internally.
            sim_df = load_simulation_pressure(sim_archive, str(reviewed["sim_member_expected"]))
            fault_df = build_sim_fault_windows(
                sim_time_sec=sim_df["t_sec_sim"].to_numpy(dtype=float),
                sim_pressure_stage_12_pa=sim_df["P_pa"].to_numpy(dtype=float),
                sim_label_start_s=reviewed["reviewed_sim_label_start_s"],
                sim_label_end_s=reviewed["reviewed_sim_label_end_s"],
            )
            if fault_df.empty:
                raise ValueError("No complete 30-s simulated fault windows in reviewed observable interval.")
            fault_df = fault_df.copy()
            fault_df[EXPERIMENT_COL] = exp_key
            fault_df[EVENT_COL] = reviewed["event_key"]
            fault_df["source_sim_member"] = reviewed["sim_member_expected"]
            fault_df = _attach_window_ids(fault_df, source=f"sim:{reviewed['event_key']}")

            # Preflight both real-only and augmented mass constraints before K is frozen.
            assign_experiment_class_mass(train_pool, label_col=LABEL_COL, experiment_col=EXPERIMENT_COL)
            build_augmented_weights(
                train_pool,
                fault_df.iloc[:1].copy(),
                label_col=LABEL_COL,
            )

            # Compute q from the 300-s real pre-perturbation interval.
            real_py23 = load_real_py23(sensor_archive, exp_key)
            real_unc = load_real_uncertainty(uncertainty_archive, exp_key)
            interp = load_interpolation_flags(sensor_archive, uncertainty_archive, exp_key)
            q_result = compute_q_for_reviewed_event(
                real_py23, real_unc, interp, sim_df,
                review_record=reviewed,
                q_window_real_time=q_window,
            )
            if q_result.get("status") != "OK" or not np.isfinite(q_result.get("q_median", np.nan)):
                raise ValueError(f"Primary q computation failed: {q_result.get('status')!r}.")

            accepted_row = {
                EVENT_COL: reviewed["event_key"],
                EXPERIMENT_COL: exp_key,
                GROUP_COL: reviewed["group_id"],
                "anomaly_id": reviewed["anomaly_id"],
                "reviewed_perturbation_family": reviewed["reviewed_perturbation_family"],
                "sim_member_expected": reviewed["sim_member_expected"],
                "n_fault_windows": int(len(fault_df)),
                "n_target_real_windows": int(len(target_real_all)),
                "n_test_windows_after_q_exclusion": int(len(target_test)),
                "n_test_windows_excluded_by_q": int(len(target_real_all) - len(target_test)),
                "n_test_positive": int(target_test[LABEL_COL].sum()),
                "n_test_negative": int((target_test[LABEL_COL] == 0).sum()),
                "q_median": float(q_result["q_median"]),
                "q_p90": float(q_result["q_p90"]),
                "q_n_valid": int(q_result["n_valid"]),
                "q_valid_fraction": float(q_result["valid_fraction_of_real_anchors"]),
                "sim_to_real_offset_s": float(reviewed["reviewed_sim_to_real_time_offset_s"]),
                "mapped_sim_observable_start_real_s": float(reviewed["mapped_sim_observable_start_real_s"]),
                "mapped_sim_observable_end_real_s": float(reviewed["mapped_sim_observable_end_real_s"]),
                "real_window_status": target_audit.get("status"),
                "interpolation_flag_source": interp.attrs.get("source_provenance", {}).get("flag_source"),
            }
            accepted.append(accepted_row)
            event_context[reviewed["event_key"]] = {
                "reviewed": reviewed,
                "fault_pool": fault_df,
                "q": q_result,
                "target_test": target_test,
                "train_pool": train_pool,
                "target_real_all": target_real_all,
            }
            q_provenance_rows.append({EVENT_COL: reviewed["event_key"], **q_result})
            test_window_rows.extend({
                EVENT_COL: reviewed["event_key"],
                "window_id": str(test_row["window_id"]),
                "experiment_key": exp_key,
                "window_start_s": float(test_row[WINDOW_START_COL]),
                "window_end_s": float(test_row[WINDOW_END_COL]),
                "label_anomaly": int(test_row[LABEL_COL]),
            } for _, test_row in target_test.iterrows())
        except Exception as exc:
            rejected.append({
                "registry_row_index": int(row_idx),
                "experiment_key": raw.get("experiment_key", ""),
                "anomaly_id": raw.get("anomaly_id", ""),
                "reason": repr(exc),
            })

    return {
        "real_experiment_keys": all_real_keys,
        "windows_all": windows_all,
        "real_window_audit": real_audit,
        "accepted": pd.DataFrame(accepted),
        "rejected": pd.DataFrame(rejected),
        "event_context": event_context,
        "q_provenance": pd.DataFrame(q_provenance_rows),
        "test_window_manifest": pd.DataFrame(test_window_rows),
        "real_cohort_manifest": pd.DataFrame({EXPERIMENT_COL: all_real_keys}),
    }


def _choose_matched_donor(
    target_event_key: str,
    accepted: pd.DataFrame,
    event_context: dict[str, dict[str, Any]],
    windows_all: pd.DataFrame,
    K: int,
) -> tuple[str | None, str]:
    """Choose one same-chemistry/same-operating-point donor run, deterministically.

    If the target has reviewed perturbation-family metadata, require an exact family
    match. Otherwise, match only on chemical system + operating point and report that
    weaker matching level explicitly.
    """
    target_row = accepted.loc[accepted[EVENT_COL] == target_event_key].iloc[0]
    target_group = str(target_row[GROUP_COL])
    target_family = str(target_row.get("reviewed_perturbation_family", "")).strip()
    candidates = []
    for _, row in accepted.iterrows():
        donor_event = str(row[EVENT_COL])
        if donor_event == target_event_key or str(row[GROUP_COL]) != target_group:
            continue
        donor_family = str(row.get("reviewed_perturbation_family", "")).strip()
        if target_family and donor_family != target_family:
            continue
        donor_exp = str(row[EXPERIMENT_COL])
        donor_real = windows_all.loc[windows_all[EXPERIMENT_COL] == donor_exp]
        donor_pos = donor_real.loc[donor_real[LABEL_COL] == 1]
        donor_sim = event_context[donor_event]["fault_pool"]
        if len(donor_pos) >= K and len(donor_sim) >= K:
            candidates.append((donor_event, donor_exp, donor_family))
    if not candidates:
        return None, "NO_SAME_GROUP_DONOR_WITH_REQUIRED_K"
    candidates = sorted(candidates)
    seed = _stable_seed(target_event_key, 9000)
    chosen = candidates[int(np.random.default_rng(seed).integers(0, len(candidates)))]
    level = "same_group_and_perturbation_family" if target_family else "same_chemical_and_operating_point_only"
    return chosen[0], level


def _feature_decorrelated(sample: pd.DataFrame, seed: int) -> pd.DataFrame:
    """Preserve per-feature marginals while breaking within-row feature pairing."""
    out = sample.copy().reset_index(drop=True)
    rng = np.random.default_rng(seed)
    for col in FEATURES:
        out[col] = rng.permutation(out[col].to_numpy(dtype=float))
    out["control_type"] = "independent_per_feature_permutation"
    return out


def _seed_summary(values: list[float], prefix: str) -> dict[str, Any]:
    if len(values) != N_SEEDS:
        return {
            f"{prefix}_mean": np.nan,
            f"{prefix}_std": np.nan,
            f"{prefix}_median": np.nan,
            f"{prefix}_min": np.nan,
            f"{prefix}_max": np.nan,
            f"{prefix}_n_seeds": int(len(values)),
        }
    arr = np.asarray(values, dtype=float)
    return {
        f"{prefix}_mean": float(arr.mean()),
        f"{prefix}_std": float(arr.std(ddof=1)),
        f"{prefix}_median": float(np.median(arr)),
        f"{prefix}_min": float(arr.min()),
        f"{prefix}_max": float(arr.max()),
        f"{prefix}_n_seeds": int(len(arr)),
    }


def _run_event_arms(
    event_key: str,
    context: dict[str, Any],
    accepted: pd.DataFrame,
    event_context: dict[str, dict[str, Any]],
    windows_all: pd.DataFrame,
    K: int,
) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    """Run primary paired augmentation and three seed-matched control arms."""
    reviewed = context["reviewed"]
    target_exp = reviewed["experiment_key"]
    target_test = context["target_test"].copy()
    train_pool = context["train_pool"].copy()
    fault_pool = context["fault_pool"].copy()
    if target_exp in set(train_pool[EXPERIMENT_COL].astype(str)):
        raise AssertionError("Target experiment leaked into the real training pool.")

    test_ids = tuple(target_test["window_id"].astype(str).tolist())
    if len(test_ids) != len(set(test_ids)):
        raise ValueError("Target test set has duplicate window IDs.")
    q_window = (
        float(reviewed["reviewed_pre_perturbation_time_s"] - Q_HORIZON_SECONDS),
        float(reviewed["reviewed_pre_perturbation_time_s"]),
    )
    if (((target_test[WINDOW_START_COL] < q_window[1])
         & (target_test[WINDOW_END_COL] > q_window[0])).any()):
        raise AssertionError("A q-window-overlapping real test window survived exclusion.")

    donor_event, donor_match_level = _choose_matched_donor(
        event_key, accepted, event_context, windows_all, K
    )
    donor_exp = None
    donor_sim_pool = None
    donor_real_pool = None
    matched_train = None
    donor_status = "UNAVAILABLE"
    if donor_event is not None:
        donor_ctx = event_context[donor_event]
        donor_exp = donor_ctx["reviewed"]["experiment_key"]
        donor_sim_pool = donor_ctx["fault_pool"].copy()
        donor_real_pool = windows_all.loc[
            (windows_all[EXPERIMENT_COL] == donor_exp) & (windows_all[LABEL_COL] == 1)
        ].copy()
        # Crucial matched-control guard: remove the donor's REAL run from training
        # for both wrong-run-simulation and real-donor augmentation comparisons.
        matched_train = windows_all.loc[
            ~windows_all[EXPERIMENT_COL].isin([target_exp, donor_exp])
        ].copy()
        if matched_train.empty or matched_train[LABEL_COL].nunique() != 2:
            donor_status = "UNAVAILABLE_MATCHED_TRAIN_SINGLE_CLASS"
            donor_event = donor_exp = donor_sim_pool = donor_real_pool = matched_train = None
        elif len(donor_real_pool) < K or len(donor_sim_pool) < K:
            donor_status = "UNAVAILABLE_DONOR_HAS_FEWER_THAN_K"
            donor_event = donor_exp = donor_sim_pool = donor_real_pool = matched_train = None
        else:
            # Preflight weight feasibility for the matched control training cohort.
            try:
                assign_experiment_class_mass(matched_train, label_col=LABEL_COL, experiment_col=EXPERIMENT_COL)
                build_augmented_weights(matched_train, donor_real_pool.iloc[:1].copy(), label_col=LABEL_COL)
                donor_status = "AVAILABLE"
            except Exception as exc:
                donor_status = f"UNAVAILABLE_WEIGHT_INFEASIBLE: {exc!r}"
                donor_event = donor_exp = donor_sim_pool = donor_real_pool = matched_train = None

    per_seed: list[dict[str, Any]] = []
    primary_deltas: list[float] = []
    wrong_deltas: list[float] = []
    real_deltas: list[float] = []
    decor_deltas: list[float] = []
    base_aps: list[float] = []
    matched_wrong_base_aps: list[float] = []
    matched_real_base_aps: list[float] = []
    prep_fingerprints: set[str] = set()

    for seed_idx in range(N_SEEDS):
        seed = _stable_seed(event_key, seed_idx)
        rng = np.random.default_rng(seed)

        # Primary paired arm: target event's own simulated fault windows.
        paired_sample = sample_fault_only_K(fault_pool, K, rng, label_col=LABEL_COL)
        paired_result = fit_predict_ap(
            train_pool, target_test, sim_fault=paired_sample,
            random_state=seed, features=FEATURES,
        )
        if paired_result is None:
            raise RuntimeError(f"Primary fit returned None at seed {seed_idx}.")
        primary_deltas.append(float(paired_result["delta_ap"]))
        base_aps.append(float(paired_result["ap_base"]))
        prep_fingerprints.add(str(paired_result["preprocessor_fingerprint"]))
        per_seed.append({
            EVENT_COL: event_key, "seed_index": seed_idx, "seed": seed,
            "arm": "paired_fault_simulation",
            "ap_base": float(paired_result["ap_base"]),
            "ap_aug": float(paired_result["ap_aug"]),
            "delta_ap": float(paired_result["delta_ap"]),
            "n_augmented_windows": int(paired_result["n_sim_fault"]),
            "weight_real_neg_mass": float(paired_result["weight_real_neg_mass"]),
            "weight_real_pos_mass": float(paired_result["weight_real_pos_mass"]),
            "weight_sim_mass": float(paired_result["weight_sim_mass"]),
            "n_train_experiments": int(paired_result["n_train_experiments"]),
            "preprocessor_fingerprint": str(paired_result["preprocessor_fingerprint"]),
            "test_window_hash": hashlib.sha256("|".join(test_ids).encode()).hexdigest(),
            "donor_experiment_key": "",
        })

        # Control 1: same target simulation sample, but independently permute each
        # feature column to destroy row-wise multivariate/time structure.
        decor_sample = _feature_decorrelated(paired_sample, _stable_seed(event_key, seed_idx + 10000))
        decor_result = fit_predict_ap(
            train_pool, target_test, sim_fault=decor_sample,
            random_state=seed, features=FEATURES,
        )
        if decor_result is None:
            raise RuntimeError(f"Feature-decorrelated control failed at seed {seed_idx}.")
        decor_deltas.append(float(decor_result["delta_ap"]))
        per_seed.append({
            EVENT_COL: event_key, "seed_index": seed_idx, "seed": seed,
            "arm": "feature_decorrelated_simulation",
            "ap_base": float(decor_result["ap_base"]),
            "ap_aug": float(decor_result["ap_aug"]),
            "delta_ap": float(decor_result["delta_ap"]),
            "n_augmented_windows": int(decor_result["n_sim_fault"]),
            "weight_real_neg_mass": float(decor_result["weight_real_neg_mass"]),
            "weight_real_pos_mass": float(decor_result["weight_real_pos_mass"]),
            "weight_sim_mass": float(decor_result["weight_sim_mass"]),
            "n_train_experiments": int(decor_result["n_train_experiments"]),
            "preprocessor_fingerprint": str(decor_result["preprocessor_fingerprint"]),
            "test_window_hash": hashlib.sha256("|".join(test_ids).encode()).hexdigest(),
            "donor_experiment_key": "",
        })

        # Controls 2 and 3 use the same matched donor run and remove that donor's
        # real trace from training. Its simulation and real-positive windows are
        # sampled with the same seed and fixed K.
        if donor_status == "AVAILABLE":
            donor_rng = np.random.default_rng(_stable_seed(event_key, seed_idx + 20000))
            wrong_sample = sample_fault_only_K(donor_sim_pool, K, donor_rng, label_col=LABEL_COL)
            wrong_result = fit_predict_ap(
                matched_train, target_test, sim_fault=wrong_sample,
                random_state=seed, features=FEATURES,
            )
            real_sample = sample_fault_only_K(donor_real_pool, K, donor_rng, label_col=LABEL_COL)
            real_result = fit_predict_ap(
                matched_train, target_test, sim_fault=real_sample,
                random_state=seed, features=FEATURES,
            )
            if wrong_result is None or real_result is None:
                raise RuntimeError(f"Matched donor control returned None at seed {seed_idx}.")
            wrong_deltas.append(float(wrong_result["delta_ap"]))
            real_deltas.append(float(real_result["delta_ap"]))
            matched_wrong_base_aps.append(float(wrong_result["ap_base"]))
            matched_real_base_aps.append(float(real_result["ap_base"]))
            for arm, result in (("wrong_run_simulation", wrong_result), ("real_donor_positive", real_result)):
                source_key = donor_exp
                per_seed.append({
                    EVENT_COL: event_key, "seed_index": seed_idx, "seed": seed,
                    "arm": arm,
                    "ap_base": float(result["ap_base"]),
                    "ap_aug": float(result["ap_aug"]),
                    "delta_ap": float(result["delta_ap"]),
                    "n_augmented_windows": int(result["n_sim_fault"]),
                    "weight_real_neg_mass": float(result["weight_real_neg_mass"]),
                    "weight_real_pos_mass": float(result["weight_real_pos_mass"]),
                    "weight_sim_mass": float(result["weight_sim_mass"]),
                    "n_train_experiments": int(result["n_train_experiments"]),
                    "preprocessor_fingerprint": str(result["preprocessor_fingerprint"]),
                    "test_window_hash": hashlib.sha256("|".join(test_ids).encode()).hexdigest(),
                    "donor_experiment_key": source_key,
                })

    if len(primary_deltas) != N_SEEDS or len(decor_deltas) != N_SEEDS:
        raise AssertionError("Primary and feature-decorrelated arms must complete all 20 seeds.")
    if len(prep_fingerprints) != 1:
        raise AssertionError("Real-only preprocessing fingerprint changed across paired seeds.")
    if donor_status == "AVAILABLE" and (len(wrong_deltas) != N_SEEDS or len(real_deltas) != N_SEEDS):
        raise AssertionError("Matched donor controls must complete all 20 seeds; partial means are prohibited.")

    row = {
        EVENT_COL: event_key,
        EXPERIMENT_COL: target_exp,
        GROUP_COL: reviewed["group_id"],
        "anomaly_id": reviewed["anomaly_id"],
        "q_median": float(context["q"]["q_median"]),
        "q_p90": float(context["q"]["q_p90"]),
        "q_n_valid": int(context["q"]["n_valid"]),
        "frozen_K": int(K),
        "n_seeds_valid": int(len(primary_deltas)),
        "n_target_real_windows": int(len(context["target_real_all"])),
        "n_test_windows": int(len(target_test)),
        "n_test_windows_excluded_by_q": int(len(context["target_real_all"]) - len(target_test)),
        "n_test_positive": int(target_test[LABEL_COL].sum()),
        "n_test_negative": int((target_test[LABEL_COL] == 0).sum()),
        "test_prevalence": float(target_test[LABEL_COL].mean()),
        "test_window_hash": hashlib.sha256("|".join(test_ids).encode()).hexdigest(),
        "n_train_experiments_primary": int(train_pool[EXPERIMENT_COL].nunique()),
        "train_experiment_keys_json": json.dumps(sorted(train_pool[EXPERIMENT_COL].astype(str).unique().tolist())),
        "train_group_ids_json": json.dumps(sorted(train_pool[GROUP_COL].astype(str).unique().tolist())),
        "n_train_experiments_matched_controls": int(matched_train[EXPERIMENT_COL].nunique()) if matched_train is not None else np.nan,
        "matched_control_train_experiment_keys_json": json.dumps(sorted(matched_train[EXPERIMENT_COL].astype(str).unique().tolist())) if matched_train is not None else "",
        "matched_control_train_group_ids_json": json.dumps(sorted(matched_train[GROUP_COL].astype(str).unique().tolist())) if matched_train is not None else "",
        "primary_preprocessor_fingerprint": next(iter(prep_fingerprints)),
        "matched_donor_event_key": donor_event or "",
        "matched_donor_experiment_key": donor_exp or "",
        "donor_matching_level": donor_match_level,
        "donor_control_status": donor_status,
    }
    row.update(_seed_summary(primary_deltas, "delta_paired"))
    row.update(_seed_summary(base_aps, "ap_base"))
    row.update(_seed_summary(decor_deltas, "delta_feature_decorrelated"))
    if donor_status == "AVAILABLE":
        row.update(_seed_summary(wrong_deltas, "delta_wrong_run"))
        row.update(_seed_summary(real_deltas, "delta_real_donor"))
        row.update(_seed_summary(matched_wrong_base_aps, "ap_wrong_matched_base"))
        row.update(_seed_summary(matched_real_base_aps, "ap_real_matched_base"))
    else:
        row.update(_seed_summary([], "delta_wrong_run"))
        row.update(_seed_summary([], "delta_real_donor"))
        row.update(_seed_summary([], "ap_wrong_matched_base"))
        row.update(_seed_summary([], "ap_real_matched_base"))
    return row, per_seed


def run_orchestrator(
    registry: pd.DataFrame,
    sensor_archive: Path,
    label_archive: Path,
    uncertainty_archive: Path,
    sim_archive: Path,
    *,
    real_experiment_keys: list[str] | None = None,
) -> dict[str, Any]:
    """Run the frozen v5.2 primary cohort using exactly 20 seeds and fixed K.

    If real_experiment_keys is omitted, all Operation sensor CSVs are discovered
    automatically. This is important: the training pool must not be restricted to
    paired/approved simulation targets.
    """
    prepared = _prepare_cohort(
        registry, sensor_archive, label_archive, uncertainty_archive, sim_archive,
        real_experiment_keys=real_experiment_keys,
    )
    accepted = prepared["accepted"]
    rejected = prepared["rejected"]
    base_result = {
        "reviewed_registry_input": registry.copy(),
        "real_window_audit": prepared["real_window_audit"],
        "real_cohort_manifest": prepared["real_cohort_manifest"],
        "q_provenance": prepared["q_provenance"],
        "test_window_manifest": prepared["test_window_manifest"],
        "accepted_registry": accepted,
        "rejected_registry": rejected,
        "n_real_experiments_discovered": int(len(prepared["real_experiment_keys"])),
        "n_real_windows": int(len(prepared["windows_all"])),
    }
    if accepted.empty:
        return {**base_result, "status": "NO_ACCEPTED_EVENTS", "frozen_K": None,
                "n_accepted": 0, "n_completed": 0,
                "per_event": pd.DataFrame(), "per_seed": pd.DataFrame(), "per_group": pd.DataFrame(),
                "run_errors": pd.DataFrame()}

    # K is frozen from the entire pre-outcome eligible target cohort.
    min_fault_windows = int(accepted["n_fault_windows"].min())
    if min_fault_windows < K_MIN:
        return {**base_result,
                "status": f"INSUFFICIENT_FAULT_WINDOWS (min={min_fault_windows} < K_MIN={K_MIN})",
                "frozen_K": None, "min_fault_windows": min_fault_windows,
                "n_accepted": int(len(accepted)), "n_completed": 0,
                "per_event": pd.DataFrame(), "per_seed": pd.DataFrame(), "per_group": pd.DataFrame(),
                "run_errors": pd.DataFrame()}
    K = int(min(K_MAX, min_fault_windows))

    if len(accepted) < MIN_ACCEPTED_EVENTS:
        return {**base_result,
                "status": f"INSUFFICIENT_ACCEPTED_EVENTS ({len(accepted)} < {MIN_ACCEPTED_EVENTS})",
                "frozen_K": K, "min_fault_windows": min_fault_windows,
                "n_accepted": int(len(accepted)), "n_completed": 0,
                "per_event": pd.DataFrame(), "per_seed": pd.DataFrame(), "per_group": pd.DataFrame(),
                "run_errors": pd.DataFrame()}

    per_event_rows: list[dict[str, Any]] = []
    per_seed_rows: list[dict[str, Any]] = []
    run_errors: list[dict[str, Any]] = []
    for event_key in accepted[EVENT_COL].astype(str).tolist():
        try:
            row, seed_rows = _run_event_arms(
                event_key, prepared["event_context"][event_key], accepted,
                prepared["event_context"], prepared["windows_all"], K,
            )
            per_event_rows.append(row)
            per_seed_rows.extend(seed_rows)
        except Exception as exc:
            run_errors.append({EVENT_COL: event_key, "error": repr(exc)})

    per_event = pd.DataFrame(per_event_rows)
    per_seed = pd.DataFrame(per_seed_rows)
    if not per_event.empty:
        per_group = per_event.groupby(GROUP_COL, dropna=False).agg(
            n_events=(EVENT_COL, "nunique"),
            median_q=("q_median", "median"),
            median_delta_paired=("delta_paired_mean", "median"),
            median_delta_wrong_run=("delta_wrong_run_mean", "median"),
            median_delta_real_donor=("delta_real_donor_mean", "median"),
            median_delta_feature_decorrelated=("delta_feature_decorrelated_mean", "median"),
        ).reset_index()
    else:
        per_group = pd.DataFrame()

    if per_event.empty:
        status = "NO_EVENTS_COMPLETED"
    elif len(per_event) != len(accepted) or run_errors:
        status = "PARTIAL_FAILURE_REVIEW_REQUIRED"
    elif (per_event["donor_control_status"] != "AVAILABLE").any():
        status = "OK_PRIMARY_WITH_CONTROL_GAPS"
    else:
        status = "OK"
    return {
        **base_result,
        "status": status,
        "frozen_K": K,
        "min_fault_windows": min_fault_windows,
        "n_accepted": int(len(accepted)),
        "n_completed": int(len(per_event)),
        "n_errors_during_run": int(len(run_errors)),
        "n_operating_point_groups_completed": int(per_event[GROUP_COL].nunique()) if not per_event.empty else 0,
        "per_event": per_event,
        "per_seed": per_seed,
        "per_group": per_group,
        "run_errors": pd.DataFrame(run_errors),
    }


def save_orchestrator_results(result: Mapping[str, Any], output_dir: Path) -> Path:
    """Save tabular outputs and a manifest; does not save raw source time series."""
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    table_keys = (
        "reviewed_registry_input", "real_window_audit", "real_cohort_manifest", "q_provenance", "test_window_manifest", "accepted_registry", "rejected_registry",
        "per_event", "per_seed", "per_group", "run_errors",
    )
    for key in table_keys:
        value = result.get(key)
        if isinstance(value, pd.DataFrame):
            value.to_csv(output_dir / f"{key}.csv", index=False)
    manifest = {
        "project": "SimTrust-Pre",
        "software_version": "v5.2-module5-reviewed",
        "status": result.get("status"),
        "frozen_K": result.get("frozen_K"),
        "n_accepted": result.get("n_accepted"),
        "n_completed": result.get("n_completed"),
        "n_real_experiments_discovered": result.get("n_real_experiments_discovered"),
        "n_real_windows": result.get("n_real_windows"),
        "n_operating_point_groups_completed": result.get("n_operating_point_groups_completed"),
        "seed_count_primary": N_SEEDS,
        "primary_estimand": "fault_segment_utility",
        "primary_q_horizon_seconds": Q_HORIZON_SECONDS,
        "note": "Software output only; empirical inference requires separate cluster-aware statistics and review of all audit tables.",
    }
    manifest_path = output_dir / "run_manifest.json"
    manifest_path.write_text(json.dumps(manifest, indent=2, ensure_ascii=False, default=str), encoding="utf-8")
    return output_dir


# ============================ Synthetic fixtures ============================
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


def _build_synthetic_archives(tmp: Path, *, n_paired: int = 6):
    sensor = tmp / "sensors.zip"
    labels = tmp / "labels.zip"
    unc = tmp / "uncertainties.zip"
    sim = tmp / "simulations.zip"
    n = 900
    times = [_to_hhmmss(i) for i in range(n)]
    registry_rows: list[dict[str, Any]] = []
    keys: list[str] = []

    for e in range(n_paired + 1):
        # Two paired target events per chemical/op-point group; final run is an
        # unpaired normal-only real experiment that must still enter training.
        group_idx = min(e // 2, 2)
        chem = ["ChemA", "ChemB", "ChemC"][group_idx]
        op = "OP1"
        exp = f"Exp{e:03d}"
        ek = f"Operation/{chem}/{op}/{exp}"
        keys.append(ek)
        base_py = 650.0 + 0.05 * np.arange(n) + 0.5 * e
        lab = np.zeros(n, dtype=int)
        if e < n_paired:
            lab[495:500] = 1   # blind phase, excluded
            lab[500:700] = 2   # observable anomaly
            lab[700:] = 3      # recovery remains positive
        _write_zip(sensor, f"{SENSOR_ROOT}/{ek}.csv",
                   pd.DataFrame({"Time": times, "PY23": base_py}))
        _write_zip(labels, f"00_Batch_Distillation_Plant_M-202210_Timeseries_Label_Anomaly_Metadata/{ek}.csv",
                   pd.DataFrame({"Time": times, "Label (anomaly)": lab}))
        _write_zip(unc, f"03_Batch_Distillation_Plant_M-202210_Timeseries_Sensor_Uncertainties/{ek}.csv",
                   pd.DataFrame({"Time": times, "±ΔPY23": np.full(n, 0.5),
                                 "Data_interpolated": np.zeros(n, dtype=int)}))
        if e < n_paired:
            sim_member = f"Operation/{chem}/{op}/{exp}.csv"
            _write_zip(sim, sim_member,
                       pd.DataFrame({"time": times,
                                     "pressure stage 12 / Pa": base_py * 100.0}), sep=";")
            registry_rows.append({
                "review_include_primary": True,
                "review_status": "APPROVED_SINGLE_EVENT",
                "experiment_key": ek,
                "anomaly_id": f"A{e:03d}",
                "sim_member_expected": sim_member,
                "reviewed_pre_perturbation_time": "00:08:15",  # real t=495s
                "reviewed_pre_perturbation_time_basis": "REAL_NATIVE_TIME",
                "reviewed_sim_label_start_time": "00:08:20",  # sim t=500s
                "reviewed_sim_label_end_time": "00:14:00",    # sim t=840s
                "reviewed_sim_label_time_basis": SIM_LABEL_TIME_BASIS,
                "reviewed_sim_label_interval_semantics": SIM_INTERVAL_SEMANTICS,
                "reviewed_observable_interval_evidence": "Synthetic fixture: label codes 2/3 span 500-900s; reviewed training interval 500-840s.",
                "reviewed_sim_to_real_time_offset_s": 0.0,
                "reviewed_primary_real_channel": "PY23",
                "reviewed_primary_sim_channel": "pressure stage 12 / Pa",
                "reviewed_primary_uncertainty_column": "±ΔPY23",
                "reviewed_primary_real_unit": "mbar",
                "reviewed_primary_sim_unit": "Pa",
                "reviewed_primary_uncertainty_unit": "mbar",
                "reviewed_uncertainty_semantics_evidence": "Synthetic fixture: defined tolerance 0.5 mbar.",
                "reviewed_interpolation_flag_source": "uncertainty",
                "reviewed_time_mapping_evidence": "Synthetic fixture: identical elapsed clock, offset=0.",
                "reviewed_mapping_evidence": "Synthetic fixture: real PY23 equals stage-12 pressure / 100.",
                "reviewed_perturbation_family": "synthetic_step_fault",
            })

    return sensor, labels, unc, sim, pd.DataFrame(registry_rows), keys


def run_smoke_tests() -> None:
    import tempfile

    print("Running reviewed synthetic smoke tests for SimTrust-Pre v5.2 Module 5...")
    with tempfile.TemporaryDirectory() as tmpdir:
        tmp = Path(tmpdir)
        sensor, labels, unc, sim, registry, all_keys = _build_synthetic_archives(tmp)

        # 1. End-to-end cohort, q, K, ΔAP and controls.
        result = run_orchestrator(registry, sensor, labels, unc, sim)
        assert result["status"] == "OK", (result.get("status"), result.get("rejected_registry"), result.get("run_errors"))
        assert result["n_accepted"] == 6 and result["n_completed"] == 6
        assert result["frozen_K"] == 11
        assert len(result["q_provenance"]) == 6
        assert len(result["reviewed_registry_input"]) == 6
        assert len(result["test_window_manifest"]) == int(result["per_event"]["n_test_windows"].sum())
        print(f"  PASS 1: end-to-end OK; accepted={result['n_accepted']}, completed={result['n_completed']}, K={result['frozen_K']}")

        # 2. Full Operation cohort discovery: unpaired 7th experiment is included.
        assert result["n_real_experiments_discovered"] == 7
        assert result["n_real_windows"] > 0
        first = result["per_event"].iloc[0]
        assert first["n_train_experiments_primary"] == 6  # seven total minus target
        print("  PASS 2: all Operation real runs included in LOEO training; unpaired real run retained")

        # 3. K fixed once across the entire eligible cohort.
        assert (result["per_event"]["frozen_K"] == 11).all()
        print("  PASS 3: one cohort-wide K frozen before outcome fitting")

        # 4. Exactly 20 seeds in every required arm.
        counts = result["per_seed"].groupby([EVENT_COL, "arm"]).size()
        assert (counts == 20).all()
        print("  PASS 4: 20 seeds completed for each event/arm")

        # 5. All arms use the same test-window hash within an event.
        arm_hash_counts = result["per_seed"].groupby(EVENT_COL)["test_window_hash"].nunique()
        assert (arm_hash_counts == 1).all()
        print("  PASS 5: paired and control arms use identical held-out test rows")

        # 6. q windows are absent from every target test set (inspect saved row manifest).
        q_lookup = result["q_provenance"].set_index(EVENT_COL)
        for event_key, test_rows in result["test_window_manifest"].groupby(EVENT_COL):
            q0 = float(q_lookup.loc[event_key, "q_window_real_start"])
            q1 = float(q_lookup.loc[event_key, "q_window_real_end"])
            assert not (((test_rows[WINDOW_START_COL] < q1)
                         & (test_rows[WINDOW_END_COL] > q0)).any())
        assert (result["per_event"]["n_test_windows"] > 0).all()
        assert (result["per_event"]["test_window_hash"].str.len() == 64).all()
        print("  PASS 6: q-window-overlapping target windows excluded (verified row-by-row)")

        # 7. Target experiment excluded from its own training pool.
        for _, row in result["per_event"].iterrows():
            assert row["n_train_experiments_primary"] == 6
        print("  PASS 7: target run excluded from real training in every LOEO fold")

        # 8. Wrong-run source provenance remains the donor, and donor run excluded from matched train.
        for _, row in result["per_event"].iterrows():
            assert row["donor_control_status"] == "AVAILABLE"
            assert row["matched_donor_experiment_key"] != row[EXPERIMENT_COL]
            assert row["n_train_experiments_matched_controls"] == 5        wrong_rows = result["per_seed"].loc[result["per_seed"]["arm"] == "wrong_run_simulation"]
        assert (wrong_rows["donor_experiment_key"] != "").all()
        print("  PASS 8: wrong-run donor provenance retained; donor's real run removed from matched control training")

        # 9. All three control arms are emitted separately and per-event summaries exist.
        expected_arms = {"paired_fault_simulation", "wrong_run_simulation",
                         "real_donor_positive", "feature_decorrelated_simulation"}
        assert set(result["per_seed"]["arm"].unique()) == expected_arms
        assert result["per_event"]["delta_wrong_run_n_seeds"].eq(20).all()
        assert result["per_event"]["delta_real_donor_n_seeds"].eq(20).all()
        assert result["per_event"]["delta_feature_decorrelated_n_seeds"].eq(20).all()
        print("  PASS 9: all matched controls use complete 20-seed summaries")

        # 10. Group aggregation is explicit; three groups from six events.
        assert result["per_group"][GROUP_COL].nunique() == 3
        assert result["n_operating_point_groups_completed"] == 3
        print("  PASS 10: group-level descriptive aggregation completed (3 operating-point groups)")

        # 11. Incomplete registry row is rejected, not silently accepted.
        bad = registry.copy()
        bad.loc[0, "reviewed_observable_interval_evidence"] = ""
        bad_res = run_orchestrator(bad, sensor, labels, unc, sim)
        assert len(bad_res["rejected_registry"]) >= 1
        assert bad_res["status"].startswith("INSUFFICIENT_ACCEPTED_EVENTS")
        print("  PASS 11: incomplete evidence row rejected")

        # 12. Insufficient cohort does not run any model.
        small = run_orchestrator(registry.iloc[:5].copy(), sensor, labels, unc, sim)
        assert small["status"].startswith("INSUFFICIENT_ACCEPTED_EVENTS")
        assert small["per_seed"].empty
        print("  PASS 12: fewer than six accepted events -> no model fitting")

        # 13. K below 10 blocks the run before any model is fitted.
        short = registry.copy()
        short.loc[0, "reviewed_sim_label_end_time"] = "00:08:50"  # 30 seconds after 500s start
        short_res = run_orchestrator(short, sensor, labels, unc, sim)
        assert "INSUFFICIENT_FAULT_WINDOWS" in short_res["status"]
        assert short_res["per_seed"].empty
        print("  PASS 13: insufficient fault windows -> K gate blocks models")

        # 14. Duplicate primary event per experiment is a hard registry error.
        duplicate = pd.concat([registry, registry.iloc[[0]]], ignore_index=True)
        try:
            run_orchestrator(duplicate, sensor, labels, unc, sim)
        except ValueError as exc:
            assert "same experiment" in str(exc)
        else:
            raise AssertionError("Duplicate primary event for one experiment was not rejected.")
        print("  PASS 14: duplicate primary event per experiment rejected")

        # 15. Wrong native simulator-time basis is rejected.
        bad_basis = registry.copy()
        bad_basis.loc[0, "reviewed_sim_label_time_basis"] = "REAL_NATIVE_TIME"
        basis_res = run_orchestrator(bad_basis, sensor, labels, unc, sim)
        assert len(basis_res["rejected_registry"]) >= 1
        print("  PASS 15: incorrect simulator interval time basis rejected")

        # 16. Interval semantics cannot be confused with perturbation interval.
        bad_sem = registry.copy()
        bad_sem.loc[0, "reviewed_sim_label_interval_semantics"] = "PERTURBATION_INTERVAL"
        sem_res = run_orchestrator(bad_sem, sensor, labels, unc, sim)
        assert len(sem_res["rejected_registry"]) >= 1
        print("  PASS 16: perturbation interval cannot silently substitute for observable fault interval")

        # 17. Mapped sim observable interval must not start before real onset.
        bad_offset = registry.copy()
        bad_offset.loc[0, "reviewed_sim_to_real_time_offset_s"] = -20.0
        offset_res = run_orchestrator(bad_offset, sensor, labels, unc, sim)
        assert len(offset_res["rejected_registry"]) >= 1
        print("  PASS 17: inconsistent offset/fault onset rejected")

        # 18. Even a sub-second mapped fault onset before real onset is not allowed:
        # q is defined on the half-open pre-onset interval and must remain separate.
        early_by_half_second = registry.copy()
        early_by_half_second.loc[0, "reviewed_sim_to_real_time_offset_s"] = -5.5
        early_res = run_orchestrator(early_by_half_second, sensor, labels, unc, sim)
        assert len(early_res["rejected_registry"]) >= 1
        print("  PASS 18: mapped fault onset cannot encroach on q window, even by a fraction of a second")

        # 19. Result saving produces auditable CSVs and a manifest.
        out_dir = tmp / "saved_results"
        save_orchestrator_results(result, out_dir)
        assert (out_dir / "per_event.csv").is_file()
        assert (out_dir / "per_seed.csv").is_file()
        assert (out_dir / "q_provenance.csv").is_file()
        assert (out_dir / "test_window_manifest.csv").is_file()
        assert (out_dir / "reviewed_registry_input.csv").is_file()
        assert (out_dir / "run_manifest.json").is_file()
        print("  PASS 19: audit tables and run manifest saved")

        # 20. Unreviewed/false candidate rows with blank fields are recorded as rejected
        # and do not block approved primary rows.
        candidate_row = {column: "" for column in registry.columns}
        candidate_row["review_include_primary"] = False
        candidate_row["review_status"] = "NOT_REVIEWED"
        registry_with_candidate = pd.concat([registry, pd.DataFrame([candidate_row])], ignore_index=True)
        candidate_res = run_orchestrator(registry_with_candidate, sensor, labels, unc, sim)
        assert candidate_res["status"] == "OK"
        assert len(candidate_res["rejected_registry"]) >= 1
        assert candidate_res["n_completed"] == 6
        print("  PASS 20: blank/unreviewed candidate row is rejected without blocking valid primary events")

    print("\nAll reviewed Module 5 smoke tests passed (synthetic ZIP fixtures only).")
    print("No Zenodo experiment was read and no empirical claim is established.")


if __name__ == "__main__":
    run_smoke_tests()