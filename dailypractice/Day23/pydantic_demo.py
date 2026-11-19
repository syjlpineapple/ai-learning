from pydantic import BaseModel, ValidationError


class User(BaseModel):
    name: str
    age: int
    email: str

user = User(
    name='jack',
    age=18,
    email='jack@email.com',
)

print(user.name)
print(user.age)
print(user.email)

try:
    user = User(
        name="jack",
        age="hello",
        email="jack@gmail.com"
    )
except ValidationError as e:
    print(e)