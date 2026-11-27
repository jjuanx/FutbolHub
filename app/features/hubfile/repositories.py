from splent_framework.repositories.BaseRepository import BaseRepository
from sqlalchemy import func

from app import db
from app.features.auth.models import User
from app.features.dataset.models import BaseDataset
from app.features.featuremodel.models import FeatureModel
from app.features.hubfile.models import Hubfile, HubfileDownloadRecord, HubfileViewRecord
from app.features.resultsfile.models import ResultsFile


class HubfileRepository(BaseRepository):
    def __init__(self):
        super().__init__(Hubfile)

    def get_owner_user_by_hubfile(self, hubfile: Hubfile) -> User:
        dataset = self.get_dataset_by_hubfile(hubfile)
        return dataset.user if dataset else None

    def get_dataset_by_hubfile(self, hubfile: Hubfile) -> BaseDataset:
        """Dataset of the file, whatever its type: UVL (through its feature model) or football (its results file)."""
        uvl = (
            db.session.query(BaseDataset)
            .join(FeatureModel, FeatureModel.data_set_id == BaseDataset.id)
            .join(Hubfile, Hubfile.feature_model_id == FeatureModel.id)
            .filter(Hubfile.id == hubfile.id)
        )
        football = (
            db.session.query(BaseDataset)
            .join(ResultsFile, ResultsFile.data_set_id == BaseDataset.id)
            .join(Hubfile, Hubfile.results_file_id == ResultsFile.id)
            .filter(Hubfile.id == hubfile.id)
        )
        return uvl.first() or football.first()


class HubfileViewRecordRepository(BaseRepository):
    def __init__(self):
        super().__init__(HubfileViewRecord)

    def total_hubfile_views(self) -> int:
        return self.model.query.with_entities(func.count(self.model.id)).scalar() or 0

    def find_by_user_file_cookie(self, user_id, file_id: int, cookie: str):
        return self.model.query.filter_by(user_id=user_id, file_id=file_id, view_cookie=cookie).first()


class HubfileDownloadRecordRepository(BaseRepository):
    def __init__(self):
        super().__init__(HubfileDownloadRecord)

    def total_hubfile_downloads(self) -> int:
        return self.model.query.with_entities(func.count(self.model.id)).scalar() or 0

    def find_by_user_file_cookie(self, user_id, file_id: int, cookie: str):
        return self.model.query.filter_by(user_id=user_id, file_id=file_id, download_cookie=cookie).first()
