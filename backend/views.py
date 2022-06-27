
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import authentication, permissions
from ml.data_retrieval import get_articles
from ml.pipelines import sliding_window_optics_pipeline


class Timeline(APIView):
    authentication_classes = []
    permission_classes = []
    def get(self, request):
        q = request.query_params['q']
        articles = get_articles(q)
        clusters = sliding_window_optics_pipeline(articles)
        return Response(data=clusters)
