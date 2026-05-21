# Kitsu Gantt Plugin

A production Gantt chart plugin for [Kitsu](https://www.cg-wire.com/kitsu) — the open-source production management platform for animation, VFX, and game studios.

Reads task dates, schedule items, dependencies and milestones live from Zou, and visualises them as an interactive Gantt chart inside the Kitsu project sidebar.

> **Status: MVP.** v0.1.0 ships a read-only Gantt rendered from Zou tasks. Drag-to-reschedule, dependencies, milestones and schedule-version comparison are on the roadmap.

## Why

Kitsu's built-in Production Schedule is excellent for the high-level man-days/task-type matrix, but it isn't a timeline. Studios planning multi-month CGI productions still want a real Gantt view: bars on a calendar, drag to reschedule, dependency arrows between shots, critical path. This plugin adds that on top of the data Kitsu already stores.

## Features (v0.1.0 — MVP)

- Project Gantt rendered from live `task.start_date` / `task.end_date` / `task.due_date`
- Two data sources: **Tasks** (granular) or **Schedule items** (high-level per task-type per entity)
- View modes: Quarter Day · Half Day · Day · Week · Month
- Colour-by-status (uses each task status's configured colour)
- Progress bar derived from status (`done`→100%, `wfa`→90%, `wip`→50%, `retake`→30%, `todo`→0%)
- "No dated tasks" empty state with onboarding hint

## Roadmap

- **v0.2** — Drag start-date / end-date → `PATCH /api/data/tasks/<id>`, snap to day, optimistic UI
- **v0.3** — Dependency arrows from `entity_link`, critical path highlight, milestones from the `milestone` table
- **v0.4** — Saved views (`plugin_gantt_view` table is shipped in v0.1 already): per-user filter / group-by / colour preset
- **v0.5** — Schedule version comparison (snapshot diff using `production_schedule_version`), Gantt diff overlay
- **v0.6** — Resource view (who-when-what), workload heatmap, conflict detection
- **v1.0** — Export to PNG / PDF / MS-Project XML, scenario "what-if" mode

## Installation

### Requirements

- Zou ≥ 1.0.23 (plugin system required — earlier versions can't load any plugin)
- Kitsu ≥ 1.0.23 (same — sidebar menu needs the `/api/data/plugins` registry)
- Python 3.10+, PostgreSQL

### Quick install (recommended — ZIP)

1. Download `kitsu-gantt-plugin.zip` from the [latest release](https://github.com/INGIPSA/kitsu-gantt-plugin/releases/latest).
2. Install on your Zou server:

```bash
zou install-plugin --path ~/kitsu-gantt-plugin.zip
```

3. Restart Zou:

```bash
sudo systemctl restart zou zou-events
```

4. Hard-reload Kitsu in the browser (Ctrl+Shift+R). The **Gantt** entry now appears in every project's sidebar.

### Install from source

```bash
git clone https://github.com/INGIPSA/kitsu-gantt-plugin.git ~/kitsu-gantt-plugin
cd ~                                          # ⚠️ run install from OUTSIDE the plugin dir
zou install-plugin --path ./kitsu-gantt-plugin
```

> Do not run `zou install-plugin --path .` from inside the plugin folder — Zou's `PLUGIN_FOLDER` defaults to `./plugins/` and `shutil.copytree` will recurse into itself.

### Verifying the install

```bash
# Plugin should be listed:
zou list-plugins | grep gantt

# Static frontend — expect 200:
curl -o /dev/null -w "%{http_code}\n" https://<your-kitsu>/api/plugins/gantt/frontend/

# API route — expect 401 (auth gate; proves the route is registered):
curl -o /dev/null -w "%{http_code}\n" https://<your-kitsu>/api/plugins/gantt/tasks?project_id=...
```

## API

All endpoints require a valid Kitsu JWT (`Authorization: Bearer <token>` or session cookie set after browser login).

| Method | Path | Description |
|---|---|---|
| GET | `/api/plugins/gantt/tasks?project_id=<uuid>` | All tasks of a project, shaped for a Gantt chart |
| GET | `/api/plugins/gantt/schedule-items?project_id=<uuid>` | High-level schedule items (per task-type per entity) |
| GET | `/api/plugins/gantt/views?project_id=<uuid>` | List saved view configurations |
| POST | `/api/plugins/gantt/views` | Create a saved view |
| GET | `/api/plugins/gantt/views/<view_id>` | Get one view |
| PUT | `/api/plugins/gantt/views/<view_id>` | Update a view |
| DELETE | `/api/plugins/gantt/views/<view_id>` | Delete a view |

### Task payload shape

```json
{
  "id": "uuid",
  "name": "SH010 / Lighting",
  "entity_id": "uuid",
  "entity_name": "SH010",
  "task_type_id": "uuid",
  "task_type_name": "Lighting",
  "task_type_color": "#fbbf24",
  "task_status_id": "uuid",
  "task_status_name": "Work In Progress",
  "task_status_color": "#3b82f6",
  "task_status_short_name": "wip",
  "start": "2026-03-04T00:00:00",
  "end": "2026-03-12T00:00:00",
  "due_date": "2026-03-12T00:00:00",
  "real_start_date": null,
  "done_date": null,
  "duration": 5.0,
  "estimation": 4.0,
  "priority": 2,
  "progress": 50,
  "has_dates": true
}
```

## Database

The plugin creates one table:

| Table | Purpose |
|---|---|
| `plugin_gantt_view` | Persists saved Gantt view configurations (filters, grouping, colour mode, zoom). The Gantt data itself is read live from Zou — no duplication. |

Migration is applied automatically by `zou install-plugin` (runs `migrate-plugin-db gantt`).

## Development

```bash
# Backend — start Zou normally
zou start

# Frontend — MVP is a single-file dist/index.html with frappe-gantt from CDN.
# Edit dist/index.html, refresh Kitsu — that's it.
```

A proper Vue build mirroring the Whiteboard plugin is on the roadmap (v0.4+).

## License

AGPL-3.0 — see [LICENSE](LICENSE).

## Credits

- [Kitsu](https://www.cg-wire.com/kitsu) by CGWire
- [frappe-gantt](https://github.com/frappe/gantt) (MIT)
- Built by **Piotr Buczkowski (Bucz)** — [INGIPSA](https://github.com/INGIPSA)
