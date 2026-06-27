# Nestrova Trading OS v3.1 Full

This is the full AI Engine 2.0 version with `.env` API key management.

## Setup

1. Copy `.env.example` to `.env`
2. Fill in your Upbit and Telegram keys
3. Install dependencies
4. Run `main.py`

## Run

```bash
pip3 install -r requirements.txt
python3 -m py_compile main.py
python3 main.py
```

## VPS screen

```bash
screen -S nestrova
python3 main.py
# detach: Ctrl+A then D
```
