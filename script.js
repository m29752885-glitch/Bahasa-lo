const USER = "m29752885-glitch";
const REPO = "Bahasa-lo";
const BRANCH = "main";

async function fetchRepo(path = "") {
    const url = `https://api.github.com/repos/${USER}/${REPO}/contents/${path}?ref=${BRANCH}`;
    const res = await fetch(url);
    const data = await res.json();
    return data;
}

async function renderFiles(path = "") {
    const fileList = document.getElementById("file-list");
    fileList.innerHTML = "";
    const items = await fetchRepo(path);
    items.forEach(item => {
        const li = document.createElement("li");
        li.textContent = item.name;
        li.style.cursor = "pointer";
        li.onclick = () => {
            if (item.type === "dir") {
                renderFiles(item.path);
            } else {
                fetchFile(item.path);
            }
        };
        fileList.appendChild(li);
    });
}

async function fetchFile(path) {
    const url = `https://api.github.com/repos/${USER}/${REPO}/contents/${path}?ref=${BRANCH}`;
    const res = await fetch(url);
    const data = await res.json();
    const content = atob(data.content);
    document.getElementById("file-content").textContent = content;
}

// Init
renderFiles();
