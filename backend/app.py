from fastapi import FastAPI, APIRouter, HTTPException, UploadFile, File, Form
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from tensorflow.keras.models import load_model
from tensorflow.keras.preprocessing.image import img_to_array
from tensorflow.keras.applications.xception import preprocess_input
from PIL import Image
import numpy as np
import io
from datetime import datetime
import boto3
from botocore.exceptions import NoCredentialsError
import uuid

# uvicorn app:app --reload --host 0.0.0.0 --port 8000


# AWS Configuration
AWS_ACCESS_KEY = ""
AWS_SECRET_KEY = ""
S3_BUCKET_NAME = "news1-bucket"
S3_BUCKET_NAME_POSTS = "feedsbuck" 
S3_REGION_NAME = "us-east-1"

DYNAMODB_TABLE_VALID_DATA = "registrations"
DYNAMODB_TABLE_FAKE_DATA = "fake_registrations"
DYNAMODB_TABLE_POSTS = "posts"  

# Initialize AWS Clients
s3_client = boto3.client(
    "s3",
    aws_access_key_id=AWS_ACCESS_KEY,
    aws_secret_access_key=AWS_SECRET_KEY,
    region_name=S3_REGION_NAME,
)

dynamodb = boto3.resource(
    "dynamodb",
    aws_access_key_id=AWS_ACCESS_KEY,
    aws_secret_access_key=AWS_SECRET_KEY,
    region_name=S3_REGION_NAME,
)

registration_table = dynamodb.Table(DYNAMODB_TABLE_VALID_DATA)
fake_registrations_table = dynamodb.Table(DYNAMODB_TABLE_FAKE_DATA)
posts_table = dynamodb.Table(DYNAMODB_TABLE_POSTS)

# Load Pretrained Model for Fake Image Detection
model = load_model("fine_tuned_xception_best_model.keras")

# FastAPI App Initialization
app = FastAPI(title="Deepfake News Verification API")
router = APIRouter()

class Registration(BaseModel):
    email: str
    username: str
    password: str
    profile_image_url: str


class FakeRegistration(BaseModel):
    email: str
    username: str
    password: str


class Post(BaseModel):
    user_id: str
    content: str
    status: bool
    image_url: str


def upload_to_s3(file, bucket_name, file_name):
    """Uploads a file to S3 and returns the public URL."""
    try:
        s3_client.upload_fileobj(file, bucket_name, file_name)
        return f"https://{bucket_name}.s3.{S3_REGION_NAME}.amazonaws.com/{file_name}"
    except NoCredentialsError:
        raise HTTPException(status_code=500, detail="AWS credentials not available")


def store_in_dynamodb(table, data):
    """Stores an item in a DynamoDB table with an ID and timestamp."""
    try:
        # Ensure data is a dictionary
        if isinstance(data, BaseModel):  # Convert Pydantic model to dictionary if needed
            data = data.dict()

        # Ensure 'id' is always included
        if "id" not in data or not data["id"]:
            data["id"] = str(uuid.uuid4())

        # Ensure 'timestamp' is always included
        if "timestamp" not in data:
            data["timestamp"] = datetime.utcnow().isoformat()

        # Insert data into DynamoDB
        table.put_item(Item=data)
        return data

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"DynamoDB Error: {str(e)}")




def preprocess_image(image):
    """Preprocesses an image for XceptionNet."""
    if image.mode != "RGB":
        image = image.convert("RGB")
    image = image.resize((150, 150))
    image = img_to_array(image)
    image = np.expand_dims(image, axis=0)
    return preprocess_input(image)


def predict_image(image):
    """Predicts whether an image is fake or real."""
    try:
        processed_image = preprocess_image(image)
        prediction = model.predict(processed_image)
        return "Fake" if prediction[0][0] > 0.5 else "Real"
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Prediction Error: {str(e)}")


@app.get("/")
def root():
    return {"message": "Welcome to the Deepfake News Verification API"}


@app.post("/login")
async def login(username: str = Form(...), password: str = Form(...)):
    """Authenticates a user by comparing the username and plain text password in DynamoDB."""
    try:
        # Query the DynamoDB table for the user
        response = registration_table.scan(
            FilterExpression="username = :username",
            ExpressionAttributeValues={":username": username}
        )
        users = response.get("Items", [])

        if not users:
            raise HTTPException(status_code=400, detail="Invalid username or password.")

        user = users[0]  # Assuming username is unique

        # Compare plain text password
        if password != user["password"]:
            raise HTTPException(status_code=400, detail="Invalid username or password.")

        # Return user details (excluding password for security)
        return {
            "message": "Login successful!",
            "user_data": {
                "id": user["id"],
                "username": user["username"],
                "email": user["email"],
                "profile_image_url": user.get("profile_image_url", None),
                "timestamp": user.get("timestamp", "")  # Ensure timestamp is included
            }
        }



    except Exception as e:
        raise HTTPException(status_code=500, detail=f"DynamoDB Error: {str(e)}")


@app.post("/register")
async def register(
    username: str = Form(...),
    email: str = Form(...),
    password: str = Form(...),
    profile_image: UploadFile = File(...)
):
    if not username or not email or not password or not profile_image:
        raise HTTPException(status_code=400, detail="All fields are required!")

    try:
        image = Image.open(profile_image.file)
        if predict_image(image) == "Fake":
            fake_user = FakeRegistration(username=username, email=email, password=password)
            store_in_dynamodb(fake_registrations_table, fake_user)
            raise HTTPException(status_code=400, detail="The uploaded image is fake!")

        # Upload real image to S3
        image_bytes = io.BytesIO()
        image.save(image_bytes, format="PNG")
        image_bytes.seek(0)
        clean_filename = profile_image.filename.replace(" ", "_")
        s3_key = f"profile_images/{email}_{clean_filename}"
        s3_url = upload_to_s3(image_bytes, S3_BUCKET_NAME, s3_key)

        user = Registration(
            email=email,
            username=username,
            password=password,
            profile_image_url=s3_url
        )
        user_dict = user.dict()  # Convert Pydantic model to dictionary

        # Ensure 'id' is included
        user_dict["id"] = str(uuid.uuid4())  # Generate unique user ID
        user_dict["timestamp"] = datetime.utcnow().isoformat()  # Add timestamp

        store_in_dynamodb(registration_table, user_dict)  # Save to DynamoDB



        # Store the dictionary directly in DynamoDB
        try:
            registration_table.put_item(Item=user_dict)  # Save directly in DynamoDB
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"DynamoDB Error: {str(e)}")

        return JSONResponse(status_code=200, content={
            "message": "User registered successfully!",
            "user_data": {"email": email, "username": username, "profile_image_url": s3_url},
        })
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error processing image: {str(e)}")

@app.get("/posts", response_model=list)
def get_all_posts():
    """Fetches all posts from DynamoDB and sorts them by timestamp (recent first)."""
    try:
        # Fetch all posts from DynamoDB
        response = posts_table.scan()
        posts = response.get("Items", [])

        if not posts:
            return []

        # Fetch all users from registrations table
        users_response = registration_table.scan()
        users = users_response.get("Items", [])

        # Create a mapping of email -> user details
        user_dict = {user["id"]: user for user in users}

        # Join posts with user details
        joined_posts = []
        for post in posts:
            user_id = post.get("user_id")
            user_info = user_dict.get(user_id, {})

            if not user_info:
                continue

            # Append post with user details
            joined_posts.append({
                "id": post.get("id"),
                "user_id": user_id,
                "username": user_info.get("username"),
                "email": user_info.get("email"),
                "user_profile_image_url": user_info.get("profile_image_url"),
                "content": post.get("content"), 
                "post_image_url": post.get("image_url"),
                "status": post.get("status", None),
                "timestamp": post.get("timestamp", "1970-01-01T00:00:00")  # Default timestamp if missing
            })

        # Sort posts by timestamp (newest first)
        joined_posts.sort(key=lambda x: datetime.fromisoformat(x["timestamp"]), reverse=True)

        return joined_posts
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"DynamoDB Error: {str(e)}")

@app.post("/posts")
async def create_post(
    user_id: str = Form(...),
    content: str = Form(...),
    image: UploadFile = File(...),
):
    if not user_id or not content or not image:
        raise HTTPException(status_code=400, detail="All fields are required!")

    try:
        img = Image.open(image.file)
        
        status = True
        if predict_image(img) == "Fake":
            status = False

        image_bytes = io.BytesIO()
        img.save(image_bytes, format="PNG")
        image_bytes.seek(0)
        clean_filename = image.filename.replace(" ", "_")
        s3_key = f"uploads/{user_id}_{clean_filename}"
        s3_url = upload_to_s3(image_bytes, S3_BUCKET_NAME_POSTS, s3_key)

        post = Post(user_id=user_id, content=content, image_url=s3_url, status=status)
        store_in_dynamodb(posts_table, post)

        return JSONResponse(status_code=200, content={
            "message": "Post created successfully!",
            "post_data": {"user_id": user_id, "content": content, "status": status, "image_url": s3_url},
        })
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error processing image: {str(e)}")
    
@app.get("/user/image-stats/{user_id}")
def get_user_image_stats(user_id: str):
    """Fetches the count of real and fake images uploaded by a specific user."""
    try:
        # Fetch all posts by the user
        response = posts_table.scan(
            FilterExpression="user_id = :user_id",
            ExpressionAttributeValues={":user_id": user_id}
        )
        user_posts = response.get("Items", [])

        # Count real and fake images
        real_images = sum(1 for post in user_posts if post["status"] == True)
        fake_images = sum(1 for post in user_posts if post["status"] == False)

        return {"real_images": real_images, "fake_images": fake_images}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"DynamoDB Error: {str(e)}")
