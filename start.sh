#!/bin/bash
cd "$(dirname "$0")"
.venv/bin/uvicorn main:app --reload

