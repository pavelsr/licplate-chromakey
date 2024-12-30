# docker build -t paveslr/licplate-chromakey .
# docker run --rm -t -p 7860:7860 paveslr/licplate-chromakey

FROM python:3.11-alpine
WORKDIR /app

# Install dependencies for Gradio and PIL
RUN apk add --no-cache \
    bash \
    gcc \
    libffi-dev \
    libmagic \
    musl-dev \
    && pip install --no-cache-dir \
    gradio \
    pillow \
    requests \
    && apk del gcc musl-dev libffi-dev

COPY gradio-plates-demo.py /app/
EXPOSE 7860
CMD ["python3", "gradio-plates-demo.py"]
