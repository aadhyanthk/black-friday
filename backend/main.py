# backend/main.py
import os
import asyncpg
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from dotenv import load_dotenv

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware # Add this
# ... (rest of imports)

app = FastAPI(title="Black Friday Flash Sale Engine")

# Add CORS middleware so the React app can talk to the API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

load_dotenv()

app = FastAPI(title="Black Friday Flash Sale Engine")

# Global database connection pool
db_pool = None

@app.on_event("startup")
async def startup_database():
    global db_pool
    url = os.getenv("DATABASE_URL")
    print(f"DEBUG: Connecting to {url}")
    db_pool = await asyncpg.create_pool(url)
    
    # Internal Audit: Check what tables THIS connection can see
    async with db_pool.acquire() as conn:
        tables = await conn.fetch("SELECT table_name FROM information_schema.tables WHERE table_schema = 'public'")
        print(f"DEBUG: Tables found by API: {[t['table_name'] for t in tables]}")

@app.on_event("shutdown")
async def shutdown_database():
    await db_pool.close()

class CheckoutPayload(BaseModel):
    item_id: int
    user_identifier: str

@app.post("/checkout")
async def process_checkout(payload: CheckoutPayload):
    async with db_pool.acquire() as connection:
        # Begin database transaction
        async with connection.transaction():
            # 1. Pessimistic Lock: Lock the specific inventory row
            row = await connection.fetchrow(
                "SELECT stock_count FROM public.inventory WHERE id = $1 FOR UPDATE",
                payload.item_id
            )

            if not row:
                raise HTTPException(status_code=404, detail="Item not found.")

            # 2. Concurrency Check
            if row['stock_count'] <= 0:
                await connection.execute(
                    "INSERT INTO transactions (inventory_id, user_identifier, status) VALUES ($1, $2, $3)",
                    payload.item_id, payload.user_identifier, "FAILED_OUT_OF_STOCK"
                )
                raise HTTPException(status_code=409, detail="Inventory depleted.")

            # 3. Deduct Inventory
            await connection.execute(
                "UPDATE public.inventory SET stock_count = stock_count - 1 WHERE id = $1",
                payload.item_id
            )
            
            # 3. Insert with explicit schema
            await connection.execute(
                "INSERT INTO public.transactions (inventory_id, user_identifier, status) VALUES ($1, $2, $3)",
                payload.item_id, payload.user_identifier, "SUCCESS"
            )

    return {"status": "success", "message": "Checkout completed successfully."}