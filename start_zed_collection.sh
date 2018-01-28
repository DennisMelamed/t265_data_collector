#!/bin/bash
mkdir -p zed_data
tmux kill-session -t "zed"
tmux new-session -d -s "zed"
tmux send-keys -t 'zed' 'python3 collect_zed_data.py' C-m
