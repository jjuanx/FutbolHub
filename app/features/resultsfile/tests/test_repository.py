"""Repository-level tests for resultsfile and the football dataset type, against a real database."""

import pytest
from sqlalchemy.exc import DBAPIError

from app import db
from app.features.dataset.models import BaseDataset, DataSet, DSMetaData, FootballDataSet, PublicationType
from app.features.hubfile.models import Hubfile
from app.features.hubfile.repositories import HubfileRepository
from app.features.resultsfile.models import ResultsFile
from app.features.resultsfile.repositories import ResultsFileRepository

pytestmark = pytest.mark.repository


def test_football_dataset_round_trips_its_metadata(test_app, clean_database, make_user, make_football_dataset):
    with test_app.app_context():
        dataset_id = make_football_dataset(make_user()).id
        db.session.expire_all()

        stored = db.session.get(BaseDataset, dataset_id)
        assert type(stored) is FootballDataSet
        assert stored.dataset_type == "football"
        assert (stored.competition, stored.country, stored.season) == ("LaLiga", "España", "2023-24")
        assert stored.data_source == "https://www.football-data.co.uk"


def test_base_dataset_query_returns_every_type_and_subclasses_only_their_own(
    test_app, clean_database, make_user, make_football_dataset, make_uvl_dataset
):
    with test_app.app_context():
        user = make_user()
        uvl = make_uvl_dataset(user)
        football = make_football_dataset(user)

        assert {type(d) for d in BaseDataset.query.all()} == {DataSet, FootballDataSet}
        assert [d.id for d in DataSet.query.all()] == [uvl.id]
        assert [d.id for d in FootballDataSet.query.all()] == [football.id]


def test_user_data_sets_include_datasets_of_every_type(
    test_app, clean_database, make_user, make_football_dataset, make_uvl_dataset
):
    with test_app.app_context():
        user = make_user()
        uvl = make_uvl_dataset(user)
        football = make_football_dataset(user)
        db.session.expire_all()

        assert {d.id for d in user.data_sets} == {uvl.id, football.id}


def test_existing_uvl_rows_default_to_the_uvl_type(test_app, clean_database, make_user, make_uvl_dataset):
    with test_app.app_context():
        dataset = make_uvl_dataset(make_user())
        raw = db.session.execute(db.text("SELECT dataset_type FROM data_set WHERE id = :id"), {"id": dataset.id})
        assert raw.scalar_one() == "uvl"


def test_get_by_dataset_returns_only_that_datasets_files_in_order(
    test_app, clean_database, make_user, make_football_dataset
):
    with test_app.app_context():
        user = make_user()
        dataset = make_football_dataset(user, files=(("j1-19.csv", 190), ("j20-38.csv", 190)))
        make_football_dataset(user, title="Premier League 2023-24")

        found = ResultsFileRepository().get_by_dataset(dataset.id)
        assert [rf.files[0].name for rf in found] == ["j1-19.csv", "j20-38.csv"]
        assert ResultsFileRepository().count_results_files() == 3


def test_deleting_a_football_dataset_deletes_its_results_files_and_hubfiles(
    test_app, clean_database, make_user, make_football_dataset
):
    with test_app.app_context():
        dataset = make_football_dataset(make_user(), files=(("a.csv", 10), ("b.csv", 12)))
        dataset.delete()

        assert ResultsFile.query.count() == 0
        assert Hubfile.query.count() == 0


def test_hubfile_repository_finds_the_football_dataset_and_owner(
    test_app, clean_database, make_user, make_football_dataset, make_uvl_dataset
):
    with test_app.app_context():
        owner = make_user("owner@example.com")
        other = make_user("other@example.com")
        football = make_football_dataset(owner)
        uvl = make_uvl_dataset(other)
        football_file = football.results_files[0].files[0]
        uvl_file = uvl.feature_models[0].files[0]

        repo = HubfileRepository()
        assert repo.get_dataset_by_hubfile(football_file).id == football.id
        assert repo.get_owner_user_by_hubfile(football_file).id == owner.id
        assert repo.get_dataset_by_hubfile(uvl_file).id == uvl.id
        assert repo.get_owner_user_by_hubfile(uvl_file).id == other.id


def test_football_hubfile_path_is_under_its_dataset_folder(test_app, clean_database, make_user, make_football_dataset):
    with test_app.app_context():
        user = make_user()
        dataset = make_football_dataset(user)
        path = dataset.results_files[0].files[0].get_path()
        assert path.endswith(f"uploads/user_{user.id}/dataset_{dataset.id}/results.csv")


def test_a_hubfile_without_parent_is_rejected(test_app, clean_database):
    with test_app.app_context():
        db.session.add(Hubfile(name="orphan.csv", checksum="x", size=1))
        # MariaDB reports a failed CHECK as an OperationalError (4025), other engines as an IntegrityError.
        with pytest.raises(DBAPIError, match="ck_file_exactly_one_parent"):
            db.session.commit()
        db.session.rollback()


def test_a_hubfile_with_two_parents_is_rejected(
    test_app, clean_database, make_user, make_football_dataset, make_uvl_dataset
):
    with test_app.app_context():
        user = make_user()
        results_file_id = make_football_dataset(user).results_files[0].id
        feature_model_id = make_uvl_dataset(user).feature_models[0].id

        db.session.add(
            Hubfile(
                name="both.csv",
                checksum="x",
                size=1,
                feature_model_id=feature_model_id,
                results_file_id=results_file_id,
            )
        )
        # MariaDB reports a failed CHECK as an OperationalError (4025), other engines as an IntegrityError.
        with pytest.raises(DBAPIError, match="ck_file_exactly_one_parent"):
            db.session.commit()
        db.session.rollback()


@pytest.mark.parametrize("missing", ["competition", "country", "season", "number_of_teams", "data_source"])
def test_a_football_dataset_cannot_be_saved_without_its_metadata(test_app, clean_database, make_user, missing):
    with test_app.app_context():
        meta = DSMetaData(title="Incomplete", description="d", publication_type=PublicationType.OTHER)
        db.session.add(meta)
        db.session.flush()
        fields = {
            "competition": "LaLiga",
            "country": "España",
            "season": "2023-24",
            "number_of_teams": 20,
            "data_source": "https://www.football-data.co.uk",
        }
        del fields[missing]  # never assigned, so @validates does not run for it
        db.session.add(FootballDataSet(user_id=make_user().id, ds_meta_data_id=meta.id, **fields))

        with pytest.raises(ValueError, match=missing):
            db.session.flush()
        db.session.rollback()
