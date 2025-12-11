"""
Rating Model
Model for storing artifact ratings and metrics
"""

from .Model import Model
from typing import Optional, Dict, Any
from include import belongs_to


class Rating_Model(Model):
    """
    Rating Model for storing ML model evaluation metrics.

    Database Schema:
        Table Name: Ratings
        Primary Key:
            - artifact_id (str): Unique identifier linking to artifact.
        Attributes:
            - artifact_id (str): Reference to artifact being rated
            - name (str): Name of the rated artifact
            - category (str): Model category
            - net_score (Dict): Overall score {value, latency}
            - ramp_up_time (Dict): Ease-of-adoption {value, latency}
            - bus_factor (Dict): Team redundancy {value, latency}
            - performance_claims (Dict): Performance alignment {value, latency}
            - license (Dict): Licensing suitability {value, latency}
            - dataset_and_code_score (Dict): Dataset/code quality
                                             {value, latency}
            - dataset_quality (Dict): Dataset quality {value, latency}
            - code_quality (Dict): Code quality {value, latency}
            - reproducibility (Dict): Reproducibility score {value, latency}
            - reviewedness (Dict): Peer review coverage {value, latency}
            - tree_score (Dict): Dependency health {value, latency}
            - size_score (Dict): Size suitability scores {value, latency}
    """

    table_name: str = "Ratings"

    def __init__(
        self,
        artifact_id: str,
        net_score: Optional[Dict[str, float]] = None,
        ramp_up_time: Optional[Dict[str, float]] = None,
        bus_factor: Optional[Dict[str, float]] = None,
        performance_claims: Optional[Dict[str, float]] = None,
        license: Optional[Dict[str, float]] = None,
        dataset_and_code_score: Optional[Dict[str, float]] = None,
        dataset_quality: Optional[Dict[str, float]] = None,
        code_quality: Optional[Dict[str, float]] = None,
        reproducibility: Optional[Dict[str, float]] = None,
        reviewedness: Optional[Dict[str, float]] = None,
        tree_score: Optional[Dict[str, float]] = None,
        size_score: Optional[Dict[str, Any]] = None,
        **kwargs
    ):
        """
        Initialize Rating instance

        Args:
            artifact_id: Unique identifier for the artifact being rated
            name: Name of the artifact
            category: Model category
            net_score: Overall score {value, latency}
            ramp_up_time: Ease-of-adoption {value, latency}
            bus_factor: Team redundancy {value, latency}
            performance_claims: Performance alignment {value, latency}
            license: Licensing suitability {value, latency}
            dataset_and_code_score: Dataset/code quality {value, latency}
            dataset_quality: Dataset quality {value, latency}
            code_quality: Code quality {value, latency}
            reproducibility: Reproducibility {value, latency}
            reviewedness: Peer review coverage {value, latency}
            tree_score: Dependency health {value, latency}
            size_score: Size suitability with nested device scores
        """
        self.artifact_id = artifact_id
        self.net_score = net_score or {"value": 0.0, "latency": 0.0}
        self.ramp_up_time = ramp_up_time or {"value": 0.0, "latency": 0.0}
        self.bus_factor = bus_factor or {"value": 0.0, "latency": 0.0}
        self.performance_claims = (
            performance_claims or {"value": 0.0, "latency": 0.0}
        )
        self.license = license or {"value": 0.0, "latency": 0.0}
        self.dataset_and_code_score = (
            dataset_and_code_score or {"value": 0.0, "latency": 0.0}
        )
        self.dataset_quality = (
            dataset_quality or {"value": 0.0, "latency": 0.0}
        )
        self.code_quality = code_quality or {"value": 0.0, "latency": 0.0}
        self.reproducibility = (
            reproducibility or {"value": 0.0, "latency": 0.0}
        )
        self.reviewedness = reviewedness or {"value": 0.0, "latency": 0.0}
        self.tree_score = tree_score or {"value": 0.0, "latency": 0.0}
        self.size_score = size_score or {
            "value": {
                "raspberry_pi": 0.0,
                "jetson_nano": 0.0,
                "desktop_pc": 0.0,
                "aws_server": 0.0
            },
            "latency": 0.0
        }

        super().__init__(**kwargs)

    @classmethod
    def primary_key(cls):
        """Define the primary key for database operations"""
        return ["artifact_id"]

    @classmethod
    def find_by_artifact_id(cls, artifact_id: str):
        """
        Find rating by artifact ID

        Args:
            artifact_id: The artifact ID to search for

        Returns:
            Rating_Model instance or None
        """
        return cls.get({"artifact_id": artifact_id})

    def artifact(self):
        """
        Get the artifact this rating belongs to (belongs-to relationship)

        Returns:
            Artifact_Model instance or None
        """
        from .Artifact_Model import Artifact_Model
        return belongs_to(Artifact_Model, 'artifact_id', 'id')(self)

    def to_api_response(self) -> Dict[str, Any]:
        """
        Convert to API response format matching OpenAPI spec

        Returns:
            Dictionary formatted for API response
        """
        return {
            "name": self.name,
            "category": self.category,
            "net_score": self.net_score.get("value", 0.0),
            "net_score_latency": self.net_score.get("latency", 0.0),
            "ramp_up_time": self.ramp_up_time.get("value", 0.0),
            "ramp_up_time_latency": self.ramp_up_time.get("latency", 0.0),
            "bus_factor": self.bus_factor.get("value", 0.0),
            "bus_factor_latency": self.bus_factor.get("latency", 0.0),
            "performance_claims": self.performance_claims.get("value", 0.0),
            "performance_claims_latency": (
                self.performance_claims.get("latency", 0.0)
            ),
            "license": self.license.get("value", 0.0),
            "license_latency": self.license.get("latency", 0.0),
            "dataset_and_code_score": (
                self.dataset_and_code_score.get("value", 0.0)
            ),
            "dataset_and_code_score_latency": (
                self.dataset_and_code_score.get("latency", 0.0)
            ),
            "dataset_quality": self.dataset_quality.get("value", 0.0),
            "dataset_quality_latency": (
                self.dataset_quality.get("latency", 0.0)
            ),
            "code_quality": self.code_quality.get("value", 0.0),
            "code_quality_latency": self.code_quality.get("latency", 0.0),
            "reproducibility": self.reproducibility.get("value", 0.0),
            "reproducibility_latency": (
                self.reproducibility.get("latency", 0.0)
            ),
            "reviewedness": self.reviewedness.get("value", 0.0),
            "reviewedness_latency": self.reviewedness.get("latency", 0.0),
            "tree_score": self.tree_score.get("value", 0.0),
            "tree_score_latency": self.tree_score.get("latency", 0.0),
            "size_score": self.size_score.get("value", {}),
            "size_score_latency": self.size_score.get("latency", 0.0)
        }
