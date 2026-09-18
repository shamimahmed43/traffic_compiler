import os
import re
import socket
import subprocess
from pathlib import Path
from flask import Flask, render_template, request, jsonify

app = Flask(__name__)

# Base directories
BASE_DIR = Path(__file__).resolve().parent.parent
INPUT_FILE = BASE_DIR / "input.txt"
OUTPUT_FILE = BASE_DIR / "output.txt"
EXE_FILE = BASE_DIR / "traffic.exe"

def get_local_ip():
    """Retrieve the local LAN IP address to show on the mobile UI."""
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        # Connect to a public DNS IP without sending actual packets
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except Exception:
        return "127.0.0.1"

def read_input_file():
    """Reads input.txt and extracts current limit and content."""
    if not INPUT_FILE.exists():
        return {"content": "", "limit": 80}
    
    with open(INPUT_FILE, "r", encoding="utf-8") as f:
        content = f.read()

    match = re.search(r"^\s*LIMIT\s+(\d+)\s*;", content, re.MULTILINE | re.IGNORECASE)
    current_limit = int(match.group(1)) if match else 80
    return {"content": content, "limit": current_limit}

def update_speed_limit(new_limit: int):
    """Updates the LIMIT line in input.txt dynamically."""
    if not INPUT_FILE.exists():
        default_content = f"LIMIT {new_limit};\n\nVEHICLE car1 SPEED 85;\nVEHICLE car2 SPEED 50;\nVEHICLE bike1 SPEED 70;\n\nANALYZE;\n"
        with open(INPUT_FILE, "w", encoding="utf-8") as f:
            f.write(default_content)
        return default_content

    with open(INPUT_FILE, "r", encoding="utf-8") as f:
        lines = f.readlines()

    limit_updated = False
    new_lines = []
    for line in lines:
        if not limit_updated and re.match(r"^\s*LIMIT\s+\d+\s*;", line, re.IGNORECASE):
            new_lines.append(f"LIMIT {new_limit};\n")
            limit_updated = True
        else:
            new_lines.append(line)

    if not limit_updated:
        new_lines.insert(0, f"LIMIT {new_limit};\n\n")

    updated_content = "".join(new_lines)
    with open(INPUT_FILE, "w", encoding="utf-8") as f:
        f.write(updated_content)

    return updated_content

def run_traffic_compiler():
    """Executes traffic.exe with input.txt and returns structured results."""
    if not EXE_FILE.exists():
        return {
            "success": False,
            "raw_output": f"Error: '{EXE_FILE.name}' not found at {EXE_FILE}.",
            "stats": None
        }

    try:
        process = subprocess.run(
            [str(EXE_FILE), str(INPUT_FILE.name)],
            cwd=str(BASE_DIR),
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            timeout=10
        )
        output = process.stdout
        if process.stderr:
            output += "\n[STDERR]:\n" + process.stderr

        # Update output.txt as well
        try:
            with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
                f.write(output)
        except Exception as e:
            print(f"Warning: Failed to write output.txt: {e}")

        # Parse output for dashboard cards
        parsed_stats = parse_compiler_output(output)

        return {
            "success": process.returncode == 0,
            "returncode": process.returncode,
            "raw_output": output,
            "stats": parsed_stats
        }
    except subprocess.TimeoutExpired:
        return {
            "success": False,
            "raw_output": "Execution timed out while running traffic.exe.",
            "stats": None
        }
    except Exception as e:
        return {
            "success": False,
            "raw_output": f"Execution error: {str(e)}",
            "stats": None
        }

def parse_compiler_output(output_text: str):
    """Parses stdout of traffic.exe to provide rich dashboard statistics."""
    stats = {
        "speed_limit": None,
        "vehicles": [],
        "total_vehicles": 0,
        "violations_count": 0,
        "safe_count": 0,
        "parsed_successfully": "Parsing Successful" in output_text
    }

    # Match speed limit
    limit_match = re.search(r"Speed Limit:\s*(\d+)\s*km/h", output_text, re.IGNORECASE)
    if limit_match:
        stats["speed_limit"] = int(limit_match.group(1))

    # Match vehicles
    vehicle_blocks = re.findall(
        r"Vehicle:\s*([^\r\n]+)\r?\nSpeed:\s*(\d+)\s*km/h\r?\nStatus:\s*([^\r\n]+)",
        output_text,
        re.MULTILINE
    )

    for name, speed, status in vehicle_blocks:
        name = name.strip()
        speed = int(speed)
        status = status.strip()
        is_violation = "VIOLATION" in status.upper()
        if is_violation:
            stats["violations_count"] += 1
        else:
            stats["safe_count"] += 1

        stats["vehicles"].append({
            "name": name,
            "speed": speed,
            "status": status,
            "is_violation": is_violation
        })

    stats["total_vehicles"] = len(stats["vehicles"])
    return stats

@app.route("/")
def index():
    local_ip = get_local_ip()
    file_data = read_input_file()
    return render_template("index.html", local_ip=local_ip, initial_limit=file_data["limit"])

@app.route("/api/status", methods=["GET"])
def api_status():
    file_data = read_input_file()
    local_ip = get_local_ip()
    return jsonify({
        "status": "online",
        "local_ip": local_ip,
        "speed_limit": file_data["limit"],
        "input_content": file_data["content"]
    })

@app.route("/api/set-limit", methods=["POST"])
def api_set_limit():
    data = request.get_json(silent=True) or {}
    speed_limit = data.get("speed_limit")

    if speed_limit is None:
        return jsonify({"success": False, "error": "Speed limit value is required"}), 400

    try:
        speed_limit = int(speed_limit)
        if speed_limit <= 0 or speed_limit > 500:
            return jsonify({"success": False, "error": "Speed limit must be between 1 and 500 km/h"}), 400
    except (ValueError, TypeError):
        return jsonify({"success": False, "error": "Invalid speed limit format. Must be an integer."}), 400

    # 1. Dynamically update input.txt
    updated_input = update_speed_limit(speed_limit)

    # 2. Execute compiler
    result = run_traffic_compiler()

    return jsonify({
        "success": result["success"],
        "speed_limit": speed_limit,
        "input_content": updated_input,
        "raw_output": result["raw_output"],
        "stats": result["stats"]
    })

@app.route("/api/run-compiler", methods=["POST"])
def api_run_compiler():
    """Runs compiler directly with existing input.txt."""
    result = run_traffic_compiler()
    return jsonify(result)

if __name__ == "__main__":
    local_ip = get_local_ip()
    print("=" * 60)
    print(" 🚦 TRAFFIC COMPILER - SMARTPHONE CONTROLLER SERVER")
    print("=" * 60)
    print(f" Local PC Access : http://127.0.0.1:5000")
    print(f" Smartphone Access: http://{local_ip}:5000")
    print(" (Make sure your smartphone is connected to the same Wi-Fi)")
    print("=" * 60)
    app.run(host="0.0.0.0", port=5000, debug=False)
