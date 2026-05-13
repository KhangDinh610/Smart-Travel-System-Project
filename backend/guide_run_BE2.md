# Huong dan chay BE2 (Streamlit Demo)

## 1) Chuan bi moi truong
```powershell
python -m venv .venv
Set-ExecutionPolicy -Scope Process -ExecutionPolicy RemoteSigned
& ".\.venv\Scripts\Activate.ps1"
```

## 2) Cai dat thu vien
```powershell
cd backend
pip install -r requirements.txt
```

## 3) Chay ung dung Streamlit
```powershell
streamlit run app.py
```

## 4) Su dung demo
- Mo URL trong terminal (thuong la http://localhost:8501).
- Upload anh .jpg/.png.
- Kiem tra anh goc va anh da xu ly.
- Xem vector dau ra (512 chieu) va 20 gia tri dau.
