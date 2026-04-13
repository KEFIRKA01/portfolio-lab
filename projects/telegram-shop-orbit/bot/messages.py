from __future__ import annotations

from .analytics import card, digest
from .domain import METRIC, OPERATOR, TITLE, Item, checklist, display_label, next_action
from .reporting import top_lines

HEADER = "🛍️ Магазин в Telegram Orbit"

def start_text() -> str:
    return f"{HEADER}\n\nФокус: магазин, каталог, корзина, доставка, допродажи\nОбъект: заказ\nРоль: {OPERATOR}\nМетрика: {METRIC}"

def help_text() -> str:
    return (
        "/start - старт\n"
        "/help - команды\n"
        "/overview - операторская сводка\n"
        "/queue - главная очередь\n"
        "/risk - рискованные кейсы\n"
        "/item <id> - карточка\n"
        "/digest - аналитика\n"
        "/scenarios - сценарии\n"
        "/newdemo - динамическая демо-запись"
    )

def item_card(item: Item) -> str:
    row = card(item)
    checks = "\n".join(f"• {value}" for value in checklist(item))
    return (
        f"{HEADER}\n━━━━━━━━━━━━━━━━━━\n"
        f"📌 {item.title}\n"
        f"ID: {item.item_id}\nКатегория: {display_label(item.category)}\nСтатус: {display_label(item.status)}\n"
        f"Бюджет: {item.budget}\nОчередь: {display_label(row.lane)}\n"
        f"Риск: {row.risk}/100\nЦенность: {row.value}/100\n"
        f"Шанс: {row.chance}/100\nОценка времени: {row.effort} ч\n"
        f"Стабильность: {row.stability}\nСоответствие: {row.fit}\n"
        f"Ответственный: {item.assigned_to or 'не назначен'}\n"
        f"Рекомендация: {row.recommendation}\n\n"
        f"Следующий шаг:\n{next_action(item)}\n\n"
        f"Чеклист:\n{checks}"
    )

def queue_text(items: list[Item]) -> str:
    if not items:
        return f"{HEADER}\n\nОчередь пустая."
    lines = [HEADER, "", "Главная очередь:"]
    for item in items[:10]:
        row = card(item)
        lines.append(f"• {item.item_id} | {display_label(item.category)} | {display_label(row.lane)} | риск {row.risk} | шанс {row.chance}")
    return "\n".join(lines)

def digest_text(items: list[Item]) -> str:
    stats = digest(items)
    lines = [
        HEADER,
        "",
        f"Метрика: {METRIC}",
        f"Средний шанс: {stats['avg_chance']}",
        f"Средняя ценность: {stats['avg_value']}",
        f"Средняя стабильность: {stats['avg_stability']}",
        f"Среднее соответствие: {stats['avg_fit']}",
        "Топ строки:",
    ]
    lines.extend(top_lines(items))
    return "\n".join(lines)
