from flask import Flask, request, jsonify
import requests
import data_pb2
import time
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad

app = Flask(__name__)

# Encryption keys
key = bytes([89, 103, 38, 116, 99, 37, 68, 69, 117, 104, 54, 37, 90, 99, 94, 56])
iv = bytes([54, 111, 121, 90, 68, 114, 50, 50, 69, 51, 121, 99, 104, 106, 77, 37])

# API لجلب JWT
jwt_api = "https://masry-jwt.vercel.app/get"

# Endpoint الرسمي لتغيير الاسم
url = "https://loginbp.ggblueshark.com/MajorModifyNickname"
freefire_version = "OB53"


@app.route("/name", methods=["GET"])
def change_name():
    uid = request.args.get("uid")
    password = request.args.get("password")
    new_name = request.args.get("name")

    if not uid or not password or not new_name:
        return jsonify({"error": "uid, password, and name are required"}), 400

    # 1️⃣ نجيب JWT من API الخارجي
    try:
        jwt_response = requests.get(f"{jwt_api}?uid={uid}&password={password}")
        jwt_data = jwt_response.json()

        if "jwt_token" not in jwt_data:
            return jsonify({"error": "Failed to get JWT", "details": jwt_data}), 400

        jwt_token = jwt_data["jwt_token"]

    except Exception as e:
        return jsonify({"error": f"JWT API Error: {str(e)}"}), 500

    # 2️⃣ نحضّر protobuf
    msg = data_pb2.Message()
    msg.data = new_name.encode("utf-8")
    msg.timestamp = int(time.time() * 1000)

    payload = msg.SerializeToString()

    # 3️⃣ تشفير البيانات
    cipher = AES.new(key, AES.MODE_CBC, iv)
    encrypted_payload = cipher.encrypt(pad(payload, AES.block_size))

    headers = {
        "Expect": "100-continue",
        "Authorization": f"Bearer {jwt_token}",
        "X-Unity-Version": "2018.4.11f1",
        "X-GA": "v1 1",
        "ReleaseVersion": freefire_version,
        "Content-Type": "application/octet-stream",
        "User-Agent": "Dalvik/2.1.0 (Linux; U; Android 11; SM-A305F Build/RP1A.200720.012)",
        "Connection": "Keep-Alive",
        "Accept-Encoding": "gzip"
    }

    # 4️⃣ إرسال الطلب إلى Garena
    try:
        response = requests.post(url, data=encrypted_payload, headers=headers)

        status = "success" if response.status_code == 200 else "failed"

        return jsonify({
            "credit": "@mahim_offcial_143",
            "jwt_status": jwt_data.get("status", "unknown"),
            "status": status,
            "headers": dict(response.headers),
            "raw_content": response.content.hex(),
            "text": response.text
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)