from locust import HttpLocust, TaskSet, task

class WebsiteTasks(TaskSet):
    def on_start(self):
        pass

    @task(1)
    def index(self):
        self.client.get("/")

    @task(2)
    def about(self):
        self.client.get("/about/")

class WebsiteUser(HttpLocust):
    host = 'http://debugtalk.com'
    task_set = WebsiteTasks
    min_wait = 1000
    max_wait = 3000
