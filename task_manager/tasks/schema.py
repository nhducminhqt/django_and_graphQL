import graphene
from graphene_django.types import DjangoObjectType
from django_filters import FilterSet, CharFilter, OrderingFilter
from .models import Task
from django.contrib.auth.models import User
from .validators import (
    validate_status,
    validate_title,
    validate_description,
    validate_user_email,
    validate_username,
    validate_password,
    validate_user_exists
)

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
        fields = ("id", "title", "description", "created_at", "updated_at", "owner", "assignee", "status")  

# Bộ lọc cho Task
class TaskFilter(FilterSet):
    owner_username = CharFilter(field_name='owner__username', lookup_expr='icontains')
    assignee_username = CharFilter(field_name='assignee__username', lookup_expr='icontains')
    title = CharFilter(field_name='title', lookup_expr='icontains')
    order_by = OrderingFilter(fields=('created_at', 'updated_at'))

    class Meta:
        model = Task
        fields = ['owner_username', 'assignee_username', 'title']

# Query GraphQL
class Query(graphene.ObjectType):
    all_tasks = graphene.List(
        TaskType,
        title=graphene.String(),
        owner_username=graphene.String(),
        assignee_username=graphene.String(),
        status=graphene.String(),
    )
    all_users = graphene.List(UserType)

    def resolve_all_tasks(self, info, title=None, owner_username=None, assignee_username=None, status=None):
        tasks = Task.objects.all()

        if title is not None:
            tasks = tasks.filter(title__icontains=title)
        if owner_username is not None:
            tasks = tasks.filter(owner__username__icontains=owner_username)
        if assignee_username is not None:
            tasks = tasks.filter(assignee__username__icontains=assignee_username)
        if status:
            validate_status(status)
            tasks = tasks.filter(status=status)

        return tasks

    def resolve_all_users(self, info):
        return User.objects.all()

    def resolve_tasks_by_owner(self, info, owner_username):
        return Task.objects.filter(owner__username__icontains=owner_username)

    def resolve_tasks_by_assignee(self, info, assignee_username):
        return Task.objects.filter(assignee__username__icontains=assignee_username)

    def resolve_tasks_by_title(self, info, title):
        return Task.objects.filter(title__icontains=title)

# Mutation thêm Task
class CreateTask(graphene.Mutation):
    class Arguments:
        title = graphene.String(required=True)
        description = graphene.String()
        owner_id = graphene.Int(required=True)
        assignee_id = graphene.Int()
        status = graphene.String()

    task = graphene.Field(TaskType)

    def mutate(self, info, title, owner_id, description=None, assignee_id=None, status="todo"):
        validate_status(status)
        validate_title(title)
        if description:
            validate_description(description)

        validate_user_exists(owner_id)
        owner = User.objects.get(id=owner_id)

        assignee = None
        if assignee_id:
            validate_user_exists(assignee_id)
            assignee = User.objects.get(id=assignee_id)

        task = Task(title=title, description=description, owner=owner, assignee=assignee, status=status)
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
        validate_user_email(email)
        validate_username(username)
        validate_password(password)

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
        try:
            task = Task.objects.get(pk=id)
            task.delete()
            success = True
        except Task.DoesNotExist:
            raise Exception("Task not found")
        return DeleteTask(success=success)

# Mutation để cập nhật Task
class UpdateTask(graphene.Mutation):
    class Arguments:
        id = graphene.ID(required=True)
        title = graphene.String()
        description = graphene.String()
        assignee_id = graphene.Int()
        status = graphene.String()

    task = graphene.Field(TaskType)

    def mutate(self, info, id, title=None, description=None, assignee_id=None, status=None):
        try:
            task = Task.objects.get(pk=id)
        except Task.DoesNotExist:
            raise Exception("Task not found")

        if title is not None:
            validate_title(title)
            task.title = title
        if description is not None:
            validate_description(description)
            task.description = description
        if assignee_id is not None:
            validate_user_exists(assignee_id)
            task.assignee = User.objects.get(id=assignee_id)
        if status:
            validate_status(status)
            task.status = status

        task.save()
        return UpdateTask(task=task)

class Mutation(graphene.ObjectType):
    createTask = CreateTask.Field()
    deleteTask = DeleteTask.Field()
    createUser = CreateUser.Field()
    updateTask = UpdateTask.Field()  

schema = graphene.Schema(query=Query, mutation=Mutation)