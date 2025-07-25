# fun.py

def include_router(prefixtags: str):
    from main import app  # Local import to avoid circular import
    from fastapi import APIRouter

    fun_router = APIRouter ()

    @fun_router.get ("/example")
    async def example():
        return {"message": "Example route"}

    app.include_router (fun_router, prefix=f"/{prefixtags}")
