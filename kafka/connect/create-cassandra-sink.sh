#!/bin/sh

echo "Starting Weather Sink"
curl -s \
     -X POST http://localhost:8083/connectors \
     -H "Content-Type: application/json" \
     -d '{
  "name": "weathersink",
  "config": {
    "connector.class": "com.datastax.oss.kafka.sink.CassandraSinkConnector",
    "value.converter": "org.apache.kafka.connect.json.JsonConverter",
    "value.converter.schemas.enable": "false",  
    "key.converter": "org.apache.kafka.connect.json.JsonConverter",
    "key.converter.schemas.enable":"false",
    "tasks.max": "10",
    "topics": "weather",
    "contactPoints": "cassandradb",
    "loadBalancing.localDc": "datacenter1",
    "topic.weather.kafkapipeline.weatherreport.mapping": "location=value.location, forecastdate=value.report_time, description=value.description, temp=value.temp, feels_like=value.feels_like, temp_min=value.temp_min, temp_max=value.temp_max, pressure=value.pressure, humidity=value.humidity, wind=value.wind, sunrise=value.sunrise, sunset=value.sunset",
    "topic.weather.kafkapipeline.weatherreport.consistencyLevel": "LOCAL_QUORUM"
  }
}'
echo "Starting Faker Sink"
curl -s \
     -X POST http://localhost:8083/connectors \
     -H "Content-Type: application/json" \
     -d '{
  "name": "fakersink",
  "config": {
    "connector.class": "com.datastax.oss.kafka.sink.CassandraSinkConnector",
    "value.converter": "org.apache.kafka.connect.json.JsonConverter",
    "value.converter.schemas.enable": "false",  
    "key.converter": "org.apache.kafka.connect.json.JsonConverter",
    "key.converter.schemas.enable":"false",
    "tasks.max": "10",
    "topics": "faker",
    "contactPoints": "cassandradb",
    "loadBalancing.localDc": "datacenter1",
    "topic.faker.kafkapipeline.fakerdata.mapping": "name=value.name, gender=value.gender, address=value.address, year=value.year, email=value.email, phone_number=value.phone_number, job=value.job, company=value.company, country=value.country, city=value.city, date_time=value.date_time, credit_card_number=value.credit_card_number",
    "topic.faker.kafkapipeline.fakerdata.consistencyLevel": "LOCAL_QUORUM"
  }
}'
echo "Starting Wikipedia Sink"
curl -s \
     -X POST http://localhost:8083/connectors \
     -H "Content-Type: application/json" \
     -d '{
  "name": "wikipediasink",
  "config": {
    "connector.class": "com.datastax.oss.kafka.sink.CassandraSinkConnector",
    "value.converter": "org.apache.kafka.connect.json.JsonConverter",
    "value.converter.schemas.enable": "false",  
    "key.converter": "org.apache.kafka.connect.json.JsonConverter",
    "key.converter.schemas.enable":"false",
    "tasks.max": "10",
    "topics": "wikipedia",
    "contactPoints": "cassandradb",
    "loadBalancing.localDc": "datacenter1",
    "topic.wikipedia.kafkapipeline.wikipediadata.mapping": "id=value.id, type=value.type, title=value.title, timestamp=value.timestamp, user=value.user, bot=value.bot, length_old=value.length_old, length_new=value.length_new, revision_old=value.revision_old, revision_new=value.revision_new",
    "topic.wikipedia.kafkapipeline.wikipediadata.consistencyLevel": "LOCAL_QUORUM"
  }
}'
echo "Done."
