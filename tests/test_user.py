import json

UID = None


def test_list_users(client):
    res = client.get("/users")

    assert res.status_code == 200
    data = json.loads(res.data)["data"]
    data = [d for d in data if d["username"] != "julians"]
    assert len(data) == 10
    assert data[0]["username"] == "demoUser0"
    assert "password" not in data[0]
    assert "pagination" in json.loads(res.data)


def test_get_user(client):
    res = client.get("/users/2")

    assert res.status_code == 200
    data = json.loads(res.data)["data"]
    assert data["username"] == "demoUser0"
    assert "password" not in data


def test_create_user(client):
    global UID

    res = client.post(
        "/users",
        json={
            "username": "testUser",
            "password": "testPassword1234!",
            "email": "test@test.com",
        },
    )

    UID = json.loads(res.data)["data"]["id"]

    assert res.status_code == 201
    assert json.loads(res.data)["data"]["username"] == "testUser"


def test_patch_user(client):
    global UID

    res = client.patch(
        f"/users/{UID}",
        json={"username": "newTestUser"},
    )

    assert res.status_code == 200
    assert json.loads(res.data)["data"]["username"] == "newTestUser"


def test_delete_user(client):
    res = client.delete(f"/users/{UID}")

    assert res.status_code == 204
    assert res.data == b""
