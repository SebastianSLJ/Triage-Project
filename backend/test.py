from datetime import datetime
def age_calculate(birthdate: str):
    today = datetime.today()    
    birthdate_convertion = datetime.strptime(birthdate,'%Y-%m-%d').date()
    age = today.year - birthdate_convertion.year
    if (today.month, today.day) < (birthdate_convertion.month, birthdate_convertion.day):
        age -= 1
    return age

edad = age_calculate("2000-04-10")
print(edad)