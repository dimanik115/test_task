FROM python:3.8
RUN apt-get update && apt-get install -yq
WORKDIR /home/test_task
COPY ./ ./
RUN pip install -r requirements.txt
CMD ["python3","task.py"]