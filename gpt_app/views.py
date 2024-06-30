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

class GPTView(APIView):
    def post(self, request):
        prompt = request.data.get("prompt", "")
        if not prompt:
            logger.debug("No prompt provided")
            return Response({"error": "No prompt provided"}, status=status.HTTP_400_BAD_REQUEST)
        
        file_path = os.path.join(os.path.dirname(__file__), "assets", "autcollection.jsonl")
        file_content = ""
        try:
            with open(file_path, "r") as file:
                for line in file:
                    file_content += json.loads(line).get("content", "") + "\n"
        except FileNotFoundError:
            logger.error("File not found")
            return Response({"error": "File not found"}, status=status.HTTP_400_BAD_REQUEST)
        except json.JSONDecodeError as e:
            logger.error(f"JSON Decode Error: {str(e)}")
            return Response({"error": f"JSON Decode Error: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        except Exception as e:
            logger.error(f"Error reading file: {str(e)}")
            return Response({"error": f"Error reading file: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        try:
            logger.debug(f"Using API key: {api_key}")  # Log the API key
            system_role_content = f"""
            You are an assistant designed to answer questions about a specific application.
            Here is some context about the application from a file:
            {file_content}
            """
            
            response = client.chat.completions.create(
                model="gpt-3.5-turbo", 
                messages=[
                    {"role": "system", "content": system_role_content },
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


