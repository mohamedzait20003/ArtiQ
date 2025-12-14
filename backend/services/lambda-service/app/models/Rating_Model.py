"""
Rating Model
Model for storing artifact ratings and metrics
"""

from .Model import Model
from include import belong_to_one
from typing import Optional, Dict, Any, TYPE_CHECKING

if TYPE_CHECKING:
    from .Artifact_Model import Artifact_Model  # noqa: F401


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
        id: str,
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
        lineage_graph: Optional[Dict[str, Any]] = None,
        **kwargs
    ):
        """
        Initialize Rating instance

        Args:
            id: Primary key for the rating
            artifact_id: Reference to the artifact being rated
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
            lineage_graph: Lineage graph with parent models
        """
        self.id = id
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
        self.lineage_graph = lineage_graph or {"parents": []}

        super().__init__(**kwargs)

    @classmethod
    def primary_key(cls):
        """Define the primary key for database operations"""
        return ["id"]

    @classmethod
    def find_by_artifact_id(cls, artifact_id: str):
        """
        Find rating by artifact ID

        Args:
            artifact_id: The artifact ID to search for

        Returns:
            List of Rating_Model instances
        """
        return cls.where({"artifact_id": artifact_id})

    def artifact(self):
        """
        Get the artifact this rating belongs to (belong-to-one relationship)

        Returns:
            Artifact_Model instance or None
        """
        return belong_to_one(Artifact_Model, 'artifact_id', 'id')(self)
