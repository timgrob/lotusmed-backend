from fastapi import APIRouter, HTTPException, status


router = APIRouter(prefix="/paraphrase", tags=["paraphrase"])


@router.post("/", response_model=str, status_code=status.HTTP_200_OK)
def paraphrase(payload: str) -> str:
    if not payload:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Payload is required")
    return payload
