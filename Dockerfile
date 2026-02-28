FROM python:3.12.12-alpine

ENV PIP_INDEX_URL=https://pypi.tuna.tsinghua.edu.cn/simple
RUN pip install --upgrade pip
RUN apk add --no-cache build-base

WORKDIR /Hello-CTF
COPY mkdocs.yml ./mkdocs.yml
COPY docs ./docs
COPY overrides ./overrides
COPY requirements.txt ./requirements.txt

RUN pip install -r requirements.txt

RUN mkdocs build

EXPOSE 8000

CMD ["mkdocs", "serve", "-a", "0.0.0.0:8000"]