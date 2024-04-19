import os

import pytest
import requests

from event_horizon import create_app

HEADERS = {
    "accept": "application/json",
    "content-type": "application/json",
    "authorization": f"Bearer {os.getenv('NEON_TOKEN')}",
}


def get_test_db_connection():
    try:
        res = requests.post(
            f"https://console.neon.tech/api/v2/projects/{os.getenv('NEON_PROJECT_ID')}/branches",
            json={
                "branch": {"name": "test", "parent_id": os.getenv("NEON_DEV_BRANCH_ID")}
            },
            headers=HEADERS,
        )
        data = res.json()
        branch_id = data.get("branch", {}).get("id")
        roles = data.get("roles", [])
        databases = data.get("databases", [])

        try:
            compute_res = requests.post(
                f"https://console.neon.tech/api/v2/projects/{os.getenv('NEON_PROJECT_ID')}/endpoints",
                headers=HEADERS,
                json={"endpoint": {"branch_id": branch_id, "type": "read_write"}},
            )
            endpoint_id = compute_res.json()["endpoint"]["id"]

            try:
                requests.post(
                    f"https://console.neon.tech/api/v2/projects/{os.getenv('NEON_PROJECT_ID')}/endpoints/{endpoint_id}/start",
                    headers=HEADERS,
                )

                try:
                    conn_res = requests.get(
                        f"https://console.neon.tech/api/v2/projects/{os.getenv('NEON_PROJECT_ID')}/connection_uri",
                        headers=HEADERS,
                        params={
                            "branch_id": branch_id,
                            "database_name": databases[0]["name"],
                            "role_name": roles[0]["name"],
                        },
                    )
                    return (
                        conn_res.json()["uri"],
                        branch_id,
                        endpoint_id,
                    )
                except Exception:
                    raise
            except Exception:
                raise
        except Exception:
            raise
    except Exception:
        raise


def delete_test_branch(branch, endpoint):
    res = requests.delete(
        f"https://console.neon.tech/api/v2/projects/{os.getenv('NEON_PROJECT_ID')}/endpoints/{endpoint}",
        headers=HEADERS,
    )
    res = requests.delete(
        f"https://console.neon.tech/api/v2/projects/{os.getenv('NEON_PROJECT_ID')}/branches/{branch}",
        headers=HEADERS,
    )

    if res.status_code != 200:
        raise RuntimeError("failed to delete test branch")


def pytest_configure():
    pytest.test_user_id = None  # type: ignore


@pytest.fixture(scope="session")
def test_app():
    (test_db_uri, test_branch_id, endpoint_id) = get_test_db_connection()

    _, uri = test_db_uri.split("://")
    formatted_uri = "://".join(["postgresql+psycopg2", uri])
    app = create_app("test", formatted_uri)

    yield app

    delete_test_branch(test_branch_id, endpoint_id)


@pytest.fixture(scope="session")
def client(test_app):
    return test_app.test_client()


@pytest.fixture(scope="session")
def runner(test_app):
    return test_app.test_cli_runner()
