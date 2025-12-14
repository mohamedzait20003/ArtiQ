"""
Download and Upload Job
Downloads artifact files from HuggingFace and uploads to S3
"""
import time
import logging
from typing import Dict, Any

# Configure logger for CloudWatch
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


class DownloadUploader:
    """
    Downloads artifact files from HuggingFace and uploads to S3
    """

    def __init__(self):
        """Initialize the Download Uploader"""
        self.timeout = 300  # 5 minutes timeout for downloads

    def download_and_upload(self, metadata) -> Dict[str, Any]:
        """
        Main method to download files from HuggingFace and upload to S3
        Args:
            metadata: Metadata object containing artifact and HuggingFace info
        Returns:
            dict: Result with success status and file information
        """
        start_time = time.time()

        try:
            logger.info("[DOWNLOAD] Starting download and upload process")
            print("[DownloadUploader] Starting download and upload...")

            artifact = metadata.artifact

            # Validate artifact type
            if artifact.artifact_type.lower() != 'model':
                logger.info(
                    f"[DOWNLOAD] Skipping non-model artifact: "
                    f"{artifact.artifact_type}"
                )
                latency = time.time() - start_time
                return self._create_skip_result(
                    "Only model artifacts are downloaded",
                    latency
                )

            # Get model info from metadata
            info = metadata.info
            if not info:
                logger.warning("[DOWNLOAD] No HuggingFace info found")
                latency = time.time() - start_time
                return self._create_error_result(
                    "No HuggingFace model info available",
                    latency
                )

            # First try: Sum up all file sizes from siblings
            total_size_bytes = 0
            siblings = getattr(info, 'siblings', [])
            files_with_size = []

            for sibling in siblings:
                rfilename = getattr(sibling, 'rfilename', '')
                if not rfilename or rfilename.endswith('/'):
                    continue

                # Check blob_id or lfs to see if size info might be in LFS
                lfs_info = getattr(sibling, 'lfs', None)
                if lfs_info and hasattr(lfs_info, 'size'):
                    size = lfs_info.size
                    total_size_bytes += size
                    files_with_size.append(rfilename)

            if files_with_size:
                logger.info(
                    f"[DOWNLOAD] Summed size from "
                    f"{len(files_with_size)} LFS files: "
                    f"{total_size_bytes / (1024*1024):.2f} MB"
                )

            # Fallback: Use SafeTensors parameter count estimate
            if total_size_bytes == 0:
                safetensors_info = getattr(info, 'safetensors', None)
                if safetensors_info:
                    param_count = getattr(safetensors_info, 'total', 0)
                    if param_count > 0:
                        # Estimate: ~4 bytes per parameter (float32)
                        total_size_bytes = param_count * 4
                        logger.info(
                            f"[DOWNLOAD] Estimated from SafeTensors params: "
                            f"{param_count:,} params = "
                            f"{total_size_bytes / (1024*1024):.2f} MB"
                        )

            # If no size yet, try to get from repo metadata size field
            if total_size_bytes == 0:
                repo_metadata = metadata.repo_metadata
                if isinstance(repo_metadata, dict):
                    size_value = repo_metadata.get('size')
                    if size_value:
                        logger.info(
                            f"[DOWNLOAD] Found size in repo_metadata: "
                            f"{size_value} (type: {type(size_value).__name__})"
                        )
                        try:
                            # Handle if it's already a number (bytes)
                            if isinstance(size_value, (int, float)):
                                total_size_bytes = int(size_value)
                                logger.info(
                                    f"[DOWNLOAD] Using size as bytes: "
                                    f"{total_size_bytes / (1024*1024):.2f} "
                                    f"MB"
                                )
                            # Handle if it's a string
                            elif isinstance(size_value, str):
                                size_parts = size_value.strip().split()
                                if len(size_parts) == 2:
                                    value = float(size_parts[0])
                                    unit = size_parts[1].upper()
                                    if unit in ['MB', 'M']:
                                        total_size_bytes = int(
                                            value * 1024 * 1024
                                        )
                                    elif unit in ['GB', 'G']:
                                        total_size_bytes = int(
                                            value * 1024 * 1024
                                            * 1024
                                        )
                                    elif unit in ['KB', 'K']:
                                        total_size_bytes = int(value * 1024)
                                    elif unit in ['B', 'BYTES']:
                                        total_size_bytes = int(value)
                                    logger.info(
                                        f"[DOWNLOAD] Parsed size: "
                                        f"{total_size_bytes / (1024*1024):.2f}"
                                        f"MB"
                                    )
                        except Exception as parse_error:
                            logger.warning(
                                f"[DOWNLOAD] Failed to parse size "
                                f"'{size_value}': {parse_error}"
                            )

            # If still no size, count siblings that exist
            if total_size_bytes == 0:
                siblings = getattr(info, 'siblings', [])
                file_count = len([s for s in siblings
                                 if getattr(s, 'rfilename', '')])
                logger.info(
                    f"[DOWNLOAD] No size info available. "
                    f"Found {file_count} files but cannot determine total size"
                )
                latency = time.time() - start_time
                return self._create_error_result(
                    f"Cannot determine model size ({file_count} files found)",
                    latency
                )

            # Convert to MB
            total_size_mb = total_size_bytes / (1024 * 1024)
            logger.info(
                f"[DOWNLOAD] Total model size: {total_size_mb:.2f} MB"
            )

            # Update the file_size in database
            artifact.file_size = int(total_size_bytes)
            artifact.save()

            logger.info(
                f"[DOWNLOAD] Updated artifact file_size to "
                f"{total_size_mb:.2f} MB"
            )
            print(
                f"[DownloadUploader] Updated file size: "
                f"{total_size_mb:.2f} MB"
            )

            latency = time.time() - start_time
            logger.info(
                f"[DOWNLOAD] Process complete (latency: {latency:.3f}s)"
            )

            return self._create_success_result(
                total_size_mb,
                latency
            )

        except Exception as e:
            logger.error(
                f"[DOWNLOAD] Error during download/upload: {e}",
                exc_info=True
            )
            print(f"[DownloadUploader] Error: {e}")
            import traceback
            traceback.print_exc()
            latency = time.time() - start_time
            return self._create_error_result(str(e), latency)

    def _create_success_result(
        self,
        size_mb: float,
        latency: float
    ) -> Dict[str, Any]:
        """Create successful result"""
        print(
            f"[DownloadUploader] Success: {size_mb:.2f} MB"
        )

        return {
            'job_name': 'download_upload',
            'success': True,
            'size_mb': size_mb,
            'latency': round(latency, 3),
            'details': {
                'status': 'size_updated',
                'message': 'File size determined and updated in database'
            }
        }

    def _create_skip_result(
        self,
        reason: str,
        latency: float,
        size_mb: float = 0.0
    ) -> Dict[str, Any]:
        """Create skip result"""
        print(f"[DownloadUploader] Skipped: {reason}")

        return {
            'job_name': 'download_upload',
            'success': True,
            'skipped': True,
            'size_mb': size_mb,
            'latency': round(latency, 3),
            'details': {
                'status': 'skipped',
                'reason': reason
            }
        }

    def _create_error_result(
        self,
        error_msg: str,
        latency: float
    ) -> Dict[str, Any]:
        """Create error result"""
        print(f"[DownloadUploader] Error: {error_msg}")

        return {
            'job_name': 'download_upload',
            'success': False,
            'error': error_msg,
            'latency': round(latency, 3),
            'details': {
                'status': 'error',
                'message': error_msg
            }
        }


# Pipeline integration function
def download_and_upload_step(context):
    """
    Download artifact files and upload to S3
    Args:
        context: Pipeline context containing metadata
    Returns:
        dict: Result without metric_name (ignored by aggregate)
    """
    metadata = context.get('last') if isinstance(context, dict) else context
    uploader = DownloadUploader()
    return uploader.download_and_upload(metadata)
