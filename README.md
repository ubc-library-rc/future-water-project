# future-water-project

Nice intro about the project and what we plan to produce

Add one or two images with visualizations that we want to produce

## Setup

1. [Download and install docker](https://docs.docker.com/get-started/)
1. [Download and install Python 3.7 or higher](https://www.python.org/downloads/)
    * You only need python locally for small tasks such as clearing the cache
1. [Download and install OpenRefine](https://openrefine.org/download.html), preferrably the stable version --- OpenRefine 3.3

## Instructions

1. Run the [python scripts](documentation/scripts.md) to fetch data
1. Upload and clean the data with [Open Refine](documentation/open-refine.md)
1. View visualizations with `TODO`


## Docker

The bulk of the project is available in a self-contained environment, aka a Docker container. Instructions on running docker are available below and also on the [python scripts](documentation/scripts.md).


1. Build the base docker container running:


```shell
cd docker/base
docker build -t libraryrc/future-waters .
```


2. Build the base docker container running:


```shell
docker build -t libraryrc/future-waters .
```

3. Run the container

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

4. Change file permissions at output folder

```shell
sudo chown -R $USER:$USER resources
```


5. Important

If there are updates on the python scripts, you must build a new image to reflect these changes on the container. Run:


```shell
docker rm libraryrc/future-waters
```

Repeat steps `1.` to `3.` afterwards


6. Helpful for development environment:

Remove last container, build and run new version in a single command

```shell
docker rm future-waters && \
docker build -t libraryrc/future-waters . && \
docker run --name=future-waters -v /home/msarthur/Workspace/future-water-project/resources:/tmp/src/resources libraryrc/future-waters
```


___

## gibberish



Use reference in member of to state from when to when

If main topic does not work, think about how to use non-wiki data
-- this is where I'm currently at

~~Sponsor is not the best field because there are multiple grants and papers before the cluster was created~~

Disconsider relative weight ofr the time being

Do not infer a ubject if there is not one
-- done


Interesting visualization https://scholia.toolforge.org/authors/Q80,Q6135847,Q30085536

https://scholia.toolforge.org/project/Q27949537


We want P859 sponsor, so we can leverage: https://scholia.toolforge.org/project/Q27949537



https://www.wikidata.org/wiki/Q57202727  --- will be edited, successfully edited




## Most realistic approach is to:

1. do for two authors
2. see all viz

3. go back and do for reminder of the cluster.
    * It alleviates work on my end as someone else can do the open refine checks while I work on viz



# Use case

https://scholia.toolforge.org/author/Q57582079

does not get https://www.wikidata.org/wiki/Q53465413 even though Ameli A Ameli is second author

## Wikidata Research Centre

https://www.wikidata.org/wiki/Q106489997

https://www.wikidata.org/wiki/Wikidata:WikiProject_Stanford_Libraries/Data_models#Research_center_affiliated_with_a_university


## Wikidata Researchers

Example of [Ghandi](https://www.wikidata.org/wiki/Q1001) shows that `member of` can be a list

## Wikidata Publications

### Examples already on Wikidata

* [Does Wetland Location Matter When Managing Wetlands for Watershed‐Scale Flood and Drought Resilience?](https://www.wikidata.org/wiki/Q104878985)
* [A test of the effects of timing of a pulsed resource subsidy on stream ecosystems.](https://www.wikidata.org/wiki/Q39924137)

## Open Refine


