from __future__ import annotations

from .scenarios import RequestBoard, ServiceRequest, manager_alert_text

try:
    from telegram import Update
    from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
except ImportError:  # pragma: no cover
    Update = None
    ContextTypes = None
    ApplicationBuilder = None
    CommandHandler = None


if ApplicationBuilder:
    def get_board(context: ContextTypes.DEFAULT_TYPE) -> RequestBoard:
        board = context.application.bot_data.get("request_board")
        if board is None:
            board = RequestBoard()
            context.application.bot_data["request_board"] = board
        return board


    async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        demo = ServiceRequest(
            request_id="demo-1",
            customer_name="Алексей",
            summary="Нужна интеграция формы с CRM",
        )
        board = get_board(context)
        board.add(demo)
        await update.message.reply_text(manager_alert_text(demo))


    async def status(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        board = get_board(context)
        digest = board.digest()
        await update.message.reply_text(
            f"Всего заявок: {digest['total']}\n"
            f"Высокий приоритет: {digest['high_priority']}\n"
            f"Ждут клиента: {digest['waiting_customer']}"
        )


    def build_app(token: str):
        app = ApplicationBuilder().token(token).build()
        app.add_handler(CommandHandler("start", start))
        app.add_handler(CommandHandler("status", status))
        return app
