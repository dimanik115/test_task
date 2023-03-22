FROM python:alpine
WORKDIR /home/test_task
COPY ./ ./
RUN pip install -r requirements.txt
CMD ["python3","task.py"]