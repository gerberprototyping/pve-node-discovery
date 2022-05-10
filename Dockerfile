FROM python:3-alpine

WORKDIR /usr/src/app

COPY pip-requirements.txt ./
RUN pip install --no-cache-dir -r pip-requirements.txt

COPY pve_node_exporter_discovery.py ./

EXPOSE 24684
CMD [ "python", "./pve_node_exporter_discovery.py" ]