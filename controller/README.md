# 🚦 Smartphone-Controlled Speed Limit System for Traffic Compiler

This system adds a modern, mobile-friendly remote web controller on top of your existing Flex/Bison `traffic_compiler` project without modifying any lexer or parser logic.

---

## 📁 Architecture & Files Created

| File | Description |
| :--- | :--- |
| [`controller/app.py`](file:///d:/Compiler%20Lab%20Project/traffic_compiler/controller/app.py) | **Flask Backend Server**: Manages web endpoints, dynamically updates `LIMIT <val>;` in `input.txt`, invokes `traffic.exe`, and returns analysis data. |
| [`controller/templates/index.html`](file:///d:/Compiler%20Lab%20Project/traffic_compiler/controller/templates/index.html) | **Mobile Web Application**: Responsive UI with dark mode, glowing indicators, slider, quick-speed presets, live violation cards, and terminal output. |
| [`controller/requirements.txt`](file:///d:/Compiler%20Lab%20Project/traffic_compiler/controller/requirements.txt) | Python dependencies (`Flask`). |
| [`start_controller.bat`](file:///d:/Compiler%20Lab%20Project/traffic_compiler/start_controller.bat) | **Windows One-Click Launcher**: Auto-detects Python executable and starts the server. |

---

## 🚀 How to Run the System on Windows

### Option 1: Double-Click Batch File (Easiest)
Simply double-click [`start_controller.bat`](file:///d:/Compiler%20Lab%20Project/traffic_compiler/start_controller.bat) in the project root directory.

### Option 2: Using Terminal / Command Prompt
Run the following command from the project root:
```bash
# If using MSYS2 / UCRT64 Python:
C:\msys64\ucrt64\bin\python.exe controller/app.py

# Or if standard Python is in your PATH:
python controller/app.py
```

---

## 📱 How to Control from a Smartphone

1. Ensure your **PC and Smartphone are connected to the same Wi-Fi network**.
2. When the Flask server starts, it displays your local network address in the console:
   ```
   Local PC Access  : http://127.0.0.1:5000
   Smartphone Access: http://<YOUR_PC_IP>:5000  (e.g., http://192.168.1.15:5000)
   ```
3. Open the **Browser** (Chrome / Safari) on your smartphone and enter the `http://<YOUR_PC_IP>:5000` URL.
4. On your smartphone:
   - Tap any quick preset (e.g., `40`, `60`, `80`, `100 km/h`) or use the slider / number input.
   - Tap **"⚡ SEND & COMPILE"**.
5. The system will:
   - Dynamically replace the `LIMIT` line in `input.txt`.
   - Run `traffic.exe input.txt`.
   - Update `output.txt`.
   - Display real-time violation alerts (🚨 **SPEED VIOLATION** vs 🚗 **SAFE**) and raw terminal logs on your phone.

---

## 🔒 Non-Intrusive Design
- **Zero changes** to `lexer.l`, `parser.y`, `lex.yy.c`, `parser.tab.c`, or `traffic.exe`.
- You can still run `traffic.exe input.txt` manually in the terminal at any time.
