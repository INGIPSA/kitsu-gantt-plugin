import json

from zou.app import db
from zou.app.models.task import Task
from zou.app.models.schedule_item import ScheduleItem
from zou.app.models.entity import Entity
from zou.app.models.task_type import TaskType
from zou.app.models.task_status import TaskStatus
from zou.app.models.person import Person

from .models import GanttView


# ---------- Live data readers (no plugin tables involved) ----------


def get_tasks_for_gantt(project_id):
    """Return tasks of a project shaped for a Gantt chart.

    Includes every task with at least a start_date OR due_date set.
    Tasks without any date are returned with `has_dates=False` so the
    frontend can list them in an "unscheduled" section.
    """
    rows = (
        db.session.query(Task, Entity, TaskType, TaskStatus)
        .join(Entity, Task.entity_id == Entity.id)
        .join(TaskType, Task.task_type_id == TaskType.id)
        .join(TaskStatus, Task.task_status_id == TaskStatus.id)
        .filter(Task.project_id == project_id)
        .all()
    )

    results = []
    for task, entity, task_type, task_status in rows:
        start = task.start_date or task.real_start_date
        end = task.end_date or task.due_date or task.done_date
        results.append(
            {
                "id": str(task.id),
                "name": f"{entity.name} / {task_type.name}",
                "entity_id": str(entity.id),
                "entity_name": entity.name,
                "task_type_id": str(task_type.id),
                "task_type_name": task_type.name,
                "task_type_color": task_type.color,
                "task_status_id": str(task_status.id),
                "task_status_name": task_status.name,
                "task_status_color": task_status.color,
                "task_status_short_name": task_status.short_name,
                "start": start.isoformat() if start else None,
                "end": end.isoformat() if end else None,
                "due_date": task.due_date.isoformat()
                if task.due_date
                else None,
                "real_start_date": task.real_start_date.isoformat()
                if task.real_start_date
                else None,
                "done_date": task.done_date.isoformat()
                if task.done_date
                else None,
                "duration": task.duration,
                "estimation": task.estimation,
                "priority": task.priority,
                "progress": _progress_from_status(task_status.short_name),
                "has_dates": bool(start or end),
            }
        )
    return results


def get_schedule_items_for_gantt(project_id):
    """Return high-level schedule items (per task_type per entity)."""
    rows = (
        db.session.query(ScheduleItem, TaskType)
        .join(TaskType, ScheduleItem.task_type_id == TaskType.id)
        .filter(ScheduleItem.project_id == project_id)
        .all()
    )

    results = []
    for item, task_type in rows:
        results.append(
            {
                "id": str(item.id),
                "object_id": str(item.object_id) if item.object_id else None,
                "task_type_id": str(task_type.id),
                "task_type_name": task_type.name,
                "task_type_color": task_type.color,
                "start": item.start_date.isoformat()
                if item.start_date
                else None,
                "end": item.end_date.isoformat() if item.end_date else None,
                "man_days": item.man_days,
            }
        )
    return results


def _progress_from_status(short_name):
    """Crude default mapping. V2 will read this from a per-status setting."""
    if not short_name:
        return 0
    s = short_name.lower()
    if s in ("done", "approved", "ok"):
        return 100
    if s in ("wfa", "wait", "review"):
        return 90
    if s in ("wip", "inprogress"):
        return 50
    if s in ("retake",):
        return 30
    if s in ("todo",):
        return 0
    return 0


# ---------- CRUD on saved views (plugin_gantt_view table) ----------


def get_views_for_project(project_id):
    views = GanttView.get_all_by(project_id=project_id)
    return [v.present() for v in views]


def get_view(view_id):
    return GanttView.get(view_id)


def create_view(
    project_id,
    name="New View",
    visibility="private",
    config=None,
    created_by=None,
):
    return GanttView.create(
        project_id=project_id,
        name=name,
        visibility=visibility,
        config=json.dumps(config) if config else None,
        created_by=created_by,
    )


def update_view(view, data):
    update = {}
    if "name" in data:
        update["name"] = data["name"]
    if "visibility" in data:
        update["visibility"] = data["visibility"]
    if "config" in data:
        update["config"] = json.dumps(data["config"])
    view.update(update)
    return view


def delete_view(view):
    view.delete()
