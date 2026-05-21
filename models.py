from sqlalchemy_utils import UUIDType

from zou.app import db
from zou.app.models.serializer import SerializerMixin
from zou.app.models.base import BaseMixin


class GanttView(db.Model, BaseMixin, SerializerMixin):
    """A saved Gantt view configuration belonging to a project.

    Stores filters, grouping, color scheme, zoom level, etc. so users
    can return to a custom view without reconfiguring it every session.
    The Gantt data itself is read live from Zou's `task` and
    `schedule_item` tables — this model only persists presentation
    preferences.
    """

    __tablename__ = "plugin_gantt_view"
    __table_args__ = {"extend_existing": True}

    project_id = db.Column(
        UUIDType(binary=False),
        db.ForeignKey("project.id"),
        nullable=False,
        index=True,
    )
    name = db.Column(db.String(255), nullable=False, default="New View")
    visibility = db.Column(db.String(20), nullable=False, default="private")
    # JSON blob holding view config:
    #   { mode: "tasks" | "schedule_items",
    #     group_by: "sequence" | "asset_type" | "task_type" | "assignee" | null,
    #     filters: { task_type_ids: [], status_ids: [], assignee_ids: [] },
    #     color_by: "status" | "task_type" | "priority",
    #     zoom: "day" | "week" | "month" | "quarter",
    #     show_dependencies: bool,
    #     show_milestones: bool }
    config = db.Column(db.Text, nullable=True)
    created_by = db.Column(
        UUIDType(binary=False),
        db.ForeignKey("person.id"),
        nullable=True,
    )

    def present(self):
        return {
            "id": str(self.id),
            "project_id": str(self.project_id),
            "name": self.name,
            "visibility": self.visibility,
            "config": self.config,
            "created_by": str(self.created_by) if self.created_by else None,
            "created_at": self.created_at.isoformat()
            if self.created_at
            else None,
            "updated_at": self.updated_at.isoformat()
            if self.updated_at
            else None,
        }
