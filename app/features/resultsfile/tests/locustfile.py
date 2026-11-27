from locust import HttpUser, TaskSet, between, task
from splent_framework.environment.host import get_host_for_locust_testing


class ResultsfileBehavior(TaskSet):
    @task
    def index(self):
        response = self.client.get("/resultsfile")
        if response.status_code != 200:
            print(f"Resultsfile index failed: {response.status_code}")


class ResultsfileUser(HttpUser):
    tasks = [ResultsfileBehavior]
    wait_time = between(5, 9)
    host = get_host_for_locust_testing()
