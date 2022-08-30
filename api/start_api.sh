#!/bin/bash

# Start the API server
cd /rmt-is-ok/api
python3 -m uvicorn main:app --reload