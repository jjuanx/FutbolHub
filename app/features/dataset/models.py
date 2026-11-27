from datetime import datetime
from enum import Enum

from flask import request
from sqlalchemy import Enum as SQLAlchemyEnum
from sqlalchemy import event
from sqlalchemy.orm import validates

from app import db

MIN_TEAMS = 2
MAX_TEAMS = 100


class PublicationType(Enum):
    NONE = "none"
    ANNOTATION_COLLECTION = "annotationcollection"
    BOOK = "book"
    BOOK_SECTION = "section"
    CONFERENCE_PAPER = "conferencepaper"
    DATA_MANAGEMENT_PLAN = "datamanagementplan"
    JOURNAL_ARTICLE = "article"
    PATENT = "patent"
    PREPRINT = "preprint"
    PROJECT_DELIVERABLE = "deliverable"
    PROJECT_MILESTONE = "milestone"
    PROPOSAL = "proposal"
    REPORT = "report"
    SOFTWARE_DOCUMENTATION = "softwaredocumentation"
    TAXONOMIC_TREATMENT = "taxonomictreatment"
    TECHNICAL_NOTE = "technicalnote"
    THESIS = "thesis"
    WORKING_PAPER = "workingpaper"
    OTHER = "other"


class Author(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    affiliation = db.Column(db.String(120))
    orcid = db.Column(db.String(120))
    ds_meta_data_id = db.Column(db.Integer, db.ForeignKey("ds_meta_data.id"))
    fm_meta_data_id = db.Column(db.Integer, db.ForeignKey("fm_meta_data.id"))

    def to_dict(self):
        return {"name": self.name, "affiliation": self.affiliation, "orcid": self.orcid}


class DatasetType(Enum):
    """Dataset types the hub supports. The value is the discriminator stored in ``data_set.dataset_type``."""

    UVL = "uvl"
    FOOTBALL = "football"


class DSMetrics(db.Model):
    """Metrics of a dataset. Each type fills only its own pair of columns.

    - UVL: ``number_of_models`` and ``number_of_features``.
    - Football: ``number_of_matches`` and ``number_of_teams`` (computed from the CSV files).
    """

    id = db.Column(db.Integer, primary_key=True)
    number_of_models = db.Column(db.String(120))
    number_of_features = db.Column(db.String(120))
    number_of_matches = db.Column(db.Integer)
    number_of_teams = db.Column(db.Integer)

    def __repr__(self):
        if self.number_of_matches is not None or self.number_of_teams is not None:
            return f"DSMetrics<matches={self.number_of_matches}, teams={self.number_of_teams}>"
        return f"DSMetrics<models={self.number_of_models}, features={self.number_of_features}>"


class DSMetaData(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    deposition_id = db.Column(db.Integer)
    title = db.Column(db.String(120), nullable=False)
    description = db.Column(db.Text, nullable=False)
    publication_type = db.Column(SQLAlchemyEnum(PublicationType), nullable=False)
    publication_doi = db.Column(db.String(120))
    dataset_doi = db.Column(db.String(120))
    tags = db.Column(db.String(120))
    ds_metrics_id = db.Column(db.Integer, db.ForeignKey("ds_metrics.id"))
    ds_metrics = db.relationship("DSMetrics", uselist=False, backref="ds_meta_data", cascade="all, delete")
    authors = db.relationship("Author", backref="ds_meta_data", lazy=True, cascade="all, delete")


class BaseDataset(db.Model):
    """Common part of every dataset, whatever its type.

    Single-table inheritance over ``data_set``: ``dataset_type`` says which subclass a row is.
    Query ``BaseDataset`` to get datasets of every type, or a subclass to get only that type.
    Subclasses implement ``files()``, which returns the dataset's ``Hubfile`` objects.
    """

    __tablename__ = "data_set"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    dataset_type = db.Column(db.String(20), nullable=False, server_default=DatasetType.UVL.value)

    ds_meta_data_id = db.Column(db.Integer, db.ForeignKey("ds_meta_data.id"), nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    ds_meta_data = db.relationship("DSMetaData", backref=db.backref("data_set", uselist=False))

    __mapper_args__ = {"polymorphic_on": dataset_type}

    def files(self):
        raise NotImplementedError(f"{type(self).__name__} must implement files()")

    def name(self):
        return self.ds_meta_data.title

    def delete(self):
        db.session.delete(self)
        db.session.commit()

    def get_cleaned_publication_type(self):
        return self.ds_meta_data.publication_type.name.replace("_", " ").title()

    def get_zenodo_url(self):
        if self.ds_meta_data.dataset_doi and self.ds_meta_data.deposition_id:
            return f"https://zenodo.org/record/{self.ds_meta_data.deposition_id}"
        return None

    def get_files_count(self):
        return len(self.files())

    def get_file_total_size(self):
        return sum(file.size for file in self.files())

    def get_file_total_size_for_human(self):
        from app.features.dataset.services import SizeService

        return SizeService().get_human_readable_size(self.get_file_total_size())

    def get_uvlhub_doi(self):
        from app.features.dataset.services import DataSetService

        return DataSetService().get_uvlhub_doi(self)

    def to_dict(self):
        files = self.files()
        return {
            "title": self.ds_meta_data.title,
            "id": self.id,
            "dataset_type": self.dataset_type,
            "created_at": self.created_at,
            "created_at_timestamp": int(self.created_at.timestamp()),
            "description": self.ds_meta_data.description,
            "authors": [author.to_dict() for author in self.ds_meta_data.authors],
            "publication_type": self.get_cleaned_publication_type(),
            "publication_doi": self.ds_meta_data.publication_doi,
            "dataset_doi": self.ds_meta_data.dataset_doi,
            "tags": self.ds_meta_data.tags.split(",") if self.ds_meta_data.tags else [],
            "url": self.get_uvlhub_doi(),
            "download": f'{request.host_url.rstrip("/")}/dataset/download/{self.id}',
            "zenodo": self.get_zenodo_url(),
            "files": [file.to_dict() for file in files],
            "files_count": len(files),
            "total_size_in_bytes": sum(file.size for file in files),
            "total_size_in_human_format": self.get_file_total_size_for_human(),
        }

    def __repr__(self):
        return f"{type(self).__name__}<{self.id}>"


class DataSet(BaseDataset):
    """UVL dataset: one or more feature models, each with its own metadata and UVL files."""

    __tablename__ = None  # single-table inheritance: Flask-SQLAlchemy must not derive a table name
    __mapper_args__ = {"polymorphic_identity": DatasetType.UVL.value}

    feature_models = db.relationship("FeatureModel", backref="data_set", lazy=True, cascade="all, delete")

    def files(self):
        return [file for fm in self.feature_models for file in fm.files]


def validate_number_of_teams(value):
    """Validate the number of teams declared in a football dataset and return it as an ``int``.

    Raise ``ValueError`` with a clear message when the value is not acceptable.
    Note that values coming from a form may arrive as strings (e.g. ``"20"``).
    """
    if value is None or isinstance(value, bool):
        raise ValueError("number_of_teams is required for a football dataset")
    try:
        teams = int(str(value).strip())
    except ValueError:
        raise ValueError(f"number_of_teams must be a whole number, got {value!r}")
    if not MIN_TEAMS <= teams <= MAX_TEAMS:
        raise ValueError(f"number_of_teams must be between {MIN_TEAMS} and {MAX_TEAMS}, got {teams}")
    return teams


class FootballDataSet(BaseDataset):
    """Football results dataset: one season of a competition, stored in one or more results CSV files.

    The football metadata lives on the dataset (option C of #15), not on each file. The columns are
    nullable in the database because they share ``data_set`` with the other types, so they are
    validated here instead.
    """

    __tablename__ = None  # single-table inheritance: Flask-SQLAlchemy must not derive a table name
    __mapper_args__ = {"polymorphic_identity": DatasetType.FOOTBALL.value}

    competition = db.Column(db.String(120))
    country = db.Column(db.String(120))
    season = db.Column(db.String(9))
    number_of_teams = db.Column(db.Integer)
    data_source = db.Column(db.String(255))

    results_files = db.relationship("ResultsFile", backref="data_set", lazy=True, cascade="all, delete")

    @validates("competition", "country", "data_source")
    def _validate_required_text(self, key, value):
        if value is None or not str(value).strip():
            raise ValueError(f"{key} is required for a football dataset")
        return str(value).strip()

    @validates("season")
    def _validate_season(self, key, value):
        from app.features.dataset.csv_validator import parse_season_range

        season = (value or "").strip()
        if not season:
            raise ValueError("season is required for a football dataset")
        parse_season_range(season=season)  # raises ValueError if the format is not recognised
        return season

    @validates("number_of_teams")
    def _validate_number_of_teams(self, key, value):
        return validate_number_of_teams(value)

    def season_range(self):
        """First and last day of the declared season, as used by the CSV validator."""
        from app.features.dataset.csv_validator import parse_season_range

        return parse_season_range(season=self.season)

    def files(self):
        return [file for results_file in self.results_files for file in results_file.files]

    def to_dict(self):
        data = super().to_dict()
        data.update(
            {
                "competition": self.competition,
                "country": self.country,
                "season": self.season,
                "number_of_teams": self.number_of_teams,
                "data_source": self.data_source,
            }
        )
        return data


FOOTBALL_REQUIRED_FIELDS = ("competition", "country", "season", "number_of_teams", "data_source")


@event.listens_for(FootballDataSet, "before_insert")
def _check_football_required_fields(mapper, connection, target):
    """``@validates`` only runs on assignment, so a field never assigned would be stored as NULL."""
    missing = [field for field in FOOTBALL_REQUIRED_FIELDS if getattr(target, field) is None]
    if missing:
        raise ValueError(f"Missing metadata for a football dataset: {', '.join(missing)}")


class DSDownloadRecord(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=True)
    dataset_id = db.Column(db.Integer, db.ForeignKey("data_set.id"))
    download_date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    download_cookie = db.Column(db.String(36), nullable=False)  # Assuming UUID4 strings

    def __repr__(self):
        return (
            f"<Download id={self.id} "
            f"dataset_id={self.dataset_id} "
            f"date={self.download_date} "
            f"cookie={self.download_cookie}>"
        )


class DSViewRecord(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=True)
    dataset_id = db.Column(db.Integer, db.ForeignKey("data_set.id"))
    view_date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    view_cookie = db.Column(db.String(36), nullable=False)  # Assuming UUID4 strings

    def __repr__(self):
        return f"<View id={self.id} dataset_id={self.dataset_id} date={self.view_date} cookie={self.view_cookie}>"


class DOIMapping(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    dataset_doi_old = db.Column(db.String(120))
    dataset_doi_new = db.Column(db.String(120))
