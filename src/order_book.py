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

https://rosettacode.org/wiki/AVL_tree#Python 
  balancing

http://www.mathcs.emory.edu/~cheung/Courses/323/Syllabus/Trees/AVL-insert.html#tri-node
  balancing
"""
import sys
from timeit import default_timer as timer

class Order:
  def __init__(self, uid, timestamp, shares, price, is_bid):
    self.uid = uid
    self.timestamp = timestamp
    self.price = price
    self.is_bid = is_bid
    self.shares = shares
    self.next_order = None
    self.prev_order = None
    self.parent_limit = None

  def reduce(self, shares_reduction):
    if shares_reduction >= self.shares:
      self.shares = 0
      self.cancel()
    else:
      self.shares -= shares_reduction

  def cancel(self):
    if self.prev_order:
      self.prev_order.next_order = self.next_order
      if self.next_order:
        self.next_order.prev_order = self.prev_order
      else:
        self.parent_limit.tail_order = self.prev_order
    else:
      self.parent_limit.head_order = self.next_order
      if self.next_order:
        self.next_order.prev_order = None
      else:
        self.parent_limit.tail_order = None

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
    if not self.head_order:
      self.head_order = order
      self.tail_order = order
    else:
      self.tail_order.next_order = order
      order.prev_order = self.tail_order
      self.tail_order = order
    self.size += 1
    self.total_volume += order.shares


class LimitTree:
  def __init__(self):
    self.root = None

  def insert(self, limit):
    if not self.root:
      self.root = limit
    else:
      ptr = self.root
      while True:
        if limit.price < ptr.price:
          if ptr.left_child is None:
            ptr.left_child = limit
            ptr.left_child.parent = ptr
            new = ptr.left_child
            break
          else:
            ptr = ptr.left_child
            continue
        else:
          if ptr.right_child is None:
            ptr.right_child = limit
            ptr.right_child.parent = ptr
            new = ptr.right_child
            break
          else:
            ptr = ptr.right_child
            continue
      self.update_height(new) #update heights of nodes up the path to the root
      x = y = z = new
      while x is not None:
        if abs(self.height(x.left_child) - self.height(x.right_child)) <= 1:
          z = y
          y = x
          x = x.parent
        else:
          break
      if x is not None:
        self.rebalance(x, y, z)

  def rebalance(self, x, y, z):
    """
    http://www.mathcs.emory.edu/~cheung/Courses/323/Syllabus/Trees/AVL-insert.html
    """
    z_is_left_child = z is y.left_child
    y_is_left_child = y is x.left_child
    if z_is_left_child and y_is_left_child:
      a = z
      b = y
      c = x
      t0 = z.left_child
      t1 = z.right_child
      t2 = y.right_child
      t3 = x.right_child
    elif not z_is_left_child and y_is_left_child:
      a = y
      b = z
      c = x
      t0 = y.left_child
      t1 = z.left_child
      t2 = z.right_child
      t3 = x.right_child
    elif z_is_left_child and not y_is_left_child:
      a = x
      b = z
      c = y
      t0 = x.left_child
      t1 = z.left_child
      t2 = z.right_child
      t3 = y.right_child
    else:
      a = x
      b = y
      c = z
      t0 = x.left_child
      t1 = y.left_child
      t2 = z.left_child
      t3 = z.right_child

    if x is self.root:
      self.root = b
      self.root.parent = None
    else:
      x_parent = x.parent
      if x is x_parent.left_child:
        b.parent = x_parent
        x_parent.left_child = b
      else:
        b.parent = x_parent
        x_parent.right_child = b
    b.left_child = a
    a.parent = b
    b.right_child = c
    c.parent = b

    a.left_child = t0
    if t0 is not None:
      t0.parent = a
    a.right_child = t1
    if t1 is not None:
      t1.parent = a

    c.left_child = t2
    if t2 is not None:
      t2.parent = c
    c.right_child = t3
    if t3 is not None:
      t3.parent = c
    self.update_height(a)
    self.update_height(c)


  def update_height(self, node):
    """
    http://www.mathcs.emory.edu/~cheung/Courses/323/Syllabus/Trees/AVL-insert.html#tri-node
    """
    while node is not None:
      node.height = 1 + max(self.height(node.left_child), self.height(node.right_child))
      node = node.parent

  def height(self, node):
    """
    https://stackoverflow.com/questions/575772/the-best-way-to-calculate-the-height-in-a-binary-search-tree-balancing-an-avl
    """
    if node is None:
      return 0
    else:
      return node.height


class Book:
  buy_tree = LimitTree()
  sell_tree = LimitTree()
  lowest_sell = None
  highest_buy = None
  buy_map = {}
  sell_map = {}
  buy_levels = {}
  sell_levels = {}

  def reduce_order(self, order_id, amount):
    if order_id in self.buy_map:
      self.buy_map[order_id].reduce(amount)
      if self.buy_map[order_id].shares == 0:
        del self.buy_map[order_id]
    elif order_id in self.sell_map:
      self.sell_map[order_id].reduce(amount)
      if self.sell_map[order_id].shares == 0:
        del self.sell_map[order_id]

  def add_order(self, order):
    if order.is_bid:
      if order.price in self.buy_levels:
        self.buy_levels[order.price].add(order)
        self.buy_map[order.uid] = order
        order.parent_limit = self.buy_levels[order.price]
      else:
        limit = Limit(order.price)
        limit.add(order)
        order.parent_limit = limit
        self.buy_map[order.uid] = order
        self.buy_tree.insert(limit)
        self.buy_levels[order.price] = limit
    else:
      if order.price in self.sell_levels:
        self.sell_levels[order.price].add(order)
        self.sell_map[order.uid] = order
        order.parent_limit = self.sell_levels[order.price]
      else:
        limit = Limit(order.price)
        limit.add(order)
        order.parent_limit = limit
        self.sell_map[order.uid] = order
        self.sell_tree.insert(limit)
        self.sell_levels[order.price] = limit


def main():
  start = timer()
  book = Book()
  #sys.stdin = open('/dev/tty'); import pdb; pdb.set_trace()
  for line in sys.stdin:
    fields = line.split()
    #print(fields)
    if fields[1] == 'A':
      order = Order(fields[2], int(fields[0]), int(fields[5]), float(fields[4]), True if fields[3] == 'B' else False)
      #uid, timestamp, shares, price, is_bid):
      book.add_order(order)
    elif fields[1] == 'R':
      book.reduce_order(fields[2], int(fields[3]))
  print(book.sell_tree.root.height)
  print(book.buy_tree.root.height)
  end = timer()
  print(end-start)

if __name__ == '__main__':
  main()
