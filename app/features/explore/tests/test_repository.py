"""Repository-level tests for explore — the dataset search query against the DB."""

from datetime import datetime

import pytest

from app import db
from app.features.auth.models import User
from app.features.dataset.models import Author, DataSet, DSMetaData, PublicationType
from app.features.explore.repositories import ExploreRepository
from app.features.featuremodel.models import FeatureModel, FMMetaData

pytestmark = pytest.mark.repository


def _owner():
    user = User.query.filter_by(email="owner@example.com").first()
    if user is None:
        user = User(email="owner@example.com")
        user.set_password("ownerpass")
        db.session.add(user)
        db.session.flush()
    return user


def _make_dataset(
    title,
    description="a description",
    author_name="Anonymous Author",
    tags="",
    created_at=None,
    publication_type=PublicationType.JOURNAL_ARTICLE,
    dataset_doi="10.1234/default",
    with_feature_model=True,
    competition=None,
    season=None,
    country=None,
    teams=None,
):
    ds_meta_data = DSMetaData(
        title=title,
        description=description,
        publication_type=publication_type,
        dataset_doi=dataset_doi,
        tags=tags,
        competition=competition,
        season=season,
        country=country,
        teams=teams,
    )
    db.session.add(ds_meta_data)
    db.session.flush()
    db.session.add(Author(name=author_name, affiliation="Some University", ds_meta_data_id=ds_meta_data.id))
    dataset = DataSet(
        user_id=_owner().id,
        ds_meta_data_id=ds_meta_data.id,
        created_at=created_at or datetime(2024, 1, 1),
    )
    db.session.add(dataset)
    db.session.flush()
    if with_feature_model:
        fm_meta_data = FMMetaData(
            uvl_filename=f"{title.lower().replace(' ', '_')}.uvl",
            title=title,
            description=description,
            publication_type=publication_type,
            tags=tags,
        )
        db.session.add(fm_meta_data)
        db.session.flush()
        db.session.add(FeatureModel(data_set_id=dataset.id, fm_meta_data_id=fm_meta_data.id))
    db.session.commit()
    return dataset


def _seed_corpus():
    """Three searchable datasets plus two the query is expected to drop."""
    _make_dataset(
        title="Smart Home",
        description="home automation product line",
        author_name="Alice Doe",
        tags="iot,home",
        created_at=datetime(2024, 1, 1),
        publication_type=PublicationType.JOURNAL_ARTICLE,
        competition="LaLiga",
        season="2024-25",
        country="España",
        teams=["Sevilla FC", "Real Betis", "Real Madrid"],
    )
    _make_dataset(
        title="Car Configurator",
        description="vehicle variability",
        author_name="Bob Roe",
        tags="automotive",
        created_at=datetime(2024, 2, 1),
        publication_type=PublicationType.BOOK,
        competition="Premier League",
        season="2024-25",
        country="England",
        teams=["Arsenal", "Chelsea"],
    )
    _make_dataset(
        title="Home Banking",
        description="finance product line",
        author_name="Carol Poe",
        tags="finance",
        created_at=datetime(2024, 3, 1),
        publication_type=PublicationType.JOURNAL_ARTICLE,
        competition="LaLiga",
        season="2023-24",
        country="España",
        teams=["Real Madrid", "FC Barcelona"],
    )
    # Never returned: the query requires a non-null dataset_doi.
    _make_dataset(title="Draft Home", dataset_doi=None, created_at=datetime(2024, 4, 1))
    # Never returned: the query inner-joins feature models.
    _make_dataset(title="Modelless Home", with_feature_model=False, created_at=datetime(2024, 5, 1))


def _titles(datasets):
    return [dataset.ds_meta_data.title for dataset in datasets]


def test_blank_query_returns_every_eligible_dataset_newest_first(test_app, clean_database):
    with test_app.app_context():
        _seed_corpus()
        results = ExploreRepository().filter("")
        assert _titles(results) == ["Home Banking", "Car Configurator", "Smart Home"]


def test_whitespace_only_query_behaves_like_a_blank_query(test_app, clean_database):
    with test_app.app_context():
        _seed_corpus()
        assert _titles(ExploreRepository().filter("   ")) == ["Home Banking", "Car Configurator", "Smart Home"]


def test_query_narrows_results_to_matching_datasets(test_app, clean_database):
    with test_app.app_context():
        _seed_corpus()
        repository = ExploreRepository()
        assert _titles(repository.filter("banking")) == ["Home Banking"]
        assert _titles(repository.filter("home")) == ["Home Banking", "Smart Home"]
        assert _titles(repository.filter("nothingmatchesthis")) == []


def test_query_matches_author_name_case_insensitively(test_app, clean_database):
    with test_app.app_context():
        _seed_corpus()
        repository = ExploreRepository()
        assert _titles(repository.filter("alice")) == ["Smart Home"]
        assert _titles(repository.filter("ALICE")) == ["Smart Home"]


def test_query_matches_tags(test_app, clean_database):
    with test_app.app_context():
        _seed_corpus()
        assert _titles(ExploreRepository().filter("automotive")) == ["Car Configurator"]


def test_query_is_normalized_for_accents_and_punctuation(test_app, clean_database):
    with test_app.app_context():
        _seed_corpus()
        repository = ExploreRepository()
        assert _titles(repository.filter("hóme")) == ["Home Banking", "Smart Home"]
        assert _titles(repository.filter("¿home?!")) == ["Home Banking", "Smart Home"]


def test_multiple_words_are_combined_with_or(test_app, clean_database):
    with test_app.app_context():
        _seed_corpus()
        results = ExploreRepository().filter("banking automotive")
        assert _titles(results) == ["Home Banking", "Car Configurator"]


def test_oldest_sorting_reverses_the_result_order(test_app, clean_database):
    with test_app.app_context():
        _seed_corpus()
        repository = ExploreRepository()
        assert _titles(repository.filter("home", sorting="oldest")) == ["Smart Home", "Home Banking"]
        assert _titles(repository.filter("home", sorting="newest")) == ["Home Banking", "Smart Home"]


def test_datasets_without_a_doi_or_a_feature_model_are_never_returned(test_app, clean_database):
    with test_app.app_context():
        _seed_corpus()
        repository = ExploreRepository()
        assert _titles(repository.filter("draft")) == []
        assert _titles(repository.filter("modelless")) == []


def test_publication_type_narrows_the_results(test_app, clean_database):
    with test_app.app_context():
        _seed_corpus()
        repository = ExploreRepository()
        assert _titles(repository.filter("", publication_type="book")) == ["Car Configurator"]
        assert _titles(repository.filter("", publication_type="article")) == ["Home Banking", "Smart Home"]


def test_unknown_publication_type_is_ignored(test_app, clean_database):
    with test_app.app_context():
        _seed_corpus()
        repository = ExploreRepository()
        assert _titles(repository.filter("", publication_type="any")) == _titles(
            repository.filter("", publication_type="not-a-publication-type")
        )


def test_tags_narrow_the_results(test_app, clean_database):
    with test_app.app_context():
        _seed_corpus()
        repository = ExploreRepository()
        assert _titles(repository.filter("", tags=["iot"])) == ["Smart Home"]
        assert _titles(repository.filter("", tags=["automotive", "finance"])) == ["Home Banking", "Car Configurator"]
        assert _titles(repository.filter("", tags=["nonexistent"])) == []


def test_tags_combine_with_the_query(test_app, clean_database):
    with test_app.app_context():
        _seed_corpus()
        repository = ExploreRepository()
        # "home" alone matches two datasets; the tag narrows them to one.
        assert _titles(repository.filter("home")) == ["Home Banking", "Smart Home"]
        assert _titles(repository.filter("home", tags=["iot"])) == ["Smart Home"]


def test_filter_by_competition_season_country_and_team(test_app, clean_database):
    with test_app.app_context():
        _seed_corpus()
        repository = ExploreRepository()

        # Filtro por competición
        assert _titles(repository.filter("", competition="LaLiga")) == ["Home Banking", "Smart Home"]
        assert _titles(repository.filter("", competition="premier")) == ["Car Configurator"]

        # Filtro por temporada
        assert _titles(repository.filter("", season="2024-25")) == ["Car Configurator", "Smart Home"]
        assert _titles(repository.filter("", season="2023-24")) == ["Home Banking"]

        # Filtro por país (con y sin tilde)
        assert _titles(repository.filter("", country="España")) == ["Home Banking", "Smart Home"]
        assert _titles(repository.filter("", country="espana")) == ["Home Banking", "Smart Home"]
        assert _titles(repository.filter("", country="England")) == ["Car Configurator"]

        # Filtro por equipo
        assert _titles(repository.filter("", team="Sevilla FC")) == ["Smart Home"]
        assert _titles(repository.filter("", team="Real Madrid")) == ["Home Banking", "Smart Home"]
        assert _titles(repository.filter("", team="Arsenal")) == ["Car Configurator"]
        assert _titles(repository.filter("", team="Equipo Inexistente")) == []


def test_domain_filters_combine_with_each_other_and_with_query(test_app, clean_database):
    with test_app.app_context():
        _seed_corpus()
        repository = ExploreRepository()

        assert _titles(
            repository.filter(
                "",
                competition="LaLiga",
                season="2024-25",
                country="España",
                team="Real Madrid",
            )
        ) == ["Smart Home"]

        assert _titles(
            repository.filter(
                "home",
                competition="LaLiga",
                team="FC Barcelona",
            )
        ) == ["Home Banking"]


def test_team_filter_detects_teams_playing_in_dataset_csv_files(test_app, clean_database, tmp_path, monkeypatch):
    monkeypatch.setenv("WORKING_DIR", str(tmp_path))
    with test_app.app_context():
        ds = _make_dataset(
            title="LaLiga CSV Temporada",
            competition="LaLiga",
            season="2024-25",
            country="España",
        )
        upload_dir = tmp_path / "uploads" / f"user_{ds.user_id}" / f"dataset_{ds.id}"
        upload_dir.mkdir(parents=True)
        (upload_dir / "jornada1.csv").write_text(
            "jornada,fecha,local,visitante,goles_local,goles_visitante\n" "1,2024-08-15,Girona FC,Rayo Vallecano,2,1\n",
            encoding="utf-8",
        )

        repository = ExploreRepository()
        assert _titles(repository.filter("", team="Girona FC")) == ["LaLiga CSV Temporada"]
        assert _titles(repository.filter("", team="Rayo Vallecano")) == ["LaLiga CSV Temporada"]
        assert _titles(repository.filter("", team="Juventus")) == []
