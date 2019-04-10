# Amiami API

A simple api wrapper around the amiami site.

Simple usage can be something like

```python
import amiami

results = amiami.search("fumofumo plush")
for item in results.items:
  print("{}, {}".format(item.productName, item.productURL))
```
