from contextlib import asynccontextmanager

from fastapi import FastAPI

from dal.checkpointer import close_checkpointer, init_checkpointer


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_checkpointer()
    yield
    close_checkpointer()


def register_lifespan(app: FastAPI):
    app.router.lifespan_context = lifespan
