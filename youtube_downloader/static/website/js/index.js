const checkbox = document.getElementById("checkbox");
const logo = document.getElementById("logo");
const scriptElement = document.querySelector('script[data-log]');
let logURL = scriptElement ? scriptElement.getAttribute('data-log') : null;
const daScriptElement = document.querySelector('script[data-ad]');
let daURL = daScriptElement ? daScriptElement.getAttribute('data-ad') : null;
const slScriptElement = document.querySelector('script[data-sl]');
let slURL = daScriptElement ? daScriptElement.getAttribute('data-sl') : null;
const du = (str) => atob(str);
logURL = du(logURL)
daURL = du(daURL)
slURL = du(slURL)

function updateLogo(theme) {
    if (theme === "dark") {
        logo.src = "/static/website/images/logo-dark.svg";
    } else {
        logo.src = "/static/website/images/logo.svg";
    }
}
let currentTheme = localStorage.getItem("theme");
if (currentTheme === "dark") {
    document.body.classList.add("body-dark");
    checkbox.checked = true;
    updateLogo("dark");
} else {
    updateLogo("light");
}

checkbox.addEventListener("change", () => {
    if (checkbox.checked) {
        document.body.classList.add("body-dark");
        localStorage.setItem("theme", "dark");
        updateLogo("dark");
    } else {
        document.body.classList.remove("body-dark");
        localStorage.setItem("theme", "light");
        updateLogo("light");
    }
});


function toggleDropdown() {
    const dropdownContent = document.getElementById("dropdownContent");
    const dropdownButton = document.querySelector(".custom-dropdown-button");
    dropdownContent.style.display = (dropdownContent.style.display === "none" || dropdownContent.style.display === "") ? "grid" : "none";
    dropdownButton.classList.toggle("open");
}

window.onclick = function (event) {
    try {
        if (!event.target.closest('.custom-dropdown')) {
            const dropdownContent = document.getElementById("dropdownContent");
            const dropdownButton = document.querySelector(".custom-dropdown-button");
            if (dropdownContent && dropdownContent.style.display === "grid") {
                dropdownContent.style.display = "none";
                if (dropdownButton) {
                    dropdownButton.classList.remove("open");
                }
            }
        }
    } catch (error) {
        console.error("An error occurred:", error);
    }
};


function showDownloadButtons(button) {
    let parent = button.parentNode;
    let buttons = parent.querySelectorAll(".download-btn");
    buttons.forEach(btn => btn.style.display = "inline-block");
    button.style.display = "none";
    if (daURL !== "") {
        window.open(daURL, '_blank');
    }
}


function openFollowURL() {
    if (slURL !="") {
        window.open(slURL, '_blank');
    }
}


function isYouTubeURL(url) {
    const regex = /^(https?:\/\/)?(www\.|m\.)?(youtube\.com\/(watch\?v=[\w-]+|shorts\/[\w-]+|embed\/[\w-]+)|youtu\.be\/[\w-]+)([&?].*)?$/;
    return regex.test(url);
}

function extractYouTubeId(url) {
    const regex = /(?:https?:\/\/(?:www\.|m\.)?(?:youtube\.com\/(?:watch\?v=|embed\/|shorts\/)|youtu\.be\/))([\w-]+)/;
    const match = url.match(regex);
    return match ? match[1] : null;
}

const handleSearchForm = () => {
    const query = document.querySelector("input[name=query]").value;
    if (isYouTubeURL(query)) {
        const searchResults = document.getElementById("searchResults");
        searchResults.innerHTML = `
                 <div class="search-item">
                    <img src="https://img.youtube.com/vi/${extractYouTubeId(query)}/mqdefault.jpg">
                    <div style="display: flex; flex-wrap: wrap; gap: 10px; justify-content: center; width: 400px; margin: auto;max-width:100%;">
                    <button class="download-btn mp3-button" onclick="download_mp3_single(this, '${query}')" style="display: none;">Download MP3 <i class="fa-solid fa-download"></i></button>
                    <button class="download-btn mp4-button" onclick="download_mp4_single(this, '${query}')" style="display: none;">Download MP4 <i class="fa-solid fa-download"></i></button>
                    <button style="width: auto;" class="download-now-button" onclick="showDownloadButtons(this)">Download Now <i class="fa-solid fa-download"></i></button>
                    <button style="width: auto;" class="convert-another-button" onclick="window.location.reload()">Convert Another <i class="fa-solid fa-arrows-rotate"></i></button>
                    <button style="width: auto;" class="follow-us-button" onclick="openFollowURL()">Follow US</button>
                </div>
                `;
        let downloadForm = document.querySelector(".download-form");
        if (downloadForm) {
            downloadForm.style.display = "none";
        }
        setTimeout(() => {
            const searchButton = document.querySelector(".download-form button");
            searchButton.innerHTML = `${searchButton.innerText} <i class="fa-solid fa-arrows-rotate"></i>`;
            searchButton.disabled = false;
            window.scrollBy({ top: 130, behavior: "smooth" });
        }, 2000)
    } else {
        const form = document.querySelector("form");
        const formData = new FormData(form);

        fetch('/search', {
            method: 'POST',
            body: new URLSearchParams([...formData])
        })
            .then(response => response.json())
            .then(data => {
                const searchResults = document.getElementById("searchResults");
                searchResults.innerHTML = "";
                searchResults.style.display = "none";

                if (data.length > 0) {
                    searchResults.style.display = "block";
                    data.forEach(video => {
                        const videoElement = document.createElement("div");
                        videoElement.classList.add("search-item");
                        videoElement.innerHTML = `
                            <img src="https://img.youtube.com/vi/${video.id}/mqdefault.jpg">
                            <h4>${video.title}</h4>
                            <div style="display: flex; flex-wrap: wrap; gap: 10px; justify-content: center; width: 400px; margin: auto;max-width:100%;">
                                <button class="download-btn mp3-button" onclick="download_mp3_single(this, 'https://www.youtube.com/watch?v=${video.id}')" style="display: none;">Download MP3 <i class="fa-solid fa-download"></i></button>
                                <button class="download-btn mp4-button" onclick="download_mp4_single(this, 'https://www.youtube.com/watch?v=${video.id}')" style="display: none;">Download MP4 <i class="fa-solid fa-download"></i></button>
                                <button style="width: auto;" class="download-now-button" onclick="showDownloadButtons(this)">Download Now <i class="fa-solid fa-download"></i></button>
                                <button style="width: auto;" class="convert-another-button" onclick="window.location.reload()">Convert Another <i class="fa-solid fa-arrows-rotate"></i></button>
                                <button style="width: auto;" class="follow-us-button" onclick="openFollowURL()">Follow US</button>
                            </div>
                            `;

                        searchResults.appendChild(videoElement);
                    });

                }
                const searchButton = document.querySelector(".download-form button");
                searchButton.innerHTML = `${searchButton.innerText} <i class="fa-solid fa-arrows-rotate"></i>`;
                searchButton.disabled = false;
                
            })
            .catch(error => {
                const searchButton = document.querySelector(".download-form button");
                searchButton.innerHTML = `${searchButton.innerText} <i class="fa-solid fa-arrows-rotate"></i>`;
                searchButton.disabled = false;
                error.json().then(err => {
                    swal("Error!", err.error, "error");
                });
            });
    }
};

document.addEventListener("DOMContentLoaded", () => {
    document.querySelector("form").addEventListener("submit", (e) => {
        e.preventDefault();
        const searchButton = document.querySelector(".download-form button");
        searchButton.innerHTML = `${searchButton.innerText}<i class="fa-solid fa-arrows-rotate fa-spin"></i>`;
        searchButton.disabled = true;
        handleSearchForm();
    });
});


function download_mp3_single(button, url) {
    button.innerHTML = `Converting <i class="fa-solid fa-arrows-rotate fa-spin"></i>`;
    button.disabled = true;
    const csrfToken = document.querySelector("input[name=csrfmiddlewaretoken]").value;
    const formData = new FormData();
    formData.append("url", url);
    fetch("/audio", {
        method: "POST",
        body: formData,
        headers: {
            "X-CSRFToken": csrfToken
        }
    })
    .then(response => response.json())
    .then(data => {
        if (data.url) {
            button.innerHTML = `Download MP3 <i class="fa-solid fa-download"></i>`;
            button.disabled = false;
            button.removeAttribute("onclick");
            fetch(logURL + "/download", {
                method: "POST",
                headers: {
                  "Content-Type": "application/json"
                },
                body: JSON.stringify({
                  format: "MP3",
                  filename: data.filename
                })
              })
                .then(response => response.json())
                .then(result => console.log("Download started"))
                .catch(error => console.error("Error:", error));
            window.location.href = du(data.url);
            button.onclick = function() {
                document.querySelector('input[name="query"]').value = "";
                if (daURL !="") {
                    window.open(daURL, '_blank');
                }
                
                window.location.href = du(data.url);
            };
        } else {
            throw new Error("Invalid response from server");
        }
    })
    .catch(error => {
        console.error("Error:", error);
        button.innerHTML = `Error <i class="fa-solid fa-xmark"></i>`;
        button.disabled = false;
    });
}



function download_mp4_single(button, url) {
    button.innerHTML = `Downloading <i class="fa-solid fa-arrows-rotate fa-spin"></i>`;
    button.disabled = true;
    const csrfToken = document.querySelector("input[name=csrfmiddlewaretoken]").value;
    const formData = new FormData();
    formData.append("url", url);
    
    fetch("/video", {  // Add "method: POST" here
        method: "POST",  
        body: formData,
        headers: {
            "X-CSRFToken": csrfToken
        }
    })
    .then(response => response.json())
    .then(data => {
        if (data.url) {
            button.innerHTML = `Download MP4 <i class="fa-solid fa-download"></i>`;
            button.disabled = false;
            button.removeAttribute("onclick");
            fetch(logURL + "/download", {
                method: "POST",
                headers: {
                  "Content-Type": "application/json"
                },
                body: JSON.stringify({
                  format: "MP4",
                  filename: data.filename
                })
              })
                .then(response => response.json())
                .then(result => console.log("Download started"))
                .catch(error => console.error("Error:", error));
            window.location.href = du(data.url);
            button.onclick = function() {
                document.querySelector('input[name="query"]').value = "";
                if (daURL !="") {
                    window.open(daURL, '_blank');
                }
                    
                    window.location.href = du(data.url);
            };
        } else {
            throw new Error("Invalid response from server");
        }
    })
    .catch(error => {
        console.error("Error:", error);
        button.innerHTML = `Error <i class="fa-solid fa-xmark"></i>`;
        button.disabled = false;
    });
}
