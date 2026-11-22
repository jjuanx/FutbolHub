from splent_framework.services.BaseService import BaseService

from app.features.explore.repositories import ExploreRepository


class ExploreService(BaseService):
    def __init__(self):
        super().__init__(ExploreRepository())

    def filter(
        self,
        query="",
        sorting="newest",
        publication_type="any",
        tags=[],
        author="",
        date_from=None,
        date_to=None,
        competition="",
        season="",
        country="",
        team="",
        min_matches=None,
        max_matches=None,
        min_teams=None,
        max_teams=None,
        **kwargs,
    ):
        return self.repository.filter(
            query=query,
            sorting=sorting,
            publication_type=publication_type,
            tags=tags,
            author=author,
            date_from=date_from,
            date_to=date_to,
            competition=competition,
            season=season,
            country=country,
            team=team,
            min_matches=min_matches,
            max_matches=max_matches,
            min_teams=min_teams,
            max_teams=max_teams,
            **kwargs,
        )
