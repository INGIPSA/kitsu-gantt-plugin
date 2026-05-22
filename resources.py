from flask import request
from flask_restful import Resource
from flask_jwt_extended import jwt_required

from zou.app.mixin import ArgsMixin
from zou.app.services import persons_service

from . import services


class GanttTasksResource(Resource, ArgsMixin):
    """Live tasks of a project, shaped for a Gantt chart."""

    @jwt_required()
    def get(self):
        project_id = self.get_text_parameter("project_id")
        if not project_id:
            return {"error": "project_id required"}, 400
        return services.get_tasks_for_gantt(project_id)


class GanttScheduleItemsResource(Resource, ArgsMixin):
    """Live schedule items (high-level per task_type per entity)."""

    @jwt_required()
    def get(self):
        project_id = self.get_text_parameter("project_id")
        if not project_id:
            return {"error": "project_id required"}, 400
        return services.get_schedule_items_for_gantt(project_id)


class GanttMilestonesResource(Resource, ArgsMixin):
    """Live milestones for a project."""

    @jwt_required()
    def get(self):
        project_id = self.get_text_parameter("project_id")
        if not project_id:
            return {"error": "project_id required"}, 400
        return services.get_milestones_for_gantt(project_id)


class GanttViewsResource(Resource, ArgsMixin):
    """Saved Gantt view configurations for a project."""

    @jwt_required()
    def get(self):
        project_id = self.get_text_parameter("project_id")
        if not project_id:
            return {"error": "project_id required"}, 400
        return services.get_views_for_project(project_id)

    @jwt_required()
    def post(self):
        data = request.get_json()
        project_id = data.get("project_id")
        if not project_id:
            return {"error": "project_id required"}, 400

        current_user = persons_service.get_current_user()
        view = services.create_view(
            project_id=project_id,
            name=data.get("name", "New View"),
            visibility=data.get("visibility", "private"),
            config=data.get("config"),
            created_by=current_user["id"],
        )
        return view.present(), 201


class GanttViewResource(Resource, ArgsMixin):

    @jwt_required()
    def get(self, view_id):
        view = services.get_view(view_id)
        if not view:
            return {"error": "View not found"}, 404
        return view.present()

    @jwt_required()
    def put(self, view_id):
        view = services.get_view(view_id)
        if not view:
            return {"error": "View not found"}, 404
        data = request.get_json()
        services.update_view(view, data)
        return view.present()

    @jwt_required()
    def delete(self, view_id):
        view = services.get_view(view_id)
        if not view:
            return {"error": "View not found"}, 404
        services.delete_view(view)
        return "", 204
