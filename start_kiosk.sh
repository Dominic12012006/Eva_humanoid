#  #!/bin/bash

# # ===== GUI =====
# export DISPLAY=${DISPLAY}
# export XAUTHORITY=/home/eva/.Xauthority

# # ===== NODE =====
# export NVM_DIR="/home/eva/.nvm"
# [ -s "$NVM_DIR/nvm.sh" ] && . "$NVM_DIR/nvm.sh"

# # ===== PYTHON =====
# source /home/eva/Desktop/dominic/.venv/bin/activate

# # ===== BACKEND =====
# cd /home/eva/Desktop/dominic
# uvicorn Eva-main.backend.main:app --host 127.0.0.1 --port 8000 > uvicorn.log 2>&1 &

# sleep 5

# # ===== FRONTEND =====
# cd /home/eva/Desktop/dominic/Eva-main/frontend
# npm run dev > nextjs.log 2>&1 &

# # ===== WAIT FOR NEXT =====
# until nc -z localhost 3000; do
#   sleep 1
# done

# # ===== KIOSK =====
# chromium-browser \
#   --kiosk \
#   --no-sandbox \
#   --disable-infobars \
#   --disable-session-crashed-bubble \
#   --disable-restore-session-state \
#   --incognito \
#   http://localhost:3000
