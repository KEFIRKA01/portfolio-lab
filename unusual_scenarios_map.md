# Unusual Scenarios Map

Этот документ нужен, чтобы профили продавали не только "типовые задачи", но и умение заходить в более редкие, неудобные и смешанные сценарии.

## Что показывает многогранность

Сильный профиль выглядит особенно убедительно, когда видно, что он покрывает не только:

- форму на сайте;
- CRM интеграцию;
- Telegram-бота;

но и более необычные задачи:

- white-label кабинеты;
- OEM/partner portal сценарии;
- нестандартные approval flow;
- rescue после проблемного релиза;
- high-value e-commerce заказы и idempotent sync;
- гибридные lead-flow с Telegram, CRM и событиями аналитики.

## Матрица нестандартных задач

| Необычная задача | Чем закрывается | Что показывать в отклике |
| --- | --- | --- |
| White-label B2B кабинет | OpsPortal + FlowDesk | approval matrix, enterprise tags, owner/security/finance approval |
| Партнёрский портал с Telegram-уведомлениями | Telegram Service Bot + OpsPortal | `partner_portal` flow, request board, roles, escalation |
| Нестабильный релиз с legacy CRM | Release Rescue Kit + FlowDesk | playbook, owner workload, maintenance risk |
| High-value интернет-магазин с интеграциями | Checkout Bridge for WooCommerce | retry queue, segment detection, idempotency key |
| Лендинг с квалификацией под разные сценарии | Conversion Landing Kit + FlowDesk | package estimator, payload preview, routing preview |
| Задача "сначала разберитесь, что нам вообще нужно" | OpsPortal + Release Rescue + Telegram | approval plan, rescue checklist, suggested reply и сценарное уточнение |

## Что говорить в профиле

Вместо общего "беру сложные проекты" лучше писать предметно:

- умею собирать white-label и partner сценарии, где есть роли, согласования и нестандартные маршруты;
- умею заходить в проблемные релизы и быстро строить rescue/playbook вокруг нестабильного сервиса;
- умею связывать e-commerce, CRM, Telegram и webhook так, чтобы всё не разваливалось на дублях и ретраях;
- умею делать lead-flow не только под типовой лендинг, но и под разные сценарии входа и квалификации клиента.

## Как распределять по площадкам

### Workspace

Лучше всего продавать:

- white-label, B2B, кабинетные и rescue-кейсы;
- задачи с несколькими ролями, согласованиями и нестандартной бизнес-логикой.

### Kwork

Лучше всего продавать:

- CRM/API flow;
- WooCommerce bridge;
- Telegram automation;
- точечные rescue и стабилизацию.

### Freelance.ru / FL.ru

Лучше всего продавать:

- смешанные сценарии: frontend + API + процесс;
- "нужно не только сделать, но и собрать правильную структуру решения".

## Как использовать в откликах

Если заказчик даёт странное, расплывчатое или "гибридное" ТЗ:

1. Сначала назвать тип сценария.
2. Потом показать 1-2 релевантных demo-проекта.
3. Затем коротко сказать, какой нестандартный риск вы уже умеете закрывать:
   - white-label;
   - approval;
   - retry/idempotency;
   - rescue/playbook;
   - partner flow;
   - lead qualification.
