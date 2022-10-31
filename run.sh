conda activate venv

cd database
uvicorn main:app --port 8000 &

cd ../face_encoding
uvicorn main:app --port 8002 &

cd ../app
python login_window.py

