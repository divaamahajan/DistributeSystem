class Node:
    def __init__(self, data=None):
        self.data = data
        self.next = None

class SortedCircularLinkedList:
    def __init__(self):
        self.head = None
        self.tail = None

    def add_node(self, data):
        node = Node(data)

        if self.head is None:
            self.head = node
            self.tail = node
            node.next = self.head
        elif data < self.head.data:
            node.next = self.head
            self.head = node
            self.tail.next = self.head
        elif data > self.tail.data:
            node.next = self.head
            self.tail.next = node
            self.tail = node
        else:
            curr = self.head
            while curr.next.data < data:
                curr = curr.next
            node.next = curr.next
            curr.next = node

    def remove_node(self, data):
        if self.head is None:
            return

        curr = self.head
        prev = self.tail

        while curr.data != data:
            prev = curr
            curr = curr.next

            if curr == self.head:
                return

        if curr == self.head:
            self.head = self.head.next
            self.tail.next = self.head
        elif curr == self.tail:
            prev.next = self.head
            self.tail = prev
        else:
            prev.next = curr.next

        curr = None

    def print_list(self):
        if self.head is None:
            return

        curr = self.head

        while True:
            print(curr.data, end=' ')
            curr = curr.next

            if curr == self.head:
                break

        print()

    def get_successor(self, data):
        if self.head is None:
            return None

        curr = self.head

        while curr.data != data:
            curr = curr.next

            if curr == self.head:
                return None

        return curr.next.data

    def get_predecessor(self, data):
        if self.head is None:
            return None

        curr = self.head
        prev = self.tail

        while curr.data != data:
            prev = curr
            curr = curr.next

            if curr == self.head:
                return None

        return prev.data
    
# Create a new linked list
linked_list = SortedCircularLinkedList()

# Add some nodes to the list
linked_list.add_node(5)
linked_list.add_node(3)
linked_list.add_node(9)
linked_list.add_node(1)
linked_list.add_node(2)
linked_list.add_node(7)

# Print the list
print("Current linked list:")
linked_list.print_list()  # Output: 1->2 -> 3 -> 5 ->7 -> 9

# Remove a node from the list
linked_list.remove_node(3)

# Print the list again
print("Updated linked list:")
linked_list.print_list()  # Output: 1->2 -> 5 -> 7 -> 9

# Get the successor of a node
successor = linked_list.get_successor(9)
print(f"The successor of 9 is {successor}")  # Output: The successor of 9 is 1

# Get the predecessor of a node
predecessor = linked_list.get_predecessor(9)
print(f"The predecessor of 9 is {predecessor}")  # Output: The predecessor of 9 is 7
