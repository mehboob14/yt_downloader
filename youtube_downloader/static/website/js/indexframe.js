const checkbox = document.getElementById("checkbox");
const logo = document.getElementById("logo");

const scriptElement = document.querySelector('script[data-api-url]');
const frameURL = scriptElement ? scriptElement.getAttribute('data-api-url') : null;

// Function to update logo based on theme
function updateLogo(theme) {
    if (theme === "dark") {
        logo.src = "/static/website/images/logo-dark.svg"; // Change to dark logo
    } else {
        logo.src = "/static/website/images/logo.svg"; // Change to default logo
    }
}

// Check local storage for theme preference
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


const isYouTubeURL = (url) => {
    const regex = /^(https?:\/\/)?(www\.|m\.)?(youtube\.com\/(watch\?v=[\w-]+|shorts\/[\w-]+|embed\/[\w-]+)|youtu\.be\/[\w-]+)(\?[=&\w-]*)?$/;
    return regex.test(url);
};

const handleSearchForm = () => {
    const query = document.querySelector("input[name=query]").value;

    if (isYouTubeURL(query)) {
        const searchResults = document.getElementById("searchResults");
        searchResults.innerHTML = `
                 <div class="search-item">
                 <iframe src="${frameURL}${query}" width="100%" 
                                    height="790" 
                                    frameborder="0" 
                                    style="border-radius: 5px;">
                                </iframe>
                 </div>
                `;
        setTimeout(() => {
            const searchButton = document.querySelector(".download-form button");
            searchButton.innerHTML = `${searchButton.innerText} <i class="fa-solid fa-arrows-rotate"></i>`;
            searchButton.disabled = false;
            window.scrollBy({ top: 340, behavior: "smooth" });
        }, 4000)
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
                                <img src="https://img.youtube.com/vi/${video.id}/mqdefault.jpg" alt="${video.title}">
                                <h4>${video.title}</h4>
                                <button class="toggle-iframe">Download</button>
                                <iframe 
                                    src="" 
                                    data-src="${frameURL}https://www.youtube.com/watch?v=${video.id}" 
                                    width="100%" 
                                    height="790" 
                                    frameborder="0" 
                                    style="border-radius: 5px; display: none;">
                                </iframe>
                            `;

                        searchResults.appendChild(videoElement);
                    });

                    // Add event listeners for all "Download" buttons
                    document.querySelectorAll(".toggle-iframe").forEach(button => {
                        button.addEventListener("click", (event) => {
                            const btn = event.target;
                            const iframe = btn.nextElementSibling; // Get the iframe next to the button

                            if (iframe.style.display === "none") {
                                iframe.src = iframe.getAttribute("data-src"); // Load the iframe
                                iframe.style.display = "block";
                                btn.textContent = "Close";
                            } else {
                                iframe.style.display = "none";
                                btn.textContent = "Download";
                            }
                        });
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