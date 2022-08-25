
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from ml.data_retrieval import get_articles
from ml.pipelines import sliding_window_optics_pipeline


class Timeline(APIView):
    authentication_classes = []
    permission_classes = []
    def get(self, request):
        q = request.query_params.get('q')
        if q is None:
            return Response(status=status.HTTP_400_BAD_REQUEST)

        try:
            articles = get_articles(q)
        except ValueError:
            # There is an invalid API key.
            return Response(status=status.HTTP_503_SERVICE_UNAVAILABLE)

        events = sliding_window_optics_pipeline(articles)
        return Response(data=events)
