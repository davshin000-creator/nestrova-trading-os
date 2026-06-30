# Nestrova 2.0 Foundation

This pack does not replace your trading logic yet.
It adds a modular OS structure so future versions can move code out of `main.py`.

Copy into existing project:
- core/
- execution/
- config/
- scripts/
- update-bot.sh

Do not replace `main.py` with this pack.

Windows:
```powershell
python -m py_compile main.py
python scripts/startup_check.py
git add .
git commit -m "Add Nestrova 2.0 foundation structure"
git push
```

VPS:
```bash
cd ~/nestrova-trading-os
git pull
chmod +x update-bot.sh
./update-bot.sh
```
