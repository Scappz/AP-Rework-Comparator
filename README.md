# AP-Rework-Comparator
Compare all the AP items and champions performance before and after the AP rework.

Watch it running here: [**AP Rework Comparator Website**](http://fromlosttotheriver.heliohost.org)

## How it works
First we run the script `extractor.py` to get all the matches information from the API. It will take days, so you better sit tight.

After all the data has been gathered, we run `summary_champs.py` and `summary_items.py` to process it all and get the summarized information that we want.

Now is turn to run `database_to_file.py` to generate the json files we will be using in our website.

You can see the results here: [**AP Rework Comparator Website**](http://fromlosttotheriver.heliohost.org)