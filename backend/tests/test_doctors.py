import pytest

@pytest.fixture()
def doctor_token(client):
    '''
    Fixture for medic auth flow automation.
    Returns a string with JWT access_token.
    '''
    # 1. Registrar médico
    # 2. Hacer login
    # 3. Retornar el access_token
    doctor_data = {
        "DNI": "123456789",
        "email": "asdacvava@example.com",
        "password": "PasswordSegura123!",
        "birthdate": "1995-05-15",
        "gender": "Male",    
        "role": "doctor"    
    }
    client.post("/api/auth/registration", json=doctor_data)
    login_res = client.post("/api/auth/login", data={
        "username": doctor_data["email"],
        "password": doctor_data["password"]
    })
    return login_res.json()["access_token"]

def test_update_doctor_profile(client, doctor_token):
    """
    Use token to test doctor profile.
    """
    headers = {"Authorization": f"Bearer {doctor_token}"}
    debug_response = client.get("/api/auth/me", headers=headers)
    print("USER ROLE:", debug_response.json())
    profile_payload = {
        "doctor_name": "Javier Beltrán",        
        "speciality": "Medicina Interna",
        "medical_license": "0230651"
    }
    
    response = client.post("/api/doctors/profile_update", json=profile_payload, headers=headers)
    print(response.json())
    me_response = client.get("/api/doctors/me", headers=headers)
    print("ME:", me_response.json())
    
    assert response.status_code == 201
    