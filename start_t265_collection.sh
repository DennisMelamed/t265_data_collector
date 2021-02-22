#!/bin/bash
mkdir -p t265_data
tmux kill-session -t "t265"
tmux new-session -d -s "t265"
tmux send-keys -t 't265' 'python3 collect_t265_data.py' C-m
tmux attach -t t265
