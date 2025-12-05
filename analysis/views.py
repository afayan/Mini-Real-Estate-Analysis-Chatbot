from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status

from .utils import build_analysis

@api_view(["POST"])
def analyze_query(request):
    query = request.data.get("query", "").strip()
    if not query:
        return Response({"error": "Query is required"}, status=status.HTTP_400_BAD_REQUEST)

    result = build_analysis(query)
    return Response(result)
