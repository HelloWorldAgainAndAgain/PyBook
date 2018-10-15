"""

MIT License

Copyright (c) 2018 Arvin Bhathal

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.

--------------------------------------------------------------------------------


Limit Order Book

3 main operations:
  add
  cancel/reduce
  execute

answer following questions:
  what are the best bid and ask
  how much volume is there between prices A and B
  what is order X's current position in the book

most activity is add and cancel, execute much less

add places order at the end of list at a particular limit price
cancel removes order from anywhere in the book
execution removes an order from the inside of the book (oldest buy order at the highest price and oldest sell order at the lowest price)

Order
  int idNumber;
  bool buyOrSell;
  int shares;
  int limit;
  int entryTime;
  int eventTime;
  Order *nextOrder;
  Order *prevOrder;
  Limit *parentLimit;

Limit  // representing a single limit price
  int limitPrice;
  int size;
  int totalVolume;
  Limit *parent;
  Limit *leftChild;
  Limit *rightChild;
  Order *headOrder;
  Order *tailOrder;

Book
  Limit *buyTree;
  Limit *sellTree;
  Limit *lowestSell;
  Limit *highestBuy;

balanced binary tree of Limit objects sorted by limitPrice -> doubly linked list of Order objects
buy and sell Limits in separate trees, so inside of corresponds to end of buy tree and beginning of sell tree
each Order is in a map keyed off idNumber
each Limit is in a map keyed off limitPrice

Add - O(logM) for the first order at a limit, O(1) for all others
Cancel - O(1)
Execute - O(1)
GetVolumeAtLimit - O(1)
GetBestBid/Offer - O(1)
where M is the number of price Limits (<< N the number of order)
"""
import sys

order_map = {}

class Order:
  def __init__(self, id, timestamp, shares, price, is_bid):
    self.id = id
    self.timestamp = timestamp
    self.price = price
    self.is_bid = is_bid
    self.shares = shares
    self.next_order = None
    self.prev_order = None
    self.parent_limit = None

  def reduce(self, shares_reduction):
    if shares_reduction >= self.shares:
      self.cancel()
    else:
      self.shares -= shares_reduction

  def cancel(self):
    if self.prev_order:
      self.prev_order.set_next(self.next_order)
      if self.next_order:
        self.next_order.set_prev(self.prev_order)
      else:
        self.parent_limit.set_tail(self.prev_order)
    else:
      self.parent_limit.set_head(self.next_order)
      if self.next_order:
        self.next_order.set_prev(None)
      else:
        self.parent_limit.set_tail(None)
    del self


class Limit:
  def __init__(self, price):
    self.price = price
    self.size = 0
    self.total_volume = 0
    self.height = 1
    self.parent = None
    self.left_child = None
    self.right_child = None
    self.head_order = None
    self.tail_order = None

  def add(self, order):
    if not head_order:
      self.head_order = order
      self.tail_order = order
    else:
      self.tail_order.set_next(order)
      order.set_prev(self.tail_order)
      self.tail_order = order
    self.size += 1
    self.total_volume += order.get_shares()


class LimitTree:
  def __init__(self):
    self.root = None

  def insert(self, limit):
    if not self.root:
      self.root = limit
    else:
      ptr = self.root
      parent = None
      while ptr is not None:
        if limit.price < ptr.price:
          parent = ptr
          ptr = ptr.left_child
        else:
          parent = ptr
          ptr = ptr.right_child
      ptr = limit
      ptr.parent = parent
      if self.is_left_child(ptr, parent):
        parent.left_child = ptr
      else:
        parent.right_child = ptr



class Book:
  buy_tree = LimitTree()
  sell_tree = LimitTree()
  lowest_sell = None
  highest_buy = None

  def add_order(self, order):
    if order.is_bid:
      if self.lowest_sell <= order.get_price():
        while True:

    else:
      book = sell_tree
    global order_map
    if order.get_price

def main():
  global order_map
  book = Book()
  for line in sys.stdin:
    #line = line.strip()
    fields = line.split()
    if fields[1] == 'A':
      order = Order(fields[2], fields[0], fields[5], fields[4], fields[3])
      book.add_order(order)
      #print(order.get_shares())
    #print(line.strip())

if __name__ == '__main__':
  main()
