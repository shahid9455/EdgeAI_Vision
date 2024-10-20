import streamlit as st
from together import Together
import base64
from io import BytesIO
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
import cv2
import numpy as np

# Set up the Together API client
client = Together(base_url="https://api.aimlapi.com/v1", api_key="AIMLAPI KEY")

# Function to analyze infrastructure
def analyze_infrastructure(image_url, analysis_type):
    try:
        response = client.chat.completions.create(
            model="meta-llama/Llama-3.2-90B-Vision-Instruct-Turbo",
            messages=[
                {
                    "role": "user",
                    "content": f"Perform the following analysis on this telecom infrastructure image: {analysis_type}. Check the image at this URL: {image_url}"
                }
            ],
            max_tokens=500
        )

        if response is None or response.choices is None:
            return "No valid response from the API. Please try again."
        
        return response.choices[0].message.content

    except Exception as e:
        return f"An error occurred: {str(e)}"

# Function to create a PDF report
def create_pdf_report(analysis_results, analysis_type):
    buffer = BytesIO()
    p = canvas.Canvas(buffer, pagesize=letter)
    p.drawString(100, 750, "Telecommunications Infrastructure Analysis Report")
    p.drawString(100, 730, f"Analysis Type: {analysis_type}")
    p.drawString(100, 710, "Analysis Results:")
    y_position = 690
    for result in analysis_results:
        p.drawString(100, y_position, f"- {result}")
        y_position -= 20
    p.save()
    buffer.seek(0)
    return buffer

# Function to highlight issues in the image
def highlight_issues(image, analysis_results):
    # For simplicity, we will just draw rectangles for demonstration.
    # In a real scenario, you would analyze the results to determine the exact coordinates.
    output_image = image.copy()
    for result in analysis_results:
        if "tower" in result.lower():
            # Simulating a bounding box around a tower
            cv2.rectangle(output_image, (50, 50), (300, 300), (0, 255, 0), 2)  # Green box for example
            cv2.putText(output_image, "Tower Detected", (50, 40), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
        elif "structural" in result.lower():
            # Simulating a bounding box for a structural issue
            cv2.rectangle(output_image, (400, 400), (600, 600), (255, 0, 0), 2)  # Red box for example
            cv2.putText(output_image, "Structural Issue", (400, 390), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 0, 0), 2)

    return output_image

# Streamlit app layout
st.title("Telecommunications Infrastructure Analysis")
st.write("Upload images of telecommunications infrastructure for detailed analysis.")

# Analysis Type Selection
analysis_type = st.selectbox("Select Analysis Type:", ["Structural Issues", "Connectivity Status", "Overall Condition"])

# File uploader for multiple images
image_files = st.file_uploader("Choose images...", type=["jpg", "jpeg", "png"], accept_multiple_files=True)

# Feedback Section
feedback = st.text_area("Feedback on previous analysis (optional):", placeholder="Let us know what you think!")

if image_files:
    analysis_history = []

    for img_file in image_files:
        # Convert each uploaded image to base64 format for display
        image_bytes = img_file.read()
        image_url = f"data:image/jpeg;base64,{base64.b64encode(image_bytes).decode()}"
        
        # Convert image bytes to OpenCV format for processing
        image_np = np.frombuffer(image_bytes, np.uint8)
        image_cv = cv2.imdecode(image_np, cv2.IMREAD_COLOR)

        st.image(image_url, caption=f"Uploaded Image: {img_file.name}", use_column_width=True)

    if st.button("Analyze All Images"):
        analysis_results = []
        for img_file in image_files:
            # Convert each uploaded image to base64 format for analysis
            image_bytes = img_file.read()
            image_url = f"data:image/jpeg;base64,{base64.b64encode(image_bytes).decode()}"

            with st.spinner(f"Analyzing {img_file.name}..."):
                analysis_result = analyze_infrastructure(image_url, analysis_type)
                analysis_results.append(f"{img_file.name}: {analysis_result}")
                
                # Highlight issues in the image
                output_image = highlight_issues(image_cv, analysis_results)
                
                # Convert back to base64 for display
                _, buffer = cv2.imencode('.jpg', output_image)
                output_image_base64 = base64.b64encode(buffer).decode()
                st.image(f"data:image/jpeg;base64,{output_image_base64}", caption=f"Highlighted Image: {img_file.name}", use_column_width=True)

        # Display all results at once
        st.subheader("Analysis Results:")
        for result in analysis_results:
            st.write(result)

        # Provide an option to download the consolidated report
        pdf_report = create_pdf_report(analysis_results, analysis_type)
        st.download_button("Download Consolidated Report", pdf_report, file_name="consolidated_analysis_report.pdf")

        # Ask user if they need to upload more images
        if st.checkbox("Would you like to upload more images for better analysis?"):
            st.success("Feel free to upload additional images!")

    # Detailed Instructions
    st.write("""
    ### Instructions:
    1. **Select Analysis Type**: Choose the type of analysis you want to perform on the uploaded images.
    2. **Upload Images**: Click on the button to upload one or more images of the telecommunications infrastructure you want to analyze.
    3. **Start Analysis**: Click the "Analyze All Images" button to receive insights based on the selected analysis type.
    4. **View Results**: After processing, all results will be displayed below the images.
    5. **Download Report**: You can download a consolidated PDF report of the analysis results.
    6. **Provide Feedback**: Share your feedback on previous analyses to help us improve.
    7. **Upload More Images**: If you're unsure or would like more clarity, you can upload additional images for better analysis.
    """)

# Footer with Contact Information
st.sidebar.write("### Contact Us")
st.sidebar.write("For any issues or suggestions, please reach out to: m.shahid9455@gmail.com")
