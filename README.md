# future-water-project

Nice intro about the project and what we plan to produce

Add one or two images with visualizations that we want to produce

## Setup

1. [Download and install docker](https://docs.docker.com/get-started/)
1. [Download and install Python 3.7 or higher](https://www.python.org/downloads/)
    * You only need python locally for small tasks such as clearing the cache
1. [Download and install OpenRefine](https://openrefine.org/download.html), preferably the stable version --- OpenRefine 3.3

## Instructions

1. Run the [python scripts](documentation/scripts.md) to fetch data
1. Upload and clean the data with Open Refine
    * [authors](documentation/open-refine.md)
    * [papers](documentation/open-refine-papers.md)
1. View visualizations with `scholia`


## Docker

The bulk of the project is available in a self-contained environment, aka a Docker container. Instructions on running docker are available below and also on the [python scripts](documentation/scripts.md).


### Data Gathering


1. Build the base docker container running:


```shell
cd data-gathering
docker build -t libraryrc/future-waters .
```

2. Create the container

First get the path where you downloaded the project

```shell
pwd
```

The output will be something similar to  `/home/msarthur/Workspace/future-water-project`

Update the path in the volume argument in the command below. `-v /home/msarthur/Workspace/future-water-project/resources:/tmp/src/resources`


```shell
docker run --name=future-waters -v <your path>/resources:/tmp/src/resources libraryrc/future-waters
```

For example, for the output path that I got, the volume path should read

3. Change file permissions at output folder

```shell
sudo chown -R $USER:$USER resources
```

4. Running the container after its creation


You need to remove previous named containers with the `future-waters` identifier. Run

```shell
docker rm future-waters && docker run --name=future-waters -v <your path>:/tmp/src/resources libraryrc/future-waters
```

For example:

```shell
docker rm future-waters && docker run --name=future-waters -v /home/msarthur/Workspace/future-water-project/data-gathering/resources:/tmp/src/resources libraryrc/future-waters
```

5. Important

If there are updates on the python scripts, you must build a new image to reflect these changes on the container. Run:

```shell
docker rm future-waters
```

Repeat steps `1.` to `4.` afterwards


6. Helpful for development environment:

Remove last container, build and run new version in a single command

docker rm future-waters && \
docker build -t libraryrc/future-waters . && \
docker run --name=future-waters -v <your path>:/tmp/src/resources libraryrc/future-waters


For example:

```shell
docker rm future-waters && \
docker build -t libraryrc/future-waters . && \
docker run --name=future-waters -v /home/msarthur/Workspace/future-water-project/data-gathering/resources:/tmp/src/resources libraryrc/future-waters
```




### Data Visualization

**IMPORTANT** all other docker commands are executed inside a specifi folder. This command should **run in the project root folder**

1. Build the container

```shell
docker build -t libraryrc/future-waters-viz .
```

2. Run the container

```shell
docker run --name=future-waters-viz -p 8100:8100  libraryrc/future-waters-viz
```

3. Subsequent executions:


```
docker rm future-waters-viz && \
docker run --name=future-waters-viz -p 8100:8100  libraryrc/future-waters-viz
```

4. Helpful for development environment:

Remove last container, build and run new version in a single command


```shell
docker rm future-waters-viz && \
docker build -t libraryrc/future-waters-viz . && \
docker run --name=future-waters-viz -p 8100:8100  libraryrc/future-waters-viz
```


