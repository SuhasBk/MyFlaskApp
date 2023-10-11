FROM python
COPY . /app/
WORKDIR /app/
RUN ["python", "-m", "pip", "install", "-r", "requirements.txt"]
EXPOSE 8080:8080
CMD ["python", "run.py"]
