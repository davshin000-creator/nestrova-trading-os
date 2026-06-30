#!/bin/bash

cd ~/nestrova-trading-os || exit

echo "1) GitHub 최신 코드 받는 중..."
git pull

echo "2) 패키지 설치/업데이트..."
python3 -m pip install -r requirements.txt --break-system-packages

echo "3) 문법 확인..."
python3 -m py_compile main.py || exit

echo "4) Startup check..."
python3 scripts/startup_check.py || true

echo "5) 기존 nestrova screen 전부 종료..."
screen -ls | grep nestrova | awk '{print $1}' | xargs -r -I {} screen -S {} -X quit

sleep 2

echo "6) 새 봇 하나만 실행..."
screen -dmS nestrova python3 main.py

echo "완료: nestrova 봇이 백그라운드에서 실행 중"
screen -ls
