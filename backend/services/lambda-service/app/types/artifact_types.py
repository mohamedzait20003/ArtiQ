from typing import Optional, List
from pydantic import BaseModel


class ArtifactQuery(BaseModel):
    name: str
    types: Optional[List[str]] = None


class ArtifactData(BaseModel):
    url: str


class ArtifactMetadata(BaseModel):
    name: str
    id: str
    type: str


class Artifact(BaseModel):
    metadata: ArtifactMetadata
    data: ArtifactData


class ArtifactRegEx(BaseModel):
    regex: str


class SimpleLicenseCheckRequest(BaseModel):
    github_url: str
