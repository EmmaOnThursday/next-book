import os
from app import app

PORT = int(os.environ.get("PORT", 5000))

app.run(debug=True, host="0.0.0.0", port=PORT)
