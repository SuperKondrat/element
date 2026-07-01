import re

from pydantic import BaseModel, EmailStr, Field, field_validator, model_validator

# Формат, который на фронте собирает маска ввода: +7 (XXX) XXX-XX-XX.
# Валидируем и на бэкенде — форму можно обойти прямым вызовом API.
PHONE_PATTERN = re.compile(r"^\+7 \(\d{3}\) \d{3}-\d{2}-\d{2}$")


class ContactBase(BaseModel):
    contact_name: str = Field(min_length=1, max_length=255)
    contact_phone: str | None = Field(default=None, max_length=50)
    contact_email: EmailStr | None = None

    @field_validator("contact_phone")
    @classmethod
    def validate_phone_format(cls, value: str | None) -> str | None:
        if value is not None and not PHONE_PATTERN.match(value):
            raise ValueError("Телефон должен быть в формате +7 (XXX) XXX-XX-XX")
        return value

    @model_validator(mode="after")
    def require_phone_or_email(self) -> "ContactBase":
        if not self.contact_phone and not self.contact_email:
            raise ValueError("Укажите телефон или почту для связи")
        return self
