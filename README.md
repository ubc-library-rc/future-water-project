# future-water-project





## Docker container instructions


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


4. Important

If there are updates on the python scripts, you must build a new image to reflect these changes on the container. Run:


```shell
docker rm libraryrc/future-waters
```

Repeat steps `1.` to `3.` afterwards










Write a docker container!


Check if one main subject per line works
-- doable, but there are still to many for manual lookup


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

https://www.youtube.com/watch?v=wfS1qTKFQoI
