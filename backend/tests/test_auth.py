def test_register_success(client):
    response = client.post("/api/auth/registration", json={
        "DNI": "123456789",
        "email": "juan.prueba@example.com",
        "password": "PasswordSegura123!",
        "birthdate": "1995-05-15",
        "gender": "Male",    
        "role": "doctor"    
    })
    assert response.status_code == 201


def test_register_duplicate_DNI(client):
    user_data = {
        "DNI": "999888777",
        "email": "original@example.com",
        "password": "Password123!",
        "birthdate": "1990-01-01",
        "gender": "Male",
        "role": "patient"
    }

    # 1. Primer registro: Debe ser exitoso (201)
    response1 = client.post("/api/auth/registration", json=user_data)
    print(response1.json())
    assert response1.status_code == 201

    # 2. Segundo registro: Mismo DNI, diferente email
    user_data["email"] = "duplicado@example.com"
    response2 = client.post("/api/auth/registration", json=user_data)
    assert response2.status_code==400
    assert "DNI already registered" in response2.json()["detail"]

def test_register_invalid_email(client):
    # Enviamos un email sin formato (le falta el @ y el dominio)
    invalid_data = {
        "DNI": "111222333",
        "email": "esto-no-es-un-email", 
        "password": "Password123!",
        "birthdate": "1990-01-01",
        "gender": "Female",
        "role": "patient"
    }

    response = client.post("/api/auth/registration", json=invalid_data)

    # 422 es el código estándar de FastAPI para fallos de validación de esquema
    assert response.status_code == 422
    # Verificamos que el error mencione el campo 'email'
    errors = response.json()["detail"]
    assert any(error["loc"][-1] == "email" for error in errors)

def test_login_auth(client):
    client.post("/api/auth/registration", json={
        "DNI": "123456789",
        "email": "email@example.com",
        "password": "Password123!",
        "birthdate": "1995-05-15",
        "gender": "Male",    
        "role": "doctor"    
    })


    response = client.post("/api/auth/login", data={
    "username": "email@example.com",
    "password": "Password123!"
})
    assert response.status_code == 200
    assert "access_token" in response.json()

