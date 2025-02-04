#!/bin/bash
Xvfb :99 -screen 0 1024x768x16 &
sleep 1
uvicorn main:app --host 0.0.0.0 --port 5200 --log-config log_config.yaml 