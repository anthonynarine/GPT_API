from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from openai import OpenAI
from decouple import config
import httpx
import logging
import json
import os

# Instantiate the OpenAI client
api_key = config('OPENAI_API_KEY')
client = OpenAI(api_key=api_key)

# Get an instance of a logger
logger = logging.getLogger('gpt_app')

def read_jsonl_file(file_path):
    """
    Reads a JSONL file and concatenates the content field from each line.

    Args:
        file_path (str): The path to the JSONL file.

    Returns:
        str: Concatenated content from the JSONL file.

    Raises:
        FileNotFoundError: If the file does not exist.
        ValueError: If there is a JSON decode error in the file.
        Exception: If any other error occurs during file reading.
    """
    content = ""
    try:
        with open(file_path, "r") as file:
            line_number = 0
            for line in file:
                line_number += 1
                try:
                    json_line = json.loads(line)
                    content += json_line.get("content", "") + "\n"
                except json.JSONDecodeError as e:
                    logger.error(f"JSON Decode Error in line {line_number}: {line.strip()}. Error: {str(e)}")
                    raise ValueError(f"JSON Decode Error in line {line_number}: {line.strip()}. Error: {str(e)}")
    except FileNotFoundError as e:
        logger.error(f"File not found: {file_path}. Error: {str(e)}")
        raise FileNotFoundError(f"File not found: {file_path}. Error: {str(e)}")
    except Exception as e:
        logger.error(f"Error reading file {file_path}: {str(e)}")
        raise Exception(f"Error reading file {file_path}: {str(e)}")

    return content

class GPTView(APIView):
    """
    API View to interact with OpenAI's GPT-3.5 model.
    Handles POST requests to generate a response based on the provided prompt.
    """

    def options(self, request, *args, **kwargs):
        """
        Handles OPTIONS requests for CORS preflight.

        Args:
            request (Request): The HTTP request object.

        Returns:
            Response: An HTTP response with the appropriate CORS headers.
        """
        response = Response(status=status.HTTP_200_OK)
        response['Access-Control-Allow-Origin'] = '*'
        response['Access-Control-Allow-Methods'] = 'GET, POST, OPTIONS'
        response['Access-Control-Allow-Headers'] = 'Content-Type, Authorization'
        return response

    def post(self, request):
        """
        Handles POST requests to generate a GPT-3.5 response.

        Args:
            request (Request): The HTTP request containing the 'prompt'.

        Returns:
            Response: The generated response from GPT-3.5 or an error message.
        """
        prompt = request.data.get("prompt", "")
        if not prompt:
            logger.debug("No prompt provided")
            return Response({"error": "No prompt provided"}, status=status.HTTP_400_BAD_REQUEST)
        
        autcollection_file_path = os.path.join(os.path.dirname(__file__), "assets", "autcollection.jsonl")

        try:
            autcollection_content = read_jsonl_file(autcollection_file_path)
        except FileNotFoundError as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except ValueError as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        combined_content = autcollection_content
        
        try:
            logger.debug(f"Using API key: {api_key}")  # Log the API key
            system_role_content = f"""
            You are an assistant designed to answer questions about a specific application.
            Here is some context about the application from a file:
            {combined_content}
            """
            
            response = client.chat.completions.create(
                model="gpt-3.5-turbo", 
                messages=[
                    {"role": "system", "content": system_role_content},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.1,
                max_tokens=150,
                n=1
            )
            logger.debug(f"Response: {response.choices[0].message.content.strip()}")
            return Response(response.choices[0].message.content.strip(), status=status.HTTP_200_OK)
        except httpx.HTTPStatusError as e:
            logger.error(f"HTTP Status Error: {str(e)}")
            if e.response.status_code == 429:
                return Response({"error": "You have exceeded your API quota. Please check your plan and billing details."}, status=status.HTTP_429_TOO_MANY_REQUESTS)
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        except httpx.RequestError as e:
            logger.error(f"Request Error: {str(e)}")
            return Response({"error": "An error occurred while making the request: " + str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        except Exception as e:
            logger.error(f"General Error: {str(e)}")
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

