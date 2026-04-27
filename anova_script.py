from __future__ import annotations

import argparse
import math
from pathlib import Path

import numpy as np
import pandas as pd


DEFAULT_INPUT = Path("results") / "Averaged_results_all_participants.csv"
DEFAULT_DVS = ("mean_reaction_time_ms",)
SUBJECT_COL = "participant_id"
FACTOR_A_COL = "load_condition"
FACTOR_B_COL = "icon_category"
POSTHOC_SUFFIX = "_posthoc"
WORKBOOK_SUFFIX = "_combined"
COMBINED_CSV_SUFFIX = "_combined"


def log_beta(a: float, b: float) -> float:
    return math.lgamma(a) + math.lgamma(b) - math.lgamma(a + b)


def regularized_incomplete_beta(x: float, a: float, b: float) -> float:
    """Numerically stable regularized incomplete beta implementation."""
    if x <= 0.0:
        return 0.0
    if x >= 1.0:
        return 1.0

    def beta_continued_fraction(x_value: float, alpha: float, beta: float) -> float:
        max_iter = 200
        eps = 3e-14
        fpmin = 1e-300

        qab = alpha + beta
        qap = alpha + 1.0
        qam = alpha - 1.0

        c = 1.0
        d = 1.0 - qab * x_value / qap
        if abs(d) < fpmin:
            d = fpmin
        d = 1.0 / d
        h = d

        for m in range(1, max_iter + 1):
            m2 = 2 * m

            aa = m * (beta - m) * x_value / ((qam + m2) * (alpha + m2))
            d = 1.0 + aa * d
            if abs(d) < fpmin:
                d = fpmin
            c = 1.0 + aa / c
            if abs(c) < fpmin:
                c = fpmin
            d = 1.0 / d
            h *= d * c

            aa = -(alpha + m) * (qab + m) * x_value / ((alpha + m2) * (qap + m2))
            d = 1.0 + aa * d
            if abs(d) < fpmin:
                d = fpmin
            c = 1.0 + aa / c
            if abs(c) < fpmin:
                c = fpmin
            d = 1.0 / d
            delta = d * c
            h *= delta

            if abs(delta - 1.0) < eps:
                break

        return h

    bt = math.exp(
        a * math.log(x) + b * math.log(1.0 - x) - log_beta(a, b)
    )

    if x < (a + 1.0) / (a + b + 2.0):
        return bt * beta_continued_fraction(x, a, b) / a

    return 1.0 - bt * beta_continued_fraction(1.0 - x, b, a) / b


def f_survival_function(f_value: float, df1: int, df2: int) -> float:
    if f_value < 0:
        return 1.0
    x = (df1 * f_value) / (df1 * f_value + df2)
    return 1.0 - regularized_incomplete_beta(x, df1 / 2.0, df2 / 2.0)


def t_two_tailed_p_value(t_value: float, df: int) -> float:
    """Return the two-tailed p-value for a Student t statistic."""
    if df <= 0:
        return float("nan")

    x = df / (df + t_value**2)
    return regularized_incomplete_beta(x, df / 2.0, 0.5)


def partial_eta_squared(ss_effect: float, ss_error: float) -> float:
    denominator = ss_effect + ss_error
    if denominator == 0:
        return float("nan")
    return ss_effect / denominator


def validate_and_pivot(data: pd.DataFrame, dv: str) -> tuple[np.ndarray, list[str], list[str], list[str]]:
    required_columns = {SUBJECT_COL, FACTOR_A_COL, FACTOR_B_COL, dv}
    missing_columns = required_columns.difference(data.columns)
    if missing_columns:
        missing_text = ", ".join(sorted(missing_columns))
        raise ValueError(f"Missing required columns: {missing_text}")

    trimmed = data[[SUBJECT_COL, FACTOR_A_COL, FACTOR_B_COL, dv]].copy()
    trimmed = trimmed.dropna()

    factor_a_levels = sorted(trimmed[FACTOR_A_COL].unique().tolist())
    factor_b_levels = sorted(trimmed[FACTOR_B_COL].unique().tolist())
    subject_levels = sorted(trimmed[SUBJECT_COL].unique().tolist())

    if len(factor_a_levels) != 2 or len(factor_b_levels) != 2:
        raise ValueError(
            "This script expects exactly 2 levels for each within-subject factor."
        )

    cell_counts = trimmed.groupby([SUBJECT_COL, FACTOR_A_COL, FACTOR_B_COL]).size()
    if (cell_counts != 1).any():
        raise ValueError(
            "Each participant must have exactly one row per factor combination."
        )

    expected_rows = len(subject_levels) * len(factor_a_levels) * len(factor_b_levels)
    if len(trimmed) != expected_rows:
        raise ValueError("Input is not fully balanced across participants and conditions.")

    pivot = (
        trimmed.pivot(
            index=SUBJECT_COL,
            columns=[FACTOR_A_COL, FACTOR_B_COL],
            values=dv,
        )
        .reindex(index=subject_levels)
        .reindex(columns=pd.MultiIndex.from_product([factor_a_levels, factor_b_levels]))
    )

    if pivot.isna().any().any():
        raise ValueError("Missing values remain after pivoting; the design must be complete.")

    values = pivot.to_numpy(dtype=float).reshape(
        len(subject_levels), len(factor_a_levels), len(factor_b_levels)
    )
    return values, subject_levels, factor_a_levels, factor_b_levels


def repeated_measures_anova_2x2(data: pd.DataFrame, dv: str) -> pd.DataFrame:
    values, _, factor_a_levels, factor_b_levels = validate_and_pivot(data, dv)

    n_subjects, a_levels, b_levels = values.shape
    grand_mean = values.mean()
    subject_means = values.mean(axis=(1, 2))
    a_means = values.mean(axis=(0, 2))
    b_means = values.mean(axis=(0, 1))
    ab_means = values.mean(axis=0)
    sa_means = values.mean(axis=2)
    sb_means = values.mean(axis=1)

    ss_total = ((values - grand_mean) ** 2).sum()
    ss_subjects = a_levels * b_levels * ((subject_means - grand_mean) ** 2).sum()
    ss_a = b_levels * n_subjects * ((a_means - grand_mean) ** 2).sum()
    ss_b = a_levels * n_subjects * ((b_means - grand_mean) ** 2).sum()
    ss_ab = n_subjects * (
        (ab_means - a_means[:, None] - b_means[None, :] + grand_mean) ** 2
    ).sum()
    ss_sa = b_levels * (
        (sa_means - subject_means[:, None] - a_means[None, :] + grand_mean) ** 2
    ).sum()
    ss_sb = a_levels * (
        (sb_means - subject_means[:, None] - b_means[None, :] + grand_mean) ** 2
    ).sum()

    ss_sab = ss_total - ss_subjects - ss_a - ss_b - ss_ab - ss_sa - ss_sb

    df_a = a_levels - 1
    df_b = b_levels - 1
    df_ab = (a_levels - 1) * (b_levels - 1)
    df_sa = (n_subjects - 1) * (a_levels - 1)
    df_sb = (n_subjects - 1) * (b_levels - 1)
    df_sab = (n_subjects - 1) * (a_levels - 1) * (b_levels - 1)

    rows = [
        (
            f"{FACTOR_A_COL} ({factor_a_levels[0]} vs {factor_a_levels[1]})",
            ss_a,
            df_a,
            ss_sa,
            df_sa,
        ),
        (
            f"{FACTOR_B_COL} ({factor_b_levels[0]} vs {factor_b_levels[1]})",
            ss_b,
            df_b,
            ss_sb,
            df_sb,
        ),
        (
            f"{FACTOR_A_COL} x {FACTOR_B_COL}",
            ss_ab,
            df_ab,
            ss_sab,
            df_sab,
        ),
    ]

    results = []
    for effect, ss_effect, df_effect, ss_error, df_error in rows:
        ms_effect = ss_effect / df_effect
        ms_error = ss_error / df_error
        f_value = ms_effect / ms_error
        p_value = f_survival_function(f_value, df_effect, df_error)
        pes = partial_eta_squared(ss_effect, ss_error)
        results.append(
            {
                "effect": effect,
                "SS": ss_effect,
                "df": df_effect,
                "MS": ms_effect,
                "SS_error": ss_error,
                "df_error": df_error,
                "MS_error": ms_error,
                "F": f_value,
                "p": p_value,
                "partial_eta_squared": pes,
            }
        )

    return pd.DataFrame(results)


def bonferroni_adjust(p_values: list[float]) -> list[float]:
    n_tests = len(p_values)
    adjusted = []
    for p_value in p_values:
        if pd.isna(p_value):
            adjusted.append(float("nan"))
        else:
            adjusted.append(min(p_value * n_tests, 1.0))
    return adjusted


def paired_t_test(left: np.ndarray, right: np.ndarray) -> dict[str, float]:
    differences = left - right
    n_subjects = len(differences)
    mean_difference = float(differences.mean())
    sd_difference = float(differences.std(ddof=1))
    df = n_subjects - 1

    if sd_difference == 0.0:
        if mean_difference == 0.0:
            t_value = 0.0
            p_value = 1.0
        else:
            t_value = math.copysign(float("inf"), mean_difference)
            p_value = 0.0
        cohen_dz = float("nan")
        se_difference = 0.0
    else:
        se_difference = sd_difference / math.sqrt(n_subjects)
        t_value = mean_difference / se_difference
        p_value = t_two_tailed_p_value(t_value, df)
        cohen_dz = mean_difference / sd_difference

    return {
        "mean_difference": mean_difference,
        "sd_difference": sd_difference,
        "se_difference": se_difference,
        "t": t_value,
        "df": df,
        "p_uncorrected": p_value,
        "cohen_dz": cohen_dz,
    }


def repeated_measures_posthoc_2x2(data: pd.DataFrame, dv: str) -> pd.DataFrame:
    values, _, factor_a_levels, factor_b_levels = validate_and_pivot(data, dv)

    comparisons: list[dict[str, float | str]] = []

    main_a = paired_t_test(values[:, 0, :].mean(axis=1), values[:, 1, :].mean(axis=1))
    comparisons.append(
        {
            "comparison_type": "main_effect",
            "effect": FACTOR_A_COL,
            "contrast": f"{factor_a_levels[0]} vs {factor_a_levels[1]}",
            **main_a,
        }
    )

    main_b = paired_t_test(values[:, :, 0].mean(axis=1), values[:, :, 1].mean(axis=1))
    comparisons.append(
        {
            "comparison_type": "main_effect",
            "effect": FACTOR_B_COL,
            "contrast": f"{factor_b_levels[0]} vs {factor_b_levels[1]}",
            **main_b,
        }
    )

    for b_index, b_level in enumerate(factor_b_levels):
        simple_a = paired_t_test(values[:, 0, b_index], values[:, 1, b_index])
        comparisons.append(
            {
                "comparison_type": "simple_effect",
                "effect": FACTOR_A_COL,
                "contrast": f"{factor_a_levels[0]} vs {factor_a_levels[1]} | {FACTOR_B_COL}={b_level}",
                **simple_a,
            }
        )

    for a_index, a_level in enumerate(factor_a_levels):
        simple_b = paired_t_test(values[:, a_index, 0], values[:, a_index, 1])
        comparisons.append(
            {
                "comparison_type": "simple_effect",
                "effect": FACTOR_B_COL,
                "contrast": f"{factor_b_levels[0]} vs {factor_b_levels[1]} | {FACTOR_A_COL}={a_level}",
                **simple_b,
            }
        )

    posthoc = pd.DataFrame(comparisons)
    posthoc["p_bonferroni"] = bonferroni_adjust(posthoc["p_uncorrected"].tolist())
    return posthoc


def format_results_table(table: pd.DataFrame) -> pd.DataFrame:
    formatted = table.copy()
    numeric_columns = [
        "SS",
        "MS",
        "SS_error",
        "MS_error",
        "F",
        "p",
        "partial_eta_squared",
    ]
    for column in numeric_columns:
        formatted[column] = formatted[column].map(
            lambda value: f"{value:.6f}" if pd.notna(value) else "nan"
        )
    return formatted


def format_posthoc_table(table: pd.DataFrame) -> pd.DataFrame:
    formatted = table.copy()
    numeric_columns = [
        "mean_difference",
        "sd_difference",
        "se_difference",
        "t",
        "p_uncorrected",
        "p_bonferroni",
        "cohen_dz",
    ]
    for column in numeric_columns:
        formatted[column] = formatted[column].map(
            lambda value: f"{value:.6f}" if pd.notna(value) else "nan"
        )
    return formatted


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Run a 2x2 repeated-measures ANOVA on aggregated participant results."
    )
    parser.add_argument(
        "--input",
        type=Path,
        default=DEFAULT_INPUT,
        help=f"Path to CSV file. Default: {DEFAULT_INPUT}",
    )
    parser.add_argument(
        "--dv",
        nargs="+",
        default=list(DEFAULT_DVS),
        help="Dependent variable column(s) to analyze.",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=None,
        help="Optional CSV output path. If omitted, saves next to the input file.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    data = pd.read_csv(args.input, encoding="utf-8-sig")

    print(f"Input file: {args.input}")
    print(f"Participants: {data[SUBJECT_COL].nunique()}")

    all_results: list[pd.DataFrame] = []
    all_posthoc_results: list[pd.DataFrame] = []

    for dv in args.dv:
        print()
        print("=" * 80)
        print(f"2x2 repeated-measures ANOVA for: {dv}")
        print("=" * 80)
        results = repeated_measures_anova_2x2(data, dv)
        results.insert(0, "dependent_variable", dv)
        all_results.append(results)
        print(format_results_table(results).to_string(index=False))

        posthoc_results = repeated_measures_posthoc_2x2(data, dv)
        posthoc_results.insert(0, "dependent_variable", dv)
        all_posthoc_results.append(posthoc_results)
        print()
        print("Post-hoc paired comparisons (Bonferroni-corrected):")
        print(format_posthoc_table(posthoc_results).to_string(index=False))

    combined_results = pd.concat(all_results, ignore_index=True)
    combined_posthoc_results = pd.concat(all_posthoc_results, ignore_index=True)
    output_path = args.output
    if output_path is None:
        output_path = args.input.with_name("Anova_results.csv")
    posthoc_output_path = output_path.with_name(f"{output_path.stem}{POSTHOC_SUFFIX}.csv")
    combined_csv_output_path = output_path.with_name(
        f"{output_path.stem}{COMBINED_CSV_SUFFIX}.csv"
    )

    combined_results.to_csv(output_path, index=False, encoding="utf-8-sig")
    combined_posthoc_results.to_csv(posthoc_output_path, index=False, encoding="utf-8-sig")
    combined_csv = pd.concat(
        [
            combined_results.assign(result_type="anova"),
            combined_posthoc_results.assign(result_type="posthoc"),
        ],
        ignore_index=True,
        sort=False,
    )
    leading_columns = ["result_type", "dependent_variable"]
    ordered_columns = leading_columns + [
        column for column in combined_csv.columns if column not in leading_columns
    ]
    combined_csv = combined_csv[ordered_columns]
    combined_csv.to_csv(combined_csv_output_path, index=False, encoding="utf-8-sig")

    workbook_output_path = output_path.with_name(f"{output_path.stem}{WORKBOOK_SUFFIX}.xlsx")
    workbook_saved = False
    try:
        with pd.ExcelWriter(workbook_output_path) as writer:
            combined_results.to_excel(writer, sheet_name="anova", index=False)
            combined_posthoc_results.to_excel(writer, sheet_name="posthoc", index=False)
        workbook_saved = True
    except ModuleNotFoundError:
        workbook_saved = False

    print()
    print(f"Saved CSV results to: {output_path}")
    print(f"Saved post-hoc CSV results to: {posthoc_output_path}")
    print(f"Saved combined CSV results to: {combined_csv_output_path}")
    if workbook_saved:
        print(f"Saved combined workbook to: {workbook_output_path}")
    else:
        print("Skipped combined workbook export because openpyxl is not installed.")


if __name__ == "__main__":
    main()
