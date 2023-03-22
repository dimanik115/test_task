FROM python:3.8.10-alpine
WORKDIR /home/test_task
COPY ./ ./
RUN pip install -r requirements.txt
CMD ["python3","task.py"]