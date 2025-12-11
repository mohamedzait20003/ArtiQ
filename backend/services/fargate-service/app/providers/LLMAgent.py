"""
LLM Agent for AWS Bedrock
Handles interactions with AWS Bedrock models for AI-powered tasks
"""

import os
import json
from include import get_bedrock
from typing import Dict, Any, Optional


class LLMAgent:
    """
    LLM Agent for interacting with AWS Bedrock models
    """

    def __init__(self, model_id: Optional[str] = None):
        """
        Initialize LLM Agent

        Args:
            model_id: Bedrock model ID (defaults to env var LLM_MODEL_ID)
        """
        self.bedrock_client = get_bedrock()
        self.model_id = model_id or os.environ.get(
            'LLM_MODEL_ID',
            'anthropic.claude-3-5-sonnet-20241022-v2:0'
        )
        print(f"[LLMAgent] Initialized with model: {self.model_id}")

    def send_prompt(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        max_tokens: int = 4096,
        temperature: float = 0.7,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Send a prompt to the LLM model

        Args:
            prompt: The user prompt/question
            system_prompt: Optional system prompt for context
            max_tokens: Maximum tokens in response
            temperature: Sampling temperature (0.0 - 1.0)
            **kwargs: Additional model-specific parameters

        Returns:
            Response dictionary with 'content' and metadata
        """
        try:
            # Build messages
            messages = [
                {
                    "role": "user",
                    "content": prompt
                }
            ]

            # Build request body based on model type
            if 'anthropic.claude' in self.model_id:
                request_body = {
                    "anthropic_version": "bedrock-2023-05-31",
                    "max_tokens": max_tokens,
                    "temperature": temperature,
                    "messages": messages
                }

                # Add system prompt if provided
                if system_prompt:
                    request_body["system"] = system_prompt

                # Add any additional parameters
                request_body.update(kwargs)

            else:
                # Generic format for other models
                request_body = {
                    "prompt": prompt,
                    "max_tokens": max_tokens,
                    "temperature": temperature,
                    **kwargs
                }

            # Invoke model
            response = self.bedrock_client.invoke_model(
                modelId=self.model_id,
                body=json.dumps(request_body),
                contentType="application/json",
                accept="application/json"
            )

            # Parse response
            response_body = json.loads(response['body'].read())

            return self.process_response(response_body)

        except Exception as e:
            print(f"[LLMAgent] Error sending prompt: {e}")
            import traceback
            traceback.print_exc()
            return {
                "success": False,
                "error": str(e),
                "content": None
            }

    def process_response(
        self,
        response_body: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Process the raw response from Bedrock

        Args:
            response_body: Raw response from Bedrock API

        Returns:
            Processed response with extracted content and metadata
        """
        try:
            # Handle Claude response format
            if 'content' in response_body:
                content_blocks = response_body.get('content', [])
                if content_blocks and len(content_blocks) > 0:
                    # Extract text from first content block
                    text_content = content_blocks[0].get('text', '')

                    return {
                        "success": True,
                        "content": text_content,
                        "full_response": response_body,
                        "usage": response_body.get('usage', {}),
                        "stop_reason": response_body.get('stop_reason'),
                        "model_id": response_body.get('model')
                    }

            # Handle generic completion format
            elif 'completion' in response_body:
                return {
                    "success": True,
                    "content": response_body['completion'],
                    "full_response": response_body,
                    "stop_reason": response_body.get('stop_reason')
                }

            # Unknown format
            else:
                return {
                    "success": False,
                    "error": "Unknown response format",
                    "content": None,
                    "full_response": response_body
                }

        except Exception as e:
            print(f"[LLMAgent] Error processing response: {e}")
            return {
                "success": False,
                "error": str(e),
                "content": None,
                "full_response": response_body
            }

    def extract_json_from_response(
        self,
        response: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        """
        Extract JSON from LLM response content

        Args:
            response: Processed response from process_response

        Returns:
            Parsed JSON dict or None if parsing fails
        """
        try:
            content = response.get('content', '')
            if not content:
                return None

            # Try to find JSON in markdown code blocks
            if '```json' in content:
                # Extract JSON from code block
                start = content.find('```json') + 7
                end = content.find('```', start)
                json_str = content[start:end].strip()
            elif '```' in content:
                # Extract from generic code block
                start = content.find('```') + 3
                end = content.find('```', start)
                json_str = content[start:end].strip()
            else:
                # Try to parse entire content as JSON
                json_str = content.strip()

            return json.loads(json_str)

        except Exception as e:
            print(f"[LLMAgent] Error extracting JSON: {e}")
            return None
