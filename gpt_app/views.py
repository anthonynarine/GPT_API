from decouple import config
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
import openai

class GPTView(APIView):
    def post(self, request):
        prompt = request.data.get("prompt", "")
        if not prompt:
            return Response({"error": "No prompt provided"}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            openai.api_key = config("OPENAI_API_KEY")
            response = openai.Completion.create(
                engine="davinci",
                prompt=prompt,
                max_tokens=150
            )
            return Response(response.choices[0].text.strip(), status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
