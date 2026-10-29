import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from fastapi import FastAPI
import gradio as gr

from roicropper.web.app import demo

app = FastAPI()
app = gr.mount_gradio_app(app, demo, path="/")
