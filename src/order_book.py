import sys

class Order:
  def __init__(self, id, timestamp, shares, next_order, prev_order, parent_limit):
    self.id = id
    self.timestamp = timestamp
    self.shares = shares
    self.next_order = next_order
    self.prev_order = prev_order
    self.parent_limit = parent_limit

  def set_next(self, next):
    self.next_order = next

  def set_prev(self, prev):
    self.prev_order = prev

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


def main():
  for line in sys.stdin:
    print(line.strip())

if __name__ == '__main__':
  main()
