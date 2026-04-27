import pandas as pd

from phases.phase1_data_ingestion.data_pipeline.validate import validate_canonical


def test_validate_filters_invalid_and_duplicates() -> None:
    df = pd.DataFrame(
        [
            {
                "name": "A",
                "city": "Delhi",
                "locality": "CP",
                "cuisines": "Indian",
                "avg_cost_for_two": 500.0,
                "rating": 4.2,
                "votes": 100,
                "tags": None,
            },
            {
                "name": "A",
                "city": "Delhi",
                "locality": "CP",
                "cuisines": "Indian",
                "avg_cost_for_two": 500.0,
                "rating": 4.2,
                "votes": 100,
                "tags": None,
            },
            {
                "name": None,
                "city": "Delhi",
                "locality": "x",
                "cuisines": None,
                "avg_cost_for_two": 200,
                "rating": 3.0,
                "votes": 10,
                "tags": None,
            },
            {
                "name": "Bad rating",
                "city": "Delhi",
                "locality": "x",
                "cuisines": None,
                "avg_cost_for_two": 200,
                "rating": 6.0,
                "votes": 10,
                "tags": None,
            },
        ]
    )
    valid, report = validate_canonical(df)
    assert len(valid) == 1
    assert report.total_rows == 4
    assert report.valid_rows == 1
    assert report.duplicate_rows == 1
    assert report.missing_name_or_city == 1
    assert report.invalid_rating_rows == 1

