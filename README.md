# **TruePix: Deepfake News Verification Web App**

## **📌 Overview**
TruePix is a deepfake detection social media platform integrating FastAPI (backend) and Streamlit (frontend). It enables user authentication, image verification using XceptionNet, and post creation with text and images. Users can interact with posts while maintaining an image authenticity history. Data is securely stored in AWS DynamoDB and S3, ensuring scalability and reliability.

---

## **🛠 Technologies Used**
### **Frontend (User Interface)**
- **Streamlit** (UI Framework)
- **HTML/CSS (Custom Styling in Markdown)**
- **JavaScript (Minimal UI Enhancements)**

### **Backend (API & Deepfake Detection)**
- **FastAPI** (Python-based Web Framework)
- **Uvicorn** (ASGI Server for FastAPI)
- **TensorFlow (XceptionNet)** (Deepfake detection model)
- **Pillow (PIL)** (Image Processing)
- **NumPy** (Numerical Computations)
- **Requests** (API Calls to the backend)

### **Database & Cloud Services (AWS Integration)**
- **Amazon S3** (Stores uploaded images)
- **Amazon DynamoDB** (Stores user data & posts)
- **Boto3** (AWS SDK for Python)
- **Botocore** (AWS Authentication & Security)

### **Development Tools**
- **Virtual Environment (`venv`)**
- **VSCode / PyCharm** (Recommended IDEs)
- **Git & GitHub** (Version Control)

---

## **📂 Project Structure**
```plaintext
📦 TruePix-WebApp
├── backend
│   ├── app.py  # FastAPI Backend
│   ├── fine_tuned_xception_best_model.keras  # Deepfake Model
├── frontend
│   ├── app.py  # Streamlit Frontend
│   ├── profile_pics/  # Profile Pictures Directory
├── requirements.txt  # Required Libraries
├── README.md  # Documentation
```

---

## **🚀 How to Set Up & Run Locally**
### **Step 1: Clone the Repository**
```sh
git clone https://github.com/your-repo/truepix-webapp.git
cd truepix-webapp
```

### **Step 2: Set Up Virtual Environment**
#### **For Windows**
```sh
python -m venv venv
venv\Scripts\activate
```
#### **For Mac/Linux**
```sh
python3 -m venv venv
source venv/bin/activate
```

### **Step 3: Install Dependencies**
```sh
pip install -r requirements.txt
```

### **Step 4: Run the Backend (FastAPI)**
```sh
cd backend
uvicorn app:app --reload --host 0.0.0.0 --port 8000
```
📌 **Backend API Documentation:** [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)

### **Step 5: Run the Frontend (Streamlit)**
```sh
cd frontend
streamlit run app.py
```
📌 **Access Frontend at:** [http://localhost:8501](http://localhost:8501)

---

## **🛠 AWS Services Used**
### **1️⃣ Amazon S3 (Image Storage)**
- Stores **profile pictures** and **post images**.
- **Bucket Names:**
  - `news1-bucket` → Stores profile images.
  - `feedsbuck` → Stores post images.

### **2️⃣ Amazon DynamoDB (NoSQL Database)**
- Stores **user credentials & post data**.
- **Tables Created:**
  - `registrations` → Stores valid users.
  - `fake_registrations` → Stores users with fake profile images.
  - `posts` → Stores posts with images and deepfake verification results.

### **3️⃣ AWS Boto3 (SDK for AWS Integration)**
- Uploads images to **S3**
- Manages **DynamoDB tables**

---

## **🔁 Web App Workflow**
### **1️⃣ User Registration & Image Validation**
1. User uploads **profile image** during registration.
2. Image is sent to **FastAPI backend**.
3. Image is **preprocessed** and passed to the **XceptionNet model**.
4. If **real**, image is stored in **AWS S3**, and user data is saved in **DynamoDB**.
5. If **fake**, registration is **rejected**, and data is stored in **fake_registrations**.

### **2️⃣ User Login**
1. User enters **username & password**.
2. Credentials are checked in **DynamoDB**.
3. If valid, user **session is started**.

### **3️⃣ Creating Posts**
1. User uploads **post content & image**.
2. Image is sent to **backend API**.
3. Model classifies the image as **real or fake**.
4. Image is stored in **S3**, and post data is saved in **DynamoDB**.

### **4️⃣ Viewing Posts & Real/Fake Classification**
1. Posts are fetched from **DynamoDB**.
2. Posts are displayed in **Streamlit UI**.
3. Each post shows **real/fake status**.

---

## **📡 API Endpoints & Functionality**
### **🔹 User Authentication**
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/register` | Registers a new user and verifies profile image authenticity |
| POST | `/login` | Authenticates user credentials |

### **🔹 Posts & Image Verification**
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/posts` | Creates a new post with an image |
| GET | `/posts` | Retrieves all posts |
| GET | `/user/image-stats/{user_id}` | Returns the number of real & fake images uploaded by a user |

### **🔹 Model Prediction API**
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/predict` | Checks if an uploaded image is real or fake using XceptionNet |

---

## **🧠 Deepfake Detection Model (XceptionNet)**
- Pre-trained **XceptionNet** model is fine-tuned for deepfake detection.
- Uses **TensorFlow/Keras**.
- Input images are **preprocessed, resized, and normalized** before prediction.
- Model output:
  - **Fake Image (Score > 0.5)** → Classified as **Fake**.
  - **Real Image (Score <= 0.5)** → Classified as **Real**.

---

## **🚀 Future Enhancements**
- Implement **JWT Authentication**.
- Add **like & comment features**.
- Enhance **model accuracy** with EfficientNet & M2TR.
- Deploy backend on **AWS EC2** and frontend on **Streamlit Cloud**.

---

## **📞 Contact & Contributions**
- Contributions are welcome! Feel free to fork and submit PRs.
- Contact us via GitHub Issues for any questions.