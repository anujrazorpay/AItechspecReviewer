import json
import boto3
import logging
from typing import Dict, Optional, Tuple
from botocore.config import Config

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class BedrockService:
    def __init__(self, region_name: str = "us-east-1"):
        """Initialize AWS Bedrock client."""
        self.client = boto3.client(
            'bedrock-runtime',
            region_name=region_name,
            config=Config(
                retries=dict(
                    max_attempts=3
                )
            )
        )
        self.model_id = "anthropic.claude-3-sonnet-20240229-v1:0"  # Using Claude 3 Sonnet
        logger.info(f"Initialized BedrockService with region: {region_name}")

    def review_document(self, prompt: str) -> Tuple[Dict, Dict]:
        """Send the structured prompt to Claude and return both request and response as dicts."""
        if not prompt:
            logger.warning("Empty prompt received")
            return (
                {'messages': []},
                {'overall_score': None, 'overall_comment': '', 'sections': []}
            )

        # Prepare the request body for Claude
        request_body = {
            "anthropic_version": "bedrock-2023-05-31",
            "max_tokens": 1500,
            "temperature": 0.7,
            "messages": [
                {
                    "role": "system",
                    "content": (
                        "You are a technical specification reviewer. "
                        "Return ONLY a valid JSON object with the following structure. "
                        "Do not include any explanation or extra text outside the JSON.\n"
                        "Example:\n"
                        "{\n"
                        "  \"overall_score\": 8,\n"
                        "  \"overall_comment\": \"The document is well-structured.\",\n"
                        "  \"sections\": [\n"
                        "    {\n"
                        "      \"header\": \"Introduction\",\n"
                        "      \"score\": 5,\n"
                        "      \"comment\": \"Clear and complete.\",\n"
                        "      \"suggestions\": \"\"\n"
                        "    },\n"
                        "    {\n"
                        "      \"header\": \"System Requirements\",\n"
                        "      \"score\": 3,\n"
                        "      \"comment\": \"Missing details on memory requirements.\",\n"
                        "      \"suggestions\": \"Add more details on hardware.\"\n"
                        "    }\n"
                        "  ]\n"
                        "}\n"
                    )
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ]
        }

        # Log the request details
        logger.info("=== Bedrock Request Details ===")
        logger.info(f"Model ID: {self.model_id}")
        logger.info("Request Body:")
        logger.info(json.dumps(request_body, indent=2))
        logger.info("=== End Request Details ===")

        try:
            # Make the API call to Bedrock
            response = self.client.invoke_model(
                modelId=self.model_id,
                body=json.dumps(request_body)
            )

            # Log the response
            logger.info("=== Bedrock Response ===")
            logger.info(f"Response Status: {response['ResponseMetadata']['HTTPStatusCode']}")
            response_body = json.loads(response['body'].read())
            logger.info("Response Body:")
            logger.info(json.dumps(response_body, indent=2))
            logger.info("=== End Response ===")

            content = response_body['content'][0]['text']

            # Try to parse the response as JSON
            try:
                ai_response = json.loads(content)
                logger.info("Successfully parsed AI response as JSON")
            except Exception as e:
                logger.warning(f"Failed to parse response as JSON: {str(e)}")
                # If the response is not valid JSON, try to extract JSON from the text
                import re
                match = re.search(r'\{.*\}', content, re.DOTALL)
                if match:
                    ai_response = json.loads(match.group(0))
                    logger.info("Successfully extracted and parsed JSON from response")
                else:
                    logger.warning("Could not extract JSON from response")
                    ai_response = {'overall_score': None, 'overall_comment': content, 'sections': []}

            return request_body, ai_response

        except Exception as e:
            logger.error(f"Error in document review: {str(e)}", exc_info=True)
            # Return the request body even if the API call failed
            return (
                request_body,
                {'overall_score': None, 'overall_comment': f"Error during review: {str(e)}", 'sections': []}
            ) 