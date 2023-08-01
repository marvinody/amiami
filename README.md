# Amiami API

A simple api wrapper around the amiami site.

Simple usage can be something like

```python
import amiami

results = amiami.search("fumofumo plush")
for item in results.items:
  print("{}, {}".format(item.productName, item.availability))
```


Sometimes items tend to result in an unknown status because the flag -> state parsing is a bit rough. These items will be added to the list with a status of `Unknown status?`. They will also print out a message with the flags and item code. Good to check your log and see what's going on.
