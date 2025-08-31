#!/bin/bash

clear

REMOTE_HOST=167.235.206.254 # change to server used to tunnel
REMOTE_USER=platrix
FRONTEND_REMOTE_PORT=6942
WS_REMOTE_PORT=6943

# check internet
if ! curl -s --head http://www.google.com/ | grep "200 OK" > /dev/null; then
    echo "No internet connection. I need that shit!"
    exit 1
fi

cat <<'EOF'
██▓███   ██▓    ▄▄▄     ▄▄▄█████▓ ██▀███   ██▓▒██   ██▒
▓██░  ██▒▓██▒   ▒████▄   ▓  ██▒ ▓▒▓██ ▒ ██▒▓██▒▒▒ █ █ ▒░
▓██░ ██▓▒▒██░   ▒██  ▀█▄ ▒ ▓██░ ▒░▓██ ░▄█ ▒▒██▒░░  █   ░
▒██▄█▓▒ ▒▒██░   ░██▄▄▄▄██░ ▓██▓ ░ ▒██▀▀█▄  ░██░ ░ █ █ ▒ 
▒██▒ ░  ░░██████▒▓█   ▓██▒ ▒██▒ ░ ░██▓ ▒██▒░██░▒██▒ ▒██▒
▒▓▒░ ░  ░░ ▒░▓  ░▒▒   ▓▒█░ ▒ ░░   ░ ▒▓ ░▒▓░░▓  ▒▒ ░ ░▓ ░
░▒ ░     ░ ░ ▒  ░ ▒   ▒▒ ░   ░      ░▒ ░ ▒░ ▒ ░░░   ░▒ ░
░░         ░ ░    ░   ▒    ░        ░░   ░  ▒ ░ ░    ░  
                         ░  ░     ░  ░           ░      ░   ░    ░  
EOF
sleep 1
echo "Waiting for backend to start, you should be seeing some colors flashing on the LED matrix"

tmux new-session -d -s platrix
tmux split-window -h -t platrix

# show pane titles
tmux set-option -t platrix -g pane-border-status top
tmux set-option -t platrix -g pane-border-format '#{pane_index} #{pane_title}'

# name panes
tmux select-pane -t platrix:0.1 \; select-pane -T 'backend'
tmux select-pane -t platrix:0.0 \; select-pane -T 'frontend'

# backend (right pane)
tmux send-keys -t platrix:0.1 'cd backend' C-m
tmux send-keys -t platrix:0.1 'sudo modprobe -r snd_bcm2835' C-m
sleep 0.5
tmux send-keys -t platrix:0.1 '.env/bin/python server.py' C-m

# wait for backend websocket port 5000
while ! nc -z localhost 5000 2>/dev/null; do sleep 0.5; done

# frontend (left top pane)
tmux send-keys -t platrix:0.0 'cd frontend' C-m
tmux send-keys -t platrix:0.0 'sudo serve -s dist -l 80' C-m

# wait for frontend port 80
while ! nc -z localhost 80 2>/dev/null; do sleep 0.5; done

# split the left pane and run monitor (left bottom pane)
tmux split-window -v -t platrix:0.0 'cd monitor && exec node index.js'
tmux select-pane -T 'monitor'

# split right pane for SSH tunnel
tmux split-window -v -t platrix:0.1
tmux select-pane -T 'tunnel'

# launch SSH (use autossh if available)
TUNNEL_CMD="autossh -M 0 -o ServerAliveInterval=30 -o ServerAliveCountMax=3 -N -R ${FRONTEND_REMOTE_PORT}:localhost:80 -R ${WS_REMOTE_PORT}:localhost:5000 ${REMOTE_USER}@${REMOTE_HOST}"
tmux send-keys -t platrix:0.2 "$TUNNEL_CMD" C-m

tmux attach -t platrix
