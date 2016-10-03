FROM python:3.3

RUN mkdir /home/molecule
WORKDIR /home/molecule

COPY requirements.txt /home/molecule/requirements.txt
RUN pip install -r requirements.txt

COPY test-requirements.txt /home/molecule/test-requirements.txt
RUN pip install -r test-requirements.txt

COPY . /home/molecule
RUN pip install .