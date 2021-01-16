#!/bin/bash
tmux kill-session -t "t265"
tmux new-session -d -s "t265"
tmux send-keys -t 't265' 'python collect_t265_data.py' C-m
