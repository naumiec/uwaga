from __future__ import annotations

import csv
from pathlib import Path

import pandas as pd


INPUT_DIR = Path("results")
OUTPUT_DIR = Path("results")
OUTPUT_COLUMNS = [
    "participant_id",
    "load_condition",
    "icon_category",
    "mean_reaction_time_ms",
    "n_trials",
    "n_correct_trials",
]
REQUIRED_COLUMNS = {
    "id_badanego",
    "czas_reakcji_ms",
    "czy_poprawna",
    "czy_trening",
    "load_condition",
    "icon_category",
}


def detect_separator(file_path: Path) -> str:
    """Detect the CSV delimiter with a safe fallback to semicolon."""
    with file_path.open("r", encoding="utf-8-sig", newline="") as handle:
        sample = handle.read(4096)

    if not sample:
        return ";"

    try:
        dialect = csv.Sniffer().sniff(sample, delimiters=";,|\t")
        return dialect.delimiter
    except csv.Error:
        return ";"


def parse_bool_like(series: pd.Series) -> pd.Series:
    """
    Convert mixed correctness values to a nullable numeric series.

    Supported examples include 0/1, True/False, yes/no, tak/nie.
    Unknown values stay missing instead of being silently replaced.
    """
    normalized = series.astype("string").str.strip().str.lower()
    mapping = {
        "1": 1.0,
        "0": 0.0,
        "true": 1.0,
        "false": 0.0,
        "t": 1.0,
        "f": 0.0,
        "yes": 1.0,
        "no": 0.0,
        "y": 1.0,
        "n": 0.0,
        "tak": 1.0,
        "nie": 0.0,
    }
    return normalized.map(mapping, na_action="ignore").astype("Float64")


def parse_training_flag(series: pd.Series) -> pd.Series:
    """Convert practice-trial markers to a nullable numeric series."""
    normalized = series.astype("string").str.strip().str.lower()
    mapping = {
        "1": 1.0,
        "0": 0.0,
        "true": 1.0,
        "false": 0.0,
        "t": 1.0,
        "f": 0.0,
        "yes": 1.0,
        "no": 0.0,
        "y": 1.0,
        "n": 0.0,
        "tak": 1.0,
        "nie": 0.0,
    }
    return normalized.map(mapping, na_action="ignore").astype("Float64")


def read_result_file(file_path: Path) -> pd.DataFrame:
    """Read a result CSV robustly while preserving missing values."""
    separator = detect_separator(file_path)
    data = pd.read_csv(
        file_path,
        sep=separator,
        encoding="utf-8-sig",
        dtype="string",
        keep_default_na=True,
    )

    missing_columns = REQUIRED_COLUMNS.difference(data.columns)
    if missing_columns:
        missing = ", ".join(sorted(missing_columns))
        raise ValueError(f"Missing required columns: {missing}")

    data["czas_reakcji_ms"] = pd.to_numeric(data["czas_reakcji_ms"], errors="coerce")
    data["czy_poprawna"] = parse_bool_like(data["czy_poprawna"])
    data["czy_trening"] = parse_training_flag(data["czy_trening"])
    data = data[data["czy_trening"] != 1].copy()
    return data


def extract_participant_id(data: pd.DataFrame) -> str:
    """Extract one participant ID from the id_badanego column."""
    participant_values = data["id_badanego"].dropna().astype("string").str.strip()
    participant_values = participant_values[participant_values != ""].unique()

    if len(participant_values) == 0:
        raise ValueError("No participant ID found in id_badanego")

    if len(participant_values) > 1:
        raise ValueError(
            f"Multiple participant IDs found in id_badanego: {participant_values.tolist()}"
        )

    return str(participant_values[0])


def aggregate_participant_file(file_path: Path) -> pd.DataFrame:
    """Aggregate one participant's file by load condition and icon category."""
    data = read_result_file(file_path)
    participant_id = extract_participant_id(data)
    valid_reaction_time = data["czas_reakcji_ms"].where(data["czas_reakcji_ms"] >= 200)
    data = data.assign(valid_reaction_time_ms=valid_reaction_time)

    grouped = (
        data.groupby(["load_condition", "icon_category"], dropna=False)
        .agg(
            mean_reaction_time_ms=("valid_reaction_time_ms", "mean"),
            n_trials=("id_badanego", "size"),
            n_correct_trials=("czy_poprawna", lambda values: values.sum(min_count=1)),
        )
        .reset_index()
    )

    grouped.insert(0, "participant_id", participant_id)
    grouped["mean_reaction_time_ms"] = grouped["mean_reaction_time_ms"].round(2)
    grouped["n_correct_trials"] = grouped["n_correct_trials"].round().astype("Int64")
    return grouped[OUTPUT_COLUMNS]


def main() -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    result_files = sorted(
        path for path in INPUT_DIR.iterdir() if path.is_file() and path.name.startswith("result_")
    )

    if not result_files:
        print(f"No files starting with 'result_' were found in {INPUT_DIR.resolve()}")
        return

    aggregated_frames: list[pd.DataFrame] = []
    processed_files = 0
    skipped_files: list[str] = []

    for file_path in result_files:
        try:
            participant_summary = aggregate_participant_file(file_path)
            participant_id = participant_summary["participant_id"].iloc[0]
            output_file = OUTPUT_DIR / f"Averaged_results_{participant_id}.csv"
            participant_summary.to_csv(output_file, index=False, encoding="utf-8-sig")

            aggregated_frames.append(participant_summary)
            processed_files += 1
        except Exception as exc:
            skipped_files.append(f"{file_path.name}: {exc}")

    if aggregated_frames:
        combined = pd.concat(aggregated_frames, ignore_index=True)
        combined = combined[OUTPUT_COLUMNS]
        combined_output = OUTPUT_DIR / "Averaged_results_all_participants.csv"
        combined.to_csv(combined_output, index=False, encoding="utf-8-sig")
    else:
        combined_output = OUTPUT_DIR / "Averaged_results_all_participants.csv"
        pd.DataFrame(columns=OUTPUT_COLUMNS).to_csv(
            combined_output, index=False, encoding="utf-8-sig"
        )

    print(f"Processed {processed_files} participant file(s) from {INPUT_DIR.resolve()}")
    print(f"Saved outputs to {OUTPUT_DIR.resolve()}")

    if skipped_files:
        print("Skipped file(s):")
        for message in skipped_files:
            print(f"- {message}")


if __name__ == "__main__":
    main()
