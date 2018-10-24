# Limit Order Book
A limit order book and matching engine written in Python. 
## Design
Written as a proof-of-concept for achieveing great average-case performance, the bid and ask order books are implemented as sepearate AVL trees. Inspired by the HFT orderbook writeup by WK Selph [1], the limit levels are stored as nodes inside the trees, with each node itself being a doubly-linked list of orders, sorted chronologically.
## Performance
The design of the Order and Limit classes make assumptions about the format of transactions and are currently based off modified market data released by RGM Advisors [2]. Processing ~1.2 million transactions takes ~5 seconds on a Intel Core i5-6200U CPU @ 2.8GHz, for an average of ~240,000 transactions per second!
## Running
Sample transaction data is included in `data/pricer.in.gz`. From the root of the repository, run the following commands:
1. `gzip -d data/pricer.in.gz` (or similar depending on the OS)
2. `python3 src/order_book.py < data/pricer.in`
## Debugging
Included in `order_book.py` is a method `validate(tree)` that will recursively verify the correctness of a given AVL tree. Inside the main method, two lines `#assert(validate(book.sell_tree))` and `#assert(validate(book.buy_tree))` can be uncommented to verify the AVL tree after every transaction. Note, this incurs a significant performance cost, lowering the average processing speed to ~3000 transactions per second!
## References
[1] https://web.archive.org/web/20110219163448/http://howtohft.wordpress.com/2011/02/15/how-to-build-a-fast-limit-order-book/

[2] https://web.archive.org/web/20161116104649/http://rgmadvisors.com/problems/orderbook/

(Both of the original websites are no longer available at their original location)
