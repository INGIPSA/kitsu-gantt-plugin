from . import resources


routes = [
    ("/tasks", resources.GanttTasksResource),
    ("/schedule-items", resources.GanttScheduleItemsResource),
    ("/milestones", resources.GanttMilestonesResource),
    ("/views", resources.GanttViewsResource),
    ("/views/<view_id>", resources.GanttViewResource),
]


def pre_install(manifest):
    pass


def post_install(manifest):
    pass


def pre_uninstall(manifest):
    pass


def post_uninstall(manifest):
    pass
