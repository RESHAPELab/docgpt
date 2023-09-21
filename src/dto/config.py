import json
from pathlib import Path

import pypandoc
from pydantic import AnyUrl, BaseModel, Field, PositiveInt, field_validator

SUPORTED_FORMATS = pypandoc.get_pandoc_formats()[0]


class Config(BaseModel):
    target: AnyUrl
    tags: list[str]
    content_format: str | None = Field(None, alias="format")
    link_deep: PositiveInt = 0

    @field_validator("content_format")
    @classmethod
    def _content_format_must_be_valid(cls, content_format: str) -> str:
        if content_format not in SUPORTED_FORMATS:
            raise ValueError(
                f"Content format {content_format} not suported by pypandoc."
            )
        return content_format

    @field_validator("tags")
    @classmethod
    def _tags_must_has_any_item(cls, tags: list[str]) -> list[str]:
        if not tags:
            raise ValueError("At least one tag is required.")
        return tags


class Project(BaseModel):
    name: str
    config: list[Config]

    @field_validator("config")
    @classmethod
    def _config_target_must_be_unique(cls, config: list[Config]) -> list[Config]:
        targets = {value.target for value in config}
        if len(targets) != len(config):
            raise ValueError("Targets must be unique.")
        return config


class ProjectWrapper(BaseModel):
    projects: list[Project]

    @field_validator("projects")
    @classmethod
    def _project_name_must_be_unique(cls, projects: list[Project]) -> list[Project]:
        names = {value.name for value in projects}
        if len(names) != len(projects):
            raise ValueError("Project names must be unique.")
        return projects

    @staticmethod
    def from_file(filepath: Path) -> "ProjectWrapper":
        config_json: list[Config] = json.loads(filepath.read_text())
        return ProjectWrapper.model_validate({"projects": config_json})
