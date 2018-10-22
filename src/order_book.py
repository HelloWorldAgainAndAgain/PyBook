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

def validate(tree):
  """Validates the tree is a valid AVL tree using a recursive helper function
  
  :param tree: LimitTree instance
  :return: boolean, True if tree is a valid AVL tree, False otherwise
  """
  return rvalidate(tree.root, None, None, None, None, 0, set())

def height(node):
    """
    https://stackoverflow.com/questions/575772/the-best-way-to-calculate-the-height-in-a-binary-search-tree-balancing-an-avl
    """
    if node is None:
      return 0
    else:
      return node.height

def balance(node):
  """Checks if balance factor is valid for a Limit instance

  :param node: Limit instance
  :return: boolean, True if balance factor is valid, False otherwise
  """
  return abs(height(node.left_child) - height(node.right_child)) <= 1

def rvalidate(node, min, max, parent, left, max_height, prices):
  """Recursively checks if AVL tree rooted at this node is valid

  :param node: Limit instance
  :param min: min price of all Limit instances rooted at node
  :param max: max price of all Limit instances rooted at node
  :param parent: parent Limit instance to check pointers
  :param left: True if node is the left child of parent, False if right child; None for initial call
  :param max_height: height of the calling node, all children nodes must have a smaller height; 0 for initial call
  :param prices: set of prices seen so far, if node's price is in set there is a duplicate Limit instance in the tree
  :return: boolean, True if tree rooted at node is a valid AVL tree, False otherwise
  """
  if node is None:
    return True
  if node.price in prices:
    print('Error with price')
    return False
  else:
    prices.add(node.price)
  if max_height > 0 and node.height >= max_height:
    print('Error with height')
    return False
  if not balance(node):
    print('Error with balance')
    return False
  if node.parent is not parent:
    print('Error with parent pointer')
    return False
  if min is not None and node.price < min:
    print('Error with min')
    return False
  if max is not None and node.price > max:
    print('Error with max')
    return False
  if left is not None:
    if left:
      if parent.left_child is not node or node.parent.left_child is not node:
        print('Error with left pointer')
        return False
    else:
      if parent.right_child is not node or node.parent.right_child is not node:
        print('Error with right pointer')
        return False
  return rvalidate(node.left_child, min, node.price, node, True, node.height, prices) \
         and rvalidate(node.right_child, node.price, max, node, False, node.height, prices)


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
      self.parent_limit.total_volume -= self.shares
    else:
      self.shares -= shares_reduction
      self.parent_limit.total_volume -= shares_reduction

  def cancel(self):
    self.parent_limit.size -= 1
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
  def __str__(self):
    left = 'None' if self.left_child is None else str(self.left_child.price)
    right = 'None' if self.right_child is None else str(self.right_child.price)
    return left + '--' + str(self.price) + '--' + right

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
    self.size = 0

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

  def successor(self, node):
    """Returns the inorder successor of the node

    :param node: Limit instance
    :return: In-order successor of input if it exists or None otherwise
    """
    if node is None:
      return None
    if node.right_child is not None:
      succ = node.right_child
      while succ.left_child is not None:
        succ = succ.left_child
      return succ
    else:
      p = node.parent
      while p is not None:
        if node is not p.right_child:
          break
        node = p
        p = p.parent
      return p
    
  def predecessor(self, node):
    """Returns the inorder predecessor of the node

    :param node: Limit instance
    :return: In-order predecessor of input if its exists or None otherwise
    """
    if node is None:
      return None
    if node.left_child is not None:
      pred = node.left_child
      while pred.right_child is not None:
        pred = pred.right_child
      return pred
    else:
      p = node.parent
      while p is not None:
        if node is not p.left_child:
          break
        node = p
        p = p.parent
      return p

  
class Book:
  buy_tree = LimitTree()
  sell_tree = LimitTree()
  lowest_sell = None
  highest_buy = None
  buy_map = {}
  sell_map = {}
  buy_levels = {}
  sell_levels = {}

  def reduce_order(self, uid, shares):
    """Reduce an order by the specified shares and remove order is necessary

    :param uid: uid of the Order to modify
    :param shares: amount of shares to reduce order
    :return:
    """
    if uid in self.buy_map:
      order = self.buy_map[uid]
      limit = self.buy_levels[order.price]
      order.reduce(shares)
      if order.shares == 0:
        del self.buy_map[uid]
      if limit.size == 0:
        self.buy_tree.size -= 1
      if order.price == self.highest_buy:
        self.update_highest_buy(limit)
    elif uid in self.sell_map:
      order = self.sell_map[uid]
      limit = self.sell_levels[order.price]
      order.reduce(shares)
      if order.shares == 0:
        del self.sell_map[uid]
      if limit.size == 0:
        self.sell_tree.size -= 1
      if order.price == self.lowest_sell:
        self.update_lowest_sell(limit)
    else:
      return
    self.update_book()

  def update_highest_buy(self, limit):
    """Update the highest buy by finding the predecessor of the old highest

    :param limit: Limit instance to start at
    :return:    
    """
    if limit.size == 0:
      #predecessor case
      limit = self.buy_tree.predecessor(limit)
      if limit is None:
        #no predecessor
        self.highest_buy = None
      else: # have a predecessor but dont know if it has order or not
        if limit.size == 0: #limit has no order but other limits in the tree might have orders
          if self.buy_tree.size == 0: #we know no other limits have an order
            self.highest_buy = None
          else: #other limits have an order
            while limit.size == 0:
              limit = self.buy_tree.predecessor(limit)
            #now our limit has a valid order
            self.highest_buy = limit.price
        else: #found valid pred
          self.highest_buy = limit.price 

  def update_lowest_sell(self, limit):
    """Update the lowest sell by finding the successor of the old lowest

    :param limit: Limit instance to start at
    :return:
    """
    if limit.size == 0:
      #successor case
      limit = self.sell_tree.successor(limit)
      if limit is None:
        #no successor
        self.lowest_sell = None
      else: #have a successor, but dont know if it has orders or not
        if limit.size == 0:#limit has no orders but other limits in the tree might have orders
          if self.sell_tree.size == 0: #we know, no other limits have an order
            self.lowest_sell = None
          else: #other limits have an order
            while limit.size == 0:
              limit = self.sell_tree.successor(limit)
            # now our limit has a valid order, and we've found the first valid successor
            self.lowest_sell = limit.price
        else: #limit has an order, we found the valid successor!
          self.lowest_sell = limit.price

  def execute_trade(self, sell, buy):
    """Execute trade

    :param sell: Sell Order instance
    :param buy: Buy Order instance
    :return:
    """
    if sell.shares > buy.shares:
      diff = min(sell.shares, buy.shares)
      buy.reduce(diff)
      sell.reduce(diff)
      del self.buy_map[buy.uid]
      # new highest buy may be at the same limit or the predecessor
      limit = buy.parent_limit
      if limit.size == 0:
        self.buy_tree.size -= 1
      self.update_highest_buy(limit)        
    elif sell.shares < buy.shares:
      diff = min(sell.shares, buy.shares)
      buy.reduce(diff)
      sell.reduce(diff)
      del self.sell_map[sell.uid]
      #new lowest sell may be at the same limit or successor
      limit = sell.parent_limit
      if limit.size == 0:
        self.sell_tree.size -= 1
      self.update_lowest_sell(limit)
    else: #equal
      buy.reduce(buy.shares)
      sell.reduce(sell.shares)
      del self.buy_map[buy.uid]
      del self.sell_map[sell.uid]
      limit = buy.parent_limit
      if limit.size == 0:
        self.buy_tree.size -= 1
      self.update_highest_buy(limit)
      limit = sell.parent_limit
      if limit.size == 0:
        self.sell_tree.size -= 1
      self.update_lowest_sell(limit)

  def update_book(self):
    """Update the order book, executing any trades that are now possible

    :param:
    :return:
    """
    while self.lowest_sell is not None and self.highest_buy is not None and self.lowest_sell <= self.highest_buy:
      sell = self.sell_levels[self.lowest_sell].head_order
      buy = self.buy_levels[self.highest_buy].head_order
      self.execute_trade(sell, buy)
      
  def add_order(self, order):
    """Add an order to the correct tree at the correct Limit level

    :param order: Order instance
    :return:
    """
    if order.is_bid:
      if order.price in self.buy_levels:
        limit = self.buy_levels[order.price]
        if limit.size == 0:
          self.buy_tree.size += 1
        limit.add(order)
        self.buy_map[order.uid] = order
        order.parent_limit = limit
      else:
        limit = Limit(order.price)
        limit.add(order)
        self.buy_map[order.uid] = order
        self.buy_tree.insert(limit)
        self.buy_tree.size += 1
        self.buy_levels[order.price] = limit
        order.parent_limit = self.buy_levels[order.price]
      if self.highest_buy is None or order.price > self.highest_buy:
        self.highest_buy = order.price
    else:
      if order.price in self.sell_levels:
        limit = self.sell_levels[order.price]
        if limit.size == 0:
          self.sell_tree.size += 1
        limit.add(order)
        self.sell_map[order.uid] = order
        order.parent_limit = self.sell_levels[order.price]
      else:
        limit = Limit(order.price)
        limit.add(order)
        self.sell_map[order.uid] = order
        self.sell_tree.insert(limit)
        self.sell_tree.size += 1
        self.sell_levels[order.price] = limit
        order.parent_limit = self.sell_levels[order.price]
      if self.lowest_sell is None or order.price < self.lowest_sell:
        self.lowest_sell = order.price
    self.update_book()

def main():
  start = timer()
  book = Book()
  count = 1
  for line in sys.stdin:
    fields = line.split()
    if fields[1] == 'A':
      order = Order(fields[2], int(fields[0]), int(fields[5]), float(fields[4]), True if fields[3] == 'B' else False)
      book.add_order(order)
    elif fields[1] == 'R':
      book.reduce_order(fields[2], int(fields[3]))
    count += 1

    # the below asserts verify the correctness of the AVL tree after every transaction
    #assert(validate(book.sell_tree))
    #assert(validate(book.buy_tree))
  end = timer()
  total = end - start
  print('Processed {} transactions in {:.2f} seconds, for an average of {} transactions/second'.format(count, total, int(count/total)))

if __name__ == '__main__':
  main()


