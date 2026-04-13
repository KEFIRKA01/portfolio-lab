from datetime import datetime, timedelta, timezone

from bot.dispatch import DispatchBoard, DispatchTask


def test_eta_breach_and_handoff_detection() -> None:
    now = datetime.now(timezone.utc)
    board = DispatchBoard()
    board.add(DispatchTask(task_id="d-1", title="Late", region="moscow", due_at=now - timedelta(minutes=5)))
    board.add(DispatchTask(task_id="d-2", title="Soon", region="spb", due_at=now + timedelta(minutes=40)))
    board.assign("d-2", "crew-7")
    assert len(board.eta_breaches(now)) == 1
    assert len(board.handoff_candidates(now)) == 1
