import pytest
from ...models import apartments
from ...services.apartment import AparmentService
from ...models.repository import MongoRepository, GridFSRepository, FileModel
from bson import ObjectId

pytest_plugins = ('pytest_asyncio',)

@pytest.fixture
def apartment_input():
    return apartments.ApartmentInput(
        title="Test Apartment",
        description="A nice place to live",
        location={"type": "Point", "coordinates": [50.0, 50.0]},
        price=1500.0,
        bedrooms=2,
        dateadded="2022-01-01",
        image=b"fake_image_data",
        realtor="realtor_username"
    )

@pytest.fixture
def apartment_update():
    return apartments.ApartmentUpdate(
        title="Updated Test Apartment",
        description="An even nicer place to live",
        location={"type": "Point", "coordinates": [51.0, 51.0]},
        price=1600.0,
        bedrooms=3,
        image=b"updated_fake_image_data"
    )

@pytest.fixture
def apartment_in_db(apartment_input):
    return apartments.ApartmentInDB(
        id=ObjectId(),
        title=apartment_input.title,
        description=apartment_input.description,
        location=apartment_input.location,
        price=apartment_input.price,
        bedrooms=apartment_input.bedrooms,
        dateadded=apartment_input.dateadded,
        image_id=str(ObjectId()),
        realtor="realtor_username"
    )

@pytest.fixture
def apartment_collection(apartment_in_db):
    return apartments.ApartmentCollection(apartments=[apartment_in_db])

@pytest.fixture
def geo_search():
    return apartments.GeospatialApartmentSearch(
        radius=10,
        lat=50.0,
        lon=50.0,
        radius_unit=apartments.RadiusUnit.km,
        page=1
    )

@pytest.mark.asyncio
async def test_should_create_apartment_write_apartment_and_file(apartment_input: apartments.ApartmentInput):
    repo = MongoRepository()
    file_repo = GridFSRepository()
    
    response = await AparmentService.create_apartment(apartment_input, "realtor_username")
    
    assert response.title == apartment_input.title
    assert response.realtor == "realtor_username"

    # Clean up
    await repo.delete(str(response.id), response.collection)
    await file_repo.delete(response.image_id)

@pytest.mark.asyncio
async def test_should_update_apartment_replace_apartment_and_file(
    apartment_update: apartments.ApartmentUpdate, apartment_in_db: apartments.ApartmentInDB
):
    repo = MongoRepository()
    file_repo = GridFSRepository()
    
    created_apartment = await repo.add(apartment_in_db)
    apartment_id = str(created_apartment["_id"])

    response = await AparmentService.update_apartment(apartment_id, "realtor_username", apartment_update)
    
    assert response["title"] == apartment_update.title
    assert response["description"] == apartment_update.description

    # Clean up
    await repo.delete(apartment_id, apartment_update.collection)
    if "image_id" in response:
        await file_repo.delete(response["image_id"])

@pytest.mark.asyncio
async def test_should_delete_apartment_delete_apartment_and_file(apartment_in_db: apartments.ApartmentInDB):
    repo = MongoRepository()
    file_repo = GridFSRepository()
    file_id = await file_repo.add(FileModel(data=b"Some data"))
    apartment_in_db.image_id = str(file_id)
    created_apartment = await repo.add(apartment_in_db)
    apartment_id = str(created_apartment["_id"])
    image_id = str(apartment_in_db.image_id)

    result = await AparmentService.delete_apartment(apartment_id, "realtor_username")
    
    assert result is True

    # Clean up
    await repo.delete(apartment_id, apartment_in_db.collection)
    await file_repo.delete(image_id)

@pytest.mark.asyncio
async def test_should_list_apartment_return_a_list_of_apartments(apartment_in_db):
    repo = MongoRepository()
    await repo.add(apartment_in_db)
    response = await AparmentService.list_apartments("realtor_username", 1)
    
    assert len(response.apartments) >= 1

    # Clean up
    for apt in response.apartments:
        await repo.delete(str(apt.id), apt.collection)

@pytest.fixture
def multiple_apartments():
    inside_radius = [
        apartments.ApartmentInDB(
            id=ObjectId(),
            title=f"Test Apartment Inside {i}",
            description="A nice place to live inside radius",
            location={"type": "Point", "coordinates": [50.0 + i*0.01, 50.0]},
            price=1500.0 + i*100,
            bedrooms=2 + i,
            dateadded="2022-01-01",
            image_id=str(ObjectId()),
            realtor="realtor_username"
        ) for i in range(7)
    ]

    outside_radius = [
        apartments.ApartmentInDB(
            id=ObjectId(),
            title=f"Test Apartment Outside {i}",
            description="A nice place to live outside radius",
            location={"type": "Point", "coordinates": [70.0 + i*0.01, 70.0]},
            price=2500.0 + i*100,
            bedrooms=3 + i,
            dateadded="2022-01-01",
            image_id=str(ObjectId()),
            realtor="realtor_username"
        ) for i in range(3)
    ]

    return inside_radius + outside_radius

@pytest.mark.asyncio
async def test_should_list_apartments_by_radius_return_apartments_inside_radius_only(geo_search, multiple_apartments):
    repo = MongoRepository()

    ids = []
    for apartment in multiple_apartments:
        created = await repo.add(apartment)
        ids.append(created["_id"])

    response = await AparmentService.list_apartments_by_radius(geo_search)
    
    assert len(response.apartments) == 7
    assert all(50.0 <= apt.location["coordinates"][0] < 51.0 for apt in response.apartments)

    for id in ids:
        await repo.delete(str(id), multiple_apartments[0].collection)

@pytest.mark.asyncio
async def test_should_list_apartments_by_radius_with_specific_distances():
    repo = MongoRepository()
    
    location_a = {"type": "Point", "coordinates": [0, 0]} 
    location_b = {"type": "Point", "coordinates": [0.0899322, 0]}  #(approx. 10km from A)
    location_c = {"type": "Point", "coordinates": [1, 1]} 

    # Create apartments in locations A, B, and C
    apartment_a = apartments.ApartmentInDB(
        title="Apartment A",
        description="Nice apartment at Location A",
        location=location_a,
        price=1000.0,
        bedrooms=2,
        dateadded="2023-01-01",
        image_id="dummy_image_id",
        realtor="user_a"
    )
    
    apartment_b = apartments.ApartmentInDB(
        title="Apartment B",
        description="Nice apartment at Location B",
        location=location_b,
        price=1200.0,
        bedrooms=3,
        dateadded="2023-01-02",
        image_id="dummy_image_id",
        realtor="user_b"
    )
    
    apartment_c = apartments.ApartmentInDB(
        title="Apartment C",
        description="Nice apartment at Location C",
        location=location_c,
        price=1400.0,
        bedrooms=4,
        dateadded="2023-01-03",
        image_id="dummy_image_id",
        realtor="user_c"
    )
    
    ids = []
    created = await repo.add(apartment_a)
    ids.append(created["_id"])
    created = await repo.add(apartment_b)
    ids.append(created["_id"])
    created = await repo.add(apartment_c)
    ids.append(created["_id"])
    
    geo_search_5km = apartments.GeospatialApartmentSearch(
        radius=5,
        lat=0,
        lon=0,
        radius_unit=apartments.RadiusUnit.km,
        page=1
    )
    
    results_5km = await AparmentService.list_apartments_by_radius(geo_search_5km)
    assert len(results_5km.apartments) == 1
    assert results_5km.apartments[0].title == "Apartment A"
    
    geo_search_11km = apartments.GeospatialApartmentSearch(
        radius=11,
        lat=0,
        lon=0,
        radius_unit=apartments.RadiusUnit.km,
        page=1
    )

    km_to_miles = 0.621371
    radius_5km_in_miles = 5 * km_to_miles
    radius_11km_in_miles = 11 * km_to_miles

    results_11km = await AparmentService.list_apartments_by_radius(geo_search_11km)
    assert len(results_11km.apartments) == 2
    assert any(apartment.title == "Apartment A" for apartment in results_11km.apartments)
    assert any(apartment.title == "Apartment B" for apartment in results_11km.apartments)

    geo_search_5km_in_miles = apartments.GeospatialApartmentSearch(
        radius=radius_5km_in_miles,
        lat=0,
        lon=0,
        radius_unit=apartments.RadiusUnit.mi,
        page=1
    )
    
    results_5km_in_miles = await AparmentService.list_apartments_by_radius(geo_search_5km_in_miles)
    assert len(results_5km_in_miles.apartments) == 1
    assert results_5km_in_miles.apartments[0].title == "Apartment A"

    geo_search_11km_in_miles = apartments.GeospatialApartmentSearch(
        radius=radius_11km_in_miles,
        lat=0,
        lon=0,
        radius_unit=apartments.RadiusUnit.mi,
        page=1
    )
    results_11km_in_miles = await AparmentService.list_apartments_by_radius(geo_search_11km_in_miles)
    assert len(results_11km_in_miles.apartments) == 2
    assert any(apartment.title == "Apartment A" for apartment in results_11km_in_miles.apartments)
    assert any(apartment.title == "Apartment B" for apartment in results_11km_in_miles.apartments)
    
    for id in ids:
        await repo.delete(str(id), AparmentService.DEFAULT_COLLECTION)
