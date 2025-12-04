import pytest
import pytest_asyncio
from httpx import AsyncClient
from app.main import app


@pytest_asyncio.fixture
async def client():
    async with AsyncClient(app=app, base_url="http://testserver") as ac:
        yield ac


@pytest.mark.asyncio
async def test_create_and_get_recipe(client):
    payload = {
        "title": "Test Pancakes",
        "cooking_time": 20,
        "ingredients": [{"name": "Flour", "quantity": "200 g"}],
        "description": "Test desc"
    }
    r = await client.post("/recipes", json=payload)
    assert r.status_code == 201
    data = r.json()
    assert data["title"] == payload["title"]
    recipe_id = data["id"]

    r2 = await client.get(f"/recipes/{recipe_id}")
    assert r2.status_code == 200
    assert r2.json()["views"] == 1

    r3 = await client.get(f"/recipes/{recipe_id}")
    assert r3.status_code == 200
    assert r3.json()["views"] == 2


@pytest.mark.asyncio
async def test_list_sorted_by_views(client):
    p1 = {"title":"A","cooking_time":10,"ingredients":[{"name":"X","quantity":"1"}],"description":""}
    p2 = {"title":"B","cooking_time":5,"ingredients":[{"name":"Y","quantity":"1"}],"description":""}

    r1 = await client.post("/recipes", json=p1)
    r2 = await client.post("/recipes", json=p2)
    id1 = r1.json()["id"]
    id2 = r2.json()["id"]

    # увеличиваем просмотры
    await client.get(f"/recipes/{id2}")
    await client.get(f"/recipes/{id2}")
    await client.get(f"/recipes/{id2}")
    await client.get(f"/recipes/{id1}")

    list_resp = await client.get("/recipes")
    assert list_resp.status_code == 200
    items = list_resp.json()
    assert items[0]["views"] >= items[1]["views"]
