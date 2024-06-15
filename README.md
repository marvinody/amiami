# Amiami API

A simple api wrapper around the amiami site.

Simple usage can be something like

```python
import amiami

results = amiami.search("fumofumo plush")
for item in results.items:
  print("{}, {}".format(item.productName, item.availability))
```

By default the above will lag because it searches for EVERYTHING so it may time out your script.
If you want to go through the pages yourself (for large queries), you can try the following
```python
results = amiami.searchPaginated("fumofumo plush")
# results will have up to 30 items at this point. To see if you need to fetch more, you can check the .hasMore property
while results.hasMore:
  rs.searchNextPage()
```
That will simulate the regular search function, but in your loop, you could cut if off if `results.currentPage > 10` or `len(results.items) > 100` whatever other criteria you would like.

You can pass a proxy like in [requests](https://pypi.org/project/curl-cffi/) by passing in a keyed parameter
```python
proxies = {"https": "http://localhost:3128"}
results = amiami.searchPaginated("fumofumo plush", proxies=proxies)
```


Sometimes items tend to result in an unknown status because the flag -> state parsing is a bit rough. These items will be added to the list with a status of `Unknown status?`. They will also print out a message with the flags and item code. Good to check your log and see what's going on.

