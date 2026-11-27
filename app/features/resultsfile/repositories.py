from splent_framework.repositories.BaseRepository import BaseRepository
from sqlalchemy import func

from app.features.resultsfile.models import ResultsFile


class ResultsFileRepository(BaseRepository):
    def __init__(self):
        super().__init__(ResultsFile)

    def count_results_files(self) -> int:
        return self.model.query.with_entities(func.count(self.model.id)).scalar() or 0

    def get_by_dataset(self, dataset_id: int) -> list[ResultsFile]:
        return self.model.query.filter_by(data_set_id=dataset_id).order_by(self.model.id).all()
