from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from typing import Dict, List


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


@dataclass(slots=True)
class DispatchTask:
    task_id: str
    title: str
    region: str
    due_at: datetime
    assigned_crew: str | None = None
    status: str = "new"
    notes: List[str] = field(default_factory=list)


class DispatchBoard:
    def __init__(self) -> None:
        self._tasks: Dict[str, DispatchTask] = {}

    def add(self, task: DispatchTask) -> None:
        self._tasks[task.task_id] = task

    def assign(self, task_id: str, crew: str) -> None:
        task = self._tasks[task_id]
        task.assigned_crew = crew
        task.status = "assigned"

    def mark_enroute(self, task_id: str, note: str) -> None:
        task = self._tasks[task_id]
        task.status = "enroute"
        task.notes.append(note)

    def eta_breaches(self, now: datetime) -> List[DispatchTask]:
        return [task for task in self._tasks.values() if task.status != "done" and task.due_at < now]

    def handoff_candidates(self, now: datetime) -> List[DispatchTask]:
        limit = now + timedelta(hours=1)
        return [task for task in self._tasks.values() if task.status in {"assigned", "enroute"} and task.due_at <= limit]

    def digest(self, now: datetime) -> Dict[str, int]:
        return {
            "total": len(self._tasks),
            "eta_breaches": len(self.eta_breaches(now)),
            "handoff_candidates": len(self.handoff_candidates(now)),
        }
