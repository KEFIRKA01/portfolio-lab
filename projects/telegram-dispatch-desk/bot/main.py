from __future__ import annotations

from datetime import datetime, timedelta, timezone

from .dispatch import DispatchBoard, DispatchTask

try:
    from telegram import Update
    from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
except ImportError:  # pragma: no cover
    Update = None
    ContextTypes = None
    ApplicationBuilder = None
    CommandHandler = None


if ApplicationBuilder:
    def get_board(context: ContextTypes.DEFAULT_TYPE) -> DispatchBoard:
        board = context.application.bot_data.get("dispatch_board")
        if board is None:
            board = DispatchBoard()
            board.add(DispatchTask(task_id="dispatch-1", title="Срочный выезд на объект", region="moscow", due_at=datetime.now(timezone.utc) + timedelta(minutes=40)))
            context.application.bot_data["dispatch_board"] = board
        return board


    async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        board = get_board(context)
        await update.message.reply_text(f"Активных задач: {board.digest(datetime.now(timezone.utc))['total']}")


    async def dispatch_status(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        board = get_board(context)
        digest = board.digest(datetime.now(timezone.utc))
        await update.message.reply_text(
            f"Просрочено по ETA: {digest['eta_breaches']}\n"
            f"Кандидаты на передачу: {digest['handoff_candidates']}"
        )


    def build_app(token: str):
        app = ApplicationBuilder().token(token).build()
        app.add_handler(CommandHandler("start", start))
        app.add_handler(CommandHandler("dispatchstatus", dispatch_status))
        return app

