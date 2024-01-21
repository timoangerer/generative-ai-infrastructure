FROM alpine:3.14

RUN apk add --no-cache curl

WORKDIR /app

COPY download.sh /app/download.sh

RUN chmod +x /app/download.sh

COPY models.txt .

CMD ["/app/download.sh"]
