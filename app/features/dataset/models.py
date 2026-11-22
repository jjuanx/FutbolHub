from datetime import datetime
from enum import Enum

from flask import request
from sqlalchemy import Enum as SQLAlchemyEnum
from sqlalchemy import event

from app import db


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


class DSMetrics(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    number_of_models = db.Column(db.String(120))
    number_of_features = db.Column(db.String(120))

    def __init__(self, **kwargs):
        if "number_of_matches" in kwargs and "number_of_models" not in kwargs:
            val = kwargs.pop("number_of_matches")
            kwargs["number_of_models"] = str(val) if val is not None else None
        else:
            kwargs.pop("number_of_matches", None)
        if "number_of_teams" in kwargs and "number_of_features" not in kwargs:
            val = kwargs.pop("number_of_teams")
            kwargs["number_of_features"] = str(val) if val is not None else None
        else:
            kwargs.pop("number_of_teams", None)
        super().__init__(**kwargs)

    @property
    def number_of_matches(self) -> int | None:
        if self.number_of_models is None or str(self.number_of_models).strip() == "":
            return None
        try:
            return int(str(self.number_of_models).strip())
        except ValueError:
            return None

    @number_of_matches.setter
    def number_of_matches(self, value) -> None:
        self.number_of_models = str(value) if value is not None else None

    @property
    def number_of_teams(self) -> int | None:
        if self.number_of_features is None or str(self.number_of_features).strip() == "":
            return None
        try:
            return int(str(self.number_of_features).strip())
        except ValueError:
            return None

    @number_of_teams.setter
    def number_of_teams(self, value) -> None:
        self.number_of_features = str(value) if value is not None else None

    def __repr__(self):
        return f"DSMetrics<models={self.number_of_models}, features={self.number_of_features}>"


class DSMetaData(db.Model):
    _domain_registry: dict[int, dict[str, object]] = {}

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

    def __init__(self, **kwargs):
        domain_fields = {}
        for key in ("competition", "season", "country", "teams", "source", "number_of_matches", "number_of_teams"):
            if key in kwargs:
                domain_fields[key] = kwargs.pop(key)
        super().__init__(**kwargs)
        self._pending_domain_fields = domain_fields
        for key, value in domain_fields.items():
            setattr(self, key, value)

    def _get_domain_field(self, name: str):
        pending = getattr(self, "_pending_domain_fields", None)
        if pending and name in pending:
            return pending[name]
        if self.id is not None and self.id in self._domain_registry:
            return self._domain_registry[self.id].get(name)
        return None

    def _set_domain_field(self, name: str, value) -> None:
        pending = getattr(self, "_pending_domain_fields", None)
        if pending is None:
            pending = {}
            self._pending_domain_fields = pending
        pending[name] = value
        if self.id is not None:
            self._domain_registry.setdefault(self.id, {})[name] = value

    def sync_domain_registry(self) -> None:
        pending = getattr(self, "_pending_domain_fields", None)
        if self.id is not None:
            self._domain_registry[self.id] = dict(pending or {})

    @property
    def competition(self):
        return self._get_domain_field("competition")

    @competition.setter
    def competition(self, value) -> None:
        self._set_domain_field("competition", value)

    @property
    def season(self):
        return self._get_domain_field("season")

    @season.setter
    def season(self, value) -> None:
        self._set_domain_field("season", value)

    @property
    def country(self):
        return self._get_domain_field("country")

    @country.setter
    def country(self, value) -> None:
        self._set_domain_field("country", value)

    @property
    def teams(self):
        return self._get_domain_field("teams")

    @teams.setter
    def teams(self, value) -> None:
        self._set_domain_field("teams", value)

    @property
    def number_of_matches(self):
        val = self._get_domain_field("number_of_matches")
        if val is not None:
            return int(val)
        if self.ds_metrics and self.ds_metrics.number_of_matches is not None:
            return self.ds_metrics.number_of_matches
        return None

    @number_of_matches.setter
    def number_of_matches(self, value) -> None:
        self._set_domain_field("number_of_matches", value)

    @property
    def number_of_teams(self):
        val = self._get_domain_field("number_of_teams")
        if val is not None:
            return int(val)
        if self.ds_metrics and self.ds_metrics.number_of_teams is not None:
            return self.ds_metrics.number_of_teams
        return None

    @number_of_teams.setter
    def number_of_teams(self, value) -> None:
        self._set_domain_field("number_of_teams", value)


@event.listens_for(DSMetaData, "after_insert")
@event.listens_for(DSMetaData, "after_update")
def _sync_ds_metadata_domain_registry(_mapper, _connection, target: DSMetaData) -> None:
    target.sync_domain_registry()


class DataSet(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)

    ds_meta_data_id = db.Column(db.Integer, db.ForeignKey("ds_meta_data.id"), nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    ds_meta_data = db.relationship("DSMetaData", backref=db.backref("data_set", uselist=False))
    feature_models = db.relationship("FeatureModel", backref="data_set", lazy=True, cascade="all, delete")

    def name(self):
        return self.ds_meta_data.title

    def files(self):
        return [file for fm in self.feature_models for file in fm.files]

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
        return sum(len(fm.files) for fm in self.feature_models)

    def get_file_total_size(self):
        return sum(file.size for fm in self.feature_models for file in fm.files)

    def get_file_total_size_for_human(self):
        from app.features.dataset.services import SizeService

        return SizeService().get_human_readable_size(self.get_file_total_size())

    def get_uvlhub_doi(self):
        from app.features.dataset.services import DataSetService

        return DataSetService().get_uvlhub_doi(self)

    def to_dict(self):
        return {
            "title": self.ds_meta_data.title,
            "id": self.id,
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
            "files": [file.to_dict() for fm in self.feature_models for file in fm.files],
            "files_count": self.get_files_count(),
            "total_size_in_bytes": self.get_file_total_size(),
            "total_size_in_human_format": self.get_file_total_size_for_human(),
        }

    def __repr__(self):
        return f"DataSet<{self.id}>"


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
