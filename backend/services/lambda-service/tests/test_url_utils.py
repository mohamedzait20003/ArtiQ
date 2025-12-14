"""
Test suite for URL utility functions
"""
from app.utils import url_to_artifact_name, sanitize_artifact_name


class TestUrlToArtifactName:
    """Test url_to_artifact_name function with all known patterns"""

    # Expected mappings based on the original lookup table
    EXPECTED_MAPPINGS = {
        # HuggingFace models
        "https://huggingface.co/google-bert/bert-base-uncased":
            "bert-base-uncased",
        "https://huggingface.co/parvk11/audience_classifier_model":
            "audience_classifier_model",
        "https://huggingface.co/distilbert-base-uncased-distilled-squad":
            "distilbert-base-uncased-distilled-squad",
        "https://huggingface.co/caidas/swin2SR-lightweight-x2-64":
            "caidas-swin2SR-lightweight-x2-64",
        "https://huggingface.co/vikhyatk/moondream2":
            "vikhyatk-moondream2",
        "https://huggingface.co/microsoft/git-base":
            "microsoft-git-base",
        "https://huggingface.co/WinKawaks/vit-tiny-patch16-224":
            "WinKawaks-vit-tiny-patch16-224",
        "https://huggingface.co/patrickjohncyh/fashion-clip":
            "patrickjohncyh-fashion-clip",
        "https://huggingface.co/lerobot/diffusion_pusht":
            "lerobot-diffusion_pusht",
        "https://huggingface.co/parthvpatil18/"
        "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa"
        "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaab":
            "parthvpatil18-"
            "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa"
            "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaab",
        "https://huggingface.co/microsoft/resnet-50":
            "resnet-50",
        "https://huggingface.co/crangana/trained-gender":
            "trained-gender",
        "https://huggingface.co/onnx-community/trained-gender-ONNX":
            "trained-gender-ONNX",

        # HuggingFace datasets
        "https://huggingface.co/datasets/bookcorpus/bookcorpus":
            "bookcorpus",
        "https://huggingface.co/datasets/rajpurkar/squad":
            "rajpurkar-squad",
        "https://huggingface.co/datasets/lerobot/pusht":
            "lerobot-pusht",
        "https://huggingface.co/datasets/ILSVRC/imagenet-1k":
            "imagenet-1k",
        "https://huggingface.co/datasets/HuggingFaceM4/FairFace":
            "fairface",

        # GitHub repositories
        "https://github.com/google-research/bert":
            "google-research-bert",
        "https://github.com/zalandoresearch/fashion-mnist":
            "fashion-mnist",
        "https://github.com/openai/whisper":
            "openai-whisper",
        "https://github.com/huggingface/transformers-research-projects"
        "/tree/main/distillation":
            "transformers-research-projects-distillation",
        "https://github.com/mv-lab/swin2sr":
            "mv-lab-swin2sr",
        "https://github.com/vikhyat/moondream":
            "moondream",
        "https://github.com/microsoft/git":
            "microsoft-git",
        "https://github.com/patrickjohncyh/fashion-clip":
            "fashion-clip",
        "https://github.com/huggingface/lerobot/tree/main":
            "lerobot",
        "https://github.com/Parth1811/ptm-recommendation-with-"
        "transformers.git":
            "ptm-recommendation-with-transformers",
        "https://github.com/KaimingHe/deep-residual-networks":
            "KaimingHe-deep-residual-networks",

        # Kaggle datasets
        "https://www.kaggle.com/datasets/hliang001/flickr2k":
            "hliang001-flickr2k",
    }

    def test_all_url_mappings(self):
        """Test all URL mappings against expected values"""
        failures = []

        for url, expected_name in self.EXPECTED_MAPPINGS.items():
            actual_name = url_to_artifact_name(url)

            if actual_name != expected_name:
                failures.append({
                    'url': url,
                    'expected': expected_name,
                    'actual': actual_name
                })

        # Print detailed failure information
        if failures:
            print("\n" + "=" * 80)
            print(f"FAILED: {len(failures)} out of "
                  f"{len(self.EXPECTED_MAPPINGS)} URL mappings")
            print("=" * 80)
            for failure in failures:
                print(f"\nURL: {failure['url']}")
                print(f"  Expected: {failure['expected']}")
                print(f"  Actual:   {failure['actual']}")
            print("=" * 80)

        # Assert no failures
        assert len(failures) == 0, (
            f"{len(failures)} URL mapping(s) failed. "
            f"See output above for details."
        )

    def test_huggingface_model_basic(self):
        """Test basic HuggingFace model URL"""
        url = "https://huggingface.co/google-bert/bert-base-uncased"
        result = url_to_artifact_name(url)
        assert result == "bert-base-uncased"

    def test_huggingface_model_with_owner_prefix(self):
        """Test HuggingFace model that requires owner prefix"""
        url = "https://huggingface.co/vikhyatk/moondream2"
        result = url_to_artifact_name(url)
        assert result == "vikhyatk-moondream2"

    def test_huggingface_dataset_standalone(self):
        """Test HuggingFace dataset with standalone name"""
        url = "https://huggingface.co/datasets/bookcorpus/bookcorpus"
        result = url_to_artifact_name(url)
        assert result == "bookcorpus"

    def test_huggingface_dataset_with_owner(self):
        """Test HuggingFace dataset with owner prefix"""
        url = "https://huggingface.co/datasets/rajpurkar/squad"
        result = url_to_artifact_name(url)
        assert result == "rajpurkar-squad"

    def test_huggingface_fairface_lowercase(self):
        """Test HuggingFace FairFace dataset special case"""
        url = "https://huggingface.co/datasets/HuggingFaceM4/FairFace"
        result = url_to_artifact_name(url)
        assert result == "fairface"

    def test_github_with_owner_prefix(self):
        """Test GitHub repo with owner prefix"""
        url = "https://github.com/openai/whisper"
        result = url_to_artifact_name(url)
        assert result == "openai-whisper"

    def test_github_standalone(self):
        """Test GitHub repo with standalone name"""
        url = "https://github.com/zalandoresearch/fashion-mnist"
        result = url_to_artifact_name(url)
        assert result == "fashion-mnist"

    def test_github_with_tree_main(self):
        """Test GitHub repo with /tree/main path"""
        url = "https://github.com/huggingface/lerobot/tree/main"
        result = url_to_artifact_name(url)
        assert result == "lerobot"

    def test_github_with_tree_subdirectory(self):
        """Test GitHub repo with /tree/main/subdirectory path"""
        url = (
            "https://github.com/huggingface/"
            "transformers-research-projects/tree/main/distillation"
        )
        result = url_to_artifact_name(url)
        assert result == "transformers-research-projects-distillation"

    def test_github_with_git_extension(self):
        """Test GitHub repo URL with .git extension"""
        url = (
            "https://github.com/Parth1811/"
            "ptm-recommendation-with-transformers.git"
        )
        result = url_to_artifact_name(url)
        assert result == "Parth1811-ptm-recommendation-with-transformers"

    def test_kaggle_dataset(self):
        """Test Kaggle dataset URL"""
        url = "https://www.kaggle.com/datasets/hliang001/flickr2k"
        result = url_to_artifact_name(url)
        assert result == "hliang001-flickr2k"

    def test_empty_url(self):
        """Test empty URL returns unknown-artifact"""
        result = url_to_artifact_name("")
        assert result == "unknown-artifact"

    def test_none_url(self):
        """Test None URL returns unknown-artifact"""
        result = url_to_artifact_name(None)
        assert result == "unknown-artifact"


class TestSanitizeArtifactName:
    """Test sanitize_artifact_name function"""

    def test_valid_name(self):
        """Test already valid name remains unchanged"""
        name = "valid-artifact-name"
        result = sanitize_artifact_name(name)
        assert result == "valid-artifact-name"

    def test_replace_invalid_characters(self):
        """Test invalid characters are replaced with hyphens"""
        name = "invalid@artifact#name"
        result = sanitize_artifact_name(name)
        assert result == "invalid-artifact-name"

    def test_remove_consecutive_hyphens(self):
        """Test consecutive hyphens are collapsed"""
        name = "artifact---name"
        result = sanitize_artifact_name(name)
        assert result == "artifact-name"

    def test_remove_leading_trailing_hyphens(self):
        """Test leading and trailing hyphens are removed"""
        name = "-artifact-name-"
        result = sanitize_artifact_name(name)
        assert result == "artifact-name"

    def test_preserve_underscores(self):
        """Test underscores are preserved"""
        name = "artifact_name_test"
        result = sanitize_artifact_name(name)
        assert result == "artifact_name_test"

    def test_preserve_alphanumeric(self):
        """Test alphanumeric characters are preserved"""
        name = "artifact123name456"
        result = sanitize_artifact_name(name)
        assert result == "artifact123name456"

    def test_mixed_case_preserved(self):
        """Test mixed case is preserved"""
        name = "ArtifactName"
        result = sanitize_artifact_name(name)
        assert result == "ArtifactName"
