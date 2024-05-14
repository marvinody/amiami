import os
import os
import json


# Simple script that loads search_results.json and prints out certain boolean flags
# Get the directory of the current script
script_dir = os.path.dirname(os.path.realpath(__file__))

# Join the script directory with the relative path
file_path = os.path.join(script_dir, "../data/search_results.json")


all_flags = [
  "saleitem",
  "condition_flg",
  "list_preorder_available",
  "list_backorder_available",
  "list_store_bonus",
  "list_amiami_limited",
  "instock_flg",
  "order_closed_flg",
  "preorderitem",
  "saletopitem",
  "resale_flg",
  "preowned_sale_flg",
  "buy_flg",
  "stock_flg",
]

stock_types = [
   "instock",
   "orderclosed",
   "preorder",
   "preorderclosed",
   "preowned",
]

def load_correct_stock_types():
    # go into data/instock, data/orderclosed, etc folders and look at the file names inside
    # the file names inside are the product ids
    dir_path = os.path.join(script_dir, "../data")
    # make a map of product ids to stock types
    product_id_to_stock_type = {}
    for stock_type in stock_types:
        stock_dir = os.path.join(dir_path, stock_type)
        for file_name in os.listdir(stock_dir):
            product_id = file_name.split(".")[0]
            product_id_to_stock_type[product_id] = stock_type
    return product_id_to_stock_type

def determine_stock_type(product):
    inStock = product['instock_flg'] == 1
    # is_closed seems to reflect whether or not the item is actually closed
    isClosed = product['order_closed_flg'] == 1
    # the next 2 seemed simple enough
    isPreorder = product['preorderitem'] == 1
    isBackorder = product['list_backorder_available'] == 1
    # this was found by looking at the filter they provide and seeing the
    # s_st_condition_flag query they pass. Not sure entirely yet, but seems
    # to be ok so far?
    isPreOwned = product['condition_flg'] == 1
    availability = "Unknown status?"
    if isClosed:
        if isPreorder:
            availability = "Pre-order Closed"
        elif isBackorder:
            availability = "Back-order Closed"
        else:
            availability = "Order Closed"
    elif isBackorder:
        availability = "Back-order"
    else:
        if isPreorder and inStock:
            availability = "Pre-order"
        if isPreorder and not inStock:
            availability = "Pre-order Closed"
        elif isPreOwned and inStock:
            availability = "Pre-owned"
        elif inStock:
            availability = "Available"
    return availability

def determine_stock_type_new(product):
    isSale = product['saleitem'] == 1
    isLimited = product['list_store_bonus'] == 1 or product['list_amiami_limited'] == 1
    isPreowned = product['condition_flg'] == 1
    isPreorder = product['preorderitem'] == 1
    isBackorder = product['list_backorder_available'] == 1
    isClosed = product['order_closed_flg'] == 1
    availability = "Unknown status?"
    if isClosed:
        if isPreorder:
            availability = "Pre-order Closed"
        elif isBackorder:
            availability = "Back-order Closed"
        else:
            availability = "Order Closed"
    else:
        if isPreorder:
            availability = "Pre-order"
        elif isBackorder:
            availability = "Back-order"
        elif isPreowned:
            availability = "Pre-owned"
        elif isSale:
            availability = "On Sale"
        elif isLimited:
            availability = "Limited"
        else:
            availability = "Available"

    return availability

def check_stock_types():
    product_id_to_stock_type = load_correct_stock_types()
    with open(file_path, "r") as file:
        data = json.load(file)
        for product in data["items"]:
            actual_stock_type = determine_stock_type(product)
            actual_stock_type_new = determine_stock_type_new(product)
            expected_stock_type = product_id_to_stock_type.get(product["gcode"])
            print(f"Product: {product['gcode']}")
            print(f"\tExpected: {expected_stock_type}")
            print(f"\tActual: {actual_stock_type}")
            print(f"\tNewAlgo: {actual_stock_type_new}")
                
    
           

def loginfo():
    # Check if the file exists
    if not os.path.exists(file_path):
      print("File not found:", file_path)
      return
    
    # Load the JSON data from the file
    with open(file_path, "r") as file:
      data = json.load(file)
      
      # Create a map for each flag to count the number of times it's 1
      flag_counts = {flag: 0 for flag in all_flags}

      # Iterate over each product in the data
      for product in data["items"]:
        # Iterate over each flag in the product
        for flag in all_flags:
          # If the flag is 1, increment the count
          if product[flag] == 1:
            flag_counts[flag] += 1

      # Print the counts for each flag
      for flag, count in flag_counts.items():
        print(f"{flag}: {count}") 




if __name__ == "__main__":
    # loginfo()
    check_stock_types()