FROM python:3-alpine

WORKDIR /usr/src/app

COPY pip-requirements.txt ./
RUN pip install --no-cache-dir -r pip-requirements.txt

COPY pve-node-discovery.py ./

EXPOSE 9951
ENTRYPOINT [ "python", "./pve-node-discovery.py" ]