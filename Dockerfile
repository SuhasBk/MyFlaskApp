FROM python
COPY . /app/
WORKDIR /app/
RUN ["python", "-m", "pip", "install", "-r", "requirements.txt"]
EXPOSE 8000:8000
CMD ["python", "run.py"]
