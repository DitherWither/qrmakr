const qrlist = document.querySelector("#qrlist");
const qrform: HTMLFormElement | null = document.querySelector("#qrform");

let qrcodes: {
    name: string,
    file_name: string,
    body: string,
}[] = [];


async function loadQrCodes() {
    const response = await fetch("/api/");
    qrcodes = await response.json();
    console.log(qrcodes);
    renderQrCodes();
}

async function renderQrCodes() {
    if (qrlist?.innerHTML)
        qrlist.innerHTML = "";

    if (qrcodes.length === 0)
        qrlist?.insertAdjacentHTML("beforeend", "<h1 class='text-3xl text-yellow-300 font-bold text-center'>No Qr Codes</h1>");
    else
        qrcodes.forEach(qrcode => {
            const elem = document.createElement("div");
            elem.innerHTML = `
                <div class="flex justify-center items-center flex-col bg-slate-50 h-full p-4 rounded-2xl">
                    <h2 class="text-3xl font-bold">${qrcode.name}</h2>
                    <img src="/api/${qrcode.file_name}" alt="Qr Code for ${qrcode.body}" class="m-4">
                    <a href="${qrcode.body}" class="underline text-yellow-600 p-4">${qrcode.body}</a>
                    <button class="bg-yellow-300 rounded-full p-4" >Delete</button>
                </div>
            `;

            elem.addEventListener("click", () => {
                console.log("delete clicked");
                deleteQrCode(qrcode.file_name);
            })

            qrlist?.appendChild(elem);
        });
}

async function deleteQrCode(id: string) {
    await fetch(`/api/${id}`, {
        method: "DELETE",
    });
    loadQrCodes();
}

async function createQrCode(qr: { name: string | null, body: string | null, border: number | null, fill_color: string | null, background_color: string | null }) {
    const response = await fetch("/api/", {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
        },
        body: JSON.stringify(qr),
    });
    const data = await response.text();

    console.log(data);
    loadQrCodes();
}

loadQrCodes();

qrform?.addEventListener("submit", (e) => {
    e.preventDefault();

    const formData = new FormData(qrform);

    const name = formData.get("title")?.toString() ?? null;
    const body = formData.get("body")?.toString() ?? null;
    const border: number = 0;
    const fill_color = "#000000";
    const background_color = "#ffffff";


    createQrCode({ name, body, border, fill_color, background_color });

})

