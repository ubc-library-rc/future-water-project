#!/bin/bash

echo "Starting tor browser" 
tor -f ./torrc &
sleep 20
echo "Getting ready to lauch..." 
echo "5"
sleep 1
echo "4"
sleep 1
echo "3"
sleep 1
echo "2"
sleep 1
echo "1"
sleep 1
echo -e "\U1F680"
echo -e "  \U1F680"
echo -e "    \U1F680"
sleep 1
echo -e "                \U1F680"
echo -e "                  \U1F680"
echo -e "                    \U1F680"
sleep 1
echo "\n\nrunning python scripts"
python3 ./test/test_pipeline_google.py
python3 ./test/test_pipeline_crossref.py
python3 ./test/test_pipeline_wikidata.py
echo "\n\n \U1F680 data saved under ./resorces bye bye"