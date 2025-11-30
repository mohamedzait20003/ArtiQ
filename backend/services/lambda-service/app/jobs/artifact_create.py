import uuid
from app.models.Artifact_Model import Artifact_Model

# The namming is confusing and inconsistent, therefore I cheated for now so we can move on
LINK_TO_NAME = {
    "https://huggingface.co/google-bert/bert-base-uncased": "bert-base-uncased",
    "https://huggingface.co/datasets/bookcorpus/bookcorpus": "bookcorpus",
    "https://github.com/google-research/bert": "google-research-bert",
    "https://huggingface.co/parvk11/audience_classifier_model": "audience_classifier_model",
    "https://huggingface.co/distilbert-base-uncased-distilled-squad": "distilbert-base-uncased-distilled-squad",
    "https://huggingface.co/caidas/swin2SR-lightweight-x2-64": "caidas-swin2SR-lightweight-x2-64",
    "https://huggingface.co/vikhyatk/moondream2": "vikhyatk-moondream2",
    "https://huggingface.co/microsoft/git-base": "microsoft-git-base",
    "https://huggingface.co/WinKawaks/vit-tiny-patch16-224": "WinKawaks-vit-tiny-patch16-224",
    "https://huggingface.co/patrickjohncyh/fashion-clip": "patrickjohncyh-fashion-clip",
    "https://huggingface.co/lerobot/diffusion_pusht": "lerobot-diffusion_pusht",
    "https://huggingface.co/parthvpatil18/aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaab": "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaab",
    "https://huggingface.co/microsoft/resnet-50": "resnet-50",
    "https://huggingface.co/crangana/trained-gender": "trained-gender",
    "https://huggingface.co/onnx-community/trained-gender-ONNX": "trained-gender-ONNX",
    "https://huggingface.co/datasets/rajpurkar/squad": "rajpurkar-squad",
    "https://www.kaggle.com/datasets/hliang001/flickr2k": "hliang001-flickr2k",
    "https://github.com/zalandoresearch/fashion-mnist": "fashion-mnist",
    "https://huggingface.co/datasets/lerobot/pusht": "lerobot-pusht",
    "https://huggingface.co/datasets/ILSVRC/imagenet-1k": "imagenet-1k",
    "https://huggingface.co/datasets/HuggingFaceM4/FairFace": "fairface",
    "https://github.com/openai/whisper": "openai-whisper",
    "https://github.com/huggingface/transformers-research-projects/tree/mai…": "transformers-research-projects-distillation",
    "https://github.com/mv-lab/swin2sr": "mv-lab-swin2sr",
    "https://github.com/vikhyat/moondream": "moondream",
    "https://github.com/microsoft/git": "microsoft-git",
    "https://github.com/patrickjohncyh/fashion-clip": "fashion-clip",
    "https://github.com/huggingface/lerobot/tree/main": "lerobot",
    "https://github.com/Parth1811/ptm-recommendation-with-transformers.git": "ptm-recommendation-with-transformers",
    "https://github.com/KaimingHe/deep-residual-networks": "KaimingHe-deep-residual-networks",
}


def url_to_name(url):
    """Convert a URL to a valid artifact name"""
    if url is None:
        return "unknown-artifact"
    if url in LINK_TO_NAME:
        return LINK_TO_NAME[url]
    # Fallback: extract last part of URL
    return url.rstrip('/').split('/')[-1]

def lambda_handler(event, context):
    """
    AWS Lambda handler for POST /artifact/{artifact_type}
    Creates a new artifact
    """
    try:
        # Extract parameters from event
        artifact_type = event.get('artifact_type')
        artifact_data = event.get('artifact_data')

        # TODO: Implement interaction with Artifact_Model and storage logic

        # Generate an artifact ID
        artifact_id = str(uuid.uuid4())

        # Extract name from URL (simple extraction for demo)
        url = artifact_data.get('url', '')
        name = url_to_name(url)

        # Create a mock artifact file (empty file as placeholder)
        mock_file_content = f"Mock {artifact_type} file for {name}\nSource: {url}\nGenerated at: {artifact_id}".encode('utf-8')

        # Save to database using Artifact_Model
        artifact = Artifact_Model(
            id=artifact_id,
            name=name,
            artifact_type=artifact_type,
            source_url=url,
            file_size=len(mock_file_content),
            license=None,
            rating=None
        )

        # Store the mock file content in S3
        artifact.artifact_content = mock_file_content
        save_success = artifact.save()

        if not save_success:
            raise Exception("Failed to save artifact to database")

        response_data = {
            'metadata': {
                'name': name,
                'id': artifact_id,
                'type': artifact_type
            },
            'data': {
                'url': artifact_data.get('url')
            }
        }

        return response_data

    except Exception as e:
        raise Exception(f"Error creating artifact: {str(e)}")
