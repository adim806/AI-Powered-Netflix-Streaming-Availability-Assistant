import os
from flask import Flask, jsonify, request
import requests
from dotenv import load_dotenv

# Load environment variables from the .env file
load_dotenv()

app = Flask(__name__)

# Fetch the RapidAPI key securely from the environment
RAPIDAPI_KEY = os.getenv("RAPIDAPI_KEY")
RAPIDAPI_HOST = "streaming-availability.p.rapidapi.com"

# Safety check to ensure the key was loaded
if not RAPIDAPI_KEY:
    raise ValueError(
        "No RAPIDAPI_KEY set for Flask application. Please check your .env file.")


@app.route("/")
def home():
    """
    Root endpoint to verify the server is running.
    """
    return "Streaming Proxy Server is Running! Please use the /streaming_status endpoint."


@app.route("/streaming_status", methods=["GET"])
def check_streaming():
    """
    The endpoint that receives the request from the Web UI,
    calls RapidAPI, and returns a filtered response.
    """
    # 1. Extract parameters from the request
    title = request.args.get("title")
    country = request.args.get("country", "il")  # Default: Israel (il)

    if not title:
        return jsonify({"error": "Title parameter is required"}), 400

    print(f"[Server] Searching for '{title}' in country '{country}'...")

    # 2. Configure the RapidAPI request
    url = "https://streaming-availability.p.rapidapi.com/shows/search/title"

    # Removed "show_type" to prevent 400 Bad Request error
    querystring = {
        "title": title,
        "country": country,
        "output_language": "en"
    }

    headers = {
        "X-RapidAPI-Key": RAPIDAPI_KEY,
        "X-RapidAPI-Host": RAPIDAPI_HOST
    }

    try:
        # 3. Make the call to the API
        response = requests.get(url, headers=headers, params=querystring)
        response.raise_for_status()
        data = response.json()

        # 4. Filter and parse the information
        if not data or not isinstance(data, list) or len(data) == 0:
            return jsonify({
                "message": f"Could not find any streaming data for '{title}' in '{country}'."
            })

        # Take the first result (the best match)
        first_result = data[0]
        show_title = first_result.get("title", title)

        # Extract the viewing options for the requested country
        streaming_options = first_result.get(
            "streamingOptions", {}).get(country, [])

        available_services = []
        for option in streaming_options:
            service_name = option.get("service", {}).get("name", "Unknown")
            stream_type = option.get("type", "stream")
            link = option.get("link", "No link provided")

            # Create a clear string for the model
            service_info = f"{service_name} ({stream_type}) - Link: {link}"
            if service_info not in available_services:
                available_services.append(service_info)

        # 5. Return the clean response to the Open Web UI
        return jsonify({
            "query_title": title,
            "found_title": show_title,
            "country": country,
            "availability": available_services if available_services else "Not available for streaming in this country."
        })

    except Exception as e:
        print(f"[Server Error] An error occurred: {e}")
        return jsonify({"error": "Failed to fetch data from RapidAPI", "details": str(e)}), 500


if __name__ == "__main__":
    # Listen on 0.0.0.0 to be accessible to external networks (like a Docker container)
    print("Starting Streaming Availability Proxy Server...")
    app.run(host="0.0.0.0", port=5005)
