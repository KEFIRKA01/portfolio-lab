# Архитектура: Conversion Landing Kit

```mermaid
flowchart LR
    A["Landing UI"] --> B["Quiz state"]
    A --> C["Lead form"]
    B --> D["Analytics layer"]
    C --> D
    C --> E["CRM payload builder"]
```

## Ключевой принцип

Frontend здесь не декоративный, а процессный: посетитель квалифицируется, отправляет заявку, а система готовит события и структуру лида.

