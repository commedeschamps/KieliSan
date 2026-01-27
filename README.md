# Sacred Numbers Quiz Bot 🇰🇿

## 🇰🇿 Қазақша
Қазақ халқының киелі сандарын үйретуге арналған Telegram-бот. Барлық интерфейс қазақ тілінде.

Бот: [@kieli_sandar_bot](https://t.me/kieli_sandar_bot)

### Мүмкіндіктер
- Негізгі мәзір: ақпарат, мәдени салыстыру, викторина, статистика, кері байланыс
- Киелі сандар бойынша қысқа/толық ақпарат және факт/мысалдар
- Мәдени салыстыру: әр мәдениетке бөлек батырмалар және қысқа/толық салыстыру
- Викторина: жеңіл / орташа / күрделі / аралас деңгейдегі сұрақтар
- Бір дұрыс жауап және бірнеше дұрыс жауапты сұрақтар
- FSM арқылы викторина күйін басқару
- Пайдаланушы статистикасы (quiz саны, үздік нәтиже, соңғы нәтиже)

### Орнату
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

`.env` файлын толтырыңыз:
```
BOT_TOKEN=YOUR_TELEGRAM_BOT_TOKEN
```

### Іске қосу
```bash
python3 main.py
```

### Әзірлеу режимі (auto-reload)
```bash
python3 scripts/dev.py
```

### Құрылым
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
│   │   ├── compare_questions.json
│   │   ├── compare_text.txt
│   │   └── sacred_numbers.json
│   └── runtime/
│       ├── stats.json
│       └── feedback.json
├── main.py
└── requirements.txt
```

### Қолмен тест жоспары
1. /start арқылы мәзірді ашу.
2. «Киелі сандар туралы» бөлімін тексеру.
3. «Мәдени салыстыру» → сан таңдаңыз → мәдениет батырмаларымен ауыстырып көру.
4. «Викторина» → деңгей таңдау → бірнеше сұраққа жауап беру.
5. Нәтиже шыққанын және «Статистика» бөлімінде сақталғанын тексеру.
6. «Кері байланыс» бөлімінде хабарлама жіберіп көру.

---

## English
Telegram bot to teach sacred numbers in Kazakh culture. The entire UI is in Kazakh.

Bot: [@kieli_sandar_bot](https://t.me/kieli_sandar_bot)

### Features
- Main menu: info, cultural comparison, quiz, stats, feedback
- Short/full number info with examples and facts
- Cultural comparison: per-culture buttons + short/full comparison views
- Quiz levels: easy / medium / hard / mixed
- Single-answer and multi-answer questions
- FSM-based quiz flow
- User stats (quizzes taken, best score, last score)

### Install
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Fill in `.env`:
```
BOT_TOKEN=YOUR_TELEGRAM_BOT_TOKEN
```

### Run
```bash
python3 main.py
```

### Dev (auto-reload)
```bash
python3 scripts/dev.py
```

### Structure
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
│   │   ├── compare_questions.json
│   │   ├── compare_text.txt
│   │   └── sacred_numbers.json
│   └── runtime/
│       ├── stats.json
│       └── feedback.json
├── main.py
└── requirements.txt
```

### Manual test plan
1. Open menu with /start.
2. Check “Sacred numbers” info flow.
3. Go to “Cultural comparison” → pick a number → switch cultures via buttons.
4. Run a quiz and answer a few questions.
5. Verify results and check “Stats”.
6. Send a message in “Feedback”.
