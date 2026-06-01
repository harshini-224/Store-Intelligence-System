from fastapi import APIRouter
from fastapi.responses import FileResponse

router = APIRouter()


@router.get("/heatmap/floor-a")
def floor_a_heatmap():

    return FileResponse(
        "data/outputs/heatmaps/floor_a_heatmap.jpg"
    )


@router.get("/heatmap/floor-b")
def floor_b_heatmap():

    return FileResponse(
        "data/outputs/heatmaps/floor_b_heatmap.jpg"
    )