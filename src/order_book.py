import sys


class Order:
  def __init__(self, id, timestamp, price, shares, next_order, prev_order):
    self.id = id
    self.timestamp = timestamp
    self.price = price
    self.shares = shares
    self.next_order = next_order
    self.prev_order = prev_order
    self.parent_limit = None

  def set_next(self, next):
    self.next_order = next

  def set_prev(self, prev):
    self.prev_order = prev

  def get_shares(self):
    return self.shares

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
  def __init__(self, limit_price, parent, left_child, right_child):
    self.limit_price = limit_price
    self.size = 0
    self.total_volume = 0
    self.parent = parent
    self.left_child = left_child
    self.right_child = right_child
    self.head_order = None
    self.tail_order = None

  def get_head(self):
    return self.head_order

  def set_head(self, head):
    self.head_order = head

  def get_tail(self):
    return self.tail_order

  def set_tail(self, tail):
    self.tail_order = tail

  def get_size(self):
    return self.size

  def set_size(self, new_size):
    self.size = new_size

  def get_volume(self):
    return self.total_volume

  def set_volume(self, new_volume):
    self.total_volume = new_volume

  def get_right(self):
    return self.right_child

  def set_right(self, new_right):
    self.right_child = new_right 

  def get_left(self):
    return self.left_child

  def set_left(self, new_left):
    self.left_child = new_left

  def get_parent(self):
    return self.parent

  def set_parent(self, new_parent):
    self.parent = new_parent

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


class Book:
  buy_tree = None
  sell_tree = None
  lowest_sell = None
  highest_buy = None

  def get_buy_tree(self):
    return self.buy_tree

  def set_buy_tree(self, buy):
    self.buy_tree = buy

  def get_sell_tree(self):
    return self.sell_tree

  def set_sell_tree(self, sell):
    self.sell_tree = sell

  def get_lowest_sell(self):
    return self.lowest_sell

  def set_lowest_sell(self, sell):
    self.lowest_sell = sell

  def get_highest_buy(self):
    return self.highest_buy

  def set_highest_sell(self, buy):
    self.highest_buy = buy

def main():
  for line in sys.stdin:
    print(line.strip())

if __name__ == '__main__':
  main()
