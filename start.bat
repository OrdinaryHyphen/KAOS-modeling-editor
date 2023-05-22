@echo off

start "KAOS Modeling Editor -Node.js Server-"  npm run start
python ./src/python/PythonServer.py
