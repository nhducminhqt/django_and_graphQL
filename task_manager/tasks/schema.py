import graphene
from graphene_django.types import DjangoObjectType
from graphene_django.filter import DjangoFilterConnectionField
from django_filters import FilterSet, CharFilter, OrderingFilter
from .models import Task
from django.contrib.auth.models import User

# GraphQL Type cho User
class UserType(DjangoObjectType):
    class Meta:
        model = User
        fields = ("id", "username", "email")

class TaskType(DjangoObjectType):
    owner = graphene.Field(UserType)
    assignee = graphene.Field(UserType)

    class Meta:
        model = Task
        fields = ("id", "title", "description", "created_at", "updated_at", "owner", "assignee")

# Bộ lọc cho Task
class TaskFilter(FilterSet):
    owner_username = CharFilter(field_name='owner__username', lookup_expr='icontains')
    assignee_username = CharFilter(field_name='assignee__username', lookup_expr='icontains')
    order_by = OrderingFilter(fields=('created_at', 'updated_at'))

    class Meta:
        model = Task
        fields = ['owner_username', 'assignee_username']

# Query GraphQL
class Query(graphene.ObjectType):
    task = graphene.Field(TaskType, id=graphene.Int(required=True))
    all_tasks = graphene.List(TaskType)
    all_users = graphene.List(UserType)

    def resolve_task(self, info, id):
        return Task.objects.get(pk=id)

    def resolve_all_tasks(self, info):
        return Task.objects.all()

    def resolve_all_users(self, info):
        return User.objects.all()

# Mutation để thêm Task
class CreateTask(graphene.Mutation):
    class Arguments:
        title = graphene.String(required=True)
        description = graphene.String()
        owner_id = graphene.Int(required=True)
        assignee_id = graphene.Int()

    task = graphene.Field(TaskType)

    def mutate(self, info, title, owner_id, description=None, assignee_id=None):
        owner = User.objects.get(id=owner_id)
        assignee = User.objects.get(id=assignee_id) if assignee_id else None
        task = Task(title=title, description=description, owner=owner, assignee=assignee)
        task.save()
        return CreateTask(task=task)

# Mutation để thêm User
class CreateUser(graphene.Mutation):
    class Arguments:
        username = graphene.String(required=True)
        email = graphene.String(required=True)
        password = graphene.String(required=True)

    user = graphene.Field(UserType)

    def mutate(self, info, username, email, password):
        user = User(username=username, email=email)
        user.set_password(password)
        user.save()
        return CreateUser(user=user)

# Mutation để xóa Task
class DeleteTask(graphene.Mutation):
    class Arguments:
        id = graphene.ID(required=True)

    success = graphene.Boolean()

    def mutate(self, info, id):
        task = Task.objects.get(pk=id)
        task.delete()
        return DeleteTask(success=True)

# Schema tổng hợp
class Mutation(graphene.ObjectType):
    create_task = CreateTask.Field()
    delete_task = DeleteTask.Field()
    create_user = CreateUser.Field()

schema = graphene.Schema(query=Query, mutation=Mutation)
