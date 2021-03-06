# Standard library imports.
import time

# Django imports.
from django.db import connection

# Third-party imports.
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
import django_rq
from psycopg2 import sql
from rest_framework import response, status, views, viewsets

# Local imports.
from .models import Task
from .serializers import TaskSerializer

__author__ = 'Jason Parent'

DEFAULT_DURATION = 5


def create_task(*, task_id, duration=DEFAULT_DURATION, sync=True):
    task = Task.objects.get(id=task_id)
    time.sleep(duration)
    task.status = Task.SUCCESS
    task.save()
    if not sync:
        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)(group=f'task-{task_id}', message={
            'type': 'task.status',
            'task': TaskSerializer(task).data,
        })


class TasksView(viewsets.ModelViewSet):
    queryset = Task.objects.all()
    serializer_class = TaskSerializer
    lookup_url_kwarg = 'task_id'

    def perform_create(self, serializer):
        task = serializer.save()
        django_rq.enqueue(
            create_task,
            task_id=task.id,
            duration=self.request.data.get('duration', DEFAULT_DURATION),
            sync=self.request.data.get('sync', True)
        )


class ClearTasksView(views.APIView):
    def post(self, request, *args, **kwargs):
        count = Task.objects.count()
        with connection.cursor() as cursor:
            cursor.execute(sql.SQL("""
                TRUNCATE {table_name} RESTART IDENTITY CASCADE;
            """).format(table_name=sql.Identifier('tasks_task')))
        return response.Response(status=status.HTTP_200_OK, data={
            'detail': f'You deleted {count} tasks.'
        })
