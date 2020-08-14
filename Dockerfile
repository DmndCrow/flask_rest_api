# load python3.7 image
FROM python:alpine3.7

# copy files into /code directory
ADD . /code

# make directory /code as working directory
WORKDIR /code

# install python packages from requirements.txt
RUN pip install -r requirements.txt


# run app.py
CMD ["python", "app.py"]