"""Service-level tests for resultsfile — services and repositories against a real database."""

import pytest

from app.features.resultsfile.services import ResultsFileService

pytestmark = pytest.mark.service


def test_total_matches_adds_up_the_files_of_the_dataset(test_app, clean_database, make_user, make_football_dataset):
    with test_app.app_context():
        user = make_user()
        dataset = make_football_dataset(user, files=(("j1-19.csv", 190), ("j20-38.csv", 180)))
        make_football_dataset(user, title="Other", files=(("other.csv", 999),))

        assert ResultsFileService().total_matches(dataset.id) == 370


def test_total_matches_counts_files_with_unknown_matches_as_zero(
    test_app, clean_database, make_user, make_football_dataset
):
    with test_app.app_context():
        dataset = make_football_dataset(make_user(), files=(("known.csv", 10), ("pending.csv", None)))
        assert ResultsFileService().total_matches(dataset.id) == 10


def test_total_matches_of_a_dataset_without_files_is_zero(test_app, clean_database, make_user, make_football_dataset):
    with test_app.app_context():
        dataset = make_football_dataset(make_user(), files=())
        assert ResultsFileService().total_matches(dataset.id) == 0


def test_count_results_files(test_app, clean_database, make_user, make_football_dataset):
    with test_app.app_context():
        make_football_dataset(make_user(), files=(("a.csv", 1), ("b.csv", 2)))
        assert ResultsFileService().count_results_files() == 2


def test_football_dataset_to_dict_exposes_type_and_metadata(test_app, clean_database, make_user, make_football_dataset):
    with test_app.test_request_context("/"):
        data = make_football_dataset(make_user()).to_dict()

        assert data["dataset_type"] == "football"
        assert data["competition"] == "LaLiga"
        assert data["season"] == "2023-24"
        assert data["files_count"] == 1
        assert data["files"][0]["name"] == "results.csv"
