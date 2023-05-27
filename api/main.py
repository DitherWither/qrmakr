from fastapi import FastAPI, Response
import qrcode.image.svg
from pydantic import BaseModel
import qrcode
import webcolors
from deta import Deta
import random
import string

app = FastAPI(openapi_prefix="/api", title="QrMakr API", description="A simple API for creating and managing QR codes", version="0.1.0")
deta = Deta()

drive = deta.Drive("qr_codes")
db = deta.Base("qr_codes")


class QrCodeRequest(BaseModel):
    name: str
    body: str
    border: int = 4
    fill_color: str = "#000000"
    background_color: str = "#FFFFFF"


def randomword(length):
    letters = string.ascii_lowercase
    return ''.join(random.choice(letters) for i in range(length))


def parse_color(color: str) -> tuple[int, int, int]:
    color = color.strip()

    if color.startswith('#'):
        return webcolors.hex_to_rgb(color)
    if color.startswith('rgb'):
        return tuple(map(int, color.replace(" ", "").removeprefix("rgb(").removesuffix(")").split(",")))

    # Assume that the color is a name
    return webcolors.name_to_rgb(color, spec="css3")


@app.post("/")
async def create_qr(qr_code_request: QrCodeRequest):
    """
        Create a new QR code

        The color functionality is currently broken, as for some reason we are
        always getting a black QR code.
    """

    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.ERROR_CORRECT_L,
        box_size=10,
        border=qr_code_request.border,
    )

    qr.add_data(qr_code_request.body)
    qr.make(fit=True)

    fill_color = parse_color(qr_code_request.fill_color)
    back_color = parse_color(qr_code_request.background_color)

    img = qr.make_image(fill_color=fill_color,
                        back_color=back_color,
                        image_factory=qrcode.image.svg.SvgPathImage)

    # Create a random name for the file
    file_name = randomword(10) + ".svg"

    # Save the file to the drive
    drive.put(file_name, data=img.to_string())

    # Save the file name to the database
    db.put({"name": qr_code_request.name, "file_name": file_name,
           "body": qr_code_request.body}, key=file_name)

    return Response(content=img.to_string(), media_type="image/svg+xml")


@app.get("/")
def get_all():
    """
        Get all QR codes

        Returns a list of all QR codes
    """
    return db.fetch().items


@app.get("/{file_name}")
async def get_qr(file_name: str):
    """
        Get a QR code by file name

        Returns the QR code with the given file name
    """
    buf = drive.get(file_name)
    if buf is None:
        return Response(content='{"detail": "Not Found"}', media_type="application/json", status_code=404)

    content = buf.read()


    return Response(content=content, media_type="image/svg+xml")


@app.delete("/{file_name}")
def delete_qr(file_name: str):
    """
        Delete a QR code by file name
    """
    db.delete(file_name)
    drive.delete(file_name)
    return Response(content='{"message": "Deleted successfully"}', media_type="application/json")
