from typing import Annotated, Any

from fastapi import FastAPI, Form, Request, Response
from fastapi.responses import HTMLResponse, PlainTextResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from src import database
from src.models.utils import get_model
from src.mushroom import MUSHROOM_CHARACTERISTICS, Mushroom
from src.prediction.prepare_features import prepare_features

app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")

templates = Jinja2Templates(directory="templates")

model = get_model()


@app.get("/", response_class=HTMLResponse)
async def root(request: Request) -> Response:
    context = {"request": request, "characteristics": MUSHROOM_CHARACTERISTICS}
    return templates.TemplateResponse("index.html", context)


@app.post("/predict", response_class=HTMLResponse)
async def post_predict(
    request: Request,
    cap_shape: Annotated[str, Form()],
    cap_surface: Annotated[str, Form()],
    cap_color: Annotated[str, Form()],
    bruises: Annotated[str, Form()],
    odor: Annotated[str, Form()],
    gill_attachment: Annotated[str, Form()],
    gill_spacing: Annotated[str, Form()],
    gill_size: Annotated[str, Form()],
    gill_color: Annotated[str, Form()],
    stalk_shape: Annotated[str, Form()],
    stalk_root: Annotated[str, Form()],
    stalk_surface_above_ring: Annotated[str, Form()],
    stalk_surface_below_ring: Annotated[str, Form()],
    stalk_color_above_ring: Annotated[str, Form()],
    stalk_color_below_ring: Annotated[str, Form()],
    veil_type: Annotated[str, Form()],
    veil_color: Annotated[str, Form()],
    ring_number: Annotated[str, Form()],
    ring_type: Annotated[str, Form()],
    spore_print_color: Annotated[str, Form()],
    population: Annotated[str, Form()],
    habitat: Annotated[str, Form()],
) -> Response:
    # pylint: disable=too-many-arguments,too-many-locals
    feature_dict = {
        "cap_shape": cap_shape,
        "cap_surface": cap_surface,
        "cap_color": cap_color,
        "bruises": bruises,
        "odor": odor,
        "gill_attachment": gill_attachment,
        "gill_spacing": gill_spacing,
        "gill_size": gill_size,
        "gill_color": gill_color,
        "stalk_shape": stalk_shape,
        "stalk_root": stalk_root,
        "stalk_surface_above_ring": stalk_surface_above_ring,
        "stalk_surface_below_ring": stalk_surface_below_ring,
        "stalk_color_above_ring": stalk_color_above_ring,
        "stalk_color_below_ring": stalk_color_below_ring,
        "veil_type": veil_type,
        "veil_color": veil_color,
        "ring_number": ring_number,
        "ring_type": ring_type,
        "spore_print_color": spore_print_color,
        "population": population,
        "habitat": habitat,
    }

    features = prepare_features(feature_dict)

    pred = model.predict(features)[0]

    context = {"request": request, "features": feature_dict, "pred": pred}

    return templates.TemplateResponse("submit.html", context)


@app.post("/api/predict", status_code=200)
async def get_prediction(mushroom: Mushroom) -> dict[str, float]:
    features = prepare_features(mushroom.dict())

    pred = model.predict(features)[0]

    result = {"poisonous-probability": float(pred)}
    return result


@app.post("/confirm_classification", status_code=200, response_class=PlainTextResponse)
async def confirm_classification(
    request: Request,
    mushroom_classification: float = Form(...),
    confirmation: str = Form(...),
):
    form_data = await request.form()
    is_poisonous = mushroom_classification > 0.5
    if confirmation == "no":
        is_poisonous = not is_poisonous

    characteristics: dict[str, Any] = {
        field: value
        for field, value in form_data.items()
        if field in MUSHROOM_CHARACTERISTICS
    }
    characteristics["class"] = "p" if is_poisonous else "e"
    characteristics["id"] = None

    conn = database.create_connection()
    database.create_table(conn)

    cursor = conn.cursor()
    insert_query = database.get_insert_query()
    cursor.execute(insert_query, characteristics)

    conn.commit()
    conn.close()

    return "Form submitted successfully!"
