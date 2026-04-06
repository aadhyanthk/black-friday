# backend/main.py
import os
import asyncpg
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv

load_dotenv()

app = FastAPI(title="Black Friday Flash Sale Engine")

# Explicitly whitelist the Vite React origin
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

db_pool = None

@app.on_event("startup")
async def startup_database():
    global db_pool
    url = os.getenv("DATABASE_URL")
    db_pool = await asyncpg.create_pool(url)

@app.on_event("shutdown")
async def shutdown_database():
    await db_pool.close()

class CheckoutPayload(BaseModel):
    item_id: int
    user_identifier: str

@app.get("/inventory/{item_id}")
async def get_inventory(item_id: int):
    async with db_pool.acquire() as connection:
        row = await connection.fetchrow(
            "SELECT item_name, stock_count FROM public.inventory WHERE id = $1",
            item_id
        )
        if not row:
            raise HTTPException(status_code=404, detail="Item not found")
        return {"item_name": row['item_name'], "stock_count": row['stock_count']}

@app.post("/checkout")
async def process_checkout(payload: CheckoutPayload):
    async with db_pool.acquire() as connection:
        async with connection.transaction():
            row = await connection.fetchrow(
                "SELECT stock_count FROM public.inventory WHERE id = $1 FOR UPDATE",
                payload.item_id
            )

            if not row:
                raise HTTPException(status_code=404, detail="Item not found.")

            if row['stock_count'] <= 0:
                await connection.execute(
                    "INSERT INTO public.transactions (inventory_id, user_identifier, status) VALUES ($1, $2, $3)",
                    payload.item_id, payload.user_identifier, "FAILED_OUT_OF_STOCK"
                )
                raise HTTPException(status_code=409, detail="Inventory depleted.")

            await connection.execute(
                "UPDATE public.inventory SET stock_count = stock_count - 1 WHERE id = $1",
                payload.item_id
            )

            await connection.execute(
                "INSERT INTO public.transactions (inventory_id, user_identifier, status) VALUES ($1, $2, $3)",
                payload.item_id, payload.user_identifier, "SUCCESS"
            )

    return {"status": "success", "message": "Checkout completed successfully."}