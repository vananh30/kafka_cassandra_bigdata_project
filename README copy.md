# Data Pipeline with Docker, Kafka, and Cassandra

The resources in this GitHub can be used to deploy an end-to-end data pipeline on your local computer using Docker containerized Kafka (data streaming), Cassandra (NoSQL database) and Jupyter Lab (data analysis visualization).

This bases on the repo https://github.com/salcaino/sfucmpt733/tree/main/foobar-kafka Substantial changes and bug fixes have been made.

For demo video, please access the [Youtube Link](https://youtu.be/pO5KWI55B0Q) or the [OneDrive Link](https://rmiteduau-my.sharepoint.com/:v:/g/personal/s3818102_rmit_edu_vn/ETEEcc-si-hInmHe29STbR8BBmSbBHK1Atq8FKPSzIyVRg?e=flWDKJ) shared to you within RMIT access.

## ⚙️ Installation and Launch Script

### 🔸 Pre-requisite

You need to obtain the API from [OpenWeatherMap API](https://openweathermap.org/api)

After successfully obtaining the API, please create new files `openweathermap_service.cfg` based on the `...-test.cfg` files provided.

### 🔺 Known issue on MacOS M1 with Docker

There will be `kafka-connect` and `kafka-manager` containers will be run in an unstable condition due to incompatibility of M1 Chip with Docker. Please check the tag `Troubleshoot` for M1 unstable condition in the recommended flow.

### 📄 Script Description

`run.sh` will help you to start the project more easily.
**Note** In MacOS, you may need to grant permission to run the file

```bash
chmod +x ./run.sh
```

```bash
./run.sh [build|setup|start|stop|bash|clean]
```

- **build**: automatically build the according images to the required containers for the project (can be selected with y/N options)
- **setup**: automatically setup Cassandra and Kafka (including Kafka Connect) sequentially and effectively link necessary services together for a functional flow
- **start**: automatically launch the producers, consumers, and dashboard (can be selected with y/N options)
- **stop**: automatically stop all running containers and remove networks
- **bash**: access the preferred container's shell (support direct CQLSH access for Cassandra container)
- **clean**: remove everything ‼️

### 🧬 Recommended flow:

Make sure Docker 🐳 is running in your local machine before executing the below flow

0. (Optional) Pre-`build` all the images first

```bash
./run.sh build
```

1. `setup` Kafka & Cassandra network

```bash
./run.sh setup
```

2. Kafka-Manager front end is available at http://localhost:9000 (you may need to wait a while to get this online - please check the container's log with `bash`). Create a cluster with `Cluster Zookeeper Hosts` = `zookeeper:2181`

> For first-time user, username = admin, password = bigbang to access the site

3. `Troubleshoot` Check for the `kafka/connect` container. If the `./start-and-wait.sh` script were down (not successfully create sink and return HTML error 404), please retry with the below command. You need to make sure that the sink connection was established. Otherwise Cassandra cannot receive any data.

```bash
docker exec -it kafka-connect bash ./start-and-wait.sh
```

`Troubleshoot`: If the **"Kafka Connect listener HTTP state: 000"** took so much time, jump to step 7 to `stop` all containers and retry from step 1.

4. `Start` the producers and consumers

```bash
./run.sh start
```

5. Access any container's shell with `bash`. Cassandra's shell is already supported with a shortcut to `cqlsh`

```bash
./run.sh bash
```

`Troubleshoot`: Please always check log on `kafka-connect` at this time. If it stop for a long time, jump to step 7 to `stop` all containers and retry from step 1. (This should happen once only)

6. Jupyter Lab and Notebook can be accessed at http://localhost:8888 but make sure you're not running any other notebook in your machine (otherwise it will block UI access to the running notebook inside the container). For Dash app, please access http://localhost:8050

7. After finish running, `stop` all the containers

```bash
./run.sh stop
```

or `clean` everything

```bash
./run.sh clean
```

## 🧱 Pipeline's containers and architecture

<div align="center">
  <img src="https://i.imgur.com/r4qZb9N.png" alt="docker-container">
</div>

### API Description

- OpenWeather API will retrieve the weather data from 3 cities: `Thanh pho Ho Chi Minh, VN`, `Singapore, SG`, and `Sydney, AU`.
- Faker Python library will generate fake data in the context of registered users on their car with 10 data fields.
- Binance API will allow websocket streaming the KLine (Candlestick) data of 1 minute interval from 2 pairs `BTCUSDT` and `ETHUSDT`.

### Visualization

To get the best visualization result, the pipeline must collect enough data for at least two hours. For `Jupyter Notebook`, basic EDA on each dataset is performed (line chart, boxplot, and histogram). For cryptocurrency price, I tried to fit into [Prophet](https://facebook.github.io/prophet/) to predict the future price based on time-series model. However, the collected data is not enough to get an accurate and meaningful result.

`Dash app` is also developed for OLHCV cryptocurrency chart. I tried to apply Bollinger Bands as a technical indicator for the chart but it didn't look good with data collected less than 1 hours. Below is an example of 5-minute interval chart (need resampling from time-series data) and having the indicator after more than 2 hours

<div align="center">
  <img src="https://i.imgur.com/Yvrq6Na.png" alt="docker-container">
</div>
