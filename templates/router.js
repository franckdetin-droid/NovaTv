const app = document.getElementById("app");

async function charger(page) {
    try {
        const r = await fetch(page);
        const html = await r.text();
        app.innerHTML = html;
    } catch {
        app.innerHTML = "<h2>Page introuvable</h2>";
    }
}

function router() {
    switch (location.hash) {
        case "#/about":
            charger("about.html");
            break;

        case "#/contact":
            charger("contact.html");
            break;

        case "#/privacy":
            charger("privacy.html");
            break;

        case "#/terms":
            charger("terms.html");
            break;

        default:
            charger("home.html");
    }
}

window.addEventListener("hashchange", router);
window.addEventListener("load", router);
