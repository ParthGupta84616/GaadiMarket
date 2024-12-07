from flask import Flask, jsonify, request , send_from_directory , abort
from flask_cors import CORS
from pymongo import MongoClient
from bson.json_util import dumps
from bson.objectid import ObjectId
from datetime import datetime
import os
import json

current_directory = os.getcwd()
front_end_folder = os.path.abspath(os.path.join(current_directory, "frontend", "build"))


app = Flask(__name__, static_folder=os.path.join(front_end_folder, 'static'))
CORS(app, supports_credentials=True, origins='*')


# Replace 'your_mongo_uri' with your actual MongoDB URI
client = MongoClient('mongodb://localhost:27017')  # Connect to the MongoDB client
db = client['PartsOnline']  # Replace with your database name
collection = db['products']  # Replace with your collection name
inquiries_collection = db['inquiries']
locations_collection = db["locations"]

def check_file_permissions(file_path):
    if os.access(file_path, os.R_OK):
        print(f"File '{file_path}' is readable by the Flask server process.")
    else:
        print(f"Warning: File '{file_path}' is not readable by the Flask server process. Please check permissions.")

# Get frontend folder path

# Print the contents of the front_end_folder for debugging
try:
    contents = os.listdir(front_end_folder)
    print("Contents of the frontend build directory:", contents)
except FileNotFoundError as e:
    print("Error:", e)
    print("The directory does not exist.")

@app.route('/', defaults={"filename": ""})
@app.route('/<path:filename>')
def index(filename):
    print(filename)
    if not filename or not os.path.exists(os.path.join(front_end_folder, filename)):
        filename = "index.html"
    file_path = os.path.join(front_end_folder, filename)
    print("Requested file path:", file_path)  # Debugging requested file path
    if not os.path.exists(file_path):
        print("File not found:", file_path)  # Debugging file existence
        return abort(404)  # Return 404 if file is not found
    return send_from_directory(front_end_folder, filename)


@app.route('/static/<path:filename>')
def serve_static(filename):
    print("Requested static file:", filename)
    try:
        static_folder = os.path.join(front_end_folder, 'static')
        file_path = os.path.join(static_folder, filename)
        print("Static folder path:", static_folder)  # Debugging static folder path
        print("Requested static file path:", file_path)  # Debugging requested file path

        if not os.path.exists(file_path):
            print("Static file not found:", file_path)  # Debugging file existence
            return abort(404)  # Return 404 if file is not found

        check_file_permissions(file_path)  # Check file permissions
        return send_from_directory(static_folder, filename)
    except Exception as e:
        print("Error serving static file:", e)  # Debugging any other errors
        return abort(500)  # Return 500 for any other server errors



@app.route('/api/vehicles', methods=['GET'])
def get_vehicles():
    category = request.args.get('category')
    brand = request.args.get('brand')
    model = request.args.get('model')
    state = request.args.get('state')
    
    # Build query based on provided filters
    query = {}
    print(category)
    
    # Filter by category if provided
    if category:
        if category.lower() == "truck":
            pass
        elif category.lower() == "medium trucks":
            query["category"] = { "$regex": "^Truck$", "$options": "i" }
        else:
            query["category"] = { "$regex": f"^{category}$", "$options": "i" }  # Case-insensitive regex match
    
    # Filter by brand if provided
    if brand:
        query["brand"] = { "$regex": f"^{brand}$", "$options": "i" }  # Case-insensitive regex match

    # Filter by model if provided
    if model:
        query["model"] = { "$regex": f"^{model}$", "$options": "i" }

    if state:
        query["location"] = {"$regex": f"^{state}$", "$options": "i"}
        
    print("Query:", query)
    
    vehicles = list(collection.find(query))
    
    # If any documents are returned, process them
    if vehicles:
        # Remove unnecessary fields from each vehicle document
        for vehicle in vehicles:
            vehicle.pop("documents", None)
            vehicle.pop("description", None)
            vehicle.pop("features", None)
            vehicle.pop("location", None)
            vehicle.pop("created_at", None)
            vehicle.pop("user_info", None)
            vehicle.pop("thubmnail",None)
            vehicle.pop("cost",None)
            vehicle.pop("images",None)
            vehicle.pop("validities",None)
            vehicle.pop("rcUpload",None)
            vehicle.pop("aadhaarUpload",None)
            vehicle.pop("location",None)
        
        # Return the filtered list as a JSON response
        return dumps(vehicles), 200
    else:
        # Return an error if no vehicles were found
        return jsonify({"error": "No vehicles found matching the criteria"}), 404
   
@app.route('/api/vehicles/<id>', methods=['GET'])
def get_vehicle(id):
    vehicle = collection.find_one({"_id": ObjectId(id)})
    if vehicle:
        return dumps(vehicle)
    return jsonify({"error": "Vehicle not found"}), 404



@app.route('/api/vehicles', methods=['POST'])
def add_vehicle():
    try:
        data = request.get_json()
        print(data)

        # Construct the user_info object based on the provided profile data
        user_info = {
            "name": data["profile"]["name"],  # Required field
            "email": data["profile"].get("email"),  # Optional
            "phone": data["profile"].get("phone"),  # Optional
            "address": data["profile"].get("address"),  # Optional
            "State": data["profile"].get("State"),  # Optional
            "City": data["profile"].get("City")  # Optional
        }

        # Construct the new vehicle document based on the provided data
        new_vehicle = {
            "user_info": user_info,  # Embed user info directly
            "name": data["name"],  # Required field
            "manufacture_year": data.get("manufacture_year"),  # Optional
            "category": data.get("category"),  # Optional
            "brand": data.get("brand"),  # Optional
            "model": data.get("model"),  # Optional
            "area": data.get("area"),  # Optional
            "height": data.get("height"),  # Optional
            "width": data.get("width"),  # Optional
            "length": data.get("length"),  # Optional
            "weight": data.get("weight"),  # Optional
            "cost": data.get("cost"),  # Optional
            "wheel_count": data.get("wheel_count"),  # Optional
            "payload_capacity": data.get("payload_capacity"),  # Optional
            "fuel_type": data.get("fuel_type"),  # Optional
            "engine": {
                "type": data.get("engine_type", ""),  # Optional
                "displacement": data.get("engine_displacement", ""),  # Optional
                "power": data.get("engine_power", ""),  # Optional
                "torque": data.get("engine_torque", ""),  # Optional
            },
            "transmission": data.get("transmission"),  # Optional
            "features": data.get("features"),  # Optional
            "description": data.get("description", ""),  # Optional
            "thumbnail": data.get("thumbnail"),  # Optional
            "image": data.get("images", []),  # Optional
            "registration" : {
               "registration_city": data.get("registration_city"),  # Optional
               "registration_state":  data.get("registration_state"),     # Optional
               "AC":  data.get("AC"),     # Optional
               "wheel_count":  data.get("wheel_count"),     # Optional
               "wheel_health":  data.get("wheel_health"),     # Optional
               "onwers_till_date":  data.get("onwers_till_date"),     # Optional
               "hypothecation":  data.get("hypothecation"),     # Optional
               
            },
            "validities" : {
               "insurance_validity": data.get("insurance_validity",""),  # Optional
               "permit_validity":  data.get("permit_validity",""),     # Optional
               "tax_validity": data.get("tax_validity",""),        # Optional
               "fitness_validity": data.get("fitness_validity","")     # Optional
            },
            "rcUpload": data.get("rcUpload", {}),  # Optional
            "aadhaarUpload": data.get("aadhaarUpload", {}),  # Optional
            "documents": data.get("documents", {}),  # Optional
            "location": [
                data["profile"].get("State"),
                data["profile"].get("City")
            ],
            # "rcAvailable": data.get("rcAvailable", False),  # Optional
            # "aadhaarAvailable": data.get("aadhaarAvailable", False),  # Optional
            "created_at": datetime.utcnow(),
        }


        # Optional: Remove any fields that are None
        new_vehicle = {k: v for k, v in new_vehicle.items() if v is not None}

        # Insert the vehicle document into the database
        result = collection.insert_one(new_vehicle)
        new_vehicle["_id"] = str(result.inserted_id)  # Include the newly created ID

        return jsonify(new_vehicle), 201

    except Exception as e:
        return jsonify({"error": str(e)}), 400

@app.route('/api/inquiries', methods=['POST'])
def add_inquiry():
    try:
        data = request.get_json()
        
        # Construct the new inquiry document based on the provided data
        new_inquiry = {
            "name": data["name"],  # Required field
            "vehicle_id": data["vehicle_id"],  # Required field
            "phone": data["phone"],  # Required field
            "email": data["email"],  # New required field
            "address": data["address"],  # New required field
            "description": data["description"],  # Required field
            "created_at": datetime.utcnow(),  # Optional timestamp
            "show": True,
            "status": "Pending"
        }

        result = inquiries_collection.insert_one(new_inquiry)
        new_inquiry["_id"] = str(result.inserted_id)  # Include the newly created ID
        return jsonify(new_inquiry), 201

    except Exception as e:
        return jsonify({"error": str(e)}), 400


@app.route('/api/inquiries', methods=['GET'])
def get_inquiries():
    try:
        # Fetch inquiries where show is True
        inquiries = inquiries_collection.find({"show": True})
        inquiries_list = []

        for inquiry in inquiries:
            vehicle_id = inquiry.get("vehicle_id")

            # Check if vehicle_id exists and fetch the vehicle from products_collection
            if vehicle_id:
                vehicle_info = collection.find_one({"_id": ObjectId(vehicle_id)})
                if vehicle_info:
                    # Combine inquiry data with vehicle info
                    inquiries_list.append({
                        "_id": str(inquiry["_id"]),
                        "inquiry": {
                            "_id": str(inquiry["_id"]),
                            "name": inquiry.get("name", "Unknown"),
                            "phone": inquiry.get("phone", "Unknown"),
                            "email": inquiry.get("email", "Unknown"),
                            "address": inquiry.get("address", "Unknown"),
                            "description": inquiry.get("description", "No description provided"),
                            "created_at": inquiry.get("created_at", "Unknown"),
                            "status": inquiry.get("status", "Unknown"),
                        },
                        "vehicle": {
                            "_id": str(vehicle_info["_id"]),
                            "name": vehicle_info.get("name", "Unknown"),
                            "cost": vehicle_info.get("cost", "Unknown"),
                            "owner_info": vehicle_info.get("user_info", {}),
                            "image": vehicle_info.get("image", vehicle_info.get("thumbnail", "")),
                            "documents": vehicle_info.get("documents", []),
                            "location": vehicle_info.get("location", []),
                        }
                    })
                else:
                    continue

        return jsonify(inquiries_list), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 400


@app.route('/api/inquiries/<inquiry_id>', methods=['DELETE'])
def delete_inquiry(inquiry_id):
    
    try:
        # Step 1: Update the inquiry to set show to False (hiding the inquiry)
        result = inquiries_collection.update_one(
            {"_id": ObjectId(inquiry_id)},
            {"$set": {"show": False}}
        )

        if result.modified_count > 0:
            # Step 2: Fetch the inquiry document to get the associated vehicle_id
            inquiry = inquiries_collection.find_one({"_id": ObjectId(inquiry_id)})
            vehicle_id = inquiry.get('vehicle_id')

            if vehicle_id:
                # Step 3: Delete the product component that matches the vehicle_id
                product_result = collection.delete_one({"_id": ObjectId(vehicle_id)})

                if product_result.deleted_count > 0:
                    # Step 4: Delete the inquiry document as well
                    inquiries_collection.delete_one({"_id": ObjectId(inquiry_id)})

                    return jsonify({"message": "Inquiry and associated product deleted successfully."}), 200
                else:
                    return jsonify({"error": "Product with the specified vehicle_id not found."}), 404
            else:
                return jsonify({"error": "Inquiry found, but no associated vehicle_id."}), 404
        else:
            return jsonify({"error": "Inquiry not found or already hidden."}), 404

    except Exception as e:
        return jsonify({"error": str(e)}), 400

    
@app.route('/api/inquiries/<inquiry_id>/status', methods=['PATCH'])
def update_inquiry_status(inquiry_id):
    try:
        data = request.get_json()
        new_status = data.get("status")

        # Validate the status
        valid_statuses = ["Pending", "Discard", "Evaluating", "Confirm","Hide"]
        if new_status not in valid_statuses:
            return jsonify({"error": "Invalid status provided"}), 400

        # Update the inquiry status
        result = inquiries_collection.update_one(
            {"_id": ObjectId(inquiry_id)},
            {"$set": {"status": new_status}}
        )
        if(new_status == "Hide"):
            inquiries_collection.update_one(
            {"_id": ObjectId(inquiry_id)},
            {"$set": {"show": False}}
        )

        if result.modified_count == 0:
            return jsonify({"error": "Inquiry not found or status unchanged"}), 404

        return jsonify({"message": "Inquiry status updated successfully"}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 400



@app.route('/api/brands', methods=['GET'])
def get_brands():
    category = request.args.get('category')  # Get the category from the query params
    print(category)
    if not category:
        return jsonify({"error": "Category is required"}), 400
    if category == "Truck":
        brands = collection.distinct("brand")
        return jsonify(brands), 200
    
    try:
        # Find all vehicles with the given category and extract unique brands
        brands = collection.distinct("brand", {"category": category})
        return jsonify(brands), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/api/models', methods=['GET'])
def get_models():
    category = request.args.get('category')  # Get the category from the query params
    brand = request.args.get('brand')  # Get the brand from the query params

    if not category or not brand:
        return jsonify({"error": "Both category and brand are required"}), 400
    
    try:
        if category == "Truck":
            models = collection.distinct("model", {"brand": brand})
            return jsonify(models), 200
        # Find all vehicles with the given category and brand and extract unique models
        models = collection.distinct("model", {"category": category, "brand": brand})
        return jsonify(models), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    
    
    
@app.route('/api/locations', methods=['GET'])
def get_states():
    state = request.args.get("state")

    if state:
        state_data = locations_collection.find_one({"name": state})
        if not state_data:
            return jsonify({"error": "State not found"}), 404
        cities = state_data.get("cities", [])
        
        city_list = [city["name"] for city in cities]  
        
        return jsonify({"state": state, "city_list": city_list}), 200

    states_cursor = locations_collection.distinct("name")

    if not states_cursor:
        return jsonify({"error": "No states found"}), 404
    
    return jsonify(list(states_cursor)), 200

@app.route('/api/login', methods=['POST'])
def login():
    try:
        data = request.get_json()
        user_id = data.get("id")
        password = data.get("password")

        if user_id == "jaiguru" and password == "shah7862":
            return jsonify({"success": True}), 200
        else:
            return jsonify({"success": False}), 401

    except Exception as e:
        return jsonify({"error": str(e)}), 400
    
    
    
# with open('location.json', 'r') as file:
#     data = json.load(file)

# # Convert $oid to ObjectId
# for item in data:
#     if '_id' in item and '$oid' in item['_id']:
#         item['_id'] = ObjectId(item['_id']['$oid'])

# # Insert the data into the collection
# locations_collection.insert_many(data)