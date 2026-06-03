#!/bin/bash
export STREAMLIT_SERVER_PORT=$PORT
streamlit run frontend/app.py --server.address 0.0.0.0 --server.headless true