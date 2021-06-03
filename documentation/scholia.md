# Visualizations produced by Scholia

All visualizations in this project are dereived from [Scholia](https://github.com/fnielsen/scholia) and [Wikidata Query GUI](https://github.com/wikimedia/wikidata-query-gui)

## Scholia Visualizations

<br>
<div style="text-align:center"><img src="authors-year.png" width="75%" /></div>
<br>

Scholia visualizations are defined through `sparql` files in the `data-visualization` folder.
The following visualizations/queries are currently available:


* [Members of a research cluster](../data-visualization/scholia/app/templates/cluster_cluster-members.sparql) - tabular format
* [Publications for a research cluster](../data-visualization/scholia/app/templates/cluster_publications.sparql) - tabular format
* [Veneu statistics for a research cluster](../data-visualization/scholia/app/templates/cluster_venue-statistics.sparql) - bubble chart
* [Veneu statistics for a research cluster](../data-visualization/scholia/app/templates/cluster_venue-year-stats.sparql) - tabular format
* [Publications per year for a research cluster](../data-visualization/scholia/app/templates/cluster_publications-per-year.sparql) - bar chart
* [Publications per year and per author for a research cluster](../data-visualization/scholia/app/templates/cluster_publications-per-year-and-author.sparql) - bar chart
* [Publication citations per year](../data-visualization/scholia/app/templates/work_citations-per-year.sparql) - bar chart
* [Topic score for a publication](../data-visualization/scholia/app/templates/work_topic-scores.sparql) - buble chart


When running these queries, note that they have query arguments. Any argument with curly braces such as `{{ q }}` are dynamically modified at the moment a Web page is requested. 


For example, for the [landing page](../data-visualization/scholia/app/views.py#L87-98), we explicitly define that `q = Q106489997`, which for the [publications per year for a research cluster](../data-visualization/scholia/app/templates/cluster_publications-per-year.sparql) visualization would produce the query:


```SQL
#defaultView:BarChart
select ?year (count(?work) as ?number_of_publications) where {
  {
    select (str(?year_) as ?year) (0 as ?pages) where {
      # default values = 0
      ?year_item wdt:P31 wd:Q577 . 
      ?year_item wdt:P585 ?date .
      bind(year(?date) as ?year_)
      {
        select (min(?year_) as ?earliest_year) where {
          ?work wdt:P50 ?author .
          ?author wdt:P463 wd:Q106489997 . 
          ?work wdt:P577 ?publication_date . 
          bind(year(?publication_date) as ?year_)
        }
      }
      bind(year(now()) as ?next_year)
      filter (?year_ >= ?earliest_year && ?year_ <= ?next_year)
    }
  }
  union {
    select ?work (min(?years) as ?year) where {
      ?work wdt:P50 ?author .
      ?author wdt:P463 wd:Q106489997 . 
      ?work wdt:P577 ?publication_date . 
      ?work wdt:P577 ?dates .
      bind(str(year(?dates)) as ?years) .
    }
    group by ?work 
  }
}
group by ?year 
order by ?year
```

___


To find all the sparql queries in the project, run: 

```shell
find data-visualization -name "*.sparql"
```

Note that we do not show all the visualization/queries in this document because some of them are also available in the original [Scholia](https://github.com/fnielsen/scholia) GitHub repo.




## Custom Visualizations


<br>
<div style="text-align:center"><img src="polution.png" width="75%" /></div>
<br>


These are custom visualizations that do not consume data from Wikidata. All of these visualizations rely on the [data](../data-visualization/scholia/resources/keywords_final.json) fetched in the data-gathering stage of our visualization pipeline.

> The data is copied as part of the copy instructions of [Docker](../Dockerfile)

While these visualizations are custom, we rely on the code from the [Wikidata Query GUI](https://github.com/wikimedia/wikidata-query-gui). Despite minor modifications, we do not produce the visualizations themselves, but rather just the data needed by the scripts that generate the visualizations. 

> This design decision ensures that the custom and scholia made visualizations have the same aesthetics 

The custom code to produce the data for the visualizations is available at [research_commons.py](../data-visualization/scholia/research_commons.py) and the JSON response that we create is the same as a a JSON from the Wikidata Query GUI


In detail, we produce the following data:


* [Keyword statistics](../data-visualization/scholia/research_commons.py#L29-66) --- bubble chart
* [Network visualization of keyword and related authors](../data-visualization/scholia/research_commons.py#L178-209) --- graph
* [All keywords of interest to an author](../data-visualization/scholia/research_commons.py#L212-271) --- graph


Once we produce this data, the frontend of the application will produce the right visualization.

All the scripts needed to produce the custom visualizations are available under

```shell
data-visualization/scholia/app/static/wikidata
├── AbstractChartResultBrowser.js
├── AbstractDimpleChartResultBrowser.js
├── AbstractResultBrowser.js
├── BarChartResultBrowser.js
├── BubbleChartResultBrowser.js
├── FormatterHelper.js
├── getMessage.js
├── GraphResultBrowser.js
├── GraphResultBrowserNodeBrowser.js
├── Options.js
├── ResultView.js
└── TableResultBrowser.js
```


Note that these scripts must be imported in the header of our Web templates, e.g., [](../data-visualization/scholia/app/templates/cluster.html) lines `26` to `48`