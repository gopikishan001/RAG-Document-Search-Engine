from fastapi import APIRouter

router = APIRouter()

@router.get("/")
async def test_upload():
    return {"status": "Upload route ready"}
