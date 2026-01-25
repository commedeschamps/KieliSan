# Sacred Numbers Quiz Bot (Kazakh)

Telegram-бот қазақ халқының киелі сандарын (3, 5, 7, 9, 40, 12, 13, 41) үйретуге арналған. Барлық интерфейс қазақ тілінде.

## Мүмкіндіктер
- Негізгі мәзір: ақпарат, викторина, статистика, кері байланыс
- Деңгейлер: жеңіл / орташа / күрделі / аралас
- Бір дұрыс жауап және бірнеше дұрыс жауапты сұрақтар
- FSM арқылы викторина күйін басқару
- Пайдаланушы статистикасы (quiz саны, орташа нәтиже, үздік нәтиже)

## Орнату
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

`.env` файлын толтырыңыз:
```
BOT_TOKEN=YOUR_TELEGRAM_BOT_TOKEN
```

## Іске қосу
```bash
python3 main.py
```

## Әзірлеу режимі (auto-reload)
```bash
python3 scripts/dev.py
```

## Құрылым
```
telegram-bot/
├── bot/
│   ├── handlers/
│   │   ├── content/
│   │   ├── quiz/
│   │   └── system/
│   ├── keyboards/
│   │   ├── content/
│   │   ├── quiz/
│   │   └── system/
│   ├── states/
│   └── utils/
├── assets/
│   └── numbers/
├── data/
│   ├── content/
│   │   ├── questions.json
│   │   └── sacred_numbers.json
│   └── runtime/
│       ├── stats.json
│       └── feedback.json
├── main.py
└── requirements.txt
```

## Қолмен тест жоспары
1. /start арқылы мәзірді ашу.
2. «Киелі сандар туралы» бөлімін тексеру.
3. «Викторина» → деңгей таңдау → бірнеше сұраққа жауап беру.
4. Нәтиже шыққанын тексеру.
5. «Статистика» бөлімінде нәтижелердің сақталғанын тексеру.
6. «Кері байланыс» бөлімінде хабарлама жіберіп көру.
