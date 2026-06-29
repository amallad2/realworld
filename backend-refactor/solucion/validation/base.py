from pydantic import BaseModel, model_validator, ValidationError


class ValidatedModel(BaseModel):
    @model_validator(mode='before')
    def validate_all(cls, fields):
        for key in fields.keys():
            if not fields[key]:
                raise ValidationError(f"Validation failed for {key}")
        return fields
