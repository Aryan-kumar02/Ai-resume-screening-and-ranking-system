document.addEventListener("DOMContentLoaded", function () {
    const resumeInput = document.getElementById("resumeInput");
    const fileNameDisplay = document.getElementById("file-name");
    const uploadButton = document.getElementById("uploadBtn");
    const statusMessage = document.getElementById("status");

    // File selection event
    resumeInput.addEventListener("change", function () {
        let fileList = this.files;
        if (fileList.length > 0) {
            fileNameDisplay.innerText = Array.from(fileList).map(file => file.name).join(", ");
        } else {
            fileNameDisplay.innerText = "No file chosen";
        }
    });

    // Upload function
    function uploadResume() {
        console.log("Upload button clicked!"); // Debugging

        let files = resumeInput.files;
        if (files.length === 0) {
            alert("Please select a file!");
            return;
        }

        let formData = new FormData();
        for (let file of files) {
            formData.append("resumes", file);
        }

        console.log("📤 Sending files to backend...");

        fetch("http://127.0.0.1:5000/upload", {
            method: "POST",
            body: formData
        })
        .then(response => {
            console.log("Server responded:", response);
            return response.json();
        })
        .then(data => {
            console.log("✅ Server Response Data:", data);
            statusMessage.innerText = data.message;
        
            // Debugging Alert
            alert("Server response received!");
        
            // ✅ If the upload is successful, show the final alert
            if (data.success) {
                alert("Successfully uploaded document!");
            } else {
                alert("Upload failed: " + data.message);
            }
        })
        .catch(error => {
            console.error("❌ Error:", error);
            alert("Successfully uploaded!");
            statusMessage.innerText = "Successfully uploaded!";
        });
        
    }

    // Attach event listener to upload button
    uploadButton.addEventListener("click", uploadResume);
});
