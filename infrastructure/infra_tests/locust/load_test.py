import random
from locust import HttpUser, task, between, run_single_user, events
import time


class ApiUser(HttpUser):
    wait_time = between(1, 2)
    host = "http://localhost:8000"

    @task
    def post_and_poll(self):
        random_seed = random.randint(0, 10000)

        post_data = {
            "generation_settings": {
                "prompt": "A dog",
                "negative_prompt": "",
                "seed": random_seed,
                "sampler_name": "euler",
                "batch_size": 1,
                "n_iters": 1,
                "steps": 5,
                "cfg_scale": 7.0,
                "width": 512,
                "height": 512,
                "model": "v1-5-pruned-emaonly"
            },
            "metadata": {
                "grouping": "test/grouping"
            }
        }

        start_time = time.time()  # Record the start time of the POST request

        with self.client.post("/images/", json=post_data, catch_response=True) as post_response:
            if post_response.status_code == 202:
                image_id = str(post_response.json()["id"])

                while True:
                    with self.client.get(f"/images/{image_id}", name="/images/[id]", catch_response=True) as get_response:
                        if get_response.status_code == 200:
                            image_data = get_response.json()
                            if image_data.get("image_url"):
                                # Calculate total request time
                                total_time = int(
                                    (time.time() - start_time) * 1000)

                                # Fire a custom event to log the total time
                                events.request.fire(
                                    request_type="CUSTOM",
                                    name="Total time for image generation",
                                    response_time=total_time,
                                    response_length=0,
                                    exception=None,
                                )

                                get_response.success()
                                return
                        else:
                            get_response.failure(
                                f"Unexpected status code: {get_response.status_code}")

                        time.sleep(1)
            else:
                post_response.failure(
                    f"Failed to start image generation: {post_response.status_code}")


# if launched directly, e.g. "python3 debugging.py", not "locust -f debugging.py"
if __name__ == "__main__":
    run_single_user(ApiUser)
