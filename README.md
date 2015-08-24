# AP-Rework-Comparator
Compare all the AP items and champions performance before and after the AP rework.

Watch it running here: [**AP Rework Comparator Website**](http://scappz.github.io/AP-Rework-Comparator)

## How it works
First we run the script `apcomparison/extractor.py` to get all the matches information from the API. It will take days, so you better sit tight.

After all the data has been gathered, we run `apcomparison/summary_champs.py` and `apcomparison/summary_items.py` to process it all and get the summarized information that we want.

Now is turn to run `apcomparison/database_to_file.py` to generate the json files we will be using in our website.

You can see the results here: [**AP Rework Comparator Website**](http://scappz.github.io/AP-Rework-Comparator)
