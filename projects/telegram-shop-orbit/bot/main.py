from __future__ import annotations

import os
from datetime import timedelta

from .domain import Item, blueprints, display_label, normalize_tags, utc_now
from .admin import admin_snapshot, exception_board
from .exports import public_case_summary
from .messages import digest_text, help_text, item_card, queue_text, start_text
from .reporting import owner_report
from .seeds import load_seed
from .simulation import project
from .storage import Store
from .workflow import workflow_note

try:
    from telegram import Update
    from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
except ImportError:  # pragma: no cover
    Update = None
    ContextTypes = None
    ApplicationBuilder = None
    CommandHandler = None

def build_store() -> Store:
    store = Store()
    actors, items = load_seed()
    store.seed(actors, items)
    return store

if ApplicationBuilder:
    def get_store(context: ContextTypes.DEFAULT_TYPE) -> Store:
        store = context.application.bot_data.get("store")
        if store is None:
            store = build_store()
            context.application.bot_data["store"] = store
        return store

    async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        await update.message.reply_text(start_text())

    async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        await update.message.reply_text(help_text())

    async def overview(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        store = get_store(context)
        snapshot = admin_snapshot(store.queue())
        text = owner_report(store.queue()) + "\n" + f"Сводка администратора: {snapshot}"
        await update.message.reply_text(text)

    async def queue(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        store = get_store(context)
        await update.message.reply_text(queue_text(store.queue()))

    async def risk(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        store = get_store(context)
        risky = [item for item in store.queue() if item.status in {"blocked", "escalated"} or len(item.signals) >= 2]
        await update.message.reply_text(queue_text(risky))

    async def digest(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        store = get_store(context)
        sim = project(store.queue()[:3])
        note = "\n".join(f"{row.item_id}: {display_label(row.projected_status)} +{row.projected_delay_hours} ч" for row in sim)
        await update.message.reply_text(digest_text(store.queue()) + "\n\nПрогноз:\n" + note)

    async def item(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        store = get_store(context)
        target = context.args[0] if context.args else store.queue()[0].item_id
        record = store.get(target)
        exceptions = "; ".join(exception_board([record])) or "нет"
        text = item_card(record) + "\n\nМаршрут: " + workflow_note(record) + "\nИсключения: " + exceptions
        await update.message.reply_text(text)

    async def scenarios(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        lines = [start_text(), "", "Сценарии проекта:"]
        for row in blueprints():
            lines.append(f"• {row.name} | {display_label(row.category)} | {row.feature} | {row.risk} | {display_label(row.lane)}")
        lines.extend(["", public_case_summary(get_store(context).queue())])
        await update.message.reply_text("\n".join(lines))

    async def newdemo(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        store = get_store(context)
        blueprint = blueprints()[len(store.queue()) % len(blueprints())]
        item_id = "SHOP".lower() + "-dynamic-" + str(len(store.queue()) + 1)
        record = Item(
            item_id=item_id,
            customer_name="Демо-пользователь",
            title=blueprint.name + " / динамический сценарий",
            category=blueprint.category,
            status="new",
            priority=62,
            budget=26500,
            deadline_at=utc_now() + timedelta(hours=6),
            tags=normalize_tags([blueprint.category, blueprint.feature, "SHOP".lower()]),
            signals=["dynamic-demo", blueprint.risk],
            notes=["Создано командой /newdemo"],
            metadata={"scenario": blueprint.name, "source": "telegram"},
        )
        store.add_item(record)
        await update.message.reply_text(item_card(record))

    def build_app(token: str):
        app = ApplicationBuilder().token(token).build()
        app.add_handler(CommandHandler("start", start))
        app.add_handler(CommandHandler("help", help_command))
        app.add_handler(CommandHandler("overview", overview))
        app.add_handler(CommandHandler("queue", queue))
        app.add_handler(CommandHandler("risk", risk))
        app.add_handler(CommandHandler("digest", digest))
        app.add_handler(CommandHandler("item", item))
        app.add_handler(CommandHandler("scenarios", scenarios))
        app.add_handler(CommandHandler("newdemo", newdemo))
        return app

def main() -> None:  # pragma: no cover
    token = os.getenv("TELEGRAM_BOT_TOKEN")
    if not token:
        store = build_store()
        print(owner_report(store.queue()))
        return
    if not ApplicationBuilder:
        raise RuntimeError("python-telegram-bot is not installed")
    build_app(token).run_polling()

if __name__ == "__main__":  # pragma: no cover
    main()
