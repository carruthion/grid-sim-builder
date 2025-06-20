FROM python:3.13

WORKDIR /usr/src/app

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# TODO: in final version hardcopy python script into docker image
# COPY . .

CMD [ "python", "./main.py" ]