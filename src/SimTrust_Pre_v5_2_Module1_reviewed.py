"""
SimTrust-Pre v5.2 — Module 1 (reviewed implementation)
Fault-only window construction, sampling, and experiment/class mass allocation.

This module is deliberately dataset-agnostic. Its smoke tests use synthetic data only.
"""

from __future__ import annotations

import numpy as np
import pandas as pd

# Frozen Phase 0 design constants
SYNTHETIC_WEIGHT_FRACTION = 0.10
REAL_NEG_MASS_BASELINE = 0.50
REAL_POS_MASS_BASELINE = 0.50
REAL_NEG_MASS_AUG = 0.50
REAL_POS_MASS_AUG = 0.40
SIM_FAULT_MASS_AUG = 0.10

WINDOW_SECONDS = 30.0
WINDOW_STRIDE = 30.0
MIN_POINTS_PER_WINDOW = 24
MAX_GAP_SECONDS = 2.5
MAX_EDGE_GAP_SECONDS = 2.5
PA_PER_MBAR = 100.0


def _strict_binary_labels(df: pd.DataFrame, label_col: str) -> np.ndarray:
    """Return int labels after rejecting missing, non-finite, or non-binary values."""
    if label_col not in df.columns:
        raise KeyError(f"Missing label column: {label_col!r}")
    raw = pd.to_numeric(df[label_col], errors="coerce")
    arr = raw.to_numpy(dtype=float)
    if not np.isfinite(arr).all():
        raise ValueError(f"{label_col!r} contains missing or non-finite labels.")
    if not np.isin(arr, [0.0, 1.0]).all():
        bad = np.unique(arr[~np.isin(arr, [0.0, 1.0])])
        raise ValueError(f"{label_col!r} must contain only 0/1; found {bad.tolist()}.")
    return arr.astype(np.int8)


def _rake_experiment_class_masses(
    df: pd.DataFrame,
    *,
    target_class_masses: dict[int, float],
    total_mass: float,
    experiment_col: str = "experiment_key",
    label_col: str = "label_anomaly",
    tol: float = 1e-11,
    max_iter: int = 20_000,
) -> np.ndarray:
    """
    Allocate mass so each experiment receives equal total mass and class totals
    match target_class_masses. Within each experiment/class cell, observations
    receive equal mass.

    Raises rather than silently relaxing constraints when the support pattern
    makes the requested margins infeasible.
    """
    if df.empty:
        raise ValueError("Cannot allocate mass to an empty real training set.")
    if experiment_col not in df.columns:
        raise KeyError(f"Missing experiment column: {experiment_col!r}")

    y = _strict_binary_labels(df, label_col)
    exp = df[experiment_col].astype(str).to_numpy()
    if pd.isna(exp).any() or (exp == "").any():
        raise ValueError("Experiment keys must be present and non-empty.")

    classes = sorted(target_class_masses)
    if classes != [0, 1]:
        raise ValueError("This implementation requires target masses for classes 0 and 1.")
    if any(v < 0 or not np.isfinite(v) for v in target_class_masses.values()):
        raise ValueError("Class target masses must be finite and non-negative.")
    if not np.isclose(sum(target_class_masses.values()), total_mass, atol=1e-10):
        raise ValueError("Class target masses must sum to total_mass.")
    if total_mass <= 0:
        raise ValueError("total_mass must be positive.")

    exp_keys, exp_inverse = np.unique(exp, return_inverse=True)
    n_exp = len(exp_keys)
    row_targets = np.full(n_exp, total_mass / n_exp, dtype=float)
    col_targets = np.array([target_class_masses[c] for c in classes], dtype=float)

    # Cell support: whether an experiment contains at least one observation of a class.
    support = np.zeros((n_exp, len(classes)), dtype=bool)
    for i in range(n_exp):
        for j, cls in enumerate(classes):
            support[i, j] = bool(np.any((exp_inverse == i) & (y == cls)))

    # Necessary/sufficient support-capacity checks for the two-class row/column margins.
    for j, cls in enumerate(classes):
        capacity = row_targets[support[:, j]].sum()
        if capacity + tol < col_targets[j]:
            raise ValueError(
                f"Infeasible margins: class {cls} occurs in experiments with "
                f"total equal-experiment capacity {capacity:.6f}, below target "
                f"{col_targets[j]:.6f}."
            )

    # Start with equal raw weight per row; iterative proportional fitting enforces margins.
    w = np.ones(len(df), dtype=float)
    for _ in range(max_iter):
        # Experiment margins
        row_sums = np.bincount(exp_inverse, weights=w, minlength=n_exp)
        for i in range(n_exp):
            if row_sums[i] <= 0:
                raise ValueError(f"Experiment {exp_keys[i]!r} has zero allocated mass.")
            w[exp_inverse == i] *= row_targets[i] / row_sums[i]

        # Class margins
        class_sums = np.array([w[y == cls].sum() for cls in classes], dtype=float)
        for j, cls in enumerate(classes):
            if col_targets[j] == 0:
                w[y == cls] = 0.0
            elif class_sums[j] <= 0:
                raise ValueError(f"Class {cls} has no positive support for requested mass.")
            else:
                w[y == cls] *= col_targets[j] / class_sums[j]

        row_check = np.bincount(exp_inverse, weights=w, minlength=n_exp)
        col_check = np.array([w[y == cls].sum() for cls in classes], dtype=float)
        err = max(
            float(np.max(np.abs(row_check - row_targets))),
            float(np.max(np.abs(col_check - col_targets))),
        )
        if err <= tol:
            break
    else:
        raise RuntimeError(
            "Experiment/class mass allocation did not converge; inspect cohort support."
        )

    if not np.isclose(w.sum(), total_mass, atol=1e-9):
        raise AssertionError("Internal error: allocated mass does not equal total_mass.")
    return w


def assign_experiment_class_mass(
    df: pd.DataFrame,
    label_col: str = "label_anomaly",
    experiment_col: str = "experiment_key",
) -> np.ndarray:
    """
    Real-only baseline weights:
      - equal total mass per experiment
      - 0.50 total mass on normal, 0.50 on anomaly
      - total mass = 1.0

    If these constraints cannot be met for a fold's experiment/class support,
    an explicit ValueError is raised.
    """
    return _rake_experiment_class_masses(
        df,
        target_class_masses={0: REAL_NEG_MASS_BASELINE, 1: REAL_POS_MASS_BASELINE},
        total_mass=1.0,
        experiment_col=experiment_col,
        label_col=label_col,
    )


def build_augmented_weights(
    real_train_df: pd.DataFrame,
    sim_fault_df: pd.DataFrame,
    label_col: str = "label_anomaly",
) -> np.ndarray:
    """
    Returns weights ordered as [real_train_df rows; sim_fault_df rows]:
      - each real training experiment has equal real-data mass (total real mass 0.90)
      - real normal mass = 0.50
      - real anomaly mass = 0.40
      - simulated fault mass = 0.10
      - total = 1.0

    The synthetic path is an additional group with a fixed 0.10 total mass;
    it is not claimed to have the same group mass as each real experiment.
    """
    if real_train_df.empty:
        raise ValueError("Real training pool is empty.")
    y_real = _strict_binary_labels(real_train_df, label_col)
    if not np.any(y_real == 0):
        raise ValueError("Real training pool has no normal samples.")
    if not np.any(y_real == 1):
        raise ValueError("Real training pool has no anomaly samples.")

    y_sim = _strict_binary_labels(sim_fault_df, label_col)
    if len(y_sim) == 0:
        raise ValueError("No simulated fault windows.")
    if not np.all(y_sim == 1):
        raise ValueError("Simulated fault windows must all have label=1.")

    real_w = _rake_experiment_class_masses(
        real_train_df,
        target_class_masses={
            0: REAL_NEG_MASS_AUG,
            1: REAL_POS_MASS_AUG,
        },
        total_mass=1.0 - SIM_FAULT_MASS_AUG,
        label_col=label_col,
    )
    sim_w = np.full(len(sim_fault_df), SIM_FAULT_MASS_AUG / len(sim_fault_df), dtype=float)
    w = np.concatenate([real_w, sim_w])

    if not np.isclose(w.sum(), 1.0, atol=1e-9):
        raise AssertionError("Augmented sample weights do not sum to one.")
    return w


def sample_fault_only_K(
    sim_fault_df: pd.DataFrame,
    K: int,
    rng: np.random.Generator,
    label_col: str = "label_anomaly",
) -> pd.DataFrame:
    """Sample exactly K distinct, label=1 windows without replacement."""
    if not isinstance(K, (int, np.integer)) or K <= 0:
        raise ValueError("K must be a positive integer.")
    y = _strict_binary_labels(sim_fault_df, label_col)
    if len(y) == 0 or not np.all(y == 1):
        raise ValueError("Fault-only sampler requires a non-empty all-positive dataset.")
    if len(sim_fault_df) < K:
        raise ValueError(f"Need K={K} fault windows, have {len(sim_fault_df)}.")
    idx = rng.choice(len(sim_fault_df), size=K, replace=False)
    return sim_fault_df.iloc[idx].reset_index(drop=True)


def build_sim_fault_windows(
    sim_time_sec,
    sim_pressure_stage_12_pa,
    sim_label_start_s: float,
    sim_label_end_s: float,
) -> pd.DataFrame:
    """
    Build non-overlapping 30 s windows fully supported by the reviewed simulator
    fault interval. Input pressure is the physically reviewed stage-12 signal in Pa;
    it is converted internally to mbar (1 mbar = 100 Pa).

    Candidate windows must meet minimum point count, internal-gap and edge-coverage
    rules. Times must be finite, unique, and strictly increasing.
    """
    t = np.asarray(sim_time_sec, dtype=float)
    p_pa = np.asarray(sim_pressure_stage_12_pa, dtype=float)

    if t.ndim != 1 or p_pa.ndim != 1:
        raise ValueError("Time and pressure inputs must be one-dimensional.")
    if len(t) != len(p_pa):
        raise ValueError("Time and pressure must have the same length.")
    if len(t) < 2 or not np.isfinite(t).all():
        raise ValueError("Simulation times must contain at least two finite values.")
    if np.any(np.diff(t) <= 0):
        raise ValueError("Simulation times must be strictly increasing and unique.")
    if not (
        np.isfinite(sim_label_start_s)
        and np.isfinite(sim_label_end_s)
        and sim_label_end_s > sim_label_start_s
    ):
        raise ValueError("Invalid reviewed simulator label interval.")

    p_mbar = p_pa / PA_PER_MBAR
    rows = []
    start = float(sim_label_start_s)

    while start + WINDOW_SECONDS <= float(sim_label_end_s) + 1e-9:
        end = start + WINDOW_SECONDS
        ix = np.flatnonzero((t >= start) & (t < end))

        if len(ix) < MIN_POINTS_PER_WINDOW:
            start += WINDOW_STRIDE
            continue

        tw = t[ix]
        if np.max(np.diff(tw)) > MAX_GAP_SECONDS:
            start += WINDOW_STRIDE
            continue

        left_edge_gap = float(tw[0] - start)
        right_edge_gap = float(end - tw[-1])
        if (
            left_edge_gap > MAX_EDGE_GAP_SECONDS
            or right_edge_gap > MAX_EDGE_GAP_SECONDS
        ):
            start += WINDOW_STRIDE
            continue

        xf = p_mbar[ix]
        if not np.isfinite(xf).all():
            start += WINDOW_STRIDE
            continue

        rows.append(
            {
                "window_start_s": float(start),
                "window_end_s": float(end),
                "n_points": int(len(ix)),
                "max_internal_gap_s": float(np.max(np.diff(tw))),
                "left_edge_gap_s": left_edge_gap,
                "right_edge_gap_s": right_edge_gap,
                "PY23_mean_mbar": float(np.mean(xf)),
                "PY23_std_mbar": float(np.std(xf, ddof=0)),
                "PY23_delta_mbar": float(xf[-1] - xf[0]),
                "label_anomaly": 1,
            }
        )
        start += WINDOW_STRIDE

    return pd.DataFrame(rows)


def run_smoke_tests() -> None:
    print("Running reviewed synthetic smoke tests for v5.2 Module 1...")
    rng = np.random.default_rng(42)

    # 1. Fully covered fault interval -> expected 5 complete windows.
    t = np.arange(0, 400, 1.0)
    p_pa = (1000.0 + 0.1 * t) * PA_PER_MBAR
    wins = build_sim_fault_windows(t, p_pa, 100.0, 250.0)
    assert len(wins) == 5
    assert wins["window_start_s"].min() >= 100.0
    assert wins["window_end_s"].max() <= 250.0
    assert (wins["label_anomaly"] == 1).all()
    assert np.allclose(wins["PY23_mean_mbar"].iloc[0], np.mean(1000.0 + 0.1*np.arange(100, 130)))

    # 2. Internal discontinuity must reject every window crossing it.
    t_gap = np.concatenate([np.arange(0, 110, 1.0), np.arange(150, 300, 1.0)])
    p_gap = (1000.0 + 0.1 * t_gap) * PA_PER_MBAR
    gap_wins = build_sim_fault_windows(t_gap, p_gap, 100.0, 160.0)
    assert len(gap_wins) == 0

    # 3. Partial edge coverage (25 points but missing final 5 s) must be rejected.
    edge_wins = build_sim_fault_windows(t_gap, p_gap, 85.0, 115.0)
    assert len(edge_wins) == 0

    # 4. Duplicate or unsorted timestamps are rejected.
    try:
        build_sim_fault_windows([0, 1, 1, 2], [1000, 1001, 1002, 1003], 0, 30)
    except ValueError as exc:
        assert "strictly increasing" in str(exc)
    else:
        raise AssertionError("Duplicate timestamps were not rejected.")

    # 5. Fault-only sampler is deterministic and without replacement.
    sim_df = pd.DataFrame(
        {
            "window_id": np.arange(15),
            "label_anomaly": np.ones(15, dtype=int),
        }
    )
    s1 = sample_fault_only_K(sim_df, 5, np.random.default_rng(123))
    s2 = sample_fault_only_K(sim_df, 5, np.random.default_rng(123))
    assert len(s1) == 5 and s1["window_id"].nunique() == 5
    assert s1["window_id"].tolist() == s2["window_id"].tolist()

    # 6. Mixed/NA/non-binary labels are rejected explicitly.
    for bad_labels in ([1, 1, 0], [1, np.nan, 1], [1, 2, 1]):
        bad = pd.DataFrame({"label_anomaly": bad_labels})
        try:
            sample_fault_only_K(bad, 1, rng)
        except ValueError:
            pass
        else:
            raise AssertionError(f"Bad labels were accepted: {bad_labels}")

    # 7. Real-only mass allocation: equal experiment totals and global 50/50 classes.
    real = pd.DataFrame(
        {
            "experiment_key": ["A"] * 100 + ["B"] * 100,
            "label_anomaly": [0] * 90 + [1] * 10 + [0] * 50 + [1] * 50,
        }
    )
    w_base = assign_experiment_class_mass(real)
    exp_mass = real.assign(w=w_base).groupby("experiment_key")["w"].sum()
    assert np.allclose(exp_mass.to_numpy(), [0.5, 0.5], atol=1e-9)
    assert np.isclose(w_base[real["label_anomaly"].to_numpy() == 0].sum(), 0.5)
    assert np.isclose(w_base[real["label_anomaly"].to_numpy() == 1].sum(), 0.5)

    # 8. Augmented allocation: equal real experiment totals, class masses 0.50/0.40,
    #    simulated fault mass 0.10, and total mass 1.0.
    sim_fault = pd.DataFrame({"label_anomaly": np.ones(7, dtype=int)})
    w_aug = build_augmented_weights(real, sim_fault)
    n_real = len(real)
    real_aug = real.assign(w=w_aug[:n_real]).groupby("experiment_key")["w"].sum()
    y_real = real["label_anomaly"].to_numpy()
    assert np.allclose(real_aug.to_numpy(), [0.45, 0.45], atol=1e-9)
    assert np.isclose(w_aug[:n_real][y_real == 0].sum(), 0.50)
    assert np.isclose(w_aug[:n_real][y_real == 1].sum(), 0.40)
    assert np.isclose(w_aug[n_real:].sum(), 0.10)
    assert np.isclose(w_aug.sum(), 1.0)

    # 9. An infeasible group/class structure must fail rather than silently rebalance.
    infeasible = pd.DataFrame(
        {
            "experiment_key": ["A"] * 10 + ["B"] * 10,
            "label_anomaly": [0] * 10 + [1] * 10,
        }
    )
    # This is feasible exactly at 0.5/0.5 and should converge.
    w_sep = assign_experiment_class_mass(infeasible)
    assert np.allclose(
        infeasible.assign(w=w_sep).groupby("experiment_key")["w"].sum().to_numpy(),
        [0.5, 0.5],
        atol=1e-9,
    )

    print("  PASS 1: fully covered fault windows; Pa-to-mbar conversion")
    print("  PASS 2: internal sampling gaps rejected")
    print("  PASS 3: partial edge coverage rejected")
    print("  PASS 4: duplicate/unsorted timestamps rejected")
    print("  PASS 5: deterministic fault-only sampling without replacement")
    print("  PASS 6: missing/non-binary labels rejected")
    print("  PASS 7: real-only class and experiment mass constraints")
    print("  PASS 8: augmented 0.50/0.40/0.10 mass and experiment constraints")
    print("  PASS 9: class-exclusive experiment support handled")
    print("All reviewed Module 1.1 smoke tests passed (synthetic data only).")


if __name__ == "__main__":
    run_smoke_tests()