from splent_framework.services.BaseService import BaseService

from app.features.resultsfile.repositories import ResultsFileRepository


class ResultsFileService(BaseService):
    def __init__(self):
        super().__init__(ResultsFileRepository())

    def count_results_files(self) -> int:
        return self.repository.count_results_files()

    def get_by_dataset(self, dataset_id: int):
        return self.repository.get_by_dataset(dataset_id)

    def total_matches(self, dataset_id: int) -> int:
        """Matches of a dataset, summing its files. Files whose matches are unknown count as 0."""
        return sum(rf.number_of_matches or 0 for rf in self.get_by_dataset(dataset_id))
