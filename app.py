import hashlib
import time
from flask import Flask, jsonify, request, Response

app = Flask(__name__)

# Let's simulate a database record for a user.
# In a real app, this would come from a database query.
simulated_db_record = {
    "id": "user123",
    "data": {
        "name": "Alex",
        "preferences": {
            "theme": "dark",
            "notifications": True
        },
        "large_blob": "..." * 1000  # Represents a large amount of data
    },
    # This is our crucial, easily accessible metadata
    "metadata": {
        "version": 1,
        "last_updated": time.time()
    }
}

def generate_composite_etag(record):
    """
    This is our advanced custom algorithm.
    It generates an E-Tag from metadata only, avoiding the large data blob.
    """
    meta = record['metadata']
    # Create a consistent string from the key metadata fields
    etag_string = f"{record['id']}-{meta['version']}-{meta['last_updated']}"
    # Return the MD5 hash of this metadata string
    return hashlib.md5(etag_string.encode()).hexdigest()

@app.route('/profile', methods=['GET'])
def get_profile():
    """
    Returns the user profile. E-Tag is generated efficiently from metadata.
    """
    # In a real app: user = db.query("SELECT id, version, last_updated FROM ...")
    # Here, we just use our simulated record.
    current_etag = generate_composite_etag(simulated_db_record)

    if request.headers.get('If-None-Match') == current_etag:
        # Optimization successful! We never had to touch the 'data' blob.
        return Response(status=304)

    # If E-Tags don't match, THEN we prepare the full response body
    response_body = jsonify(simulated_db_record['data'])
    response = response_body
    response.headers['ETag'] = current_etag
    return response

@app.route('/update-profile', methods=['POST'])
def update_profile():
    """
    Updates the user profile, which changes the metadata and thus the E-Tag.
    """
    # Update the data
    update_info = request.get_json()
    simulated_db_record['data']['preferences'] = update_info.get('preferences')

    # CRITICAL: Update the metadata
    simulated_db_record['metadata']['version'] += 1
    simulated_db_record['metadata']['last_updated'] = time.time()

    return jsonify({"status": "success", "new_version": simulated_db_record['metadata']['version']})

if __name__ == '__main__':
    app.run(debug=True)