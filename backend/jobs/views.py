"""Views autenticadas para envio e acesso privado a vagas."""
# views.py
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import JobPosting
from .serializers import JobPostingSerializer


class JobPostingListCreateView(APIView):
    """
    GET  -> lista as job postings do usuário autenticado
    POST -> cria uma nova job posting (submissão de texto por enquanto)
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        job_postings = JobPosting.objects.filter(submitted_by=request.user)
        serializer = JobPostingSerializer(job_postings, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request):
        serializer = JobPostingSerializer(
            data=request.data,
            context={"request": request},
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class JobPostingDetailView(APIView):
    """
    GET    -> detalhe de uma job posting específica
    DELETE -> remove uma job posting
    """
    permission_classes = [IsAuthenticated]
    """
    separar a rota delete pra ser admin depois que finalizarmos os testes
    """
    def get_object(self, pk, user):
        try:
            return JobPosting.objects.get(pk=pk, submitted_by=user)
        except JobPosting.DoesNotExist:
            return None

    def get(self, request, pk):
        job_posting = self.get_object(pk, request.user)
        if job_posting is None:
            return Response(
                {"detail": "Job posting não encontrada."},
                status=status.HTTP_404_NOT_FOUND,
            )
        serializer = JobPostingSerializer(job_posting)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def delete(self, request, pk):
        job_posting = self.get_object(pk, request.user)
        if job_posting is None:
            return Response(
                {"detail": "Job posting não encontrada."},
                status=status.HTTP_404_NOT_FOUND,
            )
        job_posting.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)