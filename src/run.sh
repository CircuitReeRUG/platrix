#!/bin/bash

# Build the frontend (Vite + React + TypeScript)
cd frontend
npm run build
cd ..

tmux new-session -d -s platrix
tmux split-window -h -t platrix
tmux send-keys -t platrix:0.1 'python backend/mock_server.py' C-m

# Sleep for a second
sleep 1

tmux send-keys -t platrix:0.0 'cd frontend' C-m
tmux send-keys -t platrix:0.0 'serve -s dist -l 5173' C-m
tmux attach -t platrix
