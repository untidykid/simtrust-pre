"""SimTrust-Pre v5.2 — Module 2 (reviewed implementation).

Paired fault-only utility estimation with train-only preprocessing.
Uses Module 1.1 for fixed-mass sample weights and fault-only sampling.
All included smoke tests use synthetic data; they are not empirical results.
"""
from __future__ import annotations

import hashlib
from typing import Any

import numpy as np
import pandas as pd
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import average_precision_score
from sklearn.preprocessing import StandardScaler

from SimTrust_Pre_v5_2_Module1_reviewed import (
    assign_experiment_class_mass,
    build_augmented_weights,
    sample_fault_only_K,
    _strict_binary_labels,
)

# Frozen Phase 0 / Module 1.1 constants.
FEATURES = (
    "PY23_mean_mbar",
    "PY23_std_mbar",
    "PY23_delta_mbar",
)
LABEL_COL = "label_anomaly"
EXPERIMENT_COL = "experiment_key"
WINDOW_START_COL = "window_start_s"
WINDOW_END_COL = "window_end_s"
Q_HORIZON_SECONDS = 300.0
N_SEEDS_PER_TARGET = 20
LOGREG_C = 1.0
LOGREG_MAX_ITER = 3000
SEED_BASE = 20261030
MIN_TRAIN_ROWS = 20
MIN_TEST_ROWS = 10


def _stable_seed(target_key: str, seed_idx: int) -> int:
    """Deterministic seed independent of Python's randomized hash()."""
    if seed_idx < 0:
        raise ValueError("seed_idx must be non-negative.")
    digest = hashlib.sha256(f"{target_key}|{seed_idx}".encode("utf-8")).hexdigest()
    return SEED_BASE + int(digest[:8], 16) % (2**31 - 1)


def _validate_frame(
    df: pd.DataFrame,
    *,
    required_features: tuple[str, ...],
    label_col: str,
    experiment_col: str | None = None,
    require_window_bounds: bool = False,
    frame_name: str = "dataframe",
) -> pd.DataFrame:
    """Validate schema/labels while preserving feature NaNs for train-only imputation."""
    if not isinstance(df, pd.DataFrame):
        raise TypeError(f"{frame_name} must be a pandas DataFrame.")
    if df.empty:
        raise ValueError(f"{frame_name} is empty.")
    required = set(required_features) | {label_col}
    if experiment_col is not None:
        required.add(experiment_col)
    if require_window_bounds:
        required.update({WINDOW_START_COL, WINDOW_END_COL})
    missing = sorted(required - set(df.columns))
    if missing:
        raise KeyError(f"{frame_name} is missing required columns: {missing}")

    out = df.copy()
    # Missing/non-binary labels are never silently converted to normal.
    y = _strict_binary_labels(out, label_col)
    out[label_col] = y

    for col in required_features:
        raw = out[col]
        converted = pd.to_numeric(raw, errors="coerce").astype(float)
        nonnumeric = raw.notna().to_numpy() & converted.isna().to_numpy()
        if nonnumeric.any():
            examples = raw.iloc[np.flatnonzero(nonnumeric)[:5]].astype(str).tolist()
            raise ValueError(
                f"{frame_name}.{col} contains non-numeric non-missing values: {examples}"
            )
        if np.isinf(converted.to_numpy(dtype=float)).any():
            raise ValueError(f"{frame_name}.{col} contains +/- infinity; clean upstream.")
        out[col] = converted

    if experiment_col is not None:
        exp = out[experiment_col]
        if exp.isna().any() or exp.astype(str).str.strip().eq("").any():
            raise ValueError(f"{frame_name} contains missing/empty experiment keys.")
        out[experiment_col] = exp.astype(str)

    if require_window_bounds:
        starts = pd.to_numeric(out[WINDOW_START_COL], errors="coerce").to_numpy(float)
        ends = pd.to_numeric(out[WINDOW_END_COL], errors="coerce").to_numpy(float)
        if not np.isfinite(starts).all() or not np.isfinite(ends).all():
            raise ValueError(f"{frame_name} has non-finite window bounds.")
        if np.any(ends <= starts):
            raise ValueError(f"{frame_name} has window_end_s <= window_start_s.")
        out[WINDOW_START_COL] = starts
        out[WINDOW_END_COL] = ends

        # These are fixed 30-s non-overlapping windows in the frozen protocol.
        # Reject duplicated/overlapping windows within an experiment so repeated or
        # highly dependent rows cannot silently inflate the evaluation cohort.
        if experiment_col is not None:
            for exp_key, group in out.groupby(experiment_col, sort=False):
                ordered = group.sort_values(WINDOW_START_COL)
                starts_g = ordered[WINDOW_START_COL].to_numpy(float)
                ends_g = ordered[WINDOW_END_COL].to_numpy(float)
                if len(ordered) > 1 and np.any(starts_g[1:] < ends_g[:-1] - 1e-9):
                    raise ValueError(
                        f"{frame_name} contains overlapping windows within experiment {exp_key!r}."
                    )
            if "window_id" not in out.columns:
                ids = []
                for exp_key, start, end in zip(
                    out[experiment_col].astype(str), starts, ends
                ):
                    raw_id = f"{exp_key}|{start:.9f}|{end:.9f}"
                    ids.append(hashlib.sha256(raw_id.encode("utf-8")).hexdigest()[:20])
                out["window_id"] = ids
            if out["window_id"].isna().any() or out["window_id"].astype(str).duplicated().any():
                raise ValueError(f"{frame_name} has missing or duplicate window_id values.")

    return out


def _exclude_q_window_overlaps(
    df: pd.DataFrame,
    q_window: tuple[float, float],
) -> pd.DataFrame:
    """Exclude every half-open window intersecting the primary q interval."""
    if q_window is None:
        raise ValueError("q_window is required; primary evaluation may not bypass q-window exclusion.")
    if not isinstance(q_window, (tuple, list)) or len(q_window) != 2:
        raise ValueError("q_window must be a (start_s, end_s) pair.")
    q_start, q_end = map(float, q_window)
    if not (np.isfinite(q_start) and np.isfinite(q_end) and q_end > q_start):
        raise ValueError(f"Invalid q_window: {q_window}")
    if df.empty:
        return df.copy()
    if not {WINDOW_START_COL, WINDOW_END_COL}.issubset(df.columns):
        raise KeyError("Evaluation windows must include window_start_s and window_end_s.")
    overlap = (df[WINDOW_START_COL] < q_end) & (df[WINDOW_END_COL] > q_start)
    return df.loc[~overlap].copy()


def _fit_train_only_preprocessor(
    real_train: pd.DataFrame,
    *,
    features: tuple[str, ...],
) -> tuple[SimpleImputer, StandardScaler, np.ndarray]:
    """Fit median imputer and scaler on real training features only."""
    x_train_raw = real_train.loc[:, list(features)].to_numpy(dtype=float)
    # Do not quietly drop a feature that is completely unavailable in training.
    all_missing = [features[i] for i in range(x_train_raw.shape[1]) if np.isnan(x_train_raw[:, i]).all()]
    if all_missing:
        raise ValueError(f"Features entirely missing in real training data: {all_missing}")

    imputer = SimpleImputer(strategy="median")
    x_train_imp = imputer.fit_transform(x_train_raw)
    scaler = StandardScaler()
    x_train = scaler.fit_transform(x_train_imp)
    if not np.isfinite(x_train).all():
        raise ValueError("Train-only preprocessing produced non-finite training features.")
    return imputer, scaler, x_train


def _preprocessor_fingerprint(
    imputer: SimpleImputer,
    scaler: StandardScaler,
    features: tuple[str, ...],
) -> str:
    """Compact reproducibility fingerprint of the train-fitted transforms."""
    digest = hashlib.sha256()
    digest.update("|".join(features).encode("utf-8"))
    for arr in (imputer.statistics_, scaler.mean_, scaler.scale_):
        digest.update(np.asarray(arr, dtype="<f8").tobytes())
    return digest.hexdigest()


def _new_logistic_regression() -> LogisticRegression:
    """Create the frozen L2 model; explicit sample_weight handles class masses."""
    # L2 is scikit-learn's default penalty; omit the deprecated `penalty`
    # argument for forward compatibility while keeping the frozen C and solver.
    model = LogisticRegression(
        C=LOGREG_C,
        solver="lbfgs",
        class_weight=None,
        max_iter=LOGREG_MAX_ITER,
    )
    if model.get_params()["class_weight"] is not None:
        raise AssertionError("class_weight must remain None when using explicit sample weights.")
    return model


def fit_predict_ap(
    real_train: pd.DataFrame,
    test_windows: pd.DataFrame,
    *,
    sim_fault: pd.DataFrame | None,
    random_state: int,
    features: tuple[str, ...] = FEATURES,
) -> dict[str, Any] | None:
    """Fit paired real-only and fault-augmented arms on the exact same real test set.

    - Feature NaNs are median-imputed; imputer/scaler fit only on real_train.
    - Labels must be complete and binary; they are never imputed or recoded.
    - class_weight=None; Module 1.1 sample weights define class/source masses.
    - If sim_fault is absent/empty, delta_ap is exactly 0.0 by definition.
    """
    if not features:
        raise ValueError("At least one feature is required.")
    train = _validate_frame(
        real_train,
        required_features=features,
        label_col=LABEL_COL,
        experiment_col=EXPERIMENT_COL,
        frame_name="real_train",
    )
    test = _validate_frame(
        test_windows,
        required_features=features,
        label_col=LABEL_COL,
        require_window_bounds=True,
        frame_name="test_windows",
    )
    if len(train) < MIN_TRAIN_ROWS or len(test) < MIN_TEST_ROWS:
        return None

    y_train = train[LABEL_COL].to_numpy(dtype=np.int8)
    y_test = test[LABEL_COL].to_numpy(dtype=np.int8)
    if np.unique(y_train).size != 2 or np.unique(y_test).size != 2:
        return None

    imputer, scaler, x_train = _fit_train_only_preprocessor(train, features=features)
    x_test = scaler.transform(imputer.transform(test.loc[:, list(features)].to_numpy(dtype=float)))
    if not np.isfinite(x_test).all():
        raise ValueError("Test preprocessing produced non-finite features.")
    prep_fingerprint = _preprocessor_fingerprint(imputer, scaler, features)

    # Baseline: fixed 0.50 / 0.50 real class mass, with equal mass per experiment.
    w_base = assign_experiment_class_mass(train, label_col=LABEL_COL, experiment_col=EXPERIMENT_COL)
    if len(w_base) != len(train) or not np.isclose(w_base.sum(), 1.0, atol=1e-9):
        raise AssertionError("Module 1.1 returned invalid baseline sample weights.")
    model_base = _new_logistic_regression().fit(
        x_train, y_train, sample_weight=w_base
    )
    ap_base = float(average_precision_score(y_test, model_base.predict_proba(x_test)[:, 1]))

    result: dict[str, Any] = {
        "ap_base": ap_base,
        "ap_aug": np.nan,
        "ap": ap_base,
        "delta_ap": 0.0,
        "prevalence": float(y_test.mean()),
        "n_test": int(len(test)),
        "n_test_positive": int(y_test.sum()),
        "n_train_rows": int(len(train)),
        "n_train_experiments": int(train[EXPERIMENT_COL].nunique()),
        "n_sim_fault": 0,
        "seed": int(random_state),
        "weight_real_neg_mass": float(w_base[y_train == 0].sum()),
        "weight_real_pos_mass": float(w_base[y_train == 1].sum()),
        "weight_sim_mass": 0.0,
        "preprocessor_fingerprint": prep_fingerprint,
        "imputer_statistics": tuple(float(x) for x in imputer.statistics_),
        "scaler_mean": tuple(float(x) for x in scaler.mean_),
        "scaler_scale": tuple(float(x) for x in scaler.scale_),
        "n_train_feature_rows_imputed": int(train.loc[:, list(features)].isna().any(axis=1).sum()),
        "n_test_feature_rows_imputed": int(test.loc[:, list(features)].isna().any(axis=1).sum()),
    }

    if sim_fault is None or len(sim_fault) == 0:
        return result

    sim = _validate_frame(
        sim_fault,
        required_features=features,
        label_col=LABEL_COL,
        experiment_col=EXPERIMENT_COL,
        require_window_bounds=True,
        frame_name="sim_fault",
    )
    y_sim = sim[LABEL_COL].to_numpy(dtype=np.int8)
    if not np.all(y_sim == 1):
        raise ValueError("sim_fault must be fault-only (all label=1).")
    if EXPERIMENT_COL in sim.columns:
        sim_keys = sim[EXPERIMENT_COL].dropna().astype(str).unique()
        if len(sim_keys) > 1:
            raise ValueError("sim_fault contains more than one target experiment key.")

    x_sim = scaler.transform(imputer.transform(sim.loc[:, list(features)].to_numpy(dtype=float)))
    if not np.isfinite(x_sim).all():
        raise ValueError("Simulation preprocessing produced non-finite features.")

    w_aug = build_augmented_weights(train, sim, label_col=LABEL_COL)
    if len(w_aug) != len(train) + len(sim):
        raise AssertionError("Augmented sample-weight length does not match concatenated training rows.")
    if not np.isclose(w_aug.sum(), 1.0, atol=1e-9):
        raise AssertionError("Augmented sample weights do not sum to one.")

    x_train_aug = np.vstack([x_train, x_sim])
    y_train_aug = np.concatenate([y_train, y_sim])
    model_aug = _new_logistic_regression().fit(
        x_train_aug, y_train_aug, sample_weight=w_aug
    )
    ap_aug = float(average_precision_score(y_test, model_aug.predict_proba(x_test)[:, 1]))

    n_real = len(train)
    result.update(
        {
            "ap_aug": ap_aug,
            "ap": ap_aug,
            "delta_ap": ap_aug - ap_base,
            "n_sim_fault": int(len(sim)),
            "weight_real_neg_mass": float(w_aug[:n_real][y_train == 0].sum()),
            "weight_real_pos_mass": float(w_aug[:n_real][y_train == 1].sum()),
            "weight_sim_mass": float(w_aug[n_real:].sum()),
            "n_sim_feature_rows_imputed": int(sim.loc[:, list(features)].isna().any(axis=1).sum()),
        }
    )
    return result


def compute_fault_only_delta_ap(
    target_key: str,
    real_windows: pd.DataFrame,
    sim_fault_pool: pd.DataFrame,
    *,
    K: int,
    q_window: tuple[float, float],
    n_seeds: int = N_SEEDS_PER_TARGET,
    features: tuple[str, ...] = FEATURES,
) -> dict[str, Any] | None:
    """Compute 20-seed (default) paired ΔAP for one reviewed target experiment.

    The q-window is mandatory. The target real experiment is never in the real
    training pool, and all q-window-overlapping target test windows are excluded.
    K must already have been frozen from the minimum eligible fault-pool size
    across the reviewed cohort (capped at 100 by Phase 0).
    """
    if not isinstance(K, (int, np.integer)) or not 10 <= int(K) <= 100:
        raise ValueError("K must be an integer in [10, 100], determined before outcome inspection.")
    if not isinstance(n_seeds, (int, np.integer)) or int(n_seeds) != N_SEEDS_PER_TARGET:
        raise ValueError(
            f"Primary analysis requires exactly {N_SEEDS_PER_TARGET} predeclared seeds; "
            "do not tune seed count after inspecting outcomes."
        )
    if not isinstance(target_key, str) or not target_key.strip():
        raise ValueError("target_key must be a non-empty string.")

    all_real = _validate_frame(
        real_windows,
        required_features=features,
        label_col=LABEL_COL,
        experiment_col=EXPERIMENT_COL,
        require_window_bounds=True,
        frame_name="real_windows",
    )
    target_key = str(target_key)
    target_real_all = all_real.loc[all_real[EXPERIMENT_COL] == target_key].copy()
    if target_real_all.empty:
        return None
    target_real_test = _exclude_q_window_overlaps(target_real_all, q_window)
    q_start, q_end = map(float, q_window)
    if not np.isclose(q_end - q_start, Q_HORIZON_SECONDS, rtol=0.0, atol=1e-6):
        raise ValueError(
            f"Primary q_window must be exactly {Q_HORIZON_SECONDS:g} seconds; "
            "use a separately labelled sensitivity analysis for other horizons."
        )
    train_pool = all_real.loc[all_real[EXPERIMENT_COL] != target_key].copy()

    if len(target_real_test) < MIN_TEST_ROWS or len(train_pool) < MIN_TRAIN_ROWS:
        return None
    if target_real_test[LABEL_COL].nunique() != 2:
        return None
    if train_pool[LABEL_COL].nunique() != 2:
        return None

    sim_pool = _validate_frame(
        sim_fault_pool,
        required_features=features,
        label_col=LABEL_COL,
        experiment_col=EXPERIMENT_COL,
        require_window_bounds=True,
        frame_name="sim_fault_pool",
    )
    if not np.all(sim_pool[LABEL_COL].to_numpy(dtype=np.int8) == 1):
        raise ValueError("sim_fault_pool must contain fault-only windows (all label=1).")
    if len(sim_pool) < K:
        return None
    if EXPERIMENT_COL in sim_pool.columns:
        sim_keys = sim_pool[EXPERIMENT_COL].dropna().astype(str).unique()
        if len(sim_keys) != 1 or sim_keys[0] != target_key:
            raise ValueError(
                "When present, sim_fault_pool experiment_key must identify exactly the target run."
            )

    per_seed: list[dict[str, Any]] = []
    for seed_idx in range(int(n_seeds)):
        seed = _stable_seed(target_key, seed_idx)
        rng = np.random.default_rng(seed)
        sampled_sim = sample_fault_only_K(sim_pool, int(K), rng, label_col=LABEL_COL)
        res = fit_predict_ap(
            train_pool,
            target_real_test,
            sim_fault=sampled_sim,
            random_state=seed,
            features=features,
        )
        if res is None:
            raise RuntimeError(
                "A seed unexpectedly produced an ineligible fold; do not silently average a subset of seeds."
            )
        per_seed.append(res)

    deltas = np.asarray([r["delta_ap"] for r in per_seed], dtype=float)
    aps_base = np.asarray([r["ap_base"] for r in per_seed], dtype=float)
    return {
        "target_key": target_key,
        "K": int(K),
        "n_seeds_requested": int(n_seeds),
        "n_seeds_valid": int(len(per_seed)),
        "delta_ap_mean": float(deltas.mean()),
        "delta_ap_std": float(deltas.std(ddof=1)) if len(deltas) > 1 else np.nan,
        "delta_ap_median": float(np.median(deltas)),
        "delta_ap_min": float(deltas.min()),
        "delta_ap_max": float(deltas.max()),
        "ap_base_mean": float(aps_base.mean()),
        "ap_base_std_across_seeds": float(aps_base.std(ddof=1)) if len(aps_base) > 1 else 0.0,
        "prevalence": per_seed[0]["prevalence"],
        "n_test": per_seed[0]["n_test"],
        "n_test_positive": per_seed[0]["n_test_positive"],
        "n_test_windows_full_run": int(len(target_real_all)),
        "n_test_windows_excluded_by_q": int(len(target_real_all) - len(target_real_test)),
        "n_train_experiments": per_seed[0]["n_train_experiments"],
        "weight_real_neg_mass": per_seed[0]["weight_real_neg_mass"],
        "weight_real_pos_mass": per_seed[0]["weight_real_pos_mass"],
        "weight_sim_mass": per_seed[0]["weight_sim_mass"],
        "test_window_ids": tuple(target_real_test["window_id"].astype(str).tolist()),
        "train_experiment_keys": tuple(sorted(train_pool[EXPERIMENT_COL].unique().tolist())),
        "per_seed": per_seed,
    }


def _make_synthetic_windows(
    prefix: str,
    n_exps: int,
    n_per_class: int,
    rng: np.random.Generator,
) -> pd.DataFrame:
    """Create non-overlapping 30-s windows with an actual gap around q-window."""
    rows = []
    for e in range(n_exps):
        exp_key = f"{prefix}_exp_{e:02d}"
        exp_shift = rng.normal(0.0, 0.25)
        for cls in (0, 1):
            base_start = 0.0 if cls == 0 else 600.0
            for i in range(n_per_class):
                signal = 0.45 * cls + exp_shift + rng.normal(0.0, 1.6)
                start = base_start + i * 30.0
                rows.append(
                    {
                        EXPERIMENT_COL: exp_key,
                        WINDOW_START_COL: start,
                        WINDOW_END_COL: start + 30.0,
                        LABEL_COL: cls,
                        FEATURES[0]: signal,
                        FEATURES[1]: 0.5 + 0.05 * cls + rng.normal(0.0, 0.15),
                        FEATURES[2]: 0.03 * cls + rng.normal(0.0, 0.35),
                    }
                )
    return pd.DataFrame(rows)


def run_smoke_tests() -> None:
    """Run synthetic-only contract tests for Module 2; no dataset is accessed."""
    print("Running reviewed synthetic smoke tests for v5.2 Module 2...")
    rng = np.random.default_rng(20261030)
    real_train = _make_synthetic_windows("train", 6, 12, rng)
    test_full = _make_synthetic_windows("target", 1, 15, rng)
    target_key = "target_exp_00"
    q_window = (300.0, 600.0)
    test = _exclude_q_window_overlaps(test_full, q_window)
    sim_pool = _make_synthetic_windows("sim", 1, 20, rng)
    sim_pool = sim_pool.loc[sim_pool[LABEL_COL] == 1].copy()
    sim_pool[EXPERIMENT_COL] = target_key
    K = 10

    # Test 1: no simulation -> exact zero delta.
    res1 = fit_predict_ap(real_train, test, sim_fault=None, random_state=42)
    assert res1 is not None and res1["delta_ap"] == 0.0 and np.isfinite(res1["ap_base"])
    print(f"  PASS 1: sim=None -> delta_ap == 0.0; AP_base={res1['ap_base']:.3f}")

    # Test 2: empty simulation -> exact zero delta.
    empty_sim = sim_pool.iloc[0:0].copy()
    res2 = fit_predict_ap(real_train, test, sim_fault=empty_sim, random_state=42)
    assert res2 is not None and res2["delta_ap"] == 0.0
    print("  PASS 2: empty sim -> delta_ap == 0.0")

    # Test 3: change test values drastically; train-fitted transform fingerprint must not change.
    shifted_test = test.copy()
    for col in FEATURES:
        shifted_test[col] = shifted_test[col] * 100.0 + 5000.0
    res3a = fit_predict_ap(real_train, test, sim_fault=None, random_state=7)
    res3b = fit_predict_ap(real_train, shifted_test, sim_fault=None, random_state=7)
    assert res3a is not None and res3b is not None
    assert res3a["preprocessor_fingerprint"] == res3b["preprocessor_fingerprint"]
    assert np.allclose(res3a["imputer_statistics"], res3b["imputer_statistics"])
    assert np.allclose(res3a["scaler_mean"], res3b["scaler_mean"])
    print("  PASS 3: train-only imputer/scaler fingerprint invariant to altered test features")

    # Test 4: augmented arm fits with exact fixed mass allocation.
    sample = sample_fault_only_K(sim_pool, K, np.random.default_rng(123), label_col=LABEL_COL)
    res4 = fit_predict_ap(real_train, test, sim_fault=sample, random_state=42)
    assert res4 is not None and np.isfinite(res4["delta_ap"])
    assert res4["n_sim_fault"] == K
    assert np.isclose(res4["weight_real_neg_mass"], 0.50)
    assert np.isclose(res4["weight_real_pos_mass"], 0.40)
    assert np.isclose(res4["weight_sim_mass"], 0.10)
    print(f"  PASS 4: fault augmentation fit; delta_ap={res4['delta_ap']:+.4f}; masses=0.50/0.40/0.10")

    # Test 5: same sample and seed -> exact reproducibility.
    res5a = fit_predict_ap(real_train, test, sim_fault=sample, random_state=999)
    res5b = fit_predict_ap(real_train, test, sim_fault=sample, random_state=999)
    assert res5a is not None and res5b is not None
    assert res5a["delta_ap"] == res5b["delta_ap"]
    print("  PASS 5: fixed sample + fixed seed -> identical delta_ap")

    # Test 6: exact half-open q overlap rule and mandatory q window.
    excluded = _exclude_q_window_overlaps(test_full, q_window)
    overlap = (test_full[WINDOW_START_COL] < q_window[1]) & (test_full[WINDOW_END_COL] > q_window[0])
    assert len(excluded) == len(test_full) - int(overlap.sum())
    assert not ((excluded[WINDOW_START_COL] < q_window[1]) & (excluded[WINDOW_END_COL] > q_window[0])).any()
    try:
        _exclude_q_window_overlaps(test_full, None)
    except ValueError as exc:
        assert "required" in str(exc)
    else:
        raise AssertionError("q_window=None must not bypass primary overlap exclusion.")
    print(f"  PASS 6: q-window overlap exclusion is exact; {int(overlap.sum())} windows removed; None rejected")

    # Test 7: 20-seed paired aggregate, fixed target holdout, and test provenance.
    all_real = pd.concat([real_train, test_full], ignore_index=True)
    res7 = compute_fault_only_delta_ap(
        target_key=target_key,
        real_windows=all_real,
        sim_fault_pool=sim_pool,
        K=K,
        q_window=q_window,
        n_seeds=N_SEEDS_PER_TARGET,
    )
    assert res7 is not None
    assert res7["n_seeds_requested"] == N_SEEDS_PER_TARGET
    assert res7["n_seeds_valid"] == N_SEEDS_PER_TARGET
    assert res7["delta_ap_min"] <= res7["delta_ap_mean"] <= res7["delta_ap_max"]
    assert target_key not in res7["train_experiment_keys"]
    assert len(res7["test_window_ids"]) == res7["n_test"]
    assert np.isclose(res7["weight_sim_mass"], 0.10)
    print(f"  PASS 7: {N_SEEDS_PER_TARGET}-seed aggregation; mean delta_ap={res7['delta_ap_mean']:+.4f}; target held out")

    # Test 8: mixed, missing and non-binary simulation labels are rejected.
    for bad_values in ([1, 1, 0], [1, np.nan, 1], [1, 2, 1]):
        bad_sim = pd.DataFrame({
            EXPERIMENT_COL: [target_key] * 3,
            WINDOW_START_COL: [0.0, 30.0, 60.0],
            WINDOW_END_COL: [30.0, 60.0, 90.0],
            LABEL_COL: bad_values,
            **{f: [0.1, 0.2, 0.3] for f in FEATURES},
        })
        try:
            fit_predict_ap(real_train, test, sim_fault=bad_sim, random_state=42)
        except ValueError:
            pass
        else:
            raise AssertionError(f"Invalid simulation labels were accepted: {bad_values}")
    print("  PASS 8: mixed/missing/non-binary simulated labels rejected")

    # Test 9: feature NaNs are imputed (not dropped); all-missing training feature fails loudly.
    train_nan = real_train.copy()
    train_nan.loc[train_nan.index[0], FEATURES[0]] = np.nan
    test_nan = test.copy()
    test_nan.loc[test_nan.index[0], FEATURES[1]] = np.nan
    res9 = fit_predict_ap(train_nan, test_nan, sim_fault=None, random_state=42)
    assert res9 is not None
    assert res9["n_train_rows"] == len(train_nan)
    assert res9["n_test"] == len(test_nan)
    assert res9["n_train_feature_rows_imputed"] == 1
    assert res9["n_test_feature_rows_imputed"] == 1
    all_missing = real_train.copy()
    all_missing[FEATURES[0]] = np.nan
    try:
        fit_predict_ap(all_missing, test, sim_fault=None, random_state=42)
    except ValueError as exc:
        assert "entirely missing" in str(exc)
    else:
        raise AssertionError("An all-missing training feature was not rejected.")
    print("  PASS 9: feature NaNs imputed from train; all-missing train feature rejected")

    # Test 10: class_weight=None is explicit and fixed.
    assert _new_logistic_regression().get_params()["class_weight"] is None
    print("  PASS 10: class_weight=None enforced")

    # Test 11: a simulation pool from a different experiment cannot be paired.
    wrong_pool = sim_pool.copy()
    wrong_pool[EXPERIMENT_COL] = "wrong_target_exp"
    try:
        compute_fault_only_delta_ap(
            target_key=target_key, real_windows=pd.concat([real_train, test_full], ignore_index=True),
            sim_fault_pool=wrong_pool, K=K, q_window=q_window,
        )
    except ValueError as exc:
        assert "target run" in str(exc)
    else:
        raise AssertionError("A wrong-run simulation pool was accepted.")
    print("  PASS 11: wrong-run simulation provenance rejected")

    # Test 12: primary seed count is frozen at 20.
    try:
        compute_fault_only_delta_ap(
            target_key=target_key, real_windows=pd.concat([real_train, test_full], ignore_index=True),
            sim_fault_pool=sim_pool, K=K, q_window=q_window, n_seeds=19,
        )
    except ValueError as exc:
        assert "exactly 20" in str(exc)
    else:
        raise AssertionError("A non-prespecified seed count was accepted.")
    print("  PASS 12: primary 20-seed count is enforced")

    # Test 13: alternative q horizons cannot silently enter the primary analysis.
    try:
        compute_fault_only_delta_ap(
            target_key=target_key, real_windows=pd.concat([real_train, test_full], ignore_index=True),
            sim_fault_pool=sim_pool, K=K, q_window=(300.0, 599.0),
        )
    except ValueError as exc:
        assert "exactly 300" in str(exc)
    else:
        raise AssertionError("A non-300-s q horizon was accepted as primary.")
    print("  PASS 13: primary q horizon fixed at 300 seconds")

    # Test 14: overlapping real windows are rejected before outcome calculation.
    overlap_real = pd.concat([real_train, test_full], ignore_index=True)
    duplicated = overlap_real.loc[overlap_real[EXPERIMENT_COL] == target_key].iloc[[0]].copy()
    overlap_real = pd.concat([overlap_real, duplicated], ignore_index=True)
    try:
        compute_fault_only_delta_ap(
            target_key=target_key, real_windows=overlap_real,
            sim_fault_pool=sim_pool, K=K, q_window=q_window,
        )
    except ValueError as exc:
        assert "overlapping windows" in str(exc)
    else:
        raise AssertionError("Overlapping target-real windows were accepted.")
    print("  PASS 14: overlapping real windows rejected")

    print("\nAll reviewed Module 2 smoke tests passed (synthetic data only).")
    print("Module 2 does not establish any empirical claim about the Zenodo dataset.")


if __name__ == "__main__":
    run_smoke_tests()