FROM devtography/python-cuda

WORKDIR /


RUN mkdir -p /scripts
RUN mkdir -p /model


COPY model/distil-gpt2 /model/distil-gpt2
#COPY tokenizers /model/tokenizers
#COPY inference.py /scripts
COPY requirements.txt /

RUN pip install -r requirements.txt

