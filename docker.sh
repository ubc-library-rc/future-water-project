#!/bin/bash

#echo "Starting tor browser"
#tor -f ./torrc &
#sleep 15
#echo -e "\U1F680"
#echo "Getting ready to lauch..."
#for counter in 1 2 3 4 5
#do
#    let timer=6-counter
#	echo "$timer"
#    sleep 0.25
#done
#echo -e "\U1F680"
#sleep 0.05
#for counter in $(seq 1 40);
#do
#    printf %${counter}s |tr " " "  "
#    echo -e "\e[1A\e[K \U1F680"
#    sleep 0.02
#done

echo "\n\nrunning python scripts"
#python3 ./test/test_pipeline_google.py
#python3 ./test/test_pipeline_crossref.py
#python3 ./test/test_pipeline_wikidata.py

echo "\n\n"
echo "----------------------------------------------"
echo "-- FORMATTING DATA TO OPEN REFINE & SCHOLIA --"
echo "----------------------------------------------"

python3 ./test/test_openrefine_authors.py
python3 ./test/test_openrefine_papers.py


#echo "\n\n \U1F680 data saved under ./resorces bye bye"