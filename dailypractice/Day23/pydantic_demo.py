from pydantic import BaseModel, ValidationError, Field


class User(BaseModel):
    name: str = Field(min_length=2, max_length=20)
    age: int = Field(ge=0, le=120)
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