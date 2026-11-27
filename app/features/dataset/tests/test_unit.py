"""Unit tests for dataset — pure logic, no app context and no database.

The helpers under test are either module-level functions or methods that only
read attributes off ``self``, so they are exercised against lightweight stubs
instead of persisted rows.
"""

import hashlib
from datetime import date
from types import SimpleNamespace

import pytest

from app.features.dataset.forms import DataSetForm
from app.features.dataset.models import (
    MAX_TEAMS,
    MIN_TEAMS,
    BaseDataset,
    DataSet,
    DatasetType,
    DSMetrics,
    FootballDataSet,
    PublicationType,
    validate_number_of_teams,
)
from app.features.dataset.services import SizeService, calculate_checksum_and_size
from app.features.featuremodel.models import FeatureModel
from app.features.hubfile.models import Hubfile
from app.features.resultsfile.models import ResultsFile

pytestmark = pytest.mark.unit


@pytest.mark.parametrize(
    "size, expected",
    [
        (0, "0 bytes"),
        (512, "512 bytes"),
        (1023, "1023 bytes"),
        (1024, "1.0 KB"),
        (1536, "1.5 KB"),
        (1024**2, "1.0 MB"),
        (5 * 1024**2, "5.0 MB"),
        (1024**3, "1.0 GB"),
    ],
)
def test_get_human_readable_size_picks_the_right_unit(size, expected):
    assert SizeService().get_human_readable_size(size) == expected


def test_calculate_checksum_and_size_matches_file_contents(tmp_path):
    content = b"features\n\tRoot\n"
    uvl = tmp_path / "model.uvl"
    uvl.write_bytes(content)

    checksum, size = calculate_checksum_and_size(str(uvl))

    assert checksum == hashlib.md5(content).hexdigest()
    assert size == len(content)


def test_convert_publication_type_maps_enum_value_to_name():
    assert DataSetForm.convert_publication_type(None, "article") == "JOURNAL_ARTICLE"
    assert DataSetForm.convert_publication_type(None, "datamanagementplan") == "DATA_MANAGEMENT_PLAN"


def test_convert_publication_type_falls_back_to_none_for_unknown_values():
    assert DataSetForm.convert_publication_type(None, "not-a-publication-type") == "NONE"


def test_get_cleaned_publication_type_humanises_the_enum_name():
    dataset = SimpleNamespace(ds_meta_data=SimpleNamespace(publication_type=PublicationType.DATA_MANAGEMENT_PLAN))

    assert DataSet.get_cleaned_publication_type(dataset) == "Data Management Plan"


def test_get_zenodo_url_is_none_without_a_dataset_doi():
    dataset = SimpleNamespace(ds_meta_data=SimpleNamespace(deposition_id=42, dataset_doi=None))

    assert DataSet.get_zenodo_url(dataset) is None


def test_get_zenodo_url_is_none_without_a_deposition_id():
    dataset = SimpleNamespace(ds_meta_data=SimpleNamespace(deposition_id=None, dataset_doi="10.1234/dataset1"))

    assert DataSet.get_zenodo_url(dataset) is None


def test_get_zenodo_url_points_at_the_deposition_record():
    dataset = SimpleNamespace(ds_meta_data=SimpleNamespace(deposition_id=42, dataset_doi="10.1234/dataset1"))

    assert DataSet.get_zenodo_url(dataset) == "https://zenodo.org/record/42"


def test_files_and_sizes_are_aggregated_across_feature_models():
    # Transient objects (never persisted): the counters go through files(), which each type implements.
    dataset = DataSet(
        feature_models=[
            FeatureModel(files=[Hubfile(size=100), Hubfile(size=200)]),
            FeatureModel(files=[Hubfile(size=724)]),
        ]
    )

    assert dataset.get_files_count() == 3
    assert dataset.get_file_total_size() == 1024
    assert len(dataset.files()) == 3


def test_publication_type_none_is_the_documented_default_value():
    assert PublicationType.NONE.value == "none"
    assert PublicationType("article") is PublicationType.JOURNAL_ARTICLE


# --------------------------------------------------------------------------
# Dataset types (#16): common BaseDataset, UVL DataSet and FootballDataSet
# --------------------------------------------------------------------------


def _football(**overrides):
    fields = {
        "competition": "LaLiga",
        "country": "España",
        "season": "2023-24",
        "number_of_teams": 20,
        "data_source": "https://www.football-data.co.uk",
    }
    fields.update(overrides)
    return FootballDataSet(**fields)


def test_dataset_type_values_are_the_stored_discriminators():
    assert DatasetType.UVL.value == "uvl"
    assert DatasetType.FOOTBALL.value == "football"


def test_each_dataset_class_sets_its_own_type_on_creation():
    assert DataSet().dataset_type == "uvl"
    assert _football().dataset_type == "football"


def test_both_dataset_types_share_the_common_base():
    assert isinstance(DataSet(), BaseDataset)
    assert isinstance(_football(), BaseDataset)
    assert not isinstance(_football(), DataSet)


def test_base_dataset_requires_subclasses_to_list_their_files():
    with pytest.raises(NotImplementedError):
        BaseDataset.files(SimpleNamespace())


def test_football_dataset_keeps_the_declared_metadata():
    dataset = _football()
    assert dataset.competition == "LaLiga"
    assert dataset.country == "España"
    assert dataset.season == "2023-24"
    assert dataset.number_of_teams == 20
    assert dataset.data_source == "https://www.football-data.co.uk"


def test_football_dataset_strips_surrounding_whitespace():
    dataset = _football(competition="  Premier League ", season=" 2023/2024 ")
    assert dataset.competition == "Premier League"
    assert dataset.season == "2023/2024"


@pytest.mark.parametrize("field", ["competition", "country", "season", "data_source"])
@pytest.mark.parametrize("value", [None, "", "   "])
def test_football_dataset_rejects_missing_required_metadata(field, value):
    with pytest.raises(ValueError, match=field):
        _football(**{field: value})


@pytest.mark.parametrize(
    "value, expected",
    [
        (MIN_TEAMS, MIN_TEAMS),
        (MIN_TEAMS + 1, MIN_TEAMS + 1),
        (20, 20),
        (MAX_TEAMS - 1, MAX_TEAMS - 1),
        (MAX_TEAMS, MAX_TEAMS),
        ("20", 20),
        (" 20 ", 20),
    ],
)
def test_number_of_teams_accepts_whole_numbers_within_the_limits(value, expected):
    assert validate_number_of_teams(value) == expected
    assert _football(number_of_teams=value).number_of_teams == expected


@pytest.mark.parametrize("value", [MIN_TEAMS - 1, MAX_TEAMS + 1, 0, -20, "1", "101"])
def test_number_of_teams_rejects_values_outside_the_limits(value):
    with pytest.raises(ValueError, match="between"):
        validate_number_of_teams(value)


@pytest.mark.parametrize("value", [20.5, "20.5", "veinte", "", "   "])
def test_number_of_teams_rejects_values_that_are_not_whole_numbers(value):
    with pytest.raises(ValueError, match="whole number"):
        validate_number_of_teams(value)


@pytest.mark.parametrize("value", [None, True, False])
def test_number_of_teams_rejects_missing_values_and_booleans(value):
    with pytest.raises(ValueError, match="required"):
        validate_number_of_teams(value)


def test_football_dataset_validates_the_number_of_teams_on_assignment():
    with pytest.raises(ValueError):
        _football(number_of_teams=1)


@pytest.mark.parametrize("field, max_length", [("competition", 120), ("country", 120), ("data_source", 255)])
def test_football_text_metadata_accepts_values_up_to_the_column_length(field, max_length):
    assert len(getattr(_football(**{field: "x" * max_length}), field)) == max_length


@pytest.mark.parametrize("field, max_length", [("competition", 120), ("country", 120), ("data_source", 255)])
def test_football_text_metadata_rejects_values_longer_than_the_column(field, max_length):
    with pytest.raises(ValueError, match=f"{field} must be at most {max_length}"):
        _football(**{field: "x" * (max_length + 1)})


@pytest.mark.parametrize("season", ["23-24", "2023-", "temporada 2023", "2023-24-25"])
def test_football_dataset_rejects_unrecognised_season_formats(season):
    with pytest.raises(ValueError):
        _football(season=season)


@pytest.mark.parametrize(
    "season, expected",
    [
        ("2023-24", (date(2023, 7, 1), date(2024, 6, 30))),
        ("2023/2024", (date(2023, 7, 1), date(2024, 6, 30))),
        ("1999-00", (date(1999, 7, 1), date(2000, 6, 30))),
        ("2024", (date(2024, 1, 1), date(2024, 12, 31))),
    ],
)
def test_football_season_range_matches_the_csv_validator(season, expected):
    assert _football(season=season).season_range() == expected


def test_football_files_are_aggregated_across_results_files():
    dataset = _football()
    dataset.results_files = [
        ResultsFile(files=[Hubfile(name="j1-19.csv", checksum="a", size=100)]),
        ResultsFile(files=[Hubfile(name="j20-38.csv", checksum="b", size=250)]),
    ]
    assert [f.name for f in dataset.files()] == ["j1-19.csv", "j20-38.csv"]
    assert dataset.get_files_count() == 2
    assert dataset.get_file_total_size() == 350


def test_hubfile_parent_is_its_feature_model_or_its_results_file():
    feature_model, results_file = FeatureModel(), ResultsFile()
    assert Hubfile(feature_model=feature_model).parent() is feature_model
    assert Hubfile(results_file=results_file).parent() is results_file


def test_ds_metrics_repr_shows_the_metrics_of_its_type():
    assert repr(DSMetrics(number_of_models="3", number_of_features="40")) == "DSMetrics<models=3, features=40>"
    assert repr(DSMetrics(number_of_matches=380, number_of_teams=20)) == "DSMetrics<matches=380, teams=20>"


def test_dataset_repr_names_its_type():
    assert repr(DataSet(id=4)) == "DataSet<4>"
    assert repr(_football(id=5)) == "FootballDataSet<5>"
